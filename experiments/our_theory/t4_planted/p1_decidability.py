"""T4 P1 planted decidability check (synthetic only; no Stockart signal is read).

  .venv/bin/python -I experiments/our_theory/t4_planted/p1_decidability.py [n_rep]  -> p1_decidability.json

Question: with the real no-report trial counts, can the P1 pipeline tell a two-state late
VVC score (T4) from graded, unimodal alternatives?  Draft rule (T4_PREDICTIONS_DRAFT.md):
P1 is "testable" only if it passes in >= 80% of planted mixtures and <= 5% of planted nulls.

Design facts used (from the draft, checked on OSF): no-report intensity fixed at two levels
(threshold, 150%); 72 trials per level in Grenoble (3 blocks), 48 in Brno (2 blocks); the low
state is anchored by a pre-onset window from every trial. Number of VVC patients with no-report
data is not yet known: 16 assumed (VVC decoders exist for 18; 27 of 29 did no-report), 10 as a
pessimistic case.

Pipeline (what would be sealed):
 1. per patient, z-score late scores by the pre-onset reference (mean, sd over all trials);
 2. regress out trial index within block (attention drift);
 3. 5-fold CV within patient, stratified by intensity: held-out log-likelihood per trial of
    M1 mixture (low N(0,1) fixed, high N(mu_k, s), weight beta_k) vs graded rivals M2a normal
    and M2b skew-normal (|shape| <= 5) per intensity;
 4. effect = mean over patients of min(LL_M1 - LL_M2a, LL_M1 - LL_M2b) per trial; 95% patient-bootstrap CI;
 5. PASS = CI lower bound > 0 AND mean beta_150 > mean beta_thr AND 0.1 <= mean beta_thr <= 0.7.
The draft's model 3 (the authors' leaky accumulation) is used here as a generator, not a fitted
rival; its equations still have to be taken from the paper.
"""
import json
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20261119)


# ---------------- generators: return (late, ref, intensity, block, trial_index) ----------------
def design(n_per_level):
    nb = 3 if n_per_level == 72 else 2
    k = np.tile(np.r_[np.zeros(24), np.ones(24)], nb).astype(int)
    blk = np.repeat(np.arange(nb), 48)
    idx = np.tile(np.arange(48), nb)
    perm = np.concatenate([rng.permutation(48) + 48 * b for b in range(nb)])
    return k[perm], blk, idx


def noise(n, kind):
    if kind == "t5":
        return stats.t.rvs(5, size=n, random_state=rng) / np.sqrt(5 / 3)
    return rng.normal(size=n)


def gen_mixture(n, d, b_thr=0.5, b_150=0.85, nk="normal", s_high=1.0):
    k, blk, idx = design(n)
    dd = max(0.2, d + rng.normal(0, 0.25))               # patient heterogeneity
    beta = np.where(k == 0, np.clip(b_thr + rng.normal(0, 0.1), .05, .95), np.clip(b_150 + rng.normal(0, 0.05), .05, .98))
    hi = rng.random(len(k)) < beta
    late = np.where(hi, dd * np.where(k == 0, 1.0, 1.15) + s_high * noise(len(k), nk), noise(len(k), nk))
    return late, noise(len(k), nk), k, blk, idx


def gen_graded(n, d, kind="normal", b_thr=0.5, b_150=0.85, drift=0.0):
    """Unimodal with the SAME mean and variance as the matching mixture."""
    k, blk, idx = design(n)
    dd = max(0.2, d + rng.normal(0, 0.25))
    b = np.where(k == 0, b_thr, b_150); m = b * dd * np.where(k == 0, 1.0, 1.15)
    sd = np.sqrt(1 + b * (1 - b) * (dd * np.where(k == 0, 1.0, 1.15)) ** 2)
    if kind == "skew":                                   # right-skewed unimodal, a = 4
        a = 4.0; delta = a / np.sqrt(1 + a * a)
        z = stats.skewnorm.rvs(a, size=len(k), random_state=rng)
        z = (z - delta * np.sqrt(2 / np.pi)) / np.sqrt(1 - 2 * delta ** 2 / np.pi)
        late = m + sd * z
    else:
        late = m + sd * noise(len(k), kind)
    late = late - drift * (idx / 47 - 0.5) * 2           # attention falls over a block
    return late, noise(len(k), kind), k, blk, idx


