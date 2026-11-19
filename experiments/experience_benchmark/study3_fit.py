"""Study 3 fit (prereg §10; amendment 1, C4). Discovery labs only: Tononi (set 13) and Zhang & Wamsley (set 1).

  .venv/bin/python -I experiments/experience_benchmark/study3_fit.py   -> study3_model.json

Sealed before it runs. It prints ONLY the outer-fold AUC of the nested cross-validation and the sha256 of the
model file. It computes no univariate statistic. The model file is not opened by the analyst before the Tier 1
unblinding; it is sealed (HASHES.txt) and pushed as is.

Fixed choices:
- Rows: features/Tononi.jsonl and features/Zhang.jsonl with status "ok", stage N2. Labels joined from
  dream_records.csv on (Set ID, Filename) after the same Amendment de-duplication as extract.py.
  Classes: "Experience" = 1, "No experience" = 0; all other label values are left out.
  Rows with DREAM `Proportion artifacts` > 0.5 are dropped (prereg §3.4). Subject key: (lab, Subject ID).
  Only subjects with both classes are kept.
- Features (9; prereg §10, all channels, as extracted): surrogate excess m - m__ft for
  m in lz, pe, hfd, wsmi, sampen, mse, k01, dfa, tra. Total correlation is left out (§10); CSER is not in
  the §10 list. No ROI versions exist in the extraction, so the "at most 18" of §10 is 9 here.
- Scaling: each feature is z-scored WITHIN SUBJECT (subject mean and SD, ddof 0; SD 0 -> all 0), as §10
  says. This needs no stored scaler and is applied identically to any lab. Missing values -> 0 after scaling.
- Model: L2 logistic regression (sklearn, lbfgs, max_iter 5000, intercept), C in {0.01, 0.1, 1}.
- Nested CV: outer 5 folds and inner 5 folds, both subject-grouped; subjects are assigned to folds by a
  seeded permutation (seed 4242 outer, 4243 + outer fold for inner). The inner choice of C maximises the
  pooled held-out within-subject pair AUC (ties -> smaller C). The kill statistic is the pooled outer
  held-out within-subject pair AUC.
- Final model: refit on all discovery rows with the C chosen most often in the outer folds (ties -> smaller C).
- Saved: feature list, scaling rule, C, coefficients, intercept, outer AUC, the kill decision (outer AUC < 0.58),
  counts. The score of an awakening is intercept + coef . z (higher = experience predicted).
"""
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import stats as S  # noqa: E402

FEATS = ["lz", "pe", "hfd", "wsmi", "sampen", "mse", "k01", "dfa", "tra"]
CS = [0.01, 0.1, 1.0]
LAB_OF_SET = {13: "Tononi", 1: "Zhang"}


def within_subject_z(F, s):
    Z = np.zeros_like(F)
    for sb in np.unique(s):
        i = s == sb
        mu = np.nanmean(F[i], 0); sd = np.nanstd(F[i], 0)
        sd = np.where(sd > 0, sd, np.inf)
        Z[i] = (F[i] - mu) / sd
    return np.nan_to_num(Z, nan=0.0)


def load():
    rows = []
    for lab in ("Tononi", "Zhang"):
        for r in map(json.loads, open(os.path.join(HERE, "features", f"{lab}.jsonl"))):
            if r.get("status") == "ok" and r.get("stage") == "N2":
                rows.append(r)
    d = pd.read_csv(os.path.join(REPO, "experiments", "dataset_audit", "dream_records.csv"))
    d = d.sort_values("Amendment").drop_duplicates(["Set ID", "Filename"], keep="last")
    lab = {(int(a), b): (c, e, p) for a, b, c, e, p in
           zip(d["Set ID"], d["Filename"], d["Subject ID"], d["Experience"], d["Proportion artifacts"])}
    X, y, s = [], [], []
    for r in rows:
        subj, exp, part = lab[(int(r["set"]), r["file"])]
        if exp not in ("Experience", "No experience") or (pd.notna(part) and float(part) > 0.5):
            continue
        X.append([r.get(m, np.nan) - r.get(m + "__ft", np.nan) for m in FEATS])
        y.append(int(exp == "Experience")); s.append(f"{LAB_OF_SET[int(r['set'])]}|{subj}")
    X, y, s = np.array(X, float), np.array(y), np.array(s)
    kb = S.keep_both(y, s)
    return X[kb], y[kb], s[kb]


def folds(subjects, k, seed):
    p = np.random.default_rng(seed).permutation(subjects)
    return [set(p[i::k]) for i in range(k)]


def fit(Z, y, C):
    return LogisticRegression(C=C, solver="lbfgs", max_iter=5000).fit(Z, y)   # L2 is the default penalty


def cv_pred(Z, y, s, C_choice, k, seed):
    """Pooled held-out decision values over k subject-grouped folds. C_choice(Ztr, ytr, str, fold) -> C."""
    pred = np.full(len(y), np.nan); chosen = []
    for f, te_subs in enumerate(folds(np.unique(s), k, seed)):
        te = np.isin(s, list(te_subs)); tr = ~te
        C = C_choice(Z[tr], y[tr], s[tr], f); chosen.append(C)
        pred[te] = fit(Z[tr], y[tr], C).decision_function(Z[te])
    return pred, chosen


def main():
    X, y, s = load()
    Z = within_subject_z(X, s)

    def inner_choice(Ztr, ytr, str_, f):
        best, bestC = -1, None
        for C in CS:
            p, _ = cv_pred(Ztr, ytr, str_, lambda *a, C=C: C, 5, 4243 + f)
            a = S.PairAUC(ytr, str_).auc(p)
            if a > best + 1e-12:
                best, bestC = a, C
        return bestC
    outer_pred, chosen = cv_pred(Z, y, s, inner_choice, 5, 4242)
    outer_auc = S.PairAUC(y, s).auc(outer_pred)
    C_final = min(CS, key=lambda C: (-chosen.count(C), C))
    m = fit(Z, y, C_final)
    model = {"features": [f"{f} - {f}__ft" for f in FEATS], "feature_keys": FEATS,
             "scaling": "within-subject z-score (subject mean, SD ddof 0; SD 0 -> 0); NaN -> 0",
             "C": C_final, "C_outer_choices": chosen, "intercept": float(m.intercept_[0]),
             "coef": [float(c) for c in m.coef_[0]], "outer_auc": float(outer_auc),
             "killed": bool(outer_auc < 0.58), "n_rows": int(len(y)), "n_subjects": int(len(np.unique(s))),
             "score": "intercept + coef . z; higher = experience predicted"}
    path = os.path.join(HERE, "study3_model.json")
    with open(path, "w") as f:
        json.dump(model, f, indent=1)
    print("outer AUC", round(outer_auc, 4))
    print("sha256", hashlib.sha256(open(path, "rb").read()).hexdigest())


if __name__ == "__main__":
    main()
