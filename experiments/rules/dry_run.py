"""Dry run for task #1: the toolkit must catch deliberately leaked splits.

Synthetic data with NO real state effect: each subject has a label (e.g.
"sedated group" vs "awake group") and a private EEG-like fingerprint. A
classifier can only score above chance by recognising subjects. So:
  - an epoch-level split should inflate accuracy and must be flagged;
  - a subject re-uploaded under a new ID must be flagged by fingerprint;
  - a transfer split with one lab on both sides must be flagged;
  - an edited pre-registration must fail `require_sealed`;
  - the clean subject split must pass and score near chance.
Writes dry_run.json. Runs in a few seconds.
"""
import json
import os
import sys
import tempfile

import numpy as np
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from evidence import (LeakageError, Recording, SealError, auc, check_split,
                      fingerprint, require_sealed, seal, subject_folds)

rng = np.random.default_rng(1)
N_SUBJ, N_EP, D = 20, 30, 16
labs = ["labA"] * 10 + ["labB"] * 10
y_subj = np.array([0, 1] * 10)                    # label is per subject, no signal
subj_vec = rng.normal(0, 1.0, (N_SUBJ, D))        # subject identity signal
X, y, recs = [], [], []
for s in range(N_SUBJ):
    raw = rng.normal(size=(2, 2000)) + subj_vec[s, :2, None]
    fp = fingerprint(raw)
    for e in range(N_EP):
        X.append(subj_vec[s] + rng.normal(0, 0.5, D))
        y.append(y_subj[s])
        recs.append(Recording(f"s{s:02d}_e{e}", f"s{s:02d}", labs[s], "synth", fp))
X, y = np.array(X), np.array(y)


def cv_auc(folds):
    out = []
    for tr, te in folds:
        m = LogisticRegression(max_iter=2000).fit(X[tr], y[tr])
        out.append(auc(m.decision_function(X[te]), y[te]))
    return float(np.mean(out))


res = {}

# 1. leaked epoch-level split
perm = rng.permutation(len(recs))
ep_folds = [(np.setdiff1d(perm, perm[j::5]), perm[j::5]) for j in range(5)]
caught = []
for tr, te in ep_folds:
    try:
        check_split([recs[i] for i in tr], [recs[i] for i in te])
        caught.append(False)
    except LeakageError:
        caught.append(True)
res["epoch_split"] = {"auc": cv_auc(ep_folds), "folds_flagged": int(sum(caught)), "folds": 5}

# 2. clean subject split
sf = subject_folds(recs, k=5)
for tr, te in sf:
    check_split([recs[i] for i in tr], [recs[i] for i in te])   # must not raise
res["subject_split"] = {"auc": cv_auc(sf), "folds_flagged": 0, "folds": 5}

# 3. subject s00 re-uploaded as "s99" in test (same signal, new id)
dup = [Recording("s99_e0", "s99", "labA", "synth", recs[0].fingerprint)]
train = [r for r in recs if r.subject != "s99"]
try:
    check_split(train, dup)
    res["renamed_duplicate"] = "MISSED"
except LeakageError as e:
    res["renamed_duplicate"] = f"caught: {e}"
# and subject_folds keeps the duplicate with its twin
recs2 = recs + dup
together = all(((0 in te) == (len(recs) in te)) for _, te in subject_folds(recs2, k=5))
res["renamed_duplicate_kept_together_by_folds"] = bool(together)

# 4. transfer split with labA on both sides
tr = [r for r in recs if r.subject in {f"s{i:02d}" for i in range(15)}]
te = [r for r in recs if r not in tr]
try:
    check_split(tr, te, mode="transfer")
    res["transfer_same_lab"] = "MISSED"
except LeakageError as e:
    res["transfer_same_lab"] = f"caught: {e}"
lab_folds = subject_folds(recs, k=2, mode="transfer")
for a, b in lab_folds:
    check_split([recs[i] for i in a], [recs[i] for i in b], mode="transfer")
res["transfer_lab_folds_clean"] = True

# 5. sealing: edited pre-registration is caught (temp hashes file, not the real one)
with tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.abspath(__file__))) as d:
    pr, hf = os.path.join(d, "prereg.md"), os.path.join(d, "HASHES.txt")
    open(pr, "w").write("pass mark: AUC >= 0.7\n")
    seal([pr], hf)
    ok = require_sealed(pr, hf)
    open(pr, "w").write("pass mark: AUC >= 0.6\n")       # moved goalposts
    try:
        require_sealed(pr, hf)
        res["edited_prereg"] = "MISSED"
    except SealError as e:
        res["edited_prereg"] = f"caught: {e}"
    res["sealed_prereg_ok"] = bool(ok)

passed = (res["epoch_split"]["folds_flagged"] == 5
          and res["epoch_split"]["auc"] > 0.9
          and abs(res["subject_split"]["auc"] - 0.5) < 0.25
          and res["renamed_duplicate"].startswith("caught")
          and res["renamed_duplicate_kept_together_by_folds"]
          and res["transfer_same_lab"].startswith("caught")
          and res["edited_prereg"].startswith("caught"))
res["PASS"] = bool(passed)
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dry_run.json"), "w"), indent=1)
print(json.dumps(res, indent=1))
sys.exit(0 if passed else 1)
