"""NE test analysis. Prereg: docs/prereg/2026-11-18_nonequilibrium_vs_spectrum.md

  board/run.sh .venv/bin/python -I experiments/nonequilibrium/ne_analyse.py power   # P2 (no real outcomes used)
  board/run.sh .venv/bin/python -I experiments/nonequilibrium/ne_analyse.py main    # sealed tests

Reuses the CV, Freedman-Lane permutation, bootstrap and Holm code of task #4 (experiments/lz_slope/analyse.py).
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "experiments", "rules"))
sys.path.insert(0, os.path.join(REPO, "experiments", "lz_slope"))
import analyse as A  # noqa: E402  (experiments/lz_slope/analyse.py)
from evidence import auc, require_sealed  # noqa: E402

PREREG = os.path.join(REPO, "docs", "prereg", "2026-11-18_nonequilibrium_vs_spectrum.md")
BP = ["bp_delta", "bp_theta", "bp_alpha", "bp_sigma", "bp_beta", "bp_lowgamma"]
SPEC = ["slope"] + BP
# (contrast, dataset, conscious-side class, other class)
CONTRASTS = [("SE_W_vs_N3", "sleepedf", "W", "N3"), ("SE_REM_vs_N3", "sleepedf", "R", "N3"),
             ("CH_L1_vs_L3", "chennu", "L1", "L3"), ("DS_awake_vs_sed2", "ds005620", "awake", "sed2")]
PRIMARY = ["tra_x", "ne2"]
SECONDARY = ["ptir_x", "tra_xi", "tra", "lz"]


def load(kind="real"):
    df = pd.DataFrame([json.loads(l) for l in open(os.path.join(HERE, "features.jsonl"))])
    df = df[(df.kind == kind) & (df.clean)].copy()
    df["stage"] = df["cls"]
    return df


def contrast_df(df, ds, pos, neg, min_ep):
    d = df[(df.dataset == ds) & df.cls.isin([pos, neg])]
    cnt = d.groupby(["subject", "cls"]).size().unstack(fill_value=0)
    keep = cnt[(cnt.reindex(columns=[pos, neg], fill_value=0) >= min_ep).all(1)].index
    return d[d.subject.isin(keep)].reset_index(drop=True)


MIN_EP = {"sleepedf": 10, "chennu": 4, "ds005620": 2}


def gate(cv, dsurr, col, pos):
    """Fit single-measure classifier on real data (all subjects), apply to surrogates of both classes."""
    from sklearn.linear_model import LogisticRegression
    X = cv.d[[col]].values; mu, sd = X.mean(0), X.std(0) + 1e-12
    clf = LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000).fit((X - mu) / sd, cv.y)
    s = dsurr[dsurr.subject.isin(cv.subs)]
    s = s[s[col].notna()] if col in s else s.iloc[:0]   # amendment 2: tra_xi exists only on real rows
    if len(s) == 0:
        return {"auc_surr": float("nan"), "share_kept": float("nan"), "PASS": False,
                "note": "not computed: measure absent on surrogate rows"}
    ys = (s.cls == pos).astype(int).values
    sc = clf.decision_function((s[[col]].values - mu) / sd)
    a_real = auc(clf.decision_function((X - mu) / sd), cv.y)
    a_surr = auc(sc, ys) if len(set(ys)) == 2 else float("nan")
    share = (a_surr - 0.5) / (a_real - 0.5) if abs(a_real - 0.5) > 0.02 else float("nan")
    return {"auc_real_fit": a_real, "auc_surr": a_surr, "share_kept": share,
            "surr_pos_called_pos": float(np.mean(sc[ys == 1] > 0)), "real_neg_called_pos": float(np.mean(
                clf.decision_function((X[cv.y == 0] - mu) / sd) > 0)),
            "PASS": bool(not np.isnan(share) and share <= 0.5)}


def power():
    """P2: plant a synthetic feature with effect d into each contrast; uses labels and the spectral
    baseline only, never the NE measures."""
    df = load()
    rng = np.random.default_rng(22)
    out = {}
    for cname, ds, pos, neg in CONTRASTS:
        d = contrast_df(df, ds, pos, neg, MIN_EP[ds])
        if d.subject.nunique() < 5:
            continue
        cv = A.CV(d, pos, neg)
        base = cv.d[SPEC].values
        out[cname] = {}
        for dd in (0, 0.2, 0.4):
            res = [A.delta_test(cv, base, dd * (cv.y - 0.5) * 2 + rng.normal(size=len(cv.y)), 200, rng)
                   for _ in range(10)]
            out[cname][str(dd)] = {"power": float(np.mean([r["p"] < 0.05 for r in res])),
                                   "mean_delta": float(np.mean([r["delta"] for r in res]))}
            print(cname, dd, out[cname][str(dd)], flush=True)
        out[cname]["fpr_ok"] = out[cname]["0"]["power"] <= 0.2
    out["PASS"] = bool(all(v["fpr_ok"] for k, v in out.items() if isinstance(v, dict)))
    json.dump(out, open(os.path.join(HERE, "planted2.json"), "w"), indent=1)


def main():
    print("prereg sealed at", require_sealed(PREREG))
    for f in ("planted.json", "planted2.json"):
        js = json.load(open(os.path.join(HERE, f)))
        assert js.get("ALL_PASS", js.get("PASS")), f"{f} failed; real results do not count"
    df, dsurr = load("real"), load("surr")
    rng = np.random.default_rng(0)
    res = {"contrasts": {}}
    tests = []
    for cname, ds, pos, neg in CONTRASTS:
        d = contrast_df(df, ds, pos, neg, MIN_EP[ds])
        if d.subject.nunique() < 5:
            res["contrasts"][cname] = {"skipped": "fewer than 5 subjects"}; continue
        cv = A.CV(d, pos, neg)
        r = {"n_subjects": len(cv.subs), "n_epochs": cv.d.cls.value_counts().to_dict(), "single": {},
             "mean_pos": {}, "mean_neg": {}, "delta": {}, "gate": {}}
        for m in PRIMARY + SECONDARY + ["slope", "perm_entropy"]:
            if cv.d[m].isna().any():
                continue
            r["single"][m] = {"cv_auc": cv.auc(cv.d[[m]].values), "raw_auc": auc(cv.d[m].values, cv.y)}
            r["mean_pos"][m] = float(cv.d[m][cv.y == 1].mean()); r["mean_neg"][m] = float(cv.d[m][cv.y == 0].mean())
        r["single"]["spectral_baseline"] = {"cv_auc": cv.auc(cv.d[SPEC].values)}
        for m in PRIMARY + SECONDARY:
            if cv.d[m].isna().any():
                continue
            t = A.delta_test(cv, cv.d[SPEC].values, cv.d[m].values, 1000, rng)
            t["ci_delta"] = A.boot_delta(cv, cv.d[SPEC].values, cv.d[m].values, 1000, rng)
            t["measure"], t["contrast"] = m, cname
            r["delta"][m] = t
            if m in PRIMARY:
                tests.append(t)
            r["gate"][m] = gate(cv, dsurr, m, pos)
            print(cname, m, {k: round(t[k], 4) for k in ("auc_base", "auc_full", "delta", "p")},
                  "gate share", round(r["gate"][m]["share_kept"], 3), flush=True)
        if ds == "sleepedf" and not cv.d[["emg", "eog"]].isna().any().any():
            t = A.delta_test(cv, cv.d[SPEC + ["emg", "eog"]].values, cv.d["tra_x"].values, 1000, rng)
            r["delta"]["tra_x_over_spec_arousal"] = t
        res["contrasts"][cname] = r
    from analyse import holm  # noqa: E402
    adj = holm([t["p"] for t in tests])
    verdict = {}
    for t, a in zip(tests, adj):
        t["p_holm"] = float(a)
        c = res["contrasts"][t["contrast"]]
        direction = c["mean_pos"][t["measure"]] > c["mean_neg"][t["measure"]]
        adds = bool(a < 0.05 and t["delta"] >= 0.01)
        g = c["gate"][t["measure"]]["PASS"]
        verdict.setdefault(t["measure"], {})[t["contrast"]] = {
            "adds": adds, "direction_conscious_higher": bool(direction), "gate_pass": g,
            "single_cv_auc": c["single"][t["measure"]]["cv_auc"],
            "all_three": bool(adds and direction and g)}
    res["verdict_cells"] = verdict
    ho = verdict.get("tra_x", {})
    n_ok = sum(v["all_three"] for v in ho.values())
    sleep_ok = any(v["all_three"] for k, v in ho.items() if k.startswith("SE_"))
    prop_ok = any(v["all_three"] for k, v in ho.items() if not k.startswith("SE_"))
    res["H_NE_HO"] = ("SUPPORTED" if (n_ok >= 3 and sleep_ok and prop_ok) else
                      "NOT SUPPORTED" if n_ok == 0 else "PARTIAL")
    n2 = verdict.get("ne2", {})
    res["H_NE_2_replicates"] = {k: bool(v["single_cv_auc"] >= 0.70 and v["direction_conscious_higher"])
                                for k, v in n2.items()}
    res["H_NE_2_adds_beyond_spectrum"] = {k: v["adds"] for k, v in n2.items()}
    json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)
    print(json.dumps({k: res[k] for k in ("H_NE_HO", "H_NE_2_replicates", "H_NE_2_adds_beyond_spectrum")}, indent=1))


if __name__ == "__main__":
    {"power": power, "main": main}[sys.argv[1]]()
