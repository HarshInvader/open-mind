"""Synthetic power gate for the awareness x metacognition test on Rausch & Zehetleitner (2016).

No real data is read here. The design is taken from the dataset readme and the paper:
20 subjects; contrasts 2.2, 3.9, 5, 5.5, 6.9% (0% excluded: no correct answer);
63 trials per contrast; group d_a per contrast from Table 1 (0.11, 0.88, 1.55, 1.83, 1.94).

Single-evidence null observer (one evidence sample e per trial, signed toward the truth):
    e ~ N(d/2, 1); correct = e > 0
    visibility v = |e| + gamma*d + sv*N(0,1)
    confidence c = |e| + sc*N(0,1)
Planted observer: confidence noise grows on low-visibility trials,
    c = |e| + sc*exp(-lam*z(v))*N(0,1)      (z = within-subject z-score)

Statistic: in a logistic regression of correct on z(c), z(v), z(c)*z(v), contrast and subject
dummies, the coefficient on z(c)*z(v). It is compared with its distribution under the
single-evidence null, refitted to each dataset (sc, sv, gamma by simulated moments; d per
subject x contrast from accuracy). Excess = observed - null mean; one-sided p = share of null >= observed.

Gate (Fable, 2026-11-23): power >= 0.80 at the planted lam whose AUROC2 seen-minus-unseen excess
is 0.05, and false-positive rate <= 0.05 at lam = 0. Otherwise the real-data test is not run.
"""
import json, sys, time
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm

D_GROUP = np.array([0.11, 0.88, 1.55, 1.83, 1.94])
NSUB, NPER = 20, 63
K = len(D_GROUP)


def design(rng):
    """Per-subject d per contrast (subject scale ~ N(1, 0.15))."""
    s = np.clip(rng.normal(1, 0.15, NSUB), 0.5, 1.5)
    return s[:, None] * D_GROUP[None, :]


def simulate(d, sc, sv, gamma, lam, rng, tail=None):
    """Returns arrays (subj, k, correct, c, v), with c and v z-scored within subject."""
    subj = np.repeat(np.arange(NSUB), K * NPER)
    k = np.tile(np.repeat(np.arange(K), NPER), NSUB)
    dd = d[subj, k]
    e = dd / 2 + rng.standard_normal(dd.size)
    correct = (e > 0).astype(float)
    a = np.abs(e)
    v = a + gamma * dd + sv * rng.standard_normal(dd.size)
    zv = zsub(v, subj)
    noise = rng.standard_t(3, dd.size) / np.sqrt(3) if tail == "t3" else rng.standard_normal(dd.size)
    c = a + sc * np.exp(-lam * zv) * noise
    return subj, k, correct, zsub(c, subj), zv


def zsub(x, subj):
    out = np.empty_like(x)
    for s in range(NSUB):
        m = subj == s
        out[m] = (x[m] - x[m].mean()) / (x[m].std() + 1e-12)
    return out


def moments(subj, k, correct, c, v):
    """Mean within-cell correlations: (c,correct), (v,correct), (c,v); and corr(v, contrast) within subject."""
    out = np.zeros(4)
    n = 0
    for s in range(NSUB):
        for kk in range(K):
            m = (subj == s) & (k == kk)
            y = correct[m]
            if y.std() == 0:
                continue
            out[0] += np.corrcoef(c[m], y)[0, 1]
            out[1] += np.corrcoef(v[m], y)[0, 1]
            out[2] += np.corrcoef(c[m], v[m])[0, 1]
            n += 1
    out[:3] /= max(n, 1)
    out[3] = np.mean([np.corrcoef(v[subj == s], k[subj == s])[0, 1] for s in range(NSUB)])
    return out


def d_from_acc(subj, k, correct):
    d = np.zeros((NSUB, K))
    for s in range(NSUB):
        for kk in range(K):
            acc = correct[(subj == s) & (k == kk)].mean()
            acc = np.clip(acc, 0.5 + 0.5 / NPER, 1 - 0.5 / NPER)
            d[s, kk] = 2 * norm.ppf(acc)
    return d


def fit_null(data, seed):
    """Simulated method of moments for (sc, sv, gamma) with common random numbers."""
    subj, k, correct, c, v = data
    target = moments(*data)
    d = d_from_acc(subj, k, correct)

    def loss(p):
        sc, sv, g = np.exp(p[0]), np.exp(p[1]), p[2]
        tot = 0
        for r in range(2):
            sim = simulate(d, sc, sv, g, 0.0, np.random.default_rng(seed + r))
            tot += np.sum((moments(*sim) - target) ** 2)
        return tot

    best = None
    for x0 in ([0.0, 0.5, 0.3], [-0.5, 1.0, 0.0], [0.5, 0.0, 0.8]):
        r = minimize(loss, x0, method="Nelder-Mead", options={"maxiter": 120, "xatol": 1e-2, "fatol": 1e-5})
        if best is None or r.fun < best.fun:
            best = r
    return d, np.exp(best.x[0]), np.exp(best.x[1]), best.x[2]


