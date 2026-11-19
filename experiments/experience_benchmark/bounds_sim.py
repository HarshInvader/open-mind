"""Can the sealed design reach a bounded null (95% CI of the within-subject pair AUC inside [0.40, 0.60])?
Synthetic feature on the real per-subject N2 counts (de-duplicated metadata). No EEG.
  .venv/bin/python -I experiments/experience_benchmark/bounds_sim.py -> bounds_sim.json
"""
import json, os
import numpy as np, pandas as pd
from scipy.stats import norm
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
d = pd.read_csv(os.path.join(REPO, "experiments/dataset_audit/dream_records.csv"))
d = d.sort_values("Amendment").drop_duplicates(["Set ID", "Filename"], keep="last")
d = d[d.Experience.isin(["Experience", "No experience"]) & (d["Last sleep stage"].astype(str) == "N2")]
LAB = {9: "Rome", 3: "LODE", 16: "DATA1", 17: "Aamodt", 18: "Aamodt", 19: "Set19", 13: "Tononi", 1: "Zhang"}
d["lab"] = d["Set ID"].map(LAB); d = d.dropna(subset=["lab"])
subj = []
for (lab, s), g in d.groupby(["lab", "Subject ID"]):
    e, n = int((g.Experience == "Experience").sum()), int((g.Experience == "No experience").sum())
    if e and n: subj.append((lab, e, n))
rng = np.random.default_rng(7)

def pair_auc(parts):            # parts: list of (x_exp, x_no) per subject
    num = den = 0.0
    for a, b in parts:
        num += (a[:, None] > b[None, :]).sum() + 0.5 * (a[:, None] == b[None, :]).sum(); den += len(a) * len(b)
    return num / den

def one(S, auc, nb=500):
    dd = np.sqrt(2) * norm.ppf(auc)
    parts = [(rng.normal(dd, 1, e), rng.normal(0, 1, n)) for _, e, n in S]
    a0 = pair_auc(parts)
    labs = sorted({l for l, _, _ in S}); idx = {l: [i for i, s in enumerate(S) if s[0] == l] for l in labs}
    bs = [pair_auc([parts[j] for l in labs for j in rng.choice(idx[l], len(idx[l]))]) for _ in range(nb)]
    lo, hi = np.quantile(bs, [0.025, 0.975])
    return a0, lo, hi

out = {}
sets = {"confirm4 (sealed)": {"Rome", "LODE", "DATA1", "Aamodt"}, "confirm5 (+set19)": {"Rome", "LODE", "DATA1", "Aamodt", "Set19"},
        "all7 (+Tononi,Zhang)": {"Rome", "LODE", "DATA1", "Aamodt", "Set19", "Tononi", "Zhang"}}
for name, L in sets.items():
    S = [s for s in subj if s[0] in L]
    out[name] = {"n_subj": len(S), "n_exp": sum(e for _, e, _ in S), "n_no": sum(n for _, _, n in S)}
    for auc in (0.50, 0.53, 0.56):
        R = np.array([one(S, auc) for _ in range(150)])
        out[name][f"auc{auc}"] = {"P_bounded": float(np.mean((R[:, 1] > 0.4) & (R[:, 2] < 0.6))),
                                  "mean_halfwidth": round(float(np.mean((R[:, 2] - R[:, 1]) / 2)), 3)}
    print(name, out[name], flush=True)
json.dump(out, open(os.path.join(HERE, "bounds_sim.json"), "w"), indent=1)
