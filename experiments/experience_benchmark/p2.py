"""P2 (prereg §7) and K2 on the REALISED post-exclusion counts. Run after extraction, before unblinding.

  .venv/bin/python -I experiments/experience_benchmark/p2.py   -> p2.json

Reads only which records were extracted with status "ok" (features/<lab>.jsonl: set, file, stage, status)
and the per-awakening metadata (class counts per subject were already read in the audit). No feature value
is read. Counts: as analysis.py (N2, Experience vs No experience, Proportion artifacts <= 0.5, subjects with
both classes; subject key (lab, Subject ID)).

Synthetic feature per awakening: subject offset N(0, 1) + d * y + N(0, 1), d = sqrt(2) * Phi^-1(AUC).
- Power at AUC 0.60 under Holm-8 (Tier 1): one measure carries the effect; it is declared found if its
  permutation p (2,000 within-subject permutations, stats.family_a) is below 0.05 / 8, the first Holm step
  (the worst case: the effect is the only one). 300 simulated datasets. K2 needs >= 0.80.
- P(95% CI inside [0.40, 0.60]) at true AUC 0.50 and 0.53, Tier 1 and Tier 2, within-lab subject
  bootstrap (1,000 draws), 300 datasets each.
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import stats as S  # noqa: E402

TIER1 = ["Rome", "LODE", "DATA1", "Aamodt", "Set19"]
TIER2 = TIER1 + ["Tononi", "Zhang"]


def design(labs):
    d = pd.read_csv(os.path.join(REPO, "experiments", "dataset_audit", "dream_records.csv"))
    d = d.sort_values("Amendment").drop_duplicates(["Set ID", "Filename"], keep="last")
    meta = {(int(r["Set ID"]), r["Filename"]): r for r in d.to_dict("records")}
    y, s, lab = [], [], []
    for L in labs:
        for r in map(json.loads, open(os.path.join(HERE, "features", f"{L}.jsonl"))):
            if r.get("status") != "ok" or r.get("stage") != "N2":
                continue
            m = meta[(int(r["set"]), r["file"])]
            if m["Experience"] not in ("Experience", "No experience"):
                continue
            if pd.notna(m["Proportion artifacts"]) and float(m["Proportion artifacts"]) > 0.5:
                continue
            y.append(int(m["Experience"] == "Experience")); s.append(f"{L}|{m['Subject ID']}"); lab.append(L)
    y, s, lab = np.array(y), np.array(s, object), np.array(lab, object)
    kb = S.keep_both(y, s)
    return y[kb], s[kb], lab[kb]


def synth(y, s, auc, rng):
    subs, inv = np.unique(s, return_inverse=True)
    return rng.normal(size=len(subs))[inv] + np.sqrt(2) * norm.ppf(auc) * y + rng.normal(size=len(y))


def main():
    rng = np.random.default_rng(20261121)
    out = {}
    y1, s1, l1 = design(TIER1); y2, s2, l2 = design(TIER2)
    out["tier1_counts"] = {"n": int(len(y1)), "n_exp": int(y1.sum()), "n_subj": int(len(np.unique(s1)))}
    out["tier2_counts"] = {"n": int(len(y2)), "n_exp": int(y2.sum()), "n_subj": int(len(np.unique(s2)))}
    hits = 0
    for i in range(300):
        v = synth(y1, s1, 0.60, rng)
        r = S.family_a(v[:, None], ["m"], [1], y1, s1, l1, n_perm=2000, n_boot=0, seed=i)
        hits += r["m"]["p"] < 0.05 / 8
    out["power_auc060_holm8"] = hits / 300
    for name, (y, s, l) in (("tier1", (y1, s1, l1)), ("tier2", (y2, s2, l2))):
        for auc in (0.50, 0.53):
            b = 0; hw = []
            for i in range(300):
                v = synth(y, s, auc, rng)
                r = S.family_a(v[:, None], ["m"], [1], y, s, l, n_perm=0, n_boot=1000, seed=10_000 + i)
                b += r["m"]["bounded"]; hw.append((r["m"]["ci95"][1] - r["m"]["ci95"][0]) / 2)
            out[f"P_bounded_{name}_auc{auc}"] = b / 300
            out[f"halfwidth_{name}_auc{auc}"] = float(np.mean(hw))
    out["K2_pass"] = out["power_auc060_holm8"] >= 0.80
    json.dump(out, open(os.path.join(HERE, "p2.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
