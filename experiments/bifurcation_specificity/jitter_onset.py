"""Round 17 #2: does trial-to-trial onset jitter delay (or hide) the bifurcation call? (simulation only, zero data)
Prereg: docs/prereg/2026-11-25_bifurcation_onset_jitter.md

Sergent et al. 2021: the bifurcation model is "a statistically better explanation of neural activity beyond
250-300 ms post-stimulus". Single-trial late-component latencies vary by tens of ms (P3b latency SD ~ 80 ms,
Kim et al. 2024, uncorrected). Here: their two-state generator (audit.B_bifurcation shape) in which each high-state
trial switches on at its own onset o_i ~ N(0, SIGMA_L) ms around the true mean onset; each window value is the
30 ms mean (their window width) centred at W ms re the mean onset. Analysed with their 3-model comparison and the
5-model extension, both imported unchanged (audit.py, extended.py, sealed).

    python -I jitter_onset.py pilot      # timing only (one study, prints seconds)
    python -I jitter_onset.py run        # sealed run -> out_jit/<cell>.json (resume: finished files kept)
    python -I jitter_onset.py summary    # verdict -> out_jit/summary.json
"""
import json, sys, time
from pathlib import Path
from multiprocessing import Pool

import numpy as np
from scipy.special import expit
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "rules"))
import audit as A  # noqa: E402
import extended as E  # noqa: E402

OUT = HERE / "out_jit"
PREREG = HERE.parents[1] / "docs" / "prereg" / "2026-11-25_bifurcation_onset_jitter.md"
SIGMAS = [0, 40, 80]                       # ms; 80 ~ the uncorrected single-trial P3b latency SD
# window centres re the true mean onset, ms; sigma 0 rises entirely inside (-15, +15), so its grid is dense there
WIN = {0: [-40, -10, -5, 0, 5, 10, 40], 40: [-80, -40, 0, 40, 80, 120, 160], 80: [-80, -40, 0, 40, 80, 120, 160]}
HALF = 15.0                                # 30 ms windows
STUDIES = 100                              # pre-stated fallback: 50 if the pilot projects > 6 h on 4 workers
WORKERS = 4
SEED = 20261725 + 2
NBOOT = 2000
CALL = 0.95                                # protected exceedance threshold (theirs)
CROSS = 0.5                                # onset = first window where the call rate reaches 0.5
LAG_BAR = 40.0                             # ms
ANCHOR = (0.05, 0.80)                      # sigma 0: rate(W=-40) <= 0.05 and rate(W=+40) >= 0.80, else INVALID
CENSOR = 40.0                              # right-censored crossing = last window + 40 ms


def gen_jit(sigma, w, rng):
    """B_bifurcation's two states and psychometric P(high); high-state trials switch on at o ~ N(0, sigma)."""
    x, block = A.design(rng)
    n = len(x)
    a = np.where(x == 0, 0, expit(A.KM * (x - A.X0)))
    hi = rng.random(n) < a
    amp = (1.0 + 0.2 * (x - A.X0)) * A.DMAX / 1.5
    o = rng.normal(0.0, sigma, n) if sigma > 0 else np.zeros(n)
    frac = np.clip((w + HALF - o) / (2 * HALF), 0.0, 1.0)      # share of the window after this trial's onset
    y = np.where(hi, amp * frac, 0.0) + rng.normal(0, 1, n)
    return y, x, block


def one_study(args):
    sigma, w, seed = args
    rng = np.random.default_rng(seed)
    lme = []
    for _ in range(A.N_SUB):
        y, x, block = gen_jit(sigma, w, rng)
        l, _, _ = E.subject_lme5(y, x, block)
        lme.append(l)
    lme = np.array(lme)
    out = dict(finite3=bool(np.all(np.isfinite(lme[:, :3]))), finite5=bool(np.all(np.isfinite(lme))))
    if out["finite3"]:                     # each comparison is voided only by its own models' non-finite evidence
        b3 = A.spm_bms(lme[:, :3], rng)["pxp"]
        out.update(pxp3=[float(v) for v in b3], win3=int(np.argmax(b3)))
    if out["finite5"]:
        b5 = A.spm_bms(lme, rng)["pxp"]
        out.update(pxp5=[float(v) for v in b5], win5=int(np.argmax(b5)))
    return out


