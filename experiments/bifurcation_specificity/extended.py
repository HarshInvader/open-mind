"""Can an extended model set rescue the Sergent 2021 bifurcation test? (follow-up to the NOT SPECIFIC audit)
Prereg: docs/prereg/2026-11-25_bifurcation_extended_model_set.md

Adds two graded models to their set {0, 2B, 3}:
  J  jittered-threshold graded: y = c + L*logistic(k*(x - theta)) + N(0, s^2), theta ~ N(x0, tau^2) per trial
     (marginal likelihood by 40-node Gauss-Hermite quadrature over theta)
  T  heavy-tailed graded: Model 2B mean and scale, Student-t noise with estimated df
Same fitting, CV and spm_BMS as audit.py (imported, sealed, unchanged). Bifurcation call = Model 3 pxp > 0.95 among 5.

    python -I extended.py check     # likelihood correctness (quadrature vs Monte Carlo; t vs scipy); no generator outcomes
    python -I extended.py run       # sealed run -> out_ext/<cell>.json
    python -I extended.py summary   # verdict -> out_ext/summary.json
"""
import json, sys, time
from pathlib import Path
from multiprocessing import Pool

import numpy as np
from scipy.special import expit, gammaln

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "rules"))
import audit as A  # noqa: E402

OUT = HERE / "out_ext"
PREREG = HERE.parents[1] / "docs" / "prereg" / "2026-11-25_bifurcation_extended_model_set.md"
STUDIES = 150
WORKERS = 6
SEED = 20261129
GH_Z, GH_W = np.polynomial.hermite.hermgauss(40)


def llh_j(p, y, x):
    x0, k, L, c, tau, s = p
    if s <= 0 or tau <= 0:
        return -np.inf
    th = x0 + np.sqrt(2) * tau * GH_Z                       # (40,)
    mu = c + L * expit(k * (x[:, None] - th[None, :]))       # (n, 40)
    dens = (GH_W[None, :] / np.sqrt(np.pi)) * np.exp(-0.5 * ((y[:, None] - mu) / s) ** 2) / (s * np.sqrt(2 * np.pi))
    with np.errstate(divide="ignore"):
        return np.sum(np.log(dens.sum(axis=1)))


def llh_t(p, y, x):
    x0, k, L, ss, si, mumax, lnu = p
    nu = np.exp(lnu)
    if not (0.5 <= nu <= 1000):
        return -np.inf
    mu = L * expit(k * (x - x0)) - L * expit(k * (x.max() - x0)) + mumax
    sc = ss * mu + si
    if np.any(sc <= 0):
        return -np.inf
    z = (y - mu) / sc
    return np.sum(gammaln((nu + 1) / 2) - gammaln(nu / 2) - 0.5 * np.log(nu * np.pi) - np.log(sc)
                  - (nu + 1) / 2 * np.log1p(z ** 2 / nu))


def inits_ext(y, x):
    m = {l: y[x == l].mean() for l in A.LEVELS}
    sd = {l: y[x == l].std(ddof=1) for l in A.LEVELS}
    lo, hi = A.LEVELS[1], A.LEVELS[-1]
    _, i2, _ = A.inits(y, x)
    k = (m[hi] - m[lo]) / (hi - lo)
    ij = [(hi + lo) / 2, k, m[hi] - m[0], m[0], 1.0, sd[0]]
    it = list(i2) + [np.log(10.0)]
    return ij, it


def subject_lme5(y, x, block):
    out = np.zeros(5)
    conv = 0
    i0, i2, i3 = A.inits(y, x)
    ij, it = inits_ext(y, x)
    kj = []
    for f in range(5):
        te = (block >= 4 * f) & (block < 4 * f + 4)
        tr = ~te
        fits = [(A.llh_null, i0, False), (A.llh_2b, i2, True), (A.llh_3, i3, True), (llh_j, ij, True), (llh_t, it, True)]
        for m, (fn, ini, usex) in enumerate(fits):
            g = (lambda p, fn=fn: -fn(p, y[tr], x[tr])) if usex else (lambda p, fn=fn: -fn(p, y[tr]))
            p, c = A.fminsearch(g, ini)
            conv += c
            out[m] += fn(p, y[te], x[te]) if usex else fn(p, y[te])
            if m == 3:
                kj.append(abs(p[1]) * abs(p[4]))             # k*tau: large = step-like transfer relative to jitter
    return out / 5, conv / 25, float(np.median(kj))


# two held-out graded generators (in neither J nor T)
def gen_ext(cell, rng):
    if cell == "H_jitter_t":            # threshold jitter SD 1.0 AND t(4) noise
        x, block = A.design(rng)
        th = A.X0 + rng.normal(0, 1.0, len(x))
        y = A.DMAX * expit(A.KM * (x - th)) + rng.standard_t(4, len(x)) / np.sqrt(2.0)
        return y, x, block
    if cell == "H_gain":                # trial-wise multiplicative gain jitter, lognormal(0, 0.5), Gaussian noise
        x, block = A.design(rng)
        g = rng.lognormal(0, 0.5, len(x))
        y = g * A.DMAX * expit(A.KM * (x - A.X0)) + rng.normal(0, 1, len(x))
        return y, x, block
    return A.gen(cell, rng)


CELLS = A.CELLS + ["H_jitter_t", "H_gain"]
GRADED = [c for c in CELLS if c.startswith(("G_", "H_"))] + ["M2_unimodal"]


