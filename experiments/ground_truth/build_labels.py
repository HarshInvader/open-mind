"""Task #3: one row per recording (or awakening) in every qualifying dataset,
labelled by what its ground truth rests on. Writes labels.csv and counts.json.

Inputs (all metadata, no EEG): raw/*_keys.txt and raw/sleepedf_RECORDS.txt
(list_remote.py), raw/datainfo.mat (Chennu, fetched by range request),
../dataset_audit/dream_records.csv and dream_datasets_index.csv.
"""
import json
import os
import re

import numpy as np
import pandas as pd
import scipy.io as sio

HERE = os.path.dirname(os.path.abspath(__file__))
R = lambda *p: os.path.join(HERE, *p)
rows = []


def add(**k):
    base = dict(dataset="", family="", lab="", subject="", recording="", state="",
                behaviour="", report="none", truth="behaviour", l2_case=False,
                stage="", note="")
    base.update(k)
    rows.append(base)


# ---- ds005620 (Oslo, propofol). Behaviour per file; reports only as group counts.
for k in open(R("raw", "ds005620_keys.txt")).read().split():
    if not k.endswith(".vhdr"):
        continue
    f = os.path.basename(k)
    sub = re.search(r"sub-(\d+)", f).group(1)
    task = re.search(r"task-(\w+?)_", f).group(1)
    acq = re.search(r"acq-(\w+?)_", f).group(1)
    if task == "awake":
        state, beh = f"awake_{acq}", "responsive (RASS 0)"
    else:
        state = f"{task}_{acq}"
        beh = "unresponsive (target RASS -4)"
    add(dataset="ds005620", family="anaesthesia", lab="Oslo", subject=sub, recording=f, state=state,
        behaviour=beh, truth="behaviour",
        note="awakening reports exist (paper: 24 exp / 5 no-exp / 23 no-info of 52) but are not released per run"
        if task != "awake" else "")

# ---- Chennu 2016 (Cambridge, propofol). datainfo: name, level, plasma ng/ml, RT ms, hits/40.
m = sio.loadmat(R("raw", "datainfo.mat"), squeeze_me=True)["datainfo"]
lev_name = {1: "baseline", 2: "mild", 3: "moderate", 4: "recovery"}
for name, lev, conc, rt, hits in m:
    sub = str(name)[:2]
    hits = int(hits) if hits == hits else -1
    beh = "unknown" if hits < 0 else ("responsive" if hits >= 30 else ("impaired" if hits > 0 else "unresponsive"))
    add(dataset="chennu2016", family="anaesthesia", lab="Cambridge", subject=sub, recording=str(name),
        state=lev_name[int(lev)], behaviour=f"{beh} (hits {hits}/40, RT {rt} ms, propofol {conc} ng/ml)",
        truth="behaviour")

# ---- ds004541 (surgical general anaesthesia). Per file; loc/roc markers inside.
for k in open(R("raw", "ds004541_keys.txt")).read().split():
    if k.endswith("_eeg.edf"):
        f = os.path.basename(k)
        add(dataset="ds004541", family="anaesthesia", lab="Santiago (UC Chile)", subject=re.search(r"sub-(\d+)", f).group(1),
            recording=f, state="induction to recovery", behaviour="within-file: responsive before 'loc', unresponsive to 'roc' (clinical stimuli)",
            truth="behaviour", note="events: baseline, verbal/soft, verbal/strong, motor, tetanic, loc, roc")

# ---- Sleep-EDF Expanded (Leiden). Staging is the label; no reports.
for rec in open(R("raw", "sleepedf_RECORDS.txt")).read().split():
    f = os.path.basename(rec)
    add(dataset="sleep-edfx", family="sleep", lab="Leiden", subject=f[:5], recording=f,
        state="whole night (W, N1-N3/4, REM epochs)", behaviour="R&K sleep staging (not a report)", truth="behaviour",
        note="ST* = temazepam study" if f.startswith("ST") else "SC* = age study, 25-101 y")

# ---- DREAM (open sets only). Delayed report per awakening.
recs = pd.read_csv(os.path.join(HERE, "..", "dataset_audit", "dream_records.csv"))
idx = pd.read_csv(os.path.join(HERE, "..", "dataset_audit", "dream_datasets_index.csv")).drop_duplicates("Set ID", keep="last").set_index("Set ID")
rep_map = {"Experience": "experience", "No experience": "no_experience", "Without recall": "experience_without_recall",
           "No experience or without recall": "no_experience_or_no_recall", "Unknown": "unknown"}
lab_of = lambda name: "Rome (DeGennaro)" if "DeGennaro" in str(idx.loc[name, "Full name"]) or name in (7, 9, 10, 11, 12) else ("Oslo" if "Aamodt" in str(idx.loc[name, "Common name"]) else str(idx.loc[name, "Common name"]))
for _, r in recs.iterrows():
    sid = r["Set ID"]
    access = idx.loc[sid, "Accessibility"] if sid in idx.index else "unknown"
    rep = rep_map.get(r["Experience"], "unknown")
    stage = str(r["Last sleep stage"]).replace("N3/NREM3/NREM4", "N3")
    asleep = stage in ("N1", "N2", "N3", "REM")
    add(dataset=f"DREAM:{idx.loc[sid, 'Common name']}", family="sleep", lab=lab_of(sid), subject=f"{sid}_{r['Subject ID']}",
        recording=str(r["Filename"]), state="awakening", stage=stage,
        behaviour="asleep, unresponsive" if asleep else "awake/unclear stage",
        report=rep, truth="delayed_report",
        l2_case=bool(asleep and rep in ("experience", "no_experience") and access == "Open"),
        note=f"access {access}")

df = pd.DataFrame(rows)
df.to_csv(R("labels.csv"), index=False)

# ---- counts
c = {"recordings_total": int(len(df)),
     "by_dataset_truth": {f"{d}|{t}": int(n) for (d, t), n in df.groupby(["dataset", "truth"]).size().items()}}
d = df[df.truth == "delayed_report"]
l2 = df[df.l2_case]
c["delayed_report_rows"] = int(len(d))
c["l2_cases"] = int(len(l2))
c["l2_by_report"] = {k: int(v) for k, v in l2.report.value_counts().items()}
c["l2_by_stage_report"] = {f"{s}|{rp}": int(v) for (s, rp), v in l2.groupby(["stage", "report"]).size().items()}
c["l2_subjects"] = int(l2.subject.nunique())
c["l2_labs"] = sorted(l2.lab.unique().tolist())
c["l2_by_lab"] = {k: {"n": int(len(g)), "exp": int((g.report == "experience").sum()), "noexp": int((g.report == "no_experience").sum()),
                      "subjects": int(g.subject.nunique())} for k, g in l2.groupby("lab")}
# within-stage contrast usable: a subject with both experience and no-experience in the same stage
both = l2.groupby(["subject", "stage"]).report.agg(lambda s: set(s) >= {"experience", "no_experience"})
c["subject_stage_pairs_with_both_reports"] = int(both.sum())
c["subjects_with_both_in_some_stage"] = int(both[both].reset_index().subject.nunique())
c["anaesthesia_behaviour_dissociation_rows_with_report"] = 0
ch = df[df.dataset == "chennu2016"]
c["chennu_moderate_by_behaviour"] = {k: int(v) for k, v in ch[ch.state == "moderate"].behaviour.str.split(" ").str[0].value_counts().items()}
json.dump(c, open(R("counts.json"), "w"), indent=1)
print(json.dumps(c, indent=1))
