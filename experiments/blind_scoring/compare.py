"""Run only after marks.csv and totals.json were fixed. Compares blind marks with
../our_theory/coverage.csv (T1, T2 self-marks) and ../theory_scorecard/scorecard.csv (IIT, GNWT).
Run: python3 -I compare.py -> compare.json, disagreements.csv"""
import csv, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
LV = {"explains": 2, "compatible": 1, "silent": 0, "strained": -1, "contradicts": -2}
W = {"A": 3, "B": 2, "C": 1}
mine = {(r["constraint_id"], r["theory"]): r for r in csv.DictReader(open(os.path.join(HERE, "marks.csv")))}
other, oreason = {}, {}
for r in csv.DictReader(open(os.path.join(HERE, "..", "our_theory", "coverage.csv"))):
    for t in ("T1", "T2"):
        other[(r["id"], t)] = r[f"{t}_mark"].strip(); oreason[(r["id"], t)] = r[f"{t}_reason"]
for r in csv.DictReader(open(os.path.join(HERE, "..", "theory_scorecard", "scorecard.csv"))):
    if r["theory"] in ("IIT", "GNWT"):
        other[(r["constraint_id"], r["theory"])] = r["mark"].strip(); oreason[(r["constraint_id"], r["theory"])] = r["note"]
def kappa(a, b, weighted=False):
    cats = sorted(LV, key=LV.get); n = len(a); k = len(cats)
    idx = {c: i for i, c in enumerate(cats)}
    O = [[0] * k for _ in cats]
    for x, y in zip(a, b): O[idx[x]][idx[y]] += 1
    ra = [sum(row) for row in O]; cb = [sum(O[i][j] for i in range(k)) for j in range(k)]
    wt = (lambda i, j: abs(i - j) / (k - 1)) if weighted else (lambda i, j: 0 if i == j else 1)
    po = sum(wt(i, j) * O[i][j] for i in range(k) for j in range(k)) / n
    pe = sum(wt(i, j) * ra[i] * cb[j] for i in range(k) for j in range(k)) / n / n
    return 1 - po / pe if pe else float("nan")
out, dis = {}, []
for t in ("GNWT", "IIT", "T1", "T2"):
    keys = sorted(k for k in other if k[1] == t and k in mine and mine[k]["in_totals"] == "1")
    a = [mine[k]["mark"] for k in keys]; b = [other[k] for k in keys]
    strict_b = ["compatible" if (t in ("T1", "T2") and x == "explains") else x for x in b]
    their = sum(W[mine[k]["grade"]] * LV[other[k]] for k in keys)
    out[t] = {"n": len(keys), "agree": sum(x == y for x, y in zip(a, b)),
              "kappa": round(kappa(a, b), 3), "kappa_linear_weighted": round(kappa(a, b, True), 3),
              "their_total": their, "my_total": sum(W[mine[k]["grade"]] * LV[mine[k]["mark"]] for k in keys)}
    if t in ("T1", "T2"):
        out[t]["kappa_after_capping_their_explains"] = round(kappa(a, strict_b), 3)
        out[t]["their_total_capped"] = sum(W[mine[k]["grade"]] * LV[x] for k, x in zip(keys, strict_b))
    for k, x, y in zip(keys, a, b):
        if abs(LV[x] - LV[y]) >= 2:
            dis.append(dict(constraint_id=k[0], grade=mine[k]["grade"], theory=t, blind=x, original=y,
                            levels=LV[y] - LV[x], weighted_gap=W[mine[k]["grade"]] * (LV[y] - LV[x]),
                            blind_reason=mine[k]["reason"], original_reason=oreason[k][:300]))
dis.sort(key=lambda d: -abs(d["weighted_gap"]))
with open(os.path.join(HERE, "disagreements.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(dis[0])); w.writeheader(); w.writerows(dis)
json.dump(out, open(os.path.join(HERE, "compare.json"), "w"), indent=1)
print(json.dumps(out, indent=1)); print(len(dis), "cells differ by >=2 levels")
for d in dis: print(d["constraint_id"], d["grade"], d["theory"], d["blind"], "vs", d["original"], d["weighted_gap"], "|", d["original_reason"][:220])