def one_study(args):
    cell, seed = args
    rng = np.random.default_rng(seed)
    lme, conv, kt = [], [], []
    for s in range(A.N_SUB):
        y, x, block = gen_ext(cell, rng)
        l, c, k = subject_lme5(y, x, block)
        lme.append(l)
        conv.append(c)
        kt.append(k)
    lme = np.array(lme)
    finite = bool(np.all(np.isfinite(lme)))
    if finite:
        b = A.spm_bms(lme, rng)
        pxp = b["pxp"]
    else:
        pxp = [float("nan")] * 5
    return dict(pxp=pxp, pxp3=pxp[2], winner=int(np.nanargmax(pxp)) if finite else -1, conv=float(np.mean(conv)),
                subj_best=np.bincount(lme.argmax(axis=1), minlength=5).tolist(), median_ktau=float(np.median(kt)),
                finite=finite)


def run_cell(cell):
    ss = np.random.SeedSequence([SEED, CELLS.index(cell)])
    seeds = [int(s.generate_state(1)[0]) for s in ss.spawn(STUDIES)]
    t = time.time()
    with Pool(WORKERS) as p:
        res = p.map(one_study, [(cell, s) for s in seeds])
    pxp3 = np.array([r["pxp3"] for r in res])
    call = np.where(np.isnan(pxp3), False, pxp3 > 0.95)       # non-finite study = no call (prereg section 4)
    return dict(cell=cell, studies=STUDIES, rate_call=float(call.mean()),
                winner_counts=np.bincount([r["winner"] + 1 for r in res], minlength=6).tolist(),  # index 0 = nonfinite
                mean_subj_best=np.mean([r["subj_best"] for r in res], axis=0).tolist(),
                median_ktau=float(np.median([r["median_ktau"] for r in res])),
                mean_converged=float(np.mean([r["conv"] for r in res])),
                nonfinite=int(sum(not r["finite"] for r in res)), seconds=round(time.time() - t), runs=res)


def check():
    rng = np.random.default_rng(7)
    x = np.repeat(A.LEVELS, 30).astype(float)
    y = rng.normal(1, 1.2, len(x))
    p = [2.5, 3.0, 2.0, 0.1, 0.8, 0.9]
    th = rng.normal(p[0], p[4], 400_000)
    mc = 0.0
    for xi, yi in zip(x, y):
        mu = p[3] + p[2] * expit(p[1] * (xi - th))
        mc += np.log(np.mean(np.exp(-0.5 * ((yi - mu) / p[5]) ** 2) / (p[5] * np.sqrt(2 * np.pi))))
    print("J quadrature", round(llh_j(p, y, x), 3), "Monte Carlo", round(mc, 3))
    from scipy.stats import t as tdist
    q = [2.5, 1.5, 2.0, 0.1, 1.0, 1.5, np.log(4.0)]
    mu = q[2] * expit(q[1] * (x - q[0])) - q[2] * expit(q[1] * (x.max() - q[0])) + q[5]
    print("T mine", round(llh_t(q, y, x), 4), "scipy", round(float(np.sum(tdist.logpdf(y, 4.0, mu, q[3] * mu + q[4]))), 4))
    # timing on a non-cell debug generator (constant mean + Gaussian noise): no kill-test outcome is computed
    xs, block = A.design(rng)
    ys = rng.normal(0, 1, len(xs)) + 0.3 * xs
    t0 = time.time()
    l, c, k = subject_lme5(ys, xs, block)
    print("debug subject: finite", bool(np.all(np.isfinite(l))), "conv", round(c, 2), "seconds", round(time.time() - t0, 1))
    print("bms 5 models all-equal", np.round(A.spm_bms(np.zeros((20, 5)), rng)["pxp"], 3))


def run():
    from evidence import require_sealed
    for f in (PREREG, Path(__file__), HERE / "audit.py"):
        require_sealed(str(f))
    OUT.mkdir(exist_ok=True)
    for cell in sys.argv[2:] or CELLS:
        if (OUT / f"{cell}.json").exists():                    # resume rule (prereg section 4): finished cells kept
            continue
        r = run_cell(cell)
        (OUT / f"{cell}.json").write_text(json.dumps(r) + "\n")
        print(cell, r["rate_call"], r["winner_counts"], round(r["median_ktau"], 2), r["mean_converged"], r["seconds"], "s",
              flush=True)


def summary():
    R = {c: json.loads((OUT / f"{c}.json").read_text()) for c in CELLS}
    recall = R["B_bifurcation"]["rate_call"]
    false = {c: R[c]["rate_call"] for c in GRADED}
    graded_ok = all(v <= 0.10 for v in false.values())
    if recall >= 0.80 and graded_ok:
        verdict = "FIX WORKS"
    elif recall < 0.80 and graded_ok:
        verdict = "UNDECIDABLE"
    elif recall >= 0.80:
        verdict = "STILL NOT SPECIFIC"
    else:
        verdict = "FAILS BOTH"
    s = dict(verdict=verdict, bifurcation_recall=recall, graded_call_rates=false,
             winner_counts={c: R[c]["winner_counts"] for c in CELLS},
             mean_subj_best={c: [round(v, 1) for v in R[c]["mean_subj_best"]] for c in CELLS},
             median_ktau={c: R[c]["median_ktau"] for c in CELLS},
             converged={c: R[c]["mean_converged"] for c in CELLS}, nonfinite={c: R[c]["nonfinite"] for c in CELLS})
    (OUT / "summary.json").write_text(json.dumps(s, indent=1) + "\n")
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    {"check": check, "run": run, "summary": summary}[sys.argv[1]]()
