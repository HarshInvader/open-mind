"""How much does the late seen-trial signal jitter in latency? (Cohen et al. 2024, SOA 50, report block; zero new bytes)
Prereg: docs/prereg/2026-11-25_latency_spread_cohen.md

Settles the reading of the TG-square simulation (experiments/tg_square_specificity/RESULTS.md): a single brief code
gives a square at latency SD 50 ms (not 25), a chain of four brief codes at 75 ms (not 50).

Estimator (fixed in advance): per subject, 10-fold CV. In each fold a Ledoit-Wolf LDA spatial filter is trained on the
training trials (seen vs unseen, scalp mean 300-500 ms); the template is the training seen-minus-unseen mean of the
filtered time course over 300-500 ms; each held-out seen trial (minus the training unseen mean) is matched to the
template by cross-covariance over lags -100..+100 ms (2 ms steps). The subject statistic is the SD of the seen-trial
lags ("apparent SD"). Woody-type SDs are inflated by noise (about 58 ms for pure noise in a +-100 ms window), so the
apparent SD is only read through a per-subject calibration ladder built from the subject's own noise.

    python -I latency_spread.py shape     # group seen-unseen P3b-ROI difference wave -> Gaussian fit, topography
    python -I latency_spread.py ladder    # synthetic: planted jitter in own unseen-residual noise; nominal + 3 nuisance generators
    python -I latency_spread.py gate      # kill test: can the method tell 50 from 75? -> out/gate.json
    python -I latency_spread.py real      # only if the gate passed -> out/real.json and the verdict
    python -I latency_spread.py pilot     # unsealed runtime check on synthetic noise only; prints timing only
"""
import csv, json, os, sys, time
from pathlib import Path
from multiprocessing import Pool

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np  # noqa: E402
from scipy.signal import butter, filtfilt  # noqa: E402
from scipy.optimize import curve_fit  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COH = ROOT / "experiments" / "cohen_fixed_soa"
sys.path.insert(0, str(COH))
sys.path.insert(0, str(ROOT / "experiments" / "rules"))
import cohen_killtest as K  # noqa: E402  (constants and channel definitions only; its functions are not changed)

OUT = HERE / "out"
PREREG = ROOT / "docs" / "prereg" / "2026-11-25_latency_spread_cohen.md"
FS, TMIN, NS = K.FS, K.TMIN, K.NS
T = TMIN + np.arange(NS) / FS
WIN = (0.300, 0.500)                    # filter window and template segment
MAXLAG = 50                             # samples = 100 ms
FOLDS = 10
LEVELS = [0, 25, 50, 75, 100]           # planted latency SD (ms); 0 also gives the no-jitter floor
REPS = 100                              # nominal replicates per subject and level (= nominal pseudo-datasets)
NUIS_REPS = 50                          # replicates per subject for each nuisance generator at 50 and 75 ms
AMP_CV = 0.3                            # nominal trial-to-trial amplitude variability of the planted signal (gamma)
GENERATORS = {                          # name: (amplitude CV, share of seen trials with no signal)
    "nominal": (0.3, 0.0), "cv0": (0.0, 0.0), "cv06": (0.6, 0.0), "absent30": (0.3, 0.3)}
INV_LEVELS_MIN = 25                     # the curve is read (monotonicity, inversion) from 25 ms upward
BIAS_MAX = 15                           # ms
NAN_MAX = 0.05                          # bootstrap share of NaN inversions above which the verdict is UNRESOLVED
RT_CUT = 600                            # ms; seen trials with a later response (or none) form the motor-free subset
MIN_SIGMA_W = 0.010                     # s; single-trial width below this cannot be planted
CUT = 62.5                              # ms; the gate's boundary between "50" and "75"
GATE_HIT = 0.90
WORKERS = 4
SEED = 20261205
NBOOT = 2000


def sealed():
    from evidence import require_sealed
    for f in (PREREG, Path(__file__)):
        require_sealed(str(f))
    OUT.mkdir(exist_ok=True)


def eligible():
    return [r["sub"] for r in csv.DictReader(open(COH / "out" / "eligibility.csv")) if r["eligible"] == "1"]