def gen_accum(n, d, bound=None):
    """Leaky accumulator; late score = mean state 0.4-0.9 s plus measurement noise.
    Per-trial input gain varies. With `bound`, the state is absorbed at the bound."""
    k, blk, idx = design(n)
    dt, tau, sig = 1 / 64, 0.25, 0.6
    T = np.arange(0, 0.9, dt); late_w = (T >= 0.4)
    I = np.where(k == 0, 1.0, 1.5)[:, None] * np.clip(rng.normal(1, 0.5, len(k)), 0, None)[:, None]
    x = np.zeros(len(k)); acc = np.zeros(len(k)); hit = np.zeros(len(k), bool)
    for j, t in enumerate(T):
        inp = I[:, 0] * (t < 0.3) * 4.0
        x = x + dt * (-x / tau + inp) + sig * np.sqrt(dt) * rng.normal(size=len(k))
        if bound is not None:
            hit |= x >= bound; x = np.where(hit, bound, x)
        if late_w[j]:
            acc += x
    sgn = acc / late_w.sum()
    sgn = sgn / np.std(sgn) * d * 0.6                    # scale signal to the scenario's d
    return sgn + rng.normal(size=len(k)), rng.normal(size=len(k)), k, blk, idx


# ---------------- models ----------------
def fit_mix(x, k, n_init=4):
    best = None
    for it in range(n_init):
        mu = np.array([np.quantile(x[k == j], 0.75 + 0.05 * it) for j in (0, 1)])
        s, beta = 1.0, np.array([0.5, 0.7])
        for _ in range(200):
            p_lo = (1 - beta[k]) * stats.norm.pdf(x)
            p_hi = beta[k] * stats.norm.pdf(x, mu[k], s)
            r = p_hi / (p_lo + p_hi + 1e-300)
            beta = np.array([np.clip(r[k == j].mean(), 1e-3, 1 - 1e-3) for j in (0, 1)])
            mu = np.array([(r[k == j] * x[k == j]).sum() / (r[k == j].sum() + 1e-9) for j in (0, 1)])
            s = max(0.3, np.sqrt((r * (x - mu[k]) ** 2).sum() / (r.sum() + 1e-9)))
        ll = np.log((1 - beta[k]) * stats.norm.pdf(x) + beta[k] * stats.norm.pdf(x, mu[k], s)).sum()
        if best is None or ll > best[0]:
            best = (ll, mu, s, beta)
    return best[1:]


def ll_mix(par, x, k):
    mu, s, beta = par
    return np.log((1 - beta[k]) * stats.norm.pdf(x) + beta[k] * stats.norm.pdf(x, mu[k], s) + 1e-300)


def _sn1(x):
    from scipy.optimize import minimize
    m, sd = x.mean(), x.std()
    nll = lambda p: -stats.skewnorm.logpdf(x, p[0], p[1], np.exp(p[2])).sum()
    best = None
    for a0 in (-2.0, 0.0, 2.0):
        r = minimize(nll, [a0, m, np.log(sd)], method="L-BFGS-B",
                     bounds=[(-5, 5), (m - 3 * sd, m + 3 * sd), (np.log(sd) - 2, np.log(sd) + 2)])
        if best is None or r.fun < best.fun:
            best = r
    return best.x[0], best.x[1], np.exp(best.x[2])


def fit_sn(x, k):          # skew-normal per intensity, shape bounded to |a| <= 5
    return [_sn1(x[k == j]) for j in (0, 1)]


def fit_nrm(x, k):
    return [(x[k == j].mean(), x[k == j].std()) for j in (0, 1)]


def ll_nrm(par, x, k):
    out = np.empty(len(x))
    for j in (0, 1):
        out[k == j] = stats.norm.logpdf(x[k == j], *par[j])
    return out


def ll_sn(par, x, k):
    out = np.empty(len(x))
    for j in (0, 1):
        a, loc, sc = par[j]
        out[k == j] = stats.skewnorm.logpdf(x[k == j], a, loc, sc)
    return np.maximum(out, -50)


