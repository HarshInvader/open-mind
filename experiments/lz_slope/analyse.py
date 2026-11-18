"""Task #4: does LZ add AUC over the spectral exponent? Prereg: docs/prereg/2026-11-18_lz_vs_slope_sleepedf.md

  board/run.sh .venv/bin/python -I experiments/lz_slope/analyse.py planted1   # P1 state recovery (needs raw/)
  board/run.sh .venv/bin/python -I experiments/lz_slope/analyse.py planted2   # P2 calibration + power
  board/run.sh .venv/bin/python -I experiments/lz_slope/analyse.py main       # H1-H4, descriptives
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "experiments", "rules"))
sys.path.insert(0, HERE)
from evidence import Recording, auc, check_split, require_sealed, subject_folds  # noqa: E402
from features import BANDS, FS, preprocess, spectral_exponent  # noqa: E402

PREREG = os.path.join(REPO, "docs", "prereg", "2026-11-18_lz_vs_slope_sleepedf.md")
BP = ["bp_" + b for b in BANDS]
CONTRASTS = {"C1_W_vs_N3": ("W", "N3"), "C2_R_vs_N3": ("R", "N3"), "C3_W_vs_R": ("W", "R")}


def load():
    rows = [json.loads(l) for l in open(os.path.join(HERE, "features.jsonl"))]
    df = pd.DataFrame(rows)
    df = df[(df.kind == "real") & df.clean].reset_index(drop=True)
    cnt = df.groupby(["subject", "stage"]).size().unstack(fill_value=0)
    keep = cnt[(cnt[["W", "N3", "R"]] >= 10).all(1)].index
    return df[df.subject.isin(keep)].reset_index(drop=True)


class CV:
    """Fixed subject folds for one contrast; fast repeated fits."""

    def __init__(self, df, pos, neg):
        self.d = df[df.stage.isin([pos, neg])].reset_index(drop=True)
        self.y = (self.d.stage == pos).astype(int).values
        self.subs = sorted(self.d.subject.unique())
        recs = [Recording(s, s, "sleep-edf", "sleep-edf") for s in self.subs]
        self.folds = []
        for tr, te in subject_folds(recs, k=5, seed=0):
            check_split([recs[i] for i in tr], [recs[i] for i in te])
            st = {self.subs[i] for i in te}
            m = self.d.subject.isin(st).values
            self.folds.append((np.flatnonzero(~m), np.flatnonzero(m)))
        self.g = self.d.subject.values

    def oof(self, X):
        X = np.asarray(X, float).reshape(len(self.y), -1)
        p = np.empty(len(self.y))
        for tr, te in self.folds:
            mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-12
            clf = LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000)
            clf.fit((X[tr] - mu) / sd, self.y[tr])
            p[te] = clf.decision_function((X[te] - mu) / sd)
        return p

    def auc(self, X):
        return auc(self.oof(X), self.y)


def fl_residuals(cv, base, add):
    """Within-subject regression of `add` on `base` (+intercept): fitted, residual."""
    fitted, resid = np.empty(len(add)), np.empty(len(add))
    for s in cv.subs:
        ii = np.flatnonzero(cv.g == s)
        B = np.column_stack([np.ones(len(ii)), base[ii]])
        beta, *_ = np.linalg.lstsq(B, add[ii], rcond=None)
        fitted[ii] = B @ beta
        resid[ii] = add[ii] - fitted[ii]
    return fitted, resid


def delta_test(cv, base, add, n_perm, rng):
    base = np.asarray(base, float).reshape(len(cv.y), -1)
    a0 = cv.auc(base)
    a1 = cv.auc(np.column_stack([base, add]))
    obs = a1 - a0
    fitted, resid = fl_residuals(cv, base, np.asarray(add, float))
    idx = [np.flatnonzero(cv.g == s) for s in cv.subs]
    null = np.empty(n_perm)
    for b in range(n_perm):
        r = resid.copy()
        for ii in idx:
            r[ii] = resid[rng.permutation(ii)]
        null[b] = cv.auc(np.column_stack([base, fitted + r])) - a0
    p = (1 + np.sum(null >= obs)) / (n_perm + 1)
    return {"auc_base": a0, "auc_full": a1, "delta": obs, "p": float(p),
            "null_95": float(np.percentile(null, 95)), "null_mean": float(null.mean())}


def boot_delta(cv, base, add, n_boot, rng):
    base = np.asarray(base, float).reshape(len(cv.y), -1)
    p0, p1 = cv.oof(base), cv.oof(np.column_stack([base, add]))
    idx = {s: np.flatnonzero(cv.g == s) for s in cv.subs}
    d, a = [], []
    for _ in range(n_boot):
        ii = np.concatenate([idx[s] for s in rng.choice(cv.subs, len(cv.subs))])
        a.append(auc(p1[ii], cv.y[ii])); d.append(a[-1] - auc(p0[ii], cv.y[ii]))
    return [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]


def holm(ps):
    ps = np.asarray(ps); o = np.argsort(ps); m = len(ps)
    adj = np.empty(m); run = 0
    for r, i in enumerate(o):
        run = max(run, (m - r) * ps[i]); adj[i] = min(1, run)
    return adj


def planted1():
    """P1: plant slow waves into real W epochs; exponent must recover them."""
    import glob
    df = load()
    keep = set(df.subject)
    rng = np.random.default_rng(11)
    sos = butter(2, [0.5, 2], btype="band", fs=FS, output="sos")
    rows = []
    for fn in sorted(glob.glob(os.path.join(HERE, "raw", "*.npz"))):
        d = np.load(fn)
        subj = str(d["subject"])
        if subj not in keep:
            continue
        w = set(df[(df.subject == subj) & (df.stage == "W")].epoch)
        for i in np.flatnonzero(d["stage"] == "W"):
            if int(d["epoch"][i]) not in w:
                continue
            x = preprocess(d["eeg"][i])
            sw = sosfiltfilt(sos, rng.normal(size=x.shape[-1]))
            sw = sw / sw.std()
            r = {"subject": subj}
            r["orig"] = spectral_exponent(x)
            for k in (0, 0.5, 1, 2):
                r[f"k{k}"] = spectral_exponent(x + k * x.std(-1, keepdims=True) * sw[None, :])
            rows.append(r)
    p = pd.DataFrame(rows)
    out = {}
    for k in (0, 0.5, 1, 2):
        dd = pd.concat([pd.DataFrame({"subject": p.subject, "stage": "P", "f": p[f"k{k}"]}),
                        pd.DataFrame({"subject": p.subject, "stage": "O", "f": p["orig"]})], ignore_index=True)
        cv = CV(dd, "O", "P")
        out[f"k{k}"] = cv.auc(dd[["f"]].values)
    vals = [out[f"k{k}"] for k in (0, 0.5, 1, 2)]
    out["PASS"] = bool(abs(vals[0] - 0.5) < 0.05 and vals[-1] > 0.8 and all(np.diff(vals) > 0))
    out["n_epochs"] = len(p)
    json.dump(out, open(os.path.join(HERE, "planted1.json"), "w"), indent=1)
    print(out)


def planted2():
    df = load()
    cv = CV(df, "W", "N3")
    base = cv.d[["slope"]].values
    rng = np.random.default_rng(22)
    out = {}
    for dd in (0, 0.1, 0.2, 0.3, 0.5):
        res = []
        for rep in range(20):
            z = dd * (cv.y - 0.5) * 2 + rng.normal(size=len(cv.y))
            res.append(delta_test(cv, base, z, 200, rng))
        out[str(dd)] = {"power": float(np.mean([r["p"] < 0.05 for r in res])),
                        "mean_delta": float(np.mean([r["delta"] for r in res]))}
        print(dd, out[str(dd)], flush=True)
    out["fpr_ok"] = out["0"]["power"] <= 0.15
    det = [float(k) for k in ("0.1", "0.2", "0.3", "0.5") if out[k]["power"] >= 0.8]
    out["detectable_delta_auc"] = out[str(min(det))]["mean_delta"] if det else None
    out["PASS"] = bool(out["fpr_ok"])
    json.dump(out, open(os.path.join(HERE, "planted2.json"), "w"), indent=1)


def main():
    print("prereg sealed at", require_sealed(PREREG))
    # Amendment 2: P1 (slow-wave plant) failed and stays on record; P1b (spectral tilt) replaces it.
    for f in ("planted1b.json", "planted2.json"):
        assert json.load(open(os.path.join(HERE, f)))["PASS"], f"{f} failed; real results do not count"
    df = load()
    rng = np.random.default_rng(0)
    res = {"n_subjects": int(df.subject.nunique()),
           "n_epochs": df.stage.value_counts().to_dict(), "tests": {}, "single": {}}
    tests = []
    for cname in ("C1_W_vs_N3", "C2_R_vs_N3"):
        cv = CV(df, *CONTRASTS[cname])
        for h, base_cols, add in (("H1", ["slope"], "lz"), ("H2", ["slope"], "pnlz"),
                                  ("H3", ["slope"] + BP, "lz"), ("H4", ["slope"] + BP, "pnlz")):
            r = delta_test(cv, cv.d[base_cols].values, cv.d[add].values, 1000, rng)
            r["ci_delta"] = boot_delta(cv, cv.d[base_cols].values, cv.d[add].values, 1000, rng)
            r["hyp"], r["contrast"] = h, cname
            tests.append(r)
            print(h, cname, {k: r[k] for k in ("auc_base", "auc_full", "delta", "p")}, flush=True)
    adj = holm([t["p"] for t in tests])
    for t, a in zip(tests, adj):
        t["p_holm"] = float(a)
        t["verdict"] = "adds" if (a < 0.05 and t["delta"] >= 0.01) else "does not add"
        res["tests"][f"{t['hyp']}_{t['contrast']}"] = t
    for cname, (pos, neg) in CONTRASTS.items():
        cv = CV(df, pos, neg)
        res["single"][cname] = {}
        for m in ["lz", "pnlz", "slope", "perm_entropy"] + BP + [["emg", "eog"], ["slope"] + BP]:
            key = m if isinstance(m, str) else "+".join(m) if len(m) < 3 else "spectral_baseline"
            if key == "emg+eog":
                key = "arousal_emg_eog"
            cols = [m] if isinstance(m, str) else m
            a_cv = cv.auc(cv.d[cols].values)
            raw = auc(cv.d[cols[0]].values, cv.y) if len(cols) == 1 else None
            res["single"][cname][key] = {"cv_auc": a_cv, "raw_auc": raw}
    rho = {}
    for m in ("lz", "pnlz", "perm_entropy"):
        rs = [spearmanr(g[m], g["slope"])[0] for _, g in df.groupby("subject")]
        rho[m] = {"median_within_subject_rho_vs_slope": float(np.median(rs)),
                  "pooled_rho": float(spearmanr(df[m], df["slope"])[0])}
    res["rho"] = rho
    json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    print(json.dumps(res["single"], indent=1)); print(rho)


if __name__ == "__main__":
    {"planted1": planted1, "planted2": planted2, "main": main}[sys.argv[1]]()
