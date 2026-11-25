"""Round 18 item 1: can threshold jitter (k*tau) be recovered from Sergent et al. 2021's published
per-subject summaries, and if so, how often would their own model comparison call "bifurcation" on
purely graded observers with the fitted parameters?

Model (one subject; one latent drives the decoder and the rating; x in dB SNR):
    theta_i ~ N(x0, tau^2)                trial threshold
    A_i     = expit(k (x - theta_i))       access in 0..1; A = 0 on noise-alone trials
    y_i     = c + D A_i + eps              decoder decision value (one window); eps ~ N(0, sn^2)
    r_i     = clip(G A_i + eta, 0, 10)     continuous audibility rating; eta ~ N(0, se^2)
    heard   = r_i >= 3                     (Sergent's audthresh = 3)
Map axis: kt = k * tau (dimensionless).

Summaries, exactly as published (SoundConsciousEEG_MNE_SingleTrialPredict.m l.777-812, 901-902, 933;
sheets "Supplementary Figure 3 col 3-4" and "Supplementary Figure 1"):
    mH[x] = mean(y | x, heard), mN[x] = mean(y | x, not heard): RAW decision values, no baseline
            subtraction (only the SD columns are baseline-subtracted; unused); NaN if a category is empty.
    aud_mean[x], aud_sd[x] (n-1) over all trials, x in {noise, -13, -11, -9, -7, -5} dB.

Estimators (prereg docs/prereg/2026-11-25_sergent_observer_jitter.md):
    P (primary):   mH, mN + aud_mean  -> x0, tau, kt, se, G, D, c
    S (secondary): aud_mean + aud_sd  -> x0, tau, kt, se, G

Commands (python -I jitter_recovery.py ...):
    pilot                          timing only
    killtest OUTDIR                recovery simulation, 4 workers (long: launched by the coordinator)
    summarise OUTDIR               re-summarise finished cells
    real CSVDIR OUTROOT            real-data fit (needs OUTROOT/killtest/killtest_summary.json)
    place OUTROOT                  graded-observer call rate at the fitted parameters (long; coordinator)
"""
import csv, hashlib, json, os, sys, time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREREG = ROOT / "docs" / "prereg" / "2026-11-25_sergent_observer_jitter.md"
AUDIT_DIR = ROOT / "experiments" / "bifurcation_specificity"

LEVELS = np.array([-13.0, -11.0, -9.0, -7.0, -5.0])      # dB SNR; noise alone handled separately
N_TRIALS = 150                                          # per level incl. noise (their Methods: mean 150)
AUDTHRESH = 3.0
# theta integral on a fixed fine grid (40-node Gauss-Hermite was off by up to 0.06 for the
# not-heard mean at the top level, where the conditioning event lies in the threshold tail)
Z = np.linspace(-8.0, 8.0, 321)
W = norm.pdf(Z)
W = W / W.sum()

KT_GRID = [0.25, 0.5, 0.75, 1.0, 1.5, 2.25, 3.0]
TAU_GRID = [1.0, 2.0, 3.0]
PASS_KT = [0.5, 0.75, 1.0, 1.5, 2.25]
SUBJ_PER_CELL = 200
N_SUBJ = 20
N_STUDIES = 2000
TOL = np.log(1.25)
PASS_RATE = 0.90
SEED = 20261801
BOUNDS = {"x0": (-25.0, 5.0), "tau": (0.1, 10.0), "kt": (0.05, 20.0), "se": (0.3, 6.0),
          "G": (2.0, 10.0), "D": (1e-3, 1e3)}
CSV_SHA = {"Supplementary_Figure_3_col_3-4.csv": "a3dcaf15d7cb50d8ce17e5f289536c64c48b32451a90d38f1d99523b84f866c0",
           "Supplementary_Figure_1.csv": "c19a1712099a891fd5d8d86aa3b39e98527b0728b21dc83d763d155159c49d13"}
