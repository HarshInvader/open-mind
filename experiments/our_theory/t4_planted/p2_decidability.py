"""T4 P2 planted decidability check (synthetic only; no Stockart signal is read).

  .venv/bin/python -I experiments/our_theory/t4_planted/p2_decidability.py [n_rep]  -> p2_decidability.json

P2 mark 1: in delayed report, late VVC score on misses equals correct rejections:
the 90% patient-bootstrap interval of mean (miss - CR) / sd_CR lies inside +-0.2.
P2 mark 2: a label-free score predicts report (AUROC >= 0.65). Any score monotone in the
late signal does this in every world, so here we only report hit-vs-miss AUROC to calibrate.

Counts (draft, from OSF): per block 10 catch, 24 threshold, 24 at 125%; 3 blocks Grenoble,
2 Brno (1/3 of patients). 16 VVC patients assumed. FA rate about 5%.

Worlds, each calibrated by the hit-vs-miss AUROC of the late score (the paper reports about 0.8
in the best patients, lower elsewhere):
  T4:      a hidden state z decides report (with lapses); score = d * z + noise.
  GRADED:  internal evidence L = mu_int + sensory noise; report = L + decision noise > c
           (c gives 5% FA); score = a * L + measurement noise.  f = share of internal noise that
           is sensory (upstream of VVC), the rest is decision noise downstream of VVC.
"""
import json
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20261120)
C = stats.norm.ppf(0.95)


def counts(n_pat):
    return [2 if i < round(n_pat / 3) else 3 for i in range(n_pat)]


def auc(a, b):
    return stats.mannwhitneyu(a, b).statistic / (len(a) * len(b))


def patient_t4(nb, d, lapse, beta=(0.5, 0.66)):
    out = {}
    for name, n, b in (("catch", 10 * nb, 0.0), ("thr", 24 * nb, beta[0]), ("125", 24 * nb, beta[1])):
        z = rng.random(n) < b
        rep = np.where(rng.random(n) < lapse, ~z, z) if b > 0 else rng.random(n) < 0.05
        out[name] = (d * z + rng.normal(size=n), rep)
    return out


def patient_graded(nb, a, f):
    out = {}
    for name, n, mu in (("catch", 10 * nb, 0.0), ("thr", 24 * nb, C), ("125", 24 * nb, 1.25 * C)):
        L = mu + np.sqrt(f) * rng.normal(size=n)
        rep = L + np.sqrt(1 - f) * rng.normal(size=n) > C
        out[name] = (a * L + rng.normal(size=n), rep)
    return out


def one(world, n_pat):
    diffs, aucs = [], []
    for nb in counts(n_pat):
        p = world(nb)
        cr = p["catch"][0][~p["catch"][1]]
        s = np.r_[p["thr"][0], p["125"][0]]; r = np.r_[p["thr"][1], p["125"][1]]
        miss, hit = s[~r], s[r]
        diffs.append((miss.mean() - cr.mean()) / cr.std(ddof=1))
        aucs.append(auc(hit, miss))
    diffs = np.array(diffs)
    boot = np.array([diffs[rng.integers(0, n_pat, n_pat)].mean() for _ in range(2000)])
    lo, hi = np.quantile(boot, [0.05, 0.95])
    return diffs.mean(), lo, hi, np.mean(aucs)


def run(world, n_pat, n_rep, bound=0.2):
    R = np.array([one(world, n_pat) for _ in range(n_rep)])
    equiv = (R[:, 1] > -bound) & (R[:, 2] < bound)
    above = R[:, 1] > bound                      # draft "T4 fails": interval excludes +0.2 from above
    return {"mark1_pass_rate": float(equiv.mean()), "T4_fail_rate": float(above.mean()),
            "miss_minus_CR_sd": round(float(R[:, 0].mean()), 3), "ci90_width": round(float((R[:, 2] - R[:, 1]).mean()), 3),
            "hit_vs_miss_auroc": round(float(R[:, 3].mean()), 3), "n_rep": n_rep}


def main():
    n_rep = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    S = {}
    for n_pat in (16, 8):
        for d in (1.0, 1.5):
            for lapse in (0.0, 0.1):
                S[f"T4 d={d} lapse={lapse} npat={n_pat}"] = (lambda nb, d=d, l=lapse: patient_t4(nb, d, l), n_pat)
        for a in (0.5, 1.0):
            for f in (1.0, 0.5, 0.2):
                S[f"GRADED a={a} sensory_share={f} npat={n_pat}"] = (lambda nb, a=a, f=f: patient_graded(nb, a, f), n_pat)
    out = {}
    for k, (w, n) in S.items():
        out[k] = run(w, n, n_rep)
        print(k, out[k], flush=True)
    json.dump(out, open(os.path.join(HERE, "p2_decidability.json"), "w"), indent=1)


def lapse_followup(n_rep=300, bound=0.2):
    """High-confidence misses only: fewer lapses, about 30% fewer misses."""
    res = {}
    for d in (1.0, 1.5):
        for lapse in (0.03, 0.05):
            def w(nb, d=d, l=lapse):
                p = patient_t4(nb, d, l)
                for k in ("thr", "125"):
                    s, r = p[k]; keep = r | (rng.random(len(r)) < 0.7)
                    p[k] = (s[keep], r[keep])
                return p
            res[f"T4 hiconf-misses d={d} lapse={lapse} npat=16"] = run(w, 16, n_rep, bound)
    for a, f in ((0.5, 1.0), (1.0, 1.0)):
        def g(nb, a=a, f=f):
            p = patient_graded(nb, a, f)
            for k in ("thr", "125"):
                s, r = p[k]; keep = r | (rng.random(len(r)) < 0.7)
                p[k] = (s[keep], r[keep])
            return p
        res[f"GRADED hiconf-misses a={a} sensory_share={f} npat=16"] = run(g, 16, n_rep, bound)
    for k, v in res.items():
        print(k, v, flush=True)
    json.dump(res, open(os.path.join(HERE, f"p2_lapse_followup_b{bound}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
