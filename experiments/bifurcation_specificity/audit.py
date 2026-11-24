"""Specificity audit of the Sergent et al. 2021 single-trial bifurcation model comparison (simulation only, zero data).
Prereg: docs/prereg/2026-11-24_bifurcation_specificity_audit.md

Faithful Python port of the authors' OSF code (osf.io/aw3t5, Bifurcation_OSF_Scripts, CC BY 4.0, read 2026-11-24):
  LLH_fun_null.m, LLH_fun_logisticB.m (Model 2B), LLH_fun_logisbimodalfixedsigma.m (Model 3),
  SoundConscEEG_SingleTrialPred_ModelFitting_Twind30ms_batch.m (inits, 5-fold block CV, mean of summed test LLH),
  SoundConsciousEEG_SingleTrialPredict_ModelComp_Twind_PlotFig.m (spm_BMS(lme,[],0,0,1) -> protected exceedance).

    python -I audit.py smoke                 # tiny debug run (not evidence)
    python -I audit.py run [cell ...]        # sealed run: every cell, STUDIES studies each -> out/<cell>.json
    python -I audit.py summary               # verdict -> out/summary.json
"""
import json, sys, time
from pathlib import Path
from multiprocessing import Pool

import numpy as np
from scipy.optimize import minimize
from scipy.special import digamma, gammaln, expit

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
PREREG = HERE.parents[1] / "docs" / "prereg" / "2026-11-24_bifurcation_specificity_audit.md"

N_SUB = 20                  # Sergent 2021
LEVELS = np.arange(6)       # 0 = noise, 1..5 = -13..-5 dB (their SNRs - 1 coding)
N_PER = 150                 # trials per level after rejection (150 +- 6)
N_BLOCK = 20                # 5 folds x 4 blocks
STUDIES = 300
WORKERS = 4
XP_SAMPLES = 200_000
SEED = 20261128


# ---------------------------------------------------------------- the three likelihoods (port of the .m files)
def llh_null(p, y):
    s, mu = p
    if s <= 0:
        return -np.inf
    return len(y) * np.log(1 / (s * np.sqrt(2 * np.pi))) - 0.5 * np.sum((y - mu) ** 2) / s ** 2


def llh_2b(p, y, x):
    x0, k, L, ss, si, mumax = p
    mu = L * expit(k * (x - x0)) - L * expit(k * (x.max() - x0)) + mumax
    sig = ss * mu + si
    if np.any(sig <= 0):             # MATLAB would return a complex log here; we treat it as an invalid point
        return -np.inf
    return np.sum(np.log(1 / (sig * np.sqrt(2 * np.pi)))) - 0.5 * np.sum((y - mu) ** 2 / sig ** 2)


def llh_3(p, y, x, xmin=0):
    x0, k, mulow, step, Lh, kh, s = p
    if s <= 0:
        return -np.inf
    a = expit(k * (x - x0))
    a = np.where(x == xmin, 0.0, a)
    muh = Lh * expit(kh * (x - x0)) + step
    muh = np.where(x == xmin, mulow, muh)
    c = 1 / (s * np.sqrt(2 * np.pi))
    dens = (1 - a) * c * np.exp(-0.5 * ((y - mulow) / s) ** 2) + a * c * np.exp(-0.5 * ((y - muh) / s) ** 2)
    with np.errstate(divide="ignore"):
        return np.sum(np.log(dens))


def fminsearch(f, x0):
    """MATLAB fminsearch defaults: initial simplex 5% (0.00025 for zeros), TolX = TolFun = 1e-4, 200*n iter/evals."""
    n = len(x0)
    g = lambda p: (lambda v: 1e300 if not np.isfinite(v) else v)(f(p))
    r = minimize(g, np.asarray(x0, float), method="Nelder-Mead",
                 options=dict(xatol=1e-4, fatol=1e-4, maxiter=200 * n, maxfev=200 * n))
    return r.x, r.success


