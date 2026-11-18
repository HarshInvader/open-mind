"""Weighted totals (grade A3/B2/C1 x E+2 C+1 S0 T-1 X-2, C59 excluded, max 250) and
constraint-bootstrap CIs. Run: python3 -I totals.py -> totals.json"""
import csv, json, os, random
HERE = os.path.dirname(os.path.abspath(__file__))
rows = [r for r in csv.DictReader(open(os.path.join(HERE, "marks.csv"))) if r["in_totals"] == "1"]
TH = ["GNWT", "IIT", "T1", "T2"]
cids = sorted({r["constraint_id"] for r in rows})
S = {c: {} for c in cids}
for r in rows:
    S[r["constraint_id"]][r["theory"]] = int(r["weight"]) * int(r["points"])
maxs = sum(2 * int(r["weight"]) for r in rows if r["theory"] == "GNWT")
tot = {t: sum(S[c][t] for c in cids) for t in TH}
counts = {t: {} for t in TH}
for r in rows:
    counts[r["theory"]][r["mark"]] = counts[r["theory"]].get(r["mark"], 0) + 1
pairs = [("T1", "IIT"), ("T1", "GNWT"), ("T2", "IIT"), ("T2", "GNWT"), ("T1", "T2"), ("IIT", "GNWT")]
rng = random.Random(30); B = 10000
bt = {t: [] for t in TH}; bd = {p: [] for p in pairs}
for _ in range(B):
    s = [rng.choice(cids) for _ in cids]
    v = {t: sum(S[c][t] for c in s) for t in TH}
    for t in TH: bt[t].append(v[t])
    for a, b in pairs: bd[(a, b)].append(v[a] - v[b])
def ci(x):
    x = sorted(x); return [x[int(0.025 * len(x))], x[int(0.975 * len(x)) - 1]]
out = {"max": maxs, "n_constraints": len(cids), "bootstrap_reps": B,
       "totals": {t: {"score": tot[t], "ci95": ci(bt[t]), "counts": counts[t]} for t in TH},
       "differences": {f"{a}-{b}": {"diff": tot[a] - tot[b], "ci95": ci(bd[(a, b)]),
                       "share_boot_gt0": sum(d > 0 for d in bd[(a, b)]) / B} for a, b in pairs}}
json.dump(out, open(os.path.join(HERE, "totals.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