def load_subject(sub):
    """Same preprocessing and rejection as cohen_killtest.preprocess (30 Hz low-pass, linked mastoids, baseline,
    authors' p2p thresholds, bad-channel rule); returns kept scalp epochs on good channels and labels (1 = seen)."""
    d = np.load(K.EP / f"{sub}.npz")
    x = d["X"].astype(np.float64) * float(d["scale_uv"])
    bb, aa = butter(4, K.LOWPASS / (FS / 2))
    x = filtfilt(bb, aa, x, axis=2, padlen=100)
    ch = lambda c: x[:, c - 1, :]
    heog, veog = ch(K.HEOGL) - ch(K.HEOGR), ch(K.VEOG) - ch(K.FP1)
    scalp = x[:, [c - 1 for c in K.SCALP], :] - ch(K.LMAST)[:, None, :] / 2
    scalp -= scalp[:, :, :K.samp(0)].mean(axis=2, keepdims=True)
    pp = scalp.max(axis=2) - scalp.min(axis=2)
    med = np.median(pp, axis=0)
    bad = med > K.BAD_CH * np.median(med)
    keep = (np.ptp(heog, axis=1) <= K.HEOG_PP) & (np.ptp(veog, axis=1) <= K.VEOG_PP) & \
           (pp[:, ~bad].max(axis=1) <= K.SCALP_PP)
    X = scalp[keep][:, ~bad, :]
    y = (d["resp"][keep] == 1).astype(int)
    chans = [K.SCALP[i] for i in np.where(~bad)[0]]
    return X, y, chans, d["onset"][keep]


_CACHE = {}


def subject(sub):
    """Per-worker cache of load_subject."""
    if sub not in _CACHE:
        _CACHE.clear()
        _CACHE[sub] = load_subject(sub)
    return _CACHE[sub]


def lw_lda(Xtr, ytr):
    m1, m0 = Xtr[ytr == 1].mean(0), Xtr[ytr == 0].mean(0)
    Z = np.r_[Xtr[ytr == 1] - m1, Xtr[ytr == 0] - m0]
    n, p = Z.shape
    S = Z.T @ Z / n
    mu = np.trace(S) / p
    d2 = np.sum((S - mu * np.eye(p)) ** 2)
    b2 = min(d2, (np.sum(np.sum(Z ** 2, axis=1) ** 2) - n * np.sum(S ** 2)) / n ** 2)
    sh = b2 / d2 if d2 > 0 else 1.0
    return np.linalg.solve(sh * mu * np.eye(p) + (1 - sh) * S, m1 - m0)


def apparent_lags(X, y, rng, extra=False):
    """Estimator (fixed). Returns lags (ms) of all seen trials, each scored by a fold that did not train on it.
    With extra=True also returns (trial indices of those lags, held-out unseen-trial lags, held-out AUC of the
    window-mean LDA score); these are descriptive and do not change the seen-trial lags."""
    a, b = int(round((WIN[0] - TMIN) * FS)), int(round((WIN[1] - TMIN) * FS))
    feat = X[:, :, a:b].mean(axis=2)
    folds = np.empty(len(y), int)
    for lab in (0, 1):
        idx = np.where(y == lab)[0]
        folds[idx] = rng.permutation(np.arange(idx.size) % FOLDS)
    lags, idx_out, ulags = [], [], []
    score = np.full(len(y), np.nan)
    for f in range(FOLDS):
        tr, te = folds != f, (folds == f) & (y == 1)
        if te.sum() == 0:
            continue
        w = lw_lda(feat[tr], y[tr])
        P = np.einsum("nct,c->nt", X, w)
        base = P[tr & (y == 0)].mean(0)
        tmpl = P[tr & (y == 1)].mean(0) - base
        seg = tmpl[a:b] - tmpl[a:b].mean()
        lag_of = lambda i: (int(np.argmax([np.dot(seg, (P[i] - base)[a + L:b + L])
                                           for L in range(-MAXLAG, MAXLAG + 1)])) - MAXLAG) * 1000 / FS
        for i in np.where(te)[0]:
            lags.append(lag_of(i))
            idx_out.append(i)
        if extra:
            for i in np.where((folds == f) & (y == 0))[0]:
                ulags.append(lag_of(i))
            score[folds == f] = feat[folds == f] @ w
    if not extra:
        return np.array(lags)
    return np.array(lags), np.array(idx_out), np.array(ulags), auc(score, y)