# ---------------------------------------------------------------- per-subject fit (port of the batch script)
def inits(y, x):
    m = {l: y[x == l].mean() for l in LEVELS}
    sd = {l: y[x == l].std(ddof=1) for l in LEVELS}
    lo, hi = LEVELS[1], LEVELS[-1]
    i0 = [1.0, 0.0]
    k = (m[hi] - m[lo]) / (hi - lo)
    ss = (sd[hi] - sd[lo]) / (m[hi] - m[lo])
    i2 = [(hi + lo) / 2, k, 2 * m[hi], ss, sd[hi] - ss * m[hi], m[hi]]
    i3 = [(hi + lo) / 2, k, m[0], m[lo] - m[0], m[hi] - m[lo], (m[hi] - m[lo]) / (hi - lo), sd[0]]
    return i0, i2, i3


def subject_lme(y, x, block):
    """Mean over 5 folds of the summed test log-likelihood, for models 0, 2B, 3 (their Model*_LLH)."""
    out = np.zeros(3)
    conv = 0
    i0, i2, i3 = inits(y, x)                      # as in their batch script: inits from all trials of the window
    for f in range(5):
        te = (block >= 4 * f) & (block < 4 * f + 4)
        tr = ~te
        p0, c0 = fminsearch(lambda p: -llh_null(p, y[tr]), i0)
        p2, c2 = fminsearch(lambda p: -llh_2b(p, y[tr], x[tr]), i2)
        p3, c3 = fminsearch(lambda p: -llh_3(p, y[tr], x[tr]), i3)
        conv += c0 + c2 + c3
        out += [llh_null(p0, y[te]), llh_2b(p2, y[te], x[te]), llh_3(p3, y[te], x[te])]
    return out / 5, conv / 15