LATE_WINDOWS = [5, 6, 7]       # 300-400, 400-500, 500-600 ms (their windows [50:50:250 300:100:600])


# ---------------------------------------------------------------- predictions
def _cens_moments(mu, s, a=0.0, b=10.0):
    """Mean and E[Y^2] of clip(N(mu, s^2), a, b)."""
    al, be = (a - mu) / s, (b - mu) / s
    Pa, Pb = norm.cdf(al), norm.cdf(be)
    pa, pb = norm.pdf(al), norm.pdf(be)
    mid = Pb - Pa
    m1 = a * Pa + b * (1 - Pb) + mu * mid + s * (pa - pb)
    m2 = (a * a * Pa + b * b * (1 - Pb) + (mu * mu + s * s) * mid
          + 2 * mu * s * (pa - pb) + s * s * (al * pa - be * pb))
    return m1, m2


def predict(x0, tau, kt, se, G=10.0, D=1.0, c=0.0):
    """Expected summaries: mH[5], mN[5], aud_mean[6], aud_sd[6], p_heard[6] (index 0 = noise)."""
    k = kt / tau
    A = expit(k * (LEVELS[:, None] - x0) - kt * Z[None, :])          # (5, len(Z))
    ph = norm.sf((AUDTHRESH - G * A) / se)
    w = W[None, :]
    PH = (w * ph).sum(1)
    PN = 1 - PH
    mH = c + D * (w * A * ph).sum(1) / np.maximum(PH, 1e-300)
    mN = c + D * (w * A * (1 - ph)).sum(1) / np.maximum(PN, 1e-300)
    m1, m2 = _cens_moments(G * A, se)
    E1, E2 = (w * m1).sum(1), (w * m2).sum(1)
    n1, n2 = _cens_moments(np.array([0.0]), se)
    am = np.concatenate([n1, E1])
    asd = np.sqrt(np.maximum(np.concatenate([n2, E2]) - am ** 2, 1e-12))
    p_heard = np.concatenate([[norm.sf(AUDTHRESH / se)], PH])
    return mH, mN, am, asd, p_heard


# ---------------------------------------------------------------- simulation
def simulate_subject(rng, x0, tau, kt, se, sn, G=10.0, D=1.0, c=0.0, lapse=0.0, n=N_TRIALS):
    """Trial-level simulation summarised like the published sheets. On a lapse trial the rating is
    uniform on [0, 10] (a misspecification the fit does not model)."""
    k = kt / tau
    def rate(A):
        r = np.clip(G * A + rng.normal(0, se, len(A)), 0, 10)
        lap = rng.random(len(A)) < lapse
        r[lap] = rng.uniform(0, 10, lap.sum())
        return r
    r0 = rate(np.zeros(n))
    mH, mN, am, asd = [], [], [r0.mean()], [r0.std(ddof=1)]
    for x in LEVELS:
        A = expit(k * (x - rng.normal(x0, tau, n)))
        y = c + D * A + rng.normal(0, sn, n)
        r = rate(A)
        h = r >= AUDTHRESH
        mH.append(y[h].mean() if h.any() else np.nan)
        mN.append(y[~h].mean() if (~h).any() else np.nan)
        am.append(r.mean()); asd.append(r.std(ddof=1))
    return {"mH": np.array(mH), "mN": np.array(mN), "aud_mean": np.array(am), "aud_sd": np.array(asd)}


# ---------------------------------------------------------------- fitting
def _sq(p, lo, hi):                      # unconstrained -> (lo, hi), log-scaled for positive bounds
    if lo > 0:
        return float(np.exp(np.log(lo) + (np.log(hi) - np.log(lo)) * expit(p)))
    return float(lo + (hi - lo) * expit(p))


def _unsq(v, lo, hi):
    v = min(max(v, lo + 1e-9 * (hi - lo)), hi - 1e-9 * (hi - lo))
    f = (np.log(v) - np.log(lo)) / (np.log(hi) - np.log(lo)) if lo > 0 else (v - lo) / (hi - lo)
    f = min(max(f, 1e-6), 1 - 1e-6)
    return float(np.log(f / (1 - f)))


