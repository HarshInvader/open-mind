"""Confirmatory analysis (PREREG.md). Joins labels to the label-blind ROI signals, runs the four tests.

Refuses to run unless PREREG.md and the code files are sealed with their current hashes.
Run: board/run.sh .venv/bin/python -I experiments/t1_dream/analysis.py
Output: results.json, features.csv, ledger_rows.csv
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "experiments", "rules"))
import t1lib as T  # noqa: E402
from evidence import require_sealed  # noqa: E402
from planted import table_from_rows  # noqa: E402

SEALED = ["PREREG.md", "t1lib.py", "planted.py", "features.py", "analysis.py", "tailzip.py"]
DELTA = float(np.log(2.0))


def clock_hours(s):
    h, m, _ = (int(v) for v in str(s).split(":"))
    return (h + 24 if h < 18 else h) - 18 + m / 60


def main():
    for f in SEALED:
        require_sealed(os.path.join(HERE, f))
    m = pd.read_csv(os.path.join(HERE, "tononi_members.csv"))
    d = pd.read_csv(os.path.join(REPO, "experiments", "dataset_audit", "dream_records.csv"))
    d = d[(d["Set ID"] == 13) & (d.Amendment == 2)]
    meta = m.merge(d, left_on="file", right_on="Filename", how="inner")
    meta["label"] = meta.Experience.map({"Experience": "E", "No experience": "NE", "Without recall": "WR"})
    log = {}
    for ln in open(os.path.join(HERE, "fetch_log.jsonl")):
        r = json.loads(ln)
        log[r["file"]] = r
    rows, excluded = [], []
    for _, r in meta.iterrows():
        p = os.path.join(HERE, "roi", r.file.replace(".edf", ".npz"))
        if not os.path.exists(p):
            excluded.append(dict(file=r.file, label=r.label, why=log.get(r.file, {}).get("status", "not fetched")))
            continue
        z = np.load(p)
        rows.append(dict(xp=z["post"].astype(float), xf=z["front"].astype(float), subject=int(r["Subject ID"]),
                         label=r.label, clock_h=clock_hours(r["Time of awakening"]),
                         awak_idx=int(r.file.split("_ep")[1].split(".")[0]), file=r.file))
    rng = np.random.default_rng(0)
    df = table_from_rows(rows, rng, 1000)
    df["file"] = [q["file"] for q in rows]
    out = dict(prereg="experiments/t1_dream/PREREG.md", delta=DELTA)
    out["primary"] = T.run_tests(df, np.random.default_rng(1), DELTA)
    out["excluded"] = pd.DataFrame(excluded).groupby(["label", "why"]).size().reset_index().values.tolist() if excluded else []
    # pre-stated secondary analyses (not part of the verdict)
    sens = df[df.awak_idx > 1].reset_index(drop=True)
    out["secondary_excluding_first_awakening"] = T.run_tests(sens, np.random.default_rng(2), DELTA, 1000, 1000, 500)
    desc = {}
    for lab, g in df.groupby("label"):
        desc[lab] = {c: [round(float(g[c].mean()), 3), round(float(g[c].std()), 3)]
                     for c in ["logL_post", "logL_front", "n_off_post", "count10", "delta5", "delta10", "sigma", "beta5"]}
        desc[lab]["frac_no_off_post"] = round(float((g.n_off_post == 0).mean()), 3)
    out["descriptive_mean_sd"] = desc
    # single-predictor within-subject AUCs, descriptive
    from sklearn.metrics import roc_auc_score
    en = df[df.label.isin(["E", "NE"])]
    Z = T.centre_z(en[T.MODEL_A + ["logL_post", "logL_front"]].to_numpy(), en.subject.to_numpy())
    ye = (en.label == "E").to_numpy()
    out["auc_E_vs_NE_within_subject_centred"] = {c: round(float(roc_auc_score(ye, Z[:, i])), 3)
                                                for i, c in enumerate(T.MODEL_A + ["logL_post", "logL_front"])}
    # deviation: output-only fix (errors="ignore") after a crash here, before any result was printed
    df.drop(columns=["xp", "xf", "surr_logL_post"], errors="ignore").to_csv(os.path.join(HERE, "features.csv"), index=False)
    json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in ["primary", "excluded"]}, indent=1, default=float))


if __name__ == "__main__":
    main()
