"""Step 1 of task #42: K2 power check on the real per-subject awakening counts (no EEG, no features).

  python3 -I experiments/experience_benchmark/power_sim.py   -> power_sim.json

Synthetic feature = d * y + subject offset + noise. Single-measure AUC on subject-centred features,
pooled over the unexposed labs (subjects with both classes only). Null: within-subject label
permutation (300), p from a normal fit to the permutation null so Holm-level alphas are reachable. Reports power at alpha 0.05 and at the Holm-worst alpha 0.05/28 (14 measures x 2
stages), plus the false-positive rate at d = 0. AUC = Phi(d/sqrt(2)): d 0.36 -> AUC 0.60.
"""
import collections
import csv
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
UNEXPOSED = {"9": "Rome", "3": "LODE", "16": "DATA1", "17": "Aamodt", "18": "Aamodt"}


def counts(stage):
    R = list(csv.DictReader(open(os.path.join(REPO, "experiments", "dataset_audit", "dream_records.csv"))))
    st = lambda s: "N3" if s.startswith("N3") else s
    s = collections.defaultdict(collections.Counter)
    for x in R:
        if x["Set ID"] in UNEXPOSED and st(x["Last sleep stage"]) == stage and x["Experience"] in ("Experience", "No experience"):
            s[(UNEXPOSED[x["Set ID"]], x["Subject ID"])][x["Experience"]] += 1
    return [(k[0], v["Experience"], v["No experience"]) for k, v in s.items() if v["Experience"] and v["No experience"]]


def auc(score, y):
    r = np.argsort(np.argsort(score)) + 1
    n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def one(subj, d, rng, n_perm=300):
    y = np.concatenate([np.r_[np.ones(e), np.zeros(n)] for _, e, n in subj]).astype(int)
    g = np.concatenate([np.full(e + n, i) for i, (_, e, n) in enumerate(subj)])
    x = d * y + rng.normal(0, 1, len(subj))[g] + rng.normal(size=len(y))
    xc = x - np.bincount(g, x)[g] / np.bincount(g)[g]
    a0 = auc(xc, y)
    null = np.empty(n_perm)
    idx = [np.where(g == i)[0] for i in range(len(subj))]
    for k in range(n_perm):
        yp = y.copy()
        for ii in idx:
            yp[ii] = rng.permutation(y[ii])
        null[k] = auc(xc, yp)
    from math import erfc, sqrt
    z = (a0 - null.mean()) / null.std()
    return a0, 0.5 * erfc(z / sqrt(2))   # normal approximation to the permutation null (one-sided)


def main():
    rng = np.random.default_rng(42)
    out = {}
    for stage in ("N2", "REM"):
        subj = counts(stage)
        out[stage] = {"n_subjects": len(subj), "n_exp": int(sum(e for _, e, _ in subj)),
                      "n_noexp": int(sum(n for _, _, n in subj)),
                      "labs": dict(collections.Counter(l for l, _, _ in subj))}
        for d in (0.0, 0.2, 0.36, 0.5):
            res = [one(subj, d, rng) for _ in range(200)]
            a = np.array([r[0] for r in res]); p = np.array([r[1] for r in res])
            out[stage][f"d={d}"] = {"mean_auc": round(float(a.mean()), 3), "power_0.05": float(np.mean(p < 0.05)),
                                    "power_holm28": float(np.mean(p < 0.05 / 28))}
            print(stage, d, out[stage][f"d={d}"], flush=True)
    out["note"] = "p from a normal fit to 300 within-subject permutations; the sealed analysis should use >= 5000 permutations."
    json.dump(out, open(os.path.join(HERE, "power_sim.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