NAMES_P = ["x0", "tau", "kt", "se", "G", "D"]
NAMES_S = ["x0", "tau", "kt", "se", "G"]


def _unpack(p, names):
    v = {n: _sq(p[i], *BOUNDS[n]) for i, n in enumerate(names)}
    v["c"] = float(p[len(names)]) if len(p) > len(names) else 0.0
    return v


def _aud_se(d):
    return np.maximum(d["aud_sd"], 0.05) / np.sqrt(N_TRIALS)


def _split_resid(v, d, wts):
    mH, mN, am, _, ph = predict(v["x0"], v["tau"], v["kt"], v["se"], v["G"], v["D"], v["c"])
    obs = np.concatenate([d["mH"], d["mN"]])
    pred = np.concatenate([mH, mN])
    ok = np.isfinite(obs)                 # empty categories (NaN) are ignored
    return obs[ok] - pred[ok], wts[ok], am, ph


def _loss_P(p, d, wts):
    v = _unpack(p, NAMES_P)
    if wts is None:   # stage A: weights from the current parameters
        ph = predict(v["x0"], v["tau"], v["kt"], v["se"], v["G"])[4]
        wts_now = N_TRIALS * np.concatenate([ph[1:], 1 - ph[1:]]) + 1.0
    else:             # stage B: weights frozen from the stage-A estimate
        wts_now = wts
    r, w, am, _ = _split_resid(v, d, wts_now)
    rss = (w * r * r).sum() / w.sum()
    za = (d["aud_mean"] - am) / _aud_se(d)
    return 0.5 * len(r) * np.log(rss + 1e-12) + 0.5 * (za * za).sum()


def _loss_S(p, d):
    v = _unpack(p, NAMES_S)
    _, _, am, asd, _ = predict(v["x0"], v["tau"], v["kt"], v["se"], v["G"])
    za = (d["aud_mean"] - am) / _aud_se(d)
    zs = (d["aud_sd"] - asd) / (np.maximum(d["aud_sd"], 0.05) / np.sqrt(2 * (N_TRIALS - 1)))
    return 0.5 * (za * za).sum() + 0.5 * (zs * zs).sum()


def _init_x0(d):
    am = d["aud_mean"][1:]
    mid = 0.5 * (d["aud_mean"][0] + am.max())
    above = np.nonzero(am >= mid)[0]
    if len(above) == 0:
        return float(LEVELS[-1])
    i = above[0]
    if i == 0:
        return float(LEVELS[0])
    f = (mid - am[i - 1]) / max(am[i] - am[i - 1], 1e-9)
    return float(LEVELS[i - 1] + f * (LEVELS[i] - LEVELS[i - 1]))


def _nm(f, p0, args):
    return minimize(f, p0, args=args, method="Nelder-Mead",
                    options={"maxiter": 4000, "maxfev": 4000, "xatol": 1e-4, "fatol": 1e-8})