# ---------------------------------------------------------------- spm_BMS (random-effects BMS + BOR + pxp)
def spm_bms(lme, rng):
    n, K = lme.shape
    a0 = np.ones(K)
    a = a0.copy()
    for _ in range(10000):
        lu = lme + digamma(a) - digamma(a.sum())
        lu = lu - lu.max(axis=1, keepdims=True)
        u = np.exp(lu)
        g = u / u.sum(axis=1, keepdims=True)
        prev = a
        a = a0 + g.sum(axis=0)
        if np.linalg.norm(a - prev) < 1e-4:
            break
    # exceedance probability by sampling (spm_dirichlet_exceedance)
    r = rng.gamma(a, size=(XP_SAMPLES, K))
    xp = np.bincount(r.argmax(axis=1), minlength=K) / XP_SAMPLES
    # free energies of the RFX model (F1) and of the null "all models equally frequent" (F0)
    Elr = digamma(a) - digamma(a.sum())
    lu = lme + Elr
    lu = lu - lu.max(axis=1, keepdims=True)
    g = np.exp(lu)
    g /= g.sum(axis=1, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        Hg = -np.nansum(g * np.log(g))
    F1 = (np.sum(g * (lme + Elr)) + gammaln(a0.sum()) - gammaln(a0).sum() + np.sum((a0 - 1) * Elr) + Hg
          - (gammaln(a.sum()) - gammaln(a).sum() + np.sum((a - 1) * Elr)))
    m = lme.max(axis=1, keepdims=True)
    F0 = np.sum(m[:, 0] + np.log(np.exp(lme - m).sum(axis=1)) - np.log(K))
    bor = 1 / (1 + np.exp(np.clip(F1 - F0, -700, 700)))
    pxp = (1 - bor) * xp + bor / K
    return dict(freq=(a / a.sum()).tolist(), xp=xp.tolist(), pxp=pxp.tolist(), bor=float(bor))


# ---------------------------------------------------------------- generators
def design(rng):
    x = np.repeat(LEVELS, N_PER)
    block = np.empty(len(x), int)
    for l in LEVELS:                                           # spread each level evenly over the 20 blocks
        idx = np.where(x == l)[0]
        block[idx] = rng.permutation(np.arange(len(idx)) % N_BLOCK)
    return x, block


# Common scale: noise SD 1, noise mean 0; max-SNR mean DMAX; threshold between levels 2 and 3.
DMAX, X0, KM = 2.0, 2.5, 1.5


def gen(cell, rng):
    x, block = design(rng)
    n = len(x)
    if cell == "B_bifurcation":           # their Model 3 shape: two states, shared SD, P(high) logistic in SNR
        a = np.where(x == 0, 0, expit(KM * (x - X0)))
        hi = rng.random(n) < a
        y = np.where(hi, 1.0 + 0.2 * (x - X0), 0.0) * DMAX / 1.5 + rng.normal(0, 1, n)
    elif cell == "M2_unimodal":           # their Model 2B shape: Gaussian, logistic mean, SD linear in mean
        mu = DMAX * expit(KM * (x - X0))
        y = mu + (1 + 0.25 * mu) * rng.normal(0, 1, n)
    elif cell.startswith("G_jitter"):     # graded: logistic transfer of a trial-wise jittered threshold (continuous latent)
        tau = {"G_jitter_lo": 0.5, "G_jitter_mid": 1.0, "G_jitter_hi": 1.5}[cell]
        th = X0 + rng.normal(0, tau, n)
        y = DMAX * expit(KM * (x - th)) + rng.normal(0, 1, n)
    elif cell == "G_skew":                # graded: logistic mean, right-skewed noise (shifted gamma, SD 1)
        mu = DMAX * expit(KM * (x - X0))
        e = (rng.gamma(2.0, 1 / np.sqrt(2.0), n) - np.sqrt(2.0))
        y = mu + e
    elif cell == "G_heavy":               # graded: logistic mean, Student-t(4) noise scaled to SD 1
        mu = DMAX * expit(KM * (x - X0))
        y = mu + rng.standard_t(4, n) / np.sqrt(2.0)
    elif cell == "G_drift":               # graded: threshold drifts across blocks (slow state), Gaussian noise
        drift = np.cumsum(rng.normal(0, 0.35, N_BLOCK))
        drift -= drift.mean()
        y = DMAX * expit(KM * (x - X0 - drift[block])) + rng.normal(0, 1, n)
    else:
        raise ValueError(cell)
    return y, x, block


CELLS = ["B_bifurcation", "M2_unimodal", "G_jitter_lo", "G_jitter_mid", "G_jitter_hi", "G_skew", "G_heavy", "G_drift"]
GRADED = [c for c in CELLS if c.startswith("G_")]


def unimodal_check(cell, rng, n=400_000, grid=400):
    """Descriptive only: KDE peak count per level (not used in the decision; KDE is unreliable on heavy tails)."""
    from scipy.stats import gaussian_kde
    res = {}
    for l in LEVELS:
        ys = []
        while sum(len(v) for v in ys) < n:
            y, x, _ = gen(cell, rng)
            ys.append(y[x == l])
        v = np.concatenate(ys)[:n]
        kde = gaussian_kde(v[:20000])
        g = np.linspace(np.percentile(v, 0.5), np.percentile(v, 99.5), grid)
        d = kde(g)
        peaks = int(np.sum((d[1:-1] > d[:-2]) & (d[1:-1] > d[2:])))
        res[int(l)] = peaks
    return res


def one_study(args):
    cell, seed = args
    rng = np.random.default_rng(seed)
    lme, conv = [], []
    for s in range(N_SUB):
        y, x, block = gen(cell, rng)
        l, c = subject_lme(y, x, block)
        lme.append(l)
        conv.append(c)
    lme = np.array(lme)
    b = spm_bms(lme, rng)
    return dict(pxp3=b["pxp"][2], pxp=b["pxp"], bor=b["bor"], conv=float(np.mean(conv)),
                n_subj_m3_best=int(np.sum(lme.argmax(axis=1) == 2)), finite=bool(np.all(np.isfinite(lme))))


def run_cell(cell, studies):
    ss = np.random.SeedSequence([SEED, CELLS.index(cell)])
    seeds = [int(s.generate_state(1)[0]) for s in ss.spawn(studies)]
    t = time.time()
    with Pool(WORKERS) as p:
        res = p.map(one_study, [(cell, s) for s in seeds])
    pxp3 = np.array([r["pxp3"] for r in res])
    return dict(cell=cell, studies=studies, rate_pxp3_gt_095=float(np.mean(pxp3 > 0.95)),
                mean_pxp3=float(pxp3.mean()), mean_subjects_m3_best=float(np.mean([r["n_subj_m3_best"] for r in res])),
                mean_converged=float(np.mean([r["conv"] for r in res])),
                nonfinite_studies=int(sum(not r["finite"] for r in res)), seconds=round(time.time() - t), runs=res)


def smoke():
    rng = np.random.default_rng(1)
    for cell in ["B_bifurcation", "M2_unimodal"]:
        r = [one_study((cell, int(rng.integers(1 << 31)))) for _ in range(2)]
        print(cell, [(round(z["pxp3"], 3), z["n_subj_m3_best"], round(z["conv"], 2)) for z in r])
    # spm_bms sanity
    print("bms all-equal", spm_bms(np.zeros((20, 3)), rng)["pxp"])
    print("bms m3 strong", spm_bms(np.tile([0, 0, 20.0], (20, 1)), rng)["pxp"])


def run(cells):
    from evidence import require_sealed
    require_sealed(str(PREREG))
    require_sealed(str(Path(__file__)))
    OUT.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED + 1)
    for cell in cells or CELLS:
        um = unimodal_check(cell, rng)
        r = run_cell(cell, STUDIES)
        r["unimodal_peaks_per_level"] = um
        (OUT / f"{cell}.json").write_text(json.dumps(r) + "\n")
        print(cell, r["rate_pxp3_gt_095"], r["mean_pxp3"], r["mean_converged"], um, r["seconds"], "s", flush=True)