def cell_name(sigma, w):
    return f"s{sigma}_w{w:+d}"


def run_cell(sigma, w):
    f = OUT / f"{cell_name(sigma, w)}.json"
    if f.exists():
        return
    ss = np.random.SeedSequence([SEED, sigma, w + 1000])
    seeds = [int(s.generate_state(1)[0]) for s in ss.spawn(STUDIES)]
    t = time.time()
    with Pool(WORKERS) as p:
        res = p.map(one_study, [(sigma, w, s) for s in seeds])
    r = dict(sigma=sigma, w=w, studies=STUDIES, nonfinite3=sum(not x["finite3"] for x in res),
             nonfinite5=sum(not x["finite5"] for x in res),
             seconds=round(time.time() - t), runs=res)
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(r) + "\n")
    tmp.rename(f)
    print(cell_name(sigma, w), r["nonfinite3"], r["nonfinite5"], r["seconds"], "s", flush=True)


def calls(runs, key, model):
    """Per-study 0/1: model called (pxp > CALL); a study whose own comparison is non-finite counts as no call."""
    fk = "finite3" if key == "pxp3" else "finite5"
    return np.array([float(x[fk] and x[key][model] > CALL) for x in runs])


def pava(r):
    """Isotonic (non-decreasing) least-squares fit, equal weights."""
    blocks = [[float(v), 1] for v in r]
    i = 0
    while i < len(blocks) - 1:
        if blocks[i][0] > blocks[i + 1][0]:
            m = (blocks[i][0] * blocks[i][1] + blocks[i + 1][0] * blocks[i + 1][1]) / (blocks[i][1] + blocks[i + 1][1])
            blocks[i] = [m, blocks[i][1] + blocks[i + 1][1]]
            del blocks[i + 1]
            i = max(i - 1, 0)
        else:
            i += 1
    return [m for m, k in blocks for _ in range(k)]


def crossing(rates, wins):
    """First window where the isotonic-fitted rate reaches CROSS, linearly interpolated.
    Returns (value, flag): flag 'left' if already >= CROSS at the first window, 'right' if never (value = last + CENSOR)."""
    f = pava(rates)
    for i, r in enumerate(f):
        if r >= CROSS:
            if i == 0:
                return float(wins[0]), "left"
            r0 = f[i - 1]
            return float(wins[i - 1] + (CROSS - r0) / (r - r0) * (wins[i] - wins[i - 1])), None
    return float(wins[-1] + CENSOR), "right"


def lag_stats(R, key, model, rng):
    """Lag of the onset crossing at each sigma vs sigma 0; bootstrap over studies within each cell."""
    C = {s: [calls(R[(s, w)]["runs"], key, model) for w in WIN[s]] for s in SIGMAS}
    raw = {s: [float(c.mean()) for c in C[s]] for s in SIGMAS}
    point = {s: crossing(raw[s], WIN[s]) for s in SIGMAS}
    boots = {s: [] for s in SIGMAS}
    for _ in range(NBOOT):
        for s in SIGMAS:
            boots[s].append(crossing([rng.choice(c, len(c)).mean() for c in C[s]], WIN[s])[0])
    out = {}
    for s in SIGMAS[1:]:
        lags = np.array(boots[s]) - np.array(boots[0])
        c, flag = point[s]
        out[s] = dict(crossing=c, flag=flag, lag=c - point[0][0],
                      lag_lo95_onesided=float(np.percentile(lags, 5)),
                      lag_hi95_onesided=float(np.percentile(lags, 95)),
                      p_star=float(norm.cdf(c / s)))          # share of high trials switched on at the crossing
    anchors = dict(rate_first=raw[0][0], rate_last=raw[0][-1],
                   ok=raw[0][0] <= ANCHOR[0] and raw[0][-1] >= ANCHOR[1])
    nonmono = {s: bool(np.any(np.diff(raw[s]) < -0.10)) for s in SIGMAS}
    return dict(crossing0=point[0][0], flag0=point[0][1], anchors=anchors, rates=raw, nonmonotone=nonmono, lags=out)


