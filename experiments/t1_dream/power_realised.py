"""Post-seal, pre-analysis power at the REALISED sample (awakenings with saved ROI signals).

Uses labels only to count E/NE/WR per included subject; no EEG feature meets a label here.
Same synthetic worlds as planted.py (T1 at OR 2, null, recall at OR 2), 60 reps each.
Output: power_realised.json
"""
import json
import os
import sys
from multiprocessing import Pool

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import planted as P  # noqa: E402


def counts():
    m = pd.read_csv(os.path.join(HERE, "tononi_members.csv"))
    d = pd.read_csv(os.path.join(REPO, "experiments", "dataset_audit", "dream_records.csv"))
    d = d[(d["Set ID"] == 13) & (d.Amendment == 2)]
    j = m.merge(d, left_on="file", right_on="Filename")
    j = j[[os.path.exists(os.path.join(HERE, "roi", f.replace(".edf", ".npz"))) for f in j.file]]
    lab = j.Experience.map({"Experience": "E", "No experience": "NE", "Without recall": "WR"})
    c = pd.crosstab(j["Subject ID"], lab).reset_index().rename(columns={"Subject ID": "subject"})
    for k in ["E", "NE", "WR"]:
        if k not in c:
            c[k] = 0
    return c


def main():
    c = counts()
    path = os.path.join(HERE, "subject_counts_realised.csv")
    c.to_csv(path, index=False)
    P.COUNTS = path
    jobs = [(w, b, False, k) for w, b in [("T1", float(np.log(2))), ("null", 0.0), ("recall", float(np.log(2)))]
            for k in range(60)]
    with Pool(2, initializer=_init, initargs=(path,)) as pool:
        R = pd.DataFrame(pool.map(P.one_rep, jobs))
    out = dict(n=dict(E=int(c.E.sum()), NE=int(c.NE.sum()), WR=int(c.WR.sum()), subjects=len(c)))
    for (w, b), g in R.groupby(["world", "b"]):
        v = g.verdict
        out[f"{w}_OR{np.exp(b):.1f}"] = dict(reps=len(g), pass_rate=float(v.str.contains("PASS").mean()),
                                            refuted_rate=float(v.str.startswith("REFUTED").mean()))
    json.dump(out, open(os.path.join(HERE, "power_realised.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


def _init(path):
    P.COUNTS = path


if __name__ == "__main__":
    main()