def summary():
    R = {c: json.loads((OUT / f"{c}.json").read_text()) for c in CELLS}
    valid = R["B_bifurcation"]["rate_pxp3_gt_095"] >= 0.80 and R["M2_unimodal"]["rate_pxp3_gt_095"] <= 0.05
    uni = {c: R[c]["unimodal_peaks_per_level"] for c in GRADED}   # descriptive only (prereg section 3)
    rates = {c: R[c]["rate_pxp3_gt_095"] for c in GRADED}
    eligible = rates                                             # graded = no discrete latent state, by construction
    if not valid:
        verdict = "VOID"
    elif any(r >= 0.50 for r in eligible.values()):
        verdict = "NOT SPECIFIC"
    elif all(r <= 0.10 for r in eligible.values()):
        verdict = "SPECIFIC"
    else:
        verdict = "MIXED"
    s = dict(verdict=verdict, valid=valid, bifurcation_recall=R["B_bifurcation"]["rate_pxp3_gt_095"],
             model2_false=R["M2_unimodal"]["rate_pxp3_gt_095"], graded_false=rates, kde_peaks=uni,
             mean_pxp3={c: R[c]["mean_pxp3"] for c in CELLS},
             mean_subjects_m3_best={c: R[c]["mean_subjects_m3_best"] for c in CELLS},
             converged={c: R[c]["mean_converged"] for c in CELLS})
    (OUT / "summary.json").write_text(json.dumps(s, indent=1) + "\n")
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    sys.path.insert(0, str(HERE.parents[0] / "rules"))
    a = sys.argv[1]
    {"smoke": smoke, "summary": summary}.get(a, lambda: run(sys.argv[2:]))()