def fit(d, which):
    """6-start Nelder-Mead (P: two stages, weights frozen from stage A). Returns estimates or None."""
    x0i = _init_x0(d)
    Gi = float(np.clip(d["aud_mean"].max() + 0.5, 2.5, 9.5))
    names = NAMES_P if which == "P" else NAMES_S
    if which == "P":
        lo = d["mN"][np.isfinite(d["mN"])]
        hi = d["mH"][np.isfinite(d["mH"])]
        ci = float(lo[0]) if len(lo) else 0.0
        Di = float(np.clip((hi[-1] - ci) if len(hi) else 0.5, 0.01, 100))
    best = None
    for kt0 in (0.5, 1.5, 4.0):
        for tau0 in (1.0, 2.5):
            vals = {"x0": x0i, "tau": tau0, "kt": kt0, "se": 1.5, "G": Gi}
            if which == "P":
                vals["D"] = Di
            p0 = [_unsq(vals[n], *BOUNDS[n]) for n in names] + ([ci] if which == "P" else [])
            r = _nm(_loss_P, p0, (d, None)) if which == "P" else _nm(_loss_S, p0, (d,))
            if np.isfinite(r.fun) and (best is None or r.fun < best.fun):
                best = r
    if best is None:
        return None
    if which == "P":
        v = _unpack(best.x, names)
        ph = predict(v["x0"], v["tau"], v["kt"], v["se"], v["G"])[4]
        wts = N_TRIALS * np.concatenate([ph[1:], 1 - ph[1:]]) + 1.0
        r2 = _nm(_loss_P, best.x, (d, wts))
        if np.isfinite(r2.fun):
            best = r2
        v = _unpack(best.x, names)
        res, w, _, _ = _split_resid(v, d, wts)
        v["resid_over_D"] = float(np.sqrt((w * res * res).sum() / w.sum()) / v["D"])
    else:
        v = _unpack(best.x, names)
    v["k"] = v["kt"] / v["tau"]
    # at a bound = squashed coordinate beyond +-6 (within 0.25% of the range end, in fitted scale)
    v["at_bound"] = [n for i, n in enumerate(names) if abs(best.x[i]) > 6.0]
    v["loss"] = float(best.fun)
    v["converged"] = bool(best.success)
    return v


# ---------------------------------------------------------------- kill test
def _cell_job(args):
    kt, tau, outdir, nsub = args
    path = os.path.join(outdir, f"cell_kt{kt}_tau{tau}_n{nsub}.json")
    if os.path.exists(path):
        return path
    rng = np.random.default_rng(np.random.SeedSequence([SEED, int(round(kt * 100)), int(round(tau * 10))]))
    rows = []
    for _ in range(nsub):
        # per-subject truth: cell values x exp(N(0, 0.2)); nuisances fixed a priori (prereg section 3)
        t = {"kt": kt * np.exp(rng.normal(0, 0.2)), "tau": tau * np.exp(rng.normal(0, 0.2)),
             "x0": rng.uniform(-10.5, -7.5), "se": rng.uniform(1.0, 2.5), "sn": rng.uniform(1.0, 8.0),
             "G": rng.uniform(6.0, 10.0), "c": rng.normal(0, 0.5), "lapse": rng.uniform(0.0, 0.05)}
        d = simulate_subject(rng, t["x0"], t["tau"], t["kt"], t["se"], t["sn"], t["G"], 1.0, t["c"], t["lapse"])
        t["k"] = t["kt"] / t["tau"]
        rows.append({"true": t, "P": fit(d, "P"), "S": fit(d, "S")})
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"kt": kt, "tau": tau, "rows": rows}, f)
    os.replace(tmp, path)
    return path


def group_recovery(rows, which, kt_cell, tau_cell, rng):
    est = np.array([(r[which]["kt"], r[which]["tau"]) if r[which] else (np.nan, np.nan) for r in rows])
    hit = {"kt": 0, "tau": 0, "kt_and_tau": 0, "below_0.75": 0, "above_1.5": 0}
    meds = []
    for _ in range(N_STUDIES):
        m = np.nanmedian(est[rng.choice(len(rows), N_SUBJ, replace=False)], axis=0)
        e = np.abs(np.log(m / np.array([kt_cell, tau_cell])))
        hit["kt"] += e[0] <= TOL
        hit["tau"] += e[1] <= TOL
        hit["kt_and_tau"] += (e[0] <= TOL) and (e[1] <= TOL)
        hit["below_0.75"] += m[0] < 0.75
        hit["above_1.5"] += m[0] > 1.5
        meds.append(m[0])
    out = {k: v / N_STUDIES for k, v in hit.items()}
    out["study_median_kt_q05_q50_q95"] = [float(np.quantile(meds, q)) for q in (0.05, 0.5, 0.95)]
    out["n_failed_fits"] = int(np.isnan(est[:, 0]).sum())
    out["n_at_bound"] = int(sum(1 for r in rows if r[which] and r[which]["at_bound"]))
    out["n_not_converged"] = int(sum(1 for r in rows if r[which] and not r[which]["converged"]))
    return out