def auc(s, y):
    from scipy.stats import rankdata
    ok = np.isfinite(s)
    s, y = s[ok], y[ok]
    r = rankdata(s)
    n1, n0 = y.sum(), (1 - y).sum()
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


# ------------------------------------------------------------------ shape (group, label-using, after sealing)
def _sub_diff(sub):
    X, y, chans, _ = subject(sub)
    roi = [chans.index(c) for c in K.COMP["P3b"][0] if c in chans]
    dw = X[y == 1][:, roi].mean((0, 1)) - X[y == 0][:, roi].mean((0, 1))
    a, b = int(round((WIN[0] - TMIN) * FS)), int(round((WIN[1] - TMIN) * FS))
    topo = {c: float(X[y == 1][:, i, a:b].mean() - X[y == 0][:, i, a:b].mean()) for i, c in enumerate(chans)}
    return sub, dw.tolist(), topo, float(dw[a:b].mean())


def shape():
    sealed()
    subs = eligible()
    with Pool(WORKERS) as p:
        res = p.map(_sub_diff, subs)
    dw = np.mean([r[1] for r in res], axis=0)
    topo = {c: float(np.mean([r[2][c] for r in res if c in r[2]])) for c in K.SCALP}
    roi_mean = np.mean([topo[c] for c in K.COMP["P3b"][0]])
    topo = {c: v / roi_mean for c, v in topo.items()}                   # ROI mean of the topography = 1
    win_group = float(np.mean([r[3] for r in res]))
    # per-subject amplitude scale: subject's ROI 300-500 ms difference / group's, floored at 0 (prereg section 2)
    scale = {r[0]: max(r[3], 0.0) / win_group if win_group > 0 else float("nan") for r in res}
    sel = (T >= 0.2) & (T <= 0.6)
    g = lambda t, A, mu, s: A * np.exp(-(t - mu) ** 2 / (2 * s ** 2))
    try:
        (A, mu, s), _ = curve_fit(g, T[sel], dw[sel], p0=[dw[sel].max(), 0.4, 0.08], maxfev=20000)
        s = abs(s)
        r2 = float(1 - np.sum((dw[sel] - g(T[sel], A, mu, s)) ** 2) / np.sum((dw[sel] - dw[sel].mean()) ** 2))
        ok = bool(A > 0 and 0.020 <= s <= 0.200 and 0.30 <= mu <= 0.50 and r2 >= 0.70 and win_group > 0)
    except RuntimeError:
        A = mu = s = r2 = float("nan")
        ok = False
    pos = np.clip(dw[sel], 0, None)
    tw = T[sel]
    mom_sd = float(np.sqrt(np.sum(pos * (tw - np.sum(pos * tw) / pos.sum()) ** 2) / pos.sum())) if pos.sum() > 0 else None
    out = dict(subjects=len(subs), fit_ok=ok, A_uv=float(A), mu_s=float(mu), sigma_obs_s=float(s), r2=r2,
               width_bound_moment_sd_ms=None if mom_sd is None else 1000 * mom_sd,
               plantable_levels=[L for L in LEVELS if ok and s ** 2 - (L / 1000) ** 2 >= MIN_SIGMA_W ** 2],
               subject_scale=scale, subjects_scale_zero=int(sum(v == 0 for v in scale.values())),
               diff_wave_every_20ms={round(float(T[i]), 2): round(float(dw[i]), 3) for i in range(0, NS, 10)},
               topography=topo)
    (OUT / "shape.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k not in ("topography", "diff_wave_every_20ms", "subject_scale")},
                     indent=1))


