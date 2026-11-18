"""Surrogate gate (task #8). Prereg: docs/prereg/2026-11-18_surrogate_gate_sleepedf.md

  .venv/bin/python -I experiments/surrogate_gate/gate.py planted   # synthetic check, must pass first
  .venv/bin/python -I experiments/surrogate_gate/gate.py real      # Sleep-EDF features from experiments/lz_slope
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.signal import sawtooth, sosfiltfilt, butter
from sklearn.linear_model import LogisticRegression

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "experiments", "rules"))
sys.path.insert(0, os.path.join(REPO, "experiments", "lz_slope"))
from evidence import (Recording, auc, check_split, require_sealed,  # noqa: E402
                      subject_folds)
from features import (FS, phase_surrogate, preprocess, psd,  # noqa: E402
                      spectral_exponent, time_asymmetry)

PREREG = os.path.join(REPO, "docs", "prereg", "2026-11-18_surrogate_gate_sleepedf.md")


def gate(df, measures, pos="W", neg="N3", n_boot=1000, seed=0):
    """df: rows with subject, stage, kind in {real, surr}, and measure columns."""
    df = df[df.stage.isin([pos, neg])].reset_index(drop=True)
    subs = sorted(df.subject.unique())
    recs = [Recording(s, s, "sleep-edf", "sleep-edf") for s in subs]
    folds = subject_folds(recs, k=5, seed=0)
    out = {}
    for m in measures:
        pred = np.full(len(df), np.nan)       # P(conscious)
        for tr, te in folds:
            check_split([recs[i] for i in tr], [recs[i] for i in te])
            s_tr, s_te = {subs[i] for i in tr}, {subs[i] for i in te}
            fit = df[(df.kind == "real") & df.subject.isin(s_tr)]
            clf = LogisticRegression(class_weight="balanced").fit(
                fit[[m]].values, (fit.stage == pos).astype(int).values)
            ii = np.flatnonzero(df.subject.isin(s_te).values)
            pred[ii] = clf.predict_proba(df.loc[ii, [m]].values)[:, 1]
        df["_c"] = (pred > 0.5).astype(float)
        cells = {"surr_W": (df.kind == "surr") & (df.stage == pos),
                 "real_W": (df.kind == "real") & (df.stage == pos),
                 "real_N3": (df.kind == "real") & (df.stage == neg),
                 "surr_N3": (df.kind == "surr") & (df.stage == neg)}
        rates = {k: float(df.loc[v, "_c"].mean()) for k, v in cells.items()}
        real = df[df.kind == "real"]
        surr = df[df.kind == "surr"]
        a_real = auc(real[m].values, (real.stage == pos).astype(int).values)
        a_surr = auc(surr[m].values, (surr.stage == pos).astype(int).values)
        # subject-cluster bootstrap
        rng = np.random.default_rng(seed)
        by = {s: g.index.values for s, g in df.groupby("subject")}
        bs = {"surr_W": [], "real_W": [], "auc_real": [], "auc_surr": []}
        for _ in range(n_boot):
            idx = np.concatenate([by[s] for s in rng.choice(subs, len(subs))])
            b = df.loc[idx]
            bs["surr_W"].append(b.loc[(b.kind == "surr") & (b.stage == pos), "_c"].mean())
            bs["real_W"].append(b.loc[(b.kind == "real") & (b.stage == pos), "_c"].mean())
            br, bsu = b[b.kind == "real"], b[b.kind == "surr"]
            bs["auc_real"].append(auc(br[m].values, (br.stage == pos).astype(int).values))
            bs["auc_surr"].append(auc(bsu[m].values, (bsu.stage == pos).astype(int).values))
        ci = {k: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for k, v in bs.items()}
        # AUC direction: report as max(AUC, 1-AUC) w.r.t. the real direction
        flip = a_real < 0.5
        ar, asu = (1 - a_real, 1 - a_surr) if flip else (a_real, a_surr)
        if flip:
            ci["auc_real"] = [1 - ci["auc_real"][1], 1 - ci["auc_real"][0]]
            ci["auc_surr"] = [1 - ci["auc_surr"][1], 1 - ci["auc_surr"][0]]
        passed = rates["surr_W"] <= 0.5 and ci["surr_W"][1] < ci["real_W"][0]
        note = ""
        if passed and rates["surr_W"] < rates["real_N3"]:
            note = "passes, surrogate-sensitive (surrogates pushed past N3)"
        out[m] = {"rates": rates, "ci": ci, "auc_real": ar, "auc_surr": asu,
                  "spectral_share": (asu - 0.5) / (ar - 0.5) if ar != 0.5 else None,
                  "verdict": "PASS" if passed else "FAIL", "note": note,
                  "higher_is_conscious": not flip}
    return out


def synth(n_sub=20, n_ep=40, seed=7):
    rng = np.random.default_rng(seed)
    n = int(30 * FS)
    t = np.arange(n) / FS
    rows, low = [], butter(2, [0.5, 2], btype="band", fs=FS, output="sos")
    for s in range(n_sub):
        f0, amp = rng.uniform(8, 11), rng.uniform(0.8, 1.2)
        for e in range(n_ep):
            for stage in ("W", "N3"):
                if stage == "W":   # time-irreversible sawtooth alpha + white noise: flat spectrum
                    ph = 2 * np.pi * f0 * t + np.cumsum(rng.normal(0, 0.05, n))
                    x = amp * sawtooth(ph, 0.1) + rng.normal(0, 0.5, n)
                else:              # linear Gaussian, steep spectrum, plus reversible slow waves
                    x = np.cumsum(rng.normal(0, 0.3, n)) * 0.2
                    x = x + 3 * sosfiltfilt(low, rng.normal(0, 1, n)) + rng.normal(0, 0.05, n)
                x = preprocess(np.stack([x, x + rng.normal(0, 0.1, n)]))
                sur = phase_surrogate(x, rng)
                f, p1 = psd(x); _, p2 = psd(sur)
                m = (f >= 1) & (f <= 40)
                err = float(np.median(np.abs(np.log10(p1[:, m]) - np.log10(p2[:, m]))))
                for kind, y in (("real", x), ("surr", sur)):
                    rows.append({"subject": f"s{s:02d}", "stage": stage, "kind": kind,
                                 "slope": spectral_exponent(y), "asym": time_asymmetry(y),
                                 "psd_err": err if kind == "surr" else np.nan})
    return pd.DataFrame(rows)


def main(mode):
    if mode == "planted":
        df = synth()
        res = gate(df, ["slope", "asym"], n_boot=300)
        res["psd_err_median"] = float(df.psd_err.median())
        ok = (res["slope"]["verdict"] == "FAIL" and res["asym"]["verdict"] == "PASS"
              and res["psd_err_median"] < 0.05)
        res["PLANTED_CHECK_PASS"] = bool(ok)
        json.dump(res, open(os.path.join(HERE, "planted.json"), "w"), indent=1)
        print(json.dumps(res, indent=1))
        return
    print("prereg sealed at", require_sealed(PREREG))
    planted = json.load(open(os.path.join(HERE, "planted.json")))
    assert planted["PLANTED_CHECK_PASS"], "planted check failed; real run does not count"
    rows = [json.loads(l) for l in open(os.path.join(REPO, "experiments", "lz_slope", "features.jsonl"))]
    df = pd.DataFrame(rows)
    df = df[df.clean].reset_index(drop=True)
    cnt = df[df.kind == "real"].groupby(["subject", "stage"]).size().unstack(fill_value=0)
    keep = cnt[(cnt[["W", "N3", "R"]] >= 10).all(1)].index
    df = df[df.subject.isin(keep)].reset_index(drop=True)
    measures = ["lz", "pnlz", "slope", "bp_delta", "perm_entropy"]
    res = gate(df, measures)
    res["n_subjects"] = int(len(keep))
    res["n_epochs_real"] = df[df.kind == "real"].stage.value_counts().to_dict()
    res["psd_err_median"] = float(df.psd_err.median())
    res["mean_real_vs_surr"] = {m: {st: [float(df[(df.kind == k) & (df.stage == st)][m].mean())
                                         for k in ("real", "surr")] for st in ("W", "N3", "R")}
                                for m in measures}
    json.dump(res, open(os.path.join(HERE, "results_gate.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