def verdict(L):
    if not L["anchors"]["ok"] or L["flag0"] is not None:
        return "INVALID"
    s = L["lags"][SIGMAS[-1]]
    if s["lag_lo95_onesided"] >= LAG_BAR:
        return f"APPARENT ONSET LAGS BY >= {LAG_BAR:g} MS AT SD {SIGMAS[-1]} MS"
    if s["lag_hi95_onesided"] <= -LAG_BAR:
        return f"APPARENT ONSET LEADS BY >= {LAG_BAR:g} MS AT SD {SIGMAS[-1]} MS"
    if s["lag_hi95_onesided"] < LAG_BAR and s["lag_lo95_onesided"] > -LAG_BAR:
        return f"ONSET TIMING ROBUST TO SD {SIGMAS[-1]} MS JITTER (|LAG| < {LAG_BAR:g} MS)"
    return "LAG NOT RESOLVED AT THIS PRECISION"


def sealed():
    from evidence import require_sealed
    for f in (PREREG, Path(__file__), HERE / "audit.py", HERE / "extended.py"):
        require_sealed(str(f))
    OUT.mkdir(exist_ok=True)


def pilot():
    t = time.time()
    one_study((80, 40, 12345))
    print("one study, 5-model fits, seconds:", round(time.time() - t, 1))


def run():
    sealed()
    for s in SIGMAS:
        for w in WIN[s]:
            run_cell(s, w)


def summary():
    sealed()
    R = {}
    for s in SIGMAS:
        for w in WIN[s]:
            r = json.loads((OUT / f"{cell_name(s, w)}.json").read_text())
            assert r["sigma"] == s and r["w"] == w and r["studies"] == STUDIES and len(r["runs"]) == STUDIES
            R[(s, w)] = r
    rng = np.random.default_rng(SEED + 9)
    L3 = lag_stats(R, "pxp3", 2, rng)
    L5 = lag_stats(R, "pxp5", 2, rng)
    U3 = {s: [float(calls(R[(s, w)]["runs"], "pxp3", 1).mean()) for w in WIN[s]] for s in SIGMAS}
    top3 = {s: [np.bincount([x["win3"] for x in R[(s, w)]["runs"] if x["finite3"]], minlength=3).tolist()
                for w in WIN[s]] for s in SIGMAS}
    top5 = {s: [np.bincount([x["win5"] for x in R[(s, w)]["runs"] if x["finite5"]], minlength=5).tolist()
                for w in WIN[s]] for s in SIGMAS}
    S = dict(primary_3model=dict(verdict=verdict(L3), **L3),
             secondary_5model=dict(verdict=verdict(L5), **L5),
             unimodal_2b_called_3model=U3, windows=WIN, sigmas=SIGMAS, top3=top3, top5=top5,
             nonfinite={cell_name(*k): [v["nonfinite3"], v["nonfinite5"]] for k, v in R.items()})
    (OUT / "summary.json").write_text(json.dumps(S, indent=1) + "\n")
    print(json.dumps({k: S[k]["verdict"] for k in ("primary_3model", "secondary_5model")}, indent=1))
    print(json.dumps(dict(lags3=L3["lags"], lags5=L5["lags"], c0_3=L3["crossing0"], c0_5=L5["crossing0"],
                          anchors3=L3["anchors"], anchors5=L5["anchors"]), indent=1))


if __name__ == "__main__":
    {"pilot": pilot, "run": run, "summary": summary}[sys.argv[1]]()