def logit_int(subj, k, correct, c, v):
    """Fixed-effects logistic regression via IRLS; returns the c*v coefficient."""
    n = correct.size
    X = [np.ones(n), c, v, c * v]
    X += [(k == kk).astype(float) for kk in range(1, K)]
    X += [(subj == s).astype(float) for s in range(1, NSUB)]
    X = np.column_stack(X)
    b = np.zeros(X.shape[1])
    for _ in range(25):
        eta = np.clip(X @ b, -30, 30)
        p = 1 / (1 + np.exp(-eta))
        w = p * (1 - p) + 1e-9
        H = X.T @ (X * w[:, None]) + 1e-6 * np.eye(X.shape[1])
        step = np.linalg.solve(H, X.T @ (correct - p))
        b += step
        if np.max(np.abs(step)) < 1e-6:
            break
    return b[3]


def auroc(x, y):
    pos, neg = x[y == 1], x[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    r = np.argsort(np.argsort(np.concatenate([pos, neg]))) + 1
    return (r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def auroc_gap(subj, k, correct, c, v):
    """Mean over subject x contrast of AUROC2(c) in the high-v half minus the low-v half."""
    gaps = []
    for s in range(NSUB):
        for kk in range(K):
            m = (subj == s) & (k == kk)
            hi = v[m] >= np.median(v[m])
            a1, a0 = auroc(c[m][hi], correct[m][hi]), auroc(c[m][~hi], correct[m][~hi])
            if not (np.isnan(a1) or np.isnan(a0)):
                gaps.append(a1 - a0)
    return np.mean(gaps)


def test_dataset(data, seed, B):
    d, sc, sv, g = fit_null(data, seed)
    obs = logit_int(*data)
    null = np.array([logit_int(*simulate(d, sc, sv, g, 0.0, np.random.default_rng(seed + 1000 + b))) for b in range(B)])
    return dict(obs=float(obs), null_mean=float(null.mean()), excess=float(obs - null.mean()),
                p=float((1 + np.sum(null >= obs)) / (B + 1)), sc=float(sc), sv=float(sv), gamma=float(g))


TRUE = dict(sc=0.8, sv=1.5, gamma=0.5)   # generating values for the synthetic "true" datasets


def calibrate(lams, reps, seed):
    """AUROC2 gap excess (planted minus null) per lam, at the generating parameters."""
    rng = np.random.default_rng(seed)
    out = {}
    base = None
    for lam in lams:
        g = []
        for r in range(reps):
            d = design(rng)
            g.append(auroc_gap(*simulate(d, TRUE["sc"], TRUE["sv"], TRUE["gamma"], lam, rng)))
        out[lam] = float(np.mean(g))
    base = out[0.0]
    return {lam: dict(gap=v, excess=v - base) for lam, v in out.items()}


def main():
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    B = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    t0 = time.time()
    cal = calibrate([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7], 40, 1)
    print("calibration", json.dumps(cal), flush=True)
    lams = sorted(cal)
    exc = [cal[l]["excess"] for l in lams]
    lam_star = float(np.interp(0.05, exc, lams)) if max(exc) >= 0.05 else None
    print("lam* for AUROC2 excess 0.05:", lam_star, flush=True)
    res = {"calibration": cal, "lam_star": lam_star, "R": R, "B": B, "TRUE": TRUE, "conds": {}}
    conds = [("null", 0.0, None), ("null_t3", 0.0, "t3")]
    if lam_star is not None:
        conds += [("planted", lam_star, None), ("planted_half", lam_star / 2, None)]
    rng = np.random.default_rng(7)
    for name, lam, tail in conds:
        rows = []
        for r in range(R):
            d = design(rng)
            data = simulate(d, TRUE["sc"], TRUE["sv"], TRUE["gamma"], lam, rng, tail=tail)
            rows.append(test_dataset(data, 10_000 * (r + 1), B))
        rate = float(np.mean([x["p"] < 0.05 for x in rows]))
        res["conds"][name] = dict(lam=lam, tail=tail, reject_rate=rate,
                                  mean_excess=float(np.mean([x["excess"] for x in rows])), rows=rows)
        print(name, "lam", round(lam, 3), "reject rate", rate, "elapsed", round(time.time() - t0), flush=True)
    fp = res["conds"]["null"]["reject_rate"]
    pw = res["conds"].get("planted", {}).get("reject_rate")
    res["gate_pass"] = bool(pw is not None and pw >= 0.80 and fp <= 0.05)
    print("GATE", "PASS" if res["gate_pass"] else "FAIL", "power", pw, "fpr", fp)
    json.dump(res, open(__file__.replace("power_gate.py", "power_gate.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