# ------------------------------------------------------------------ synthetic ladder
def plant(sub, level_ms, shp, rng, gen="nominal", gamma_shape=False):
    """Noise: the subject's UNSEEN residuals (unseen trial minus unseen mean), resampled with replacement to the
    subject's total trial count with a random sign flip per trial, then given the real seen/unseen counts. The planted
    single-trial signal (subject-scaled amplitude) goes into the pseudo-seen trials."""
    X, y, chans, _ = subject(sub)
    U = X[y == 0] - X[y == 0].mean(0)
    n, n1 = len(y), int(y.sum())
    R = U[rng.integers(0, len(U), n)] * rng.choice([-1.0, 1.0], n)[:, None, None]
    yp = np.zeros(n, int)
    yp[rng.choice(n, n1, replace=False)] = 1
    topo = np.array([shp["topography"][str(c)] for c in chans])
    A = shp["A_uv"] * shp["subject_scale"][sub]
    mu, so = shp["mu_s"], shp["sigma_obs_s"]
    cv, absent = GENERATORS[gen]
    sj = level_ms / 1000
    sw = np.sqrt(so ** 2 - sj ** 2)
    if sj == 0:
        tau = np.zeros(n1)
    elif gamma_shape:                                                   # right-skewed, same SD (descriptive)
        k = 4.0
        tau = (rng.gamma(k, 1.0, n1) - k) / np.sqrt(k) * sj
    else:
        tau = rng.normal(0, sj, n1)
    amp = rng.gamma(1 / cv ** 2, cv ** 2, n1) if cv > 0 else np.ones(n1)
    if absent > 0:                                                      # some seen trials carry no signal;
        amp = amp * (rng.random(n1) >= absent) / (1 - absent)           # the rest are scaled so the mean is kept
    wave = A * so / sw * np.exp(-(T[None, :] - mu - tau[:, None]) ** 2 / (2 * sw ** 2)) * amp[:, None]
    R[yp == 1] += topo[None, :, None] * wave[:, None, :]
    return R, yp


def _ladder_one(args):
    sub, level, rep, shp, gen, gam = args
    gi = list(GENERATORS).index(gen)
    rng = np.random.default_rng([SEED, int(sub), level, rep, gi, int(gam)])
    X, y = plant(sub, level, shp, rng, gen, gam)
    lg, _, _, a = apparent_lags(X, y, rng, extra=True)
    return sub, level, rep, gen, gam, float(lg.std(ddof=1)), a