def killtest(outdir, nsub=SUBJ_PER_CELL):
    assert nsub in (200, 100), "only the pre-stated 200 or the fallback 100"
    from multiprocessing import Pool
    sys.path.insert(0, str(ROOT / "experiments" / "rules"))
    from evidence import require_sealed
    require_sealed(str(PREREG)); require_sealed(str(Path(__file__)))
    os.makedirs(outdir, exist_ok=True)
    jobs = [(kt, tau, outdir, nsub) for tau in TAU_GRID for kt in KT_GRID]
    t0 = time.time()
    with Pool(4) as pool:
        for p in pool.imap_unordered(_cell_job, jobs):
            print(f"[{time.time() - t0:7.0f}s] done {os.path.basename(p)}", flush=True)
    summarise(outdir, nsub)


def summarise(outdir, nsub=SUBJ_PER_CELL):
    rng = np.random.default_rng(SEED + 1)
    res = {"subjects_per_cell": nsub, "cells": [], "verdict": {}, "envelope": {}}
    allrows = []
    for tau in TAU_GRID:
        for kt in KT_GRID:
            d = json.load(open(os.path.join(outdir, f"cell_kt{kt}_tau{tau}_n{nsub}.json")))
            c = {"kt": kt, "tau": tau}
            for w in ("P", "S"):
                c[w] = group_recovery(d["rows"], w, kt, tau, rng)
            res["cells"].append(c)
            if kt in PASS_KT:
                allrows += d["rows"]
    for w in ("P", "S"):
        core = min(c[w]["kt_and_tau"] for c in res["cells"] if c["kt"] in PASS_KT)
        low = min(c[w]["below_0.75"] for c in res["cells"] if c["kt"] == 0.25)
        high = min(c[w]["above_1.5"] for c in res["cells"] if c["kt"] == 3.0)
        res["verdict"][w] = {"worst_core_kt_and_tau": core, "worst_low_end_below_0.75": low,
                             "worst_high_end_above_1.5": high,
                             "pass": bool(core >= PASS_RATE and low >= PASS_RATE and high >= PASS_RATE)}
        # applicability envelope: 2.5-97.5% of estimates over the core cells
        env = {}
        for n in ["x0", "tau", "se", "G"] + (["resid_over_D"] if w == "P" else []):
            v = np.array([r[w][n] for r in allrows if r[w]])
            env[n] = [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))]
        res["envelope"][w] = env
    P, S = res["verdict"]["P"]["pass"], res["verdict"]["S"]["pass"]
    res["verdict"]["estimator"] = "P" if P else ("S" if S else None)
    res["verdict"]["outcome"] = ("RECOVERABLE (primary, split)" if P else
                                 "RECOVERABLE (secondary, audibility SD)" if S else
                                 "TAU NOT IDENTIFIABLE FROM SERGENT'S PUBLISHED SUMMARIES")
    with open(os.path.join(outdir, "killtest_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res["verdict"], indent=1))


# ---------------------------------------------------------------- real data
def _num(c):
    return float(c) if c not in ("", "NaN") else np.nan


def read_real(csvdir, windows=LATE_WINDOWS):
    for f, h in CSV_SHA.items():
        assert hashlib.sha256(open(os.path.join(csvdir, f), "rb").read()).hexdigest() == h, f
    R = list(csv.reader(open(os.path.join(csvdir, "Supplementary_Figure_3_col_3-4.csv"))))
    assert len(R) == 42 and R[0][0].startswith("Mean projected activity, heard trials")
    assert R[21][0].startswith("Mean projected activity, not heard trials")
    assert all(len(r) == 81 for r in R[1:21] + R[22:42])
    heard = np.array([[_num(c) for c in r[:40]] for r in R[1:21]])
    nheard = np.array([[_num(c) for c in r[:40]] for r in R[22:42]])
    A = list(csv.reader(open(os.path.join(csvdir, "Supplementary_Figure_1.csv"))))
    assert len(A) == 21 and A[0][0].startswith("Mean audibility") and A[0][8].startswith("SD of audibility")
    am = np.array([[_num(c) for c in r[0:6]] for r in A[1:21]])
    asd = np.array([[_num(c) for c in r[8:14]] for r in A[1:21]])
    # columns = window * 5 + snr; equal-length windows, so the mean of window means is the 300-600 ms mean
    win = lambda M: np.mean([M[:, w * 5:(w + 1) * 5] for w in windows], axis=0)
    H, N = win(heard), win(nheard)
    # subject order is assumed identical across the two sheets (both "lines are subjects")
    return [{"mH": H[s], "mN": N[s], "aud_mean": am[s], "aud_sd": asd[s]} for s in range(20)]


def real(csvdir, outroot):
    sys.path.insert(0, str(ROOT / "experiments" / "rules"))
    from evidence import require_sealed
    require_sealed(str(PREREG)); require_sealed(str(Path(__file__)))
    kv = json.load(open(os.path.join(outroot, "killtest", "killtest_summary.json")))
    which = kv["verdict"]["estimator"]
    res = {"killtest_outcome": kv["verdict"]["outcome"], "estimator": which}
    outdir = os.path.join(outroot, "real"); os.makedirs(outdir, exist_ok=True)
    if which is None:
        res["result"] = "TAU NOT IDENTIFIABLE FROM SERGENT'S PUBLISHED SUMMARIES (no real-data estimate made)"
    else:
        subs = read_real(csvdir)
        fits = [fit(d, which) for d in subs]
        ok = [f for f in fits if f]
        kt = np.array([f["kt"] for f in ok])
        med = float(np.median(kt))
        rng = np.random.default_rng(SEED + 2)
        boots = [np.median(rng.choice(kt, len(kt), replace=True)) for _ in range(10000)]
        lo, hi = float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))
        medians = {n: float(np.median([f[n] for f in ok])) for n in ["x0", "tau", "k", "se", "G"]
                   + (["resid_over_D"] if which == "P" else [])}
        env = kv["envelope"][which]
        outside = [n for n, (a, b) in env.items() if not (a <= medians[n] <= b)]
        n_bound = sum(1 for f in ok if f["at_bound"])
        res.update({"per_subject": fits, "n_fitted": len(ok), "median_kt": med, "ci95_kt": [lo, hi],
                    "medians": medians, "envelope": env, "outside_envelope": outside, "n_at_bound": n_bound})
        if outside or n_bound > 4 or len(ok) < 16:
            res["result"] = "OUTSIDE VALIDATED RANGE: no placement"
        else:
            res["result"] = "ESTIMATED: placement pending (run `place`)"
            res["placement_points"] = {"k_per_db": medians["k"], "x0_db": medians["x0"],
                                       "kt": {"lo": lo, "median": med, "hi": hi}}
        # descriptive only
        if which == "P":
            res["descriptive_S_median_kt"] = float(np.nanmedian([(fit(d, "S") or {"kt": np.nan})["kt"] for d in subs]))
        res["descriptive_by_window_median_kt"] = {
            name: float(np.nanmedian([(fit(d, which) or {"kt": np.nan})["kt"] for d in read_real(csvdir, [w])]))
            for w, name in [(5, "300-400"), (6, "400-500"), (7, "500-600")]}
        r3 = [json.load(open(AUDIT_DIR / "out" / f"{f}.json"))["rate_pxp3_gt_095"]
              for f in ("G_jitter_lo", "G_jitter_mid", "G_jitter_hi")]
        res["descriptive_sealed_map_3model_at_median"] = float(np.interp(med, [0.75, 1.5, 2.25], r3))
    json.dump(res, open(os.path.join(outdir, "real_result.json"), "w"), indent=1)
    print(res["result"])


