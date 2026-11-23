"""Score the blinded ratings under the sealed rules (prereg docs/prereg/2026-11-23_theory_likelihood_pilot.md).

Input: ratings/rater_<k>.json (each rater's JSON array, saved verbatim) + packets/rater_<k>_key.json.
Usage: python3 -I score.py            # real ratings
       python3 -I score.py --planted  # synthetic raters with known answers (planted gate; no real ratings used)
       python3 -I score.py --planted --leak  # same, with a placebo that leans toward the real outcome (must be VOID)
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RATERS = ["r1", "r2", "r3"]
CLIP = (0.01, 0.99)
LEAK = "--leak" in sys.argv   # planted leak: placebo drifts toward the real outcome
REAL = ["IIT", "GNWT", "RPT", "HOT", "PP", "AST"]


def logit(p):
    return math.log(p / (1 - p))


def kripp_interval(mat):
    """Krippendorff's alpha, interval metric, for a units x raters matrix with no missing values."""
    mat = np.asarray(mat, float)
    n_u, m = mat.shape
    vals = mat.ravel()
    n = vals.size
    do = sum(((row[:, None] - row[None, :]) ** 2).sum() / (m - 1) for row in mat) / n
    de = ((vals[:, None] - vals[None, :]) ** 2).sum() / (n * (n - 1))
    return float(1 - do / de) if de > 0 else float("nan")


def load(planted=False, rng=None):
    d = json.load(open(os.path.join(HERE, "items.json")))
    cells = {}   # (rater, theory, item) -> p_actual
    for r in RATERS:
        key = json.load(open(os.path.join(HERE, "packets", f"rater_{r}_key.json")))
        if planted:
            arr = planted_ratings(d, key, rng)
        else:
            arr = json.load(open(os.path.join(HERE, "ratings", f"rater_{r}.json")))
        seen = set()
        for x in arr:
            fid, t = x["finding"], x["theory"]
            assert fid in key and (t, fid) not in seen, (r, t, fid)
            seen.add((t, fid))
            p = min(max(float(x["p"]), CLIP[0]), CLIP[1])
            pa = p if key[fid]["real_is_a"] else 1 - p
            cells[(r, t, key[fid]["item"])] = pa
        assert len(seen) == 8 * len(key), (r, len(seen))
    return d, cells


def planted_ratings(d, key, rng):
    """Synthetic rater: knows a planted truth table and adds noise. Toy and placebo follow their definitions;
    real theories follow a planted pattern (IIT strong on half the items, others weaker)."""
    out = []
    items = [it["id"] for it in d["items"]]
    truth = {}
    for t in REAL:
        truth[t] = {c: (0.85 if (t == "IIT" and k % 2 == 0) else 0.5 + 0.05 * ((k + len(t)) % 3)) for k, c in enumerate(items)}
    truth["TOY_Z"] = {c: {"actual": 0.85, "mirror": 0.15, "silent": 0.5}[d["toy_key"][c]] for c in items}
    truth["PLACEBO_Q"] = {c: (0.72 if LEAK else 0.5) for c in items}
    for fid, k in key.items():
        for t, tab in truth.items():
            pa = float(np.clip(tab[k["item"]] + rng.normal(0, 0.05), 0.01, 0.99))
            out.append(dict(theory=t, finding=fid, p=pa if k["real_is_a"] else 1 - pa))
    return out


def analyse(d, cells, rng):
    items = [it["id"] for it in d["items"]]
    res = {}
    # G1 toy recovery
    tk = d["toy_key"]
    com = [(r, c) for r in RATERS for c in items if tk[c] != "silent"]
    ok = sum((cells[(r, "TOY_Z", c)] >= 0.70) if tk[c] == "actual" else (cells[(r, "TOY_Z", c)] <= 0.30) for r, c in com)
    res["G1_toy_recovery"] = dict(correct=int(ok), of=len(com), frac=ok / len(com), pass_=ok / len(com) >= 0.90)
    # G2 placebo leak
    pq = np.array([cells[(r, "PLACEBO_Q", c)] for r in RATERS for c in items])
    bias = float(np.mean(pq - 0.5))
    outside = float(np.mean((pq < 0.35) | (pq > 0.65)))
    res["G2_placebo"] = dict(mean_bias_toward_real=bias, frac_outside_035_065=outside,
                             pass_=(bias <= 0.10) and (outside <= 0.20))
    # G3 agreement on the 60 real cells (logit p)
    mat = [[logit(cells[(r, t, c)]) for r in RATERS] for t in REAL for c in items]
    a = kripp_interval(mat)
    res["G3_alpha"] = dict(alpha=a, pass_=a >= 0.67)
    # Scores
    bits = {t: np.array([[math.log2(2 * cells[(r, t, c)]) for c in items] for r in RATERS]) for t in REAL}
    res["scores"] = {}
    B = 2000
    boot = {t: [] for t in REAL}
    for _ in range(B):
        ri = rng.integers(0, len(RATERS), len(RATERS))
        ci = rng.integers(0, len(items), len(items))
        for t in REAL:
            boot[t].append(bits[t][np.ix_(ri, ci)].sum(axis=1).mean())
    for t in REAL:
        pm = np.array([[cells[(r, t, c)] for c in items] for r in RATERS]).mean(axis=0)
        res["scores"][t] = dict(bits=float(bits[t].sum(axis=1).mean()),
                                ci=[float(np.percentile(boot[t], 2.5)), float(np.percentile(boot[t], 97.5))],
                                n_elastic=int(np.sum((pm >= 0.4) & (pm <= 0.6))),
                                n_predicts_real=int(np.sum(pm > 0.6)), n_predicts_mirror=int(np.sum(pm < 0.4)),
                                per_item={c: round(float(v), 3) for c, v in zip(items, pm)})
    pairs = {}
    for i, t in enumerate(REAL):
        for u in REAL[i + 1:]:
            diff = np.array(boot[t]) - np.array(boot[u])
            lo, hi = float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5))
            if lo > 0 or hi < 0:
                pairs[f"{t}-{u}"] = [lo, hi]
    res["separated_pairs"] = pairs
    g = res["G1_toy_recovery"]["pass_"] and res["G2_placebo"]["pass_"]
    if not g:
        res["verdict"] = "VOID: raters cannot score theories blind to the outcome (toy or placebo gate failed)"
    elif not res["G3_alpha"]["pass_"]:
        res["verdict"] = "UNDER-SPECIFIED: raters disagree (alpha < 0.67); theories too under-specified to score this way"
    else:
        res["verdict"] = "SCORABLE: gates pass; pilot scores reported; full 59-constraint run may proceed"
    return res


def main():
    planted = "--planted" in sys.argv
    rng = np.random.default_rng(23)
    d, cells = load(planted, rng)
    res = analyse(d, cells, np.random.default_rng(2311))
    out = os.path.join(HERE, ("planted_leak.json" if LEAK else "planted.json") if planted else "result.json")
    json.dump(res, open(out, "w"), indent=1)
    print("VERDICT:", res["verdict"])
    print(json.dumps({k: v for k, v in res.items() if k != "scores"}, indent=1))
    for t, s in res["scores"].items():
        print(t, round(s["bits"], 2), [round(x, 2) for x in s["ci"]], "elastic", s["n_elastic"],
              "real", s["n_predicts_real"], "mirror", s["n_predicts_mirror"])


if __name__ == "__main__":
    main()