def ladder():
    sealed()
    shp = json.loads((OUT / "shape.json").read_text())
    if not shp["fit_ok"]:
        print("shape fit failed: INVALID (prereg section 4)")
        return
    subs = eligible()
    levels = shp["plantable_levels"]
    jobs = [(s, L, r, shp, "nominal", False) for s in subs for L in levels for r in range(REPS)]
    jobs += [(s, L, r, shp, g, False) for g in GENERATORS if g != "nominal"
             for s in subs for L in (50, 75) if L in levels for r in range(NUIS_REPS)]
    jobs += [(s, L, r, shp, "nominal", True) for s in subs for L in (50, 75) if L in levels for r in range(REPS // 3)]
    jobs.sort(key=lambda j: j[0])                                       # group by subject so the cache is reused
    t = time.time()
    with Pool(WORKERS) as p:
        res = p.map(_ladder_one, jobs, chunksize=25)
    out, aucs = {}, {}
    for sub, L, r, gen, gam, sd, a in sorted(res, key=lambda z: (z[0], z[1], z[3], z[4], z[2])):
        key = "gamma" if gam else gen
        out.setdefault(key, {}).setdefault(sub, {}).setdefault(str(L), []).append(sd)
        aucs.setdefault(key, {}).setdefault(sub, {}).setdefault(str(L), []).append(a)
    out["auc"] = aucs
    out["seconds"] = round(time.time() - t)
    (OUT / "ladder.json").write_text(json.dumps(out) + "\n")
    print("ladder done", out["seconds"], "s", flush=True)


def curve(lad, subs, levels):
    """Group ladder: mean over subjects of each subject's mean apparent SD per level."""
    return np.array([np.mean([np.mean(lad[s][str(L)]) for s in subs]) for L in levels])


def inv_levels(levels):
    return [L for L in levels if L >= INV_LEVELS_MIN]


def invert(value, cv, levels):
    """Planted SD whose ladder value equals `value`, read on the curve from 25 ms upward (linear interpolation).
    Returns (estimate, flag); flag is "" inside the curve, "LOW" below its 25 ms point (estimate 25, an upper
    bound) and "HIGH" above its top level (estimate = top level, a lower bound). NaN if not strictly increasing."""
    if not np.all(np.diff(cv) > 0):
        return float("nan"), "NONMONOTONE"
    if value < cv[0]:
        return float(levels[0]), "LOW"
    if value > cv[-1]:
        return float(levels[-1]), "HIGH"
    return float(np.interp(value, cv, levels)), ""


def gate():
    sealed()
    shp = json.loads((OUT / "shape.json").read_text())
    full = json.loads((OUT / "ladder.json").read_text())
    lad = full["nominal"]
    subs, levels = sorted(lad), shp["plantable_levels"]
    il = inv_levels(levels)
    res = dict(levels=levels, curve_ms=dict(zip(map(str, levels), curve(lad, subs, levels).tolist())))
    if not (50 in levels and 75 in levels):
        res.update(verdict="GATE NOT RUNNABLE", reason="50 or 75 ms cannot be planted under the average's width")
    else:
        cv_nom = curve(lad, subs, il)
        monotone = bool(np.all(np.diff(cv_nom) > 0))
        per_gen = {}
        for gen in GENERATORS:
            est = {}
            for L in (50, 75):
                e = []
                nrep = REPS if gen == "nominal" else NUIS_REPS
                for k in range(nrep):                                      # pseudo-dataset k: replicate k of every subject
                    val = np.mean([full[gen][s][str(L)][k] for s in subs])
                    if gen == "nominal":                                   # leave replicate k out of the curve
                        rest = {s: {str(M): [v for j, v in enumerate(lad[s][str(M)]) if j != k] for M in il}
                                for s in subs}
                        cv_k = curve(rest, subs, il)
                    else:                                                  # nuisance data read on the nominal curve
                        cv_k = cv_nom
                    e.append(invert(val, cv_k, il)[0])
                est[L] = np.array(e)
            hit50 = float(np.mean(est[50] < CUT))
            hit75 = float(np.mean(est[75] >= CUT))
            bias = {L: float(np.nanmedian(est[L]) - L) for L in (50, 75)}
            ok = hit50 >= GATE_HIT and hit75 >= GATE_HIT and all(abs(b) <= BIAS_MAX for b in bias.values())
            per_gen[gen] = dict(hit50=hit50, hit75=hit75, median_bias_ms=bias, passes=ok,
                                group_apparent_sd_ms={L: float(np.mean([np.mean(full[gen][s][str(L)]) for s in subs]))
                                                      for L in (50, 75)},
                                est50=est[50].tolist(), est75=est[75].tolist())
        lad_g = full.get("gamma", {})
        gamma_desc = {L: float(np.mean([np.mean(lad_g[s][str(L)]) for s in lad_g])) for L in (50, 75)} if lad_g else None
        ok = monotone and all(v["passes"] for v in per_gen.values())
        res.update(monotone_from_25=monotone, generators=per_gen, gamma_curve_ms=gamma_desc,
                   verdict="GATE PASS" if ok else "METHOD BLIND")
    (OUT / "gate.json").write_text(json.dumps(res, indent=1) + "\n")
    short = {k: v for k, v in res.items() if k != "generators"}
    short["generators"] = {g: {k: v for k, v in d.items() if not k.startswith("est")}
                           for g, d in res.get("generators", {}).items()}
    print(json.dumps(short, indent=1))


# ------------------------------------------------------------------ real data
def _real_one(sub):
    X, y, _, onset = subject(sub)
    rng = np.random.default_rng([SEED, int(sub), 999])
    lg, idx, ul, a = apparent_lags(X, y, rng, extra=True)
    RT = _real_one.rt
    rt = np.array([RT.get((sub, int(onset[i])), np.inf) for i in idx])
    late = rt > RT_CUT
    fin = np.isfinite(rt)
    from scipy.stats import spearmanr
    rho = float(spearmanr(lg[fin], rt[fin])[0]) if fin.sum() >= 10 and np.ptp(lg[fin]) > 0 else float("nan")
    return sub, dict(sd=float(lg.std(ddof=1)), unseen_sd=float(ul.std(ddof=1)), auc=a,
                     sd_late_rt=float(lg[late].std(ddof=1)) if late.sum() >= 10 else float("nan"),
                     n_late_rt=int(late.sum()), n_seen=int(len(lg)), lag_rt_spearman=rho)


def _init_rt():
    _real_one.rt = K.rts()


def verdict_from_ci(lo, hi):
    if hi < 50:
        return "JITTER BELOW 50 MS"
    if lo >= 75:
        return "JITTER AT OR ABOVE 75 MS"
    if lo >= 50:
        return "JITTER AT LEAST 50 MS"
    return "UNRESOLVED"


def real():
    sealed()
    g = json.loads((OUT / "gate.json").read_text())
    if g["verdict"] != "GATE PASS":
        print("gate did not pass; the real data are not analysed (prereg section 3)")
        return
    shp = json.loads((OUT / "shape.json").read_text())
    full = json.loads((OUT / "ladder.json").read_text())
    lad = full["nominal"]
    levels = shp["plantable_levels"]
    il = inv_levels(levels)
    with Pool(WORKERS, initializer=_init_rt) as p:
        rv = dict(p.map(_real_one, sorted(lad)))
    subs = sorted(rv)
    gmean = float(np.mean([rv[s]["sd"] for s in subs]))
    point, flag = invert(gmean, curve(lad, subs, il), il)
    rng = np.random.default_rng(SEED + 1)
    boot, flags = [], []
    for _ in range(NBOOT):
        bs = list(rng.choice(subs, len(subs)))
        e, f = invert(np.mean([rv[s]["sd"] for s in bs]), curve(lad, bs, il), il)
        boot.append(e)
        flags.append(f)
    boot = np.array(boot)
    nan_share = float(np.isnan(boot).mean())
    lo, hi = (float(v) for v in np.nanpercentile(boot, [2.5, 97.5]))
    # an estimate pinned at the bottom (LOW) is an upper bound of 25; at the top (HIGH) a lower bound of the top level
    v = "UNRESOLVED" if nan_share > NAN_MAX else verdict_from_ci(lo, hi)
    rho = np.array([rv[s]["lag_rt_spearman"] for s in subs])
    rho = rho[np.isfinite(rho)]
    rho_t = float(rho.mean() / (rho.std(ddof=1) / np.sqrt(len(rho)))) if len(rho) > 2 else float("nan")
    lad_auc = {L: float(np.mean([np.mean(full["auc"]["nominal"][s][str(L)]) for s in subs])) for L in levels}
    out = dict(verdict=v, estimate_ms=point, estimate_flag=flag, ci95_ms=[lo, hi], boot_nan_share=nan_share,
               boot_flag_share={f: flags.count(f) / NBOOT for f in set(flags)},
               group_apparent_sd_ms=gmean, curve_ms=dict(zip(map(str, levels), curve(lad, subs, levels).tolist())),
               response_locked_flag=bool(np.isfinite(rho_t) and rho_t > 3),
               lag_rt_spearman_mean=float(rho.mean()) if len(rho) else None, lag_rt_spearman_t=rho_t,
               group_sd_late_rt_ms=float(np.nanmean([rv[s]["sd_late_rt"] for s in subs])),
               group_sd_same_subjects_ms=float(np.mean([rv[s]["sd"] for s in subs
                                                        if np.isfinite(rv[s]["sd_late_rt"])])),
               group_unseen_sd_ms=float(np.mean([rv[s]["unseen_sd"] for s in subs])),
               real_auc=float(np.mean([rv[s]["auc"] for s in subs])), ladder_auc=lad_auc,
               width_bound_moment_sd_ms=shp["width_bound_moment_sd_ms"], sigma_obs_ms=1000 * shp["sigma_obs_s"],
               per_subject=rv)
    (OUT / "real.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "per_subject"}, indent=1))


def pilot():
    """Unsealed: runtime of one estimator call on label-free synthetic data (noise only, random labels).
    Prints timing only."""
    sub = eligible()[0]
    t0 = time.time()
    X, y, _, _ = subject(sub)
    rng = np.random.default_rng(1)
    t = time.time()
    lg, idx, ul, a = apparent_lags(X, rng.permutation(y), rng, extra=True)
    print("load", round(t - t0, 2), "s; trials", len(y), "lags", len(lg), len(ul), "finite",
          bool(np.isfinite(lg).all()), round(time.time() - t, 2), "s")


if __name__ == "__main__":
    {"shape": shape, "ladder": ladder, "gate": gate, "real": real, "pilot": pilot}[sys.argv[1]]()