def patient(late, ref, k, blk, idx):
    x = (late - ref.mean()) / ref.std()
    for b in np.unique(blk):                           # remove linear trial-index drift within block
        m = blk == b
        X = np.c_[np.ones(m.sum()), idx[m], k[m]]
        coef = np.linalg.lstsq(X, x[m], rcond=None)[0]
        x[m] = x[m] - coef[1] * (idx[m] - idx[m].mean())
    folds = np.empty(len(x), int)
    for j in (0, 1):
        w = np.where(k == j)[0]; folds[rng.permutation(w)] = np.arange(len(w)) % 5
    lm, ls, ln = [], [], []
    for f in range(5):
        tr, te = folds != f, folds == f
        lm.append(ll_mix(fit_mix(x[tr], k[tr]), x[te], k[te]))
        ls.append(ll_sn(fit_sn(x[tr], k[tr]), x[te], k[te]))
        ln.append(ll_nrm(fit_nrm(x[tr], k[tr]), x[te], k[te]))
    lm, ls, ln = (np.concatenate(v).mean() for v in (lm, ls, ln))
    beta = fit_mix(x, k)[2]
    return min(lm - ls, lm - ln), beta     # mixture must beat the better graded rival


def run(gen, n_pat, n_rep, frac_brno=1 / 3):
    res = []
    for _ in range(n_rep):
        ns = [48 if i < round(n_pat * frac_brno) else 72 for i in range(n_pat)]
        out = [patient(*gen(n)) for n in ns]
        eff = np.array([o[0] for o in out]); bt = np.array([o[1] for o in out])
        boot = np.array([eff[rng.integers(0, n_pat, n_pat)].mean() for _ in range(2000)])
        lo = np.quantile(boot, 0.025)
        b0, b1 = bt[:, 0].mean(), bt[:, 1].mean()
        res.append(dict(eff=eff.mean(), lo=lo, b_thr=b0, b_150=b1,
                        PASS=bool(lo > 0 and b1 > b0 and 0.1 <= b0 <= 0.7)))
    return {"pass_rate": float(np.mean([r["PASS"] for r in res])),
            "ll_effect_mean": round(float(np.mean([r["eff"] for r in res])), 4),
            "ci_lo_gt0_rate": float(np.mean([r["lo"] > 0 for r in res])),
            "beta_thr_mean": round(float(np.mean([r["b_thr"] for r in res])), 3),
            "beta_150_mean": round(float(np.mean([r["b_150"] for r in res])), 3), "n_rep": n_rep}


def main():
    n_rep = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    S = {}
    n_pat = 16
    for d in (1.0, 1.5, 2.0, 3.0):
        S[f"MIX d={d} npat={n_pat}"] = (lambda n, d=d: gen_mixture(n, d), n_pat)
    S["MIX d=2.0 t5-noise npat=16"] = (lambda n: gen_mixture(n, 2.0, nk="t5"), n_pat)
    S["MIX d=3.0 npat=10"] = (lambda n: gen_mixture(n, 3.0), 10)
    for d in (1.0, 2.0):
        S[f"NULL graded-normal d={d} npat={n_pat}"] = (lambda n, d=d: gen_graded(n, d), n_pat)
    S["NULL graded-skew d=2.0 npat=16"] = (lambda n: gen_graded(n, 2.0, "skew"), n_pat)
    S["NULL graded-t5 d=2.0 npat=16"] = (lambda n: gen_graded(n, 2.0, "t5"), n_pat)
    S["NULL graded+drift d=1.0 npat=16"] = (lambda n: gen_graded(n, 1.0, drift=0.8), n_pat)
    S["NULL leaky-accumulator d=1.5 npat=16"] = (lambda n: gen_accum(n, 1.5), n_pat)
    S["AMBIG accumulator-to-bound d=1.5 npat=16"] = (lambda n: gen_accum(n, 1.5, bound=0.8), n_pat)
    out = {}
    for name, (g, n_pat) in S.items():
        out[name] = run(g, n_pat, n_rep)
        print(name, out[name], flush=True)
    json.dump(out, open(os.path.join(HERE, "p1_decidability.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