# ---------------------------------------------------------------- placement (sealed machinery, fitted parameters)
PLACE_STUDIES = 300


def _place_study(args):
    km_lvl, x0_lvl, tau_lvl, seed = args
    sys.path.insert(0, str(AUDIT_DIR))
    import audit
    rng = np.random.default_rng(seed)
    lme = []
    for _ in range(audit.N_SUB):
        x, block = audit.design(rng)
        th = x0_lvl + rng.normal(0, tau_lvl, len(x))
        a = np.where(x == 0, 0.0, expit(km_lvl * (x - th)))          # noise alone: no access (as in the fit)
        y = audit.DMAX * a + rng.normal(0, 1, len(x))                   # sealed G_jitter form and SNR otherwise
        l, _ = audit.subject_lme(y, x, block)
        lme.append(l)
    lme = np.array(lme)
    if not np.all(np.isfinite(lme)):
        return float("nan")
    b = audit.spm_bms(lme, rng)
    return float(b["pxp"][2])


def place(outroot):
    from multiprocessing import Pool
    sys.path.insert(0, str(ROOT / "experiments" / "rules"))
    from evidence import require_sealed
    require_sealed(str(PREREG)); require_sealed(str(Path(__file__)))
    require_sealed(str(AUDIT_DIR / "audit.py"))
    path = os.path.join(outroot, "real", "real_result.json")
    res = json.load(open(path))
    pts = res.get("placement_points")
    if not pts:
        print("no placement:", res["result"]); return
    k, x0 = pts["k_per_db"], pts["x0_db"]
    km_lvl, x0_lvl = 2.0 * k, (x0 + 15.0) / 2.0          # level l = 1..5 <-> -13..-5 dB
    out = {}
    with Pool(4) as pool:
        for i, (name, kt) in enumerate(pts["kt"].items()):
            tau_lvl = (kt / k) / 2.0
            ss = np.random.SeedSequence([SEED + 3, i])
            seeds = [int(s.generate_state(1)[0]) for s in ss.spawn(PLACE_STUDIES)]
            pxp3 = np.array(pool.map(_place_study, [(km_lvl, x0_lvl, tau_lvl, s) for s in seeds]))
            out[name] = {"kt": kt, "tau_db": kt / k, "rate_pxp3_gt_095": float(np.mean(pxp3 > 0.95)),
                         "n_nonfinite": int(np.sum(~np.isfinite(pxp3)))}
            print(name, out[name], flush=True)
    res["placement"] = out
    if any(o["n_nonfinite"] for o in out.values()):
        res["result"] = "INVALID: non-finite model evidence in a placement study"
    elif out["hi"]["rate_pxp3_gt_095"] <= 0.05:
        res["result"] = "CALL DIAGNOSTIC: graded observers with these parameters are rarely called bifurcation"
    elif out["lo"]["rate_pxp3_gt_095"] >= 0.50:
        res["result"] = "CALL NOT DIAGNOSTIC: graded observers with these parameters are usually called bifurcation"
    else:
        res["result"] = "INTERMEDIATE: the false-call rate crosses 0.05-0.50 inside the k*tau CI"
    json.dump(res, open(path, "w"), indent=1)
    print(res["result"])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "pilot":
        rng = np.random.default_rng(1)
        t0 = time.time()
        for _ in range(4):
            d = simulate_subject(rng, -9.0, 1.5, 1.5, 1.5, 2.0, 8.0, 1.0, 0.2, 0.02)
            fit(d, "P"); fit(d, "S")
        print(f"seconds per subject (P+S): {(time.time() - t0) / 4:.2f}")
    elif cmd == "killtest":
        killtest(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else SUBJ_PER_CELL)
    elif cmd == "summarise":
        summarise(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else SUBJ_PER_CELL)
    elif cmd == "real":
        real(sys.argv[2], sys.argv[3])
    elif cmd == "place":
        place(sys.argv[2])
    else:
        raise SystemExit("unknown command")
