"""The one unblinding run for task #42 (prereg 2026-11-19_experience_benchmark.md + amendment 1).

  .venv/bin/python -I experiments/experience_benchmark/analysis.py   -> results.json (+ printed summary)

It refuses to run unless (1) the prereg, amendment 1, measures.py, extract.py, stats.py, this file,
study3_model.json and every features/<lab>.jsonl are sealed in docs/prereg/HASHES.txt with their current
hash, and (2) positive_control.json and planted.json exist, P1(a), P1(b) and P1(c) passed, and no PC1
fault flag is set (a failure there needs a sealed amendment first, prereg §7).

Choices fixed here, before unblinding (they fill gaps the prereg leaves to this script):
- K4: Family B training data INCLUDES the discovery labs (Tononi, Zhang & Wamsley) in every fold.
- Labels as prereg §2; rows with DREAM `Proportion artifacts` > 0.5 dropped; subject key (lab, Subject ID).
- Covariates: clock time = hours after 18:00 (mod 24); awakening index = rank of clock time within
  (Set ID, Subject ID). Missing values -> subject mean (0 after centring), as §4 says.
- Baseline: exponent + 6 band powers (bp_*), or the 1-30 Hz variant (exponent_1_30 + bp30_*, 5 bands) for
  all labs at once if any Tier 1 lab triggers the §4 rule on its mean label-blind psd_log10.
- Arousal adjustment (§8, C5): m is replaced by its residual from an OLS on clock time, awakening index and
  arousal_idx, each centred within subject, fitted over all rows of the tier (label-blind).
- catch22 (C2) was never extracted; it is left out of the dissociation table, so "every marker" can only
  refer to the 8 primary + 6 secondary measures listed. Stated as a limitation.
- Secondary measures have no prereg direction: they are reported unoriented (AUC of the raw value), and a
  bound is symmetric so orientation does not matter for C2.
- Study 3 ΔAUC (§10): model 0 (baseline + covariates) and model 0 + score are fitted on the discovery rows
  (score computed there with the same frozen model) and applied to Tier 1 without refitting. CI from the
  within-lab subject bootstrap of Tier 1 (5,000).
- P2 / K2 (power at AUC 0.60 under Holm-8) is computed by p2.py from the realised post-exclusion counts
  before unblinding and read from p2.json.
"""
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "experiments", "rules"))
import evidence  # noqa: E402
import measures as M  # noqa: E402
import stats as S  # noqa: E402

TIER1 = ["Rome", "LODE", "DATA1", "Aamodt", "Set19"]
TIER2 = TIER1 + ["Tononi", "Zhang"]
DISC = ["Tononi", "Zhang"]
SET_LAB = {9: "Rome", 3: "LODE", 16: "DATA1", 17: "Aamodt", 18: "Aamodt", 19: "Set19", 13: "Tononi", 1: "Zhang"}
DIRECTION = {"post_delta": -1, "post_hf": 1, "exponent": 1, "lz": 1, "pe": 1, "hfd": 1, "wsmi": 1, "tc": -1}
FAM_B = ["lz", "pe", "hfd", "wsmi"]
NONSPEC = ["lz", "pe", "hfd", "wsmi", "tc"]
SEC = M.SECONDARY
N_PERM, N_BOOT, N_BOOT_B = 5000, 5000, 2000
PREREG = ["docs/prereg/2026-11-19_experience_benchmark.md"] + [
    f"docs/prereg/2026-11-19_experience_benchmark_amendment{k}.md" for k in (1, 2, 3)]


# ------------------------------------------------------------------ guards
def guards():
    paths = PREREG + [f"experiments/experience_benchmark/{f}" for f in
                      ("measures.py", "extract.py", "stats.py", "analysis.py", "study3_model.json")]
    paths += [f"experiments/experience_benchmark/features/{lab}.jsonl" for lab in TIER2]
    for p in paths:
        evidence.require_sealed(os.path.join(REPO, p))
    pc = json.load(open(os.path.join(HERE, "positive_control.json")))
    pl = json.load(open(os.path.join(HERE, "planted.json")))
    if not (pl["P1a_pass"] and pl["P1b_pass"] and pl["P1c"]["pass"]):
        raise SystemExit("planted check failed: a sealed amendment is needed before unblinding")
    if any(v["pc1_fault_flag"] for k, v in pc["verdict"].items() if isinstance(v, dict)):
        raise SystemExit("PC1 fault flag set: a sealed amendment is needed before unblinding")
    return pc, pl


# ------------------------------------------------------------------ data
def hours_after_18(t):
    if not isinstance(t, str) or ":" not in t:
        return np.nan
    h, m, *s = (float(v) for v in t.split(":"))
    return (h + m / 60 + (s[0] if s else 0) / 3600 - 18) % 24


def load(stage="N2", label_pos=("Experience",), label_neg=("No experience",)):
    d = pd.read_csv(os.path.join(REPO, "experiments", "dataset_audit", "dream_records.csv"))
    d = d.sort_values("Amendment").drop_duplicates(["Set ID", "Filename"], keep="last")
    meta = {(int(r["Set ID"]), r["Filename"]): r for r in d.to_dict("records")}
    rows = []
    for lab in TIER2:
        for r in map(json.loads, open(os.path.join(HERE, "features", f"{lab}.jsonl"))):
            if r.get("status") != "ok" or r.get("stage") != stage:
                continue
            m = meta[(int(r["set"]), r["file"])]
            if m["Experience"] in label_pos:
                y = 1
            elif m["Experience"] in label_neg:
                y = 0
            else:
                continue
            if pd.notna(m["Proportion artifacts"]) and float(m["Proportion artifacts"]) > 0.5:
                continue
            r = dict(r, y=y, subj=f"{lab}|{m['Subject ID']}", subj_set=f"{lab}|{m['Set ID']}|{m['Subject ID']}",
                     clock=hours_after_18(m["Time of awakening"]))
            rows.append(r)
    df = pd.DataFrame(rows)
    df["aw_idx"] = df.groupby("subj_set")["clock"].rank(method="average")
    return df


def fill_subject_mean(df, cols):
    for c in cols:
        df[c] = df[c].astype(float)
        df[c] = df[c].fillna(df.groupby("subj")[c].transform("mean")).fillna(0.0)
    return df


def baseline_cols(df):
    trig = {}
    for lab in TIER1:
        P = np.array([p for p in df.loc[df.lab == lab, "psd_log10"]])
        if len(P) == 0:
            continue
        f = np.arange(P.shape[1]) * 0.5
        mp = P.mean(0); fit = (f >= 2) & (f <= 25)
        b = np.polyfit(np.log10(f[fit]), mp[fit], 1)
        hi = (f >= 30) & (f <= 40)
        gap = float(np.mean(np.polyval(b, np.log10(f[hi])) - mp[hi]))
        trig[lab] = {"gap_log10": gap, "trigger": gap > 2}
    if any(v["trigger"] for v in trig.values()):
        return ["exponent_1_30"] + [f"bp30_{b}" for b in ("delta", "theta", "alpha", "sigma", "beta")], trig
    return ["exponent", "bp_delta", "bp_theta", "bp_alpha", "bp_sigma", "bp_beta", "bp_lowgamma"], trig


def arrays(df):
    return df.y.values.astype(int), df.subj.values.astype(object), df.lab.values.astype(object)


def residualise(df, cols):
    """Label-blind: each column regressed on [clock, aw_idx, arousal_idx], all centred within subject."""
    out = df.copy()
    s = df.subj.values
    Xc = S.centre_z(df[["clock", "aw_idx", "arousal_idx"]].astype(float).fillna(0).values, s)
    Xi = np.c_[np.ones(len(df)), Xc]
    for c in cols:
        v = df[c].astype(float).values; ok = np.isfinite(v)
        vc = v.copy()
        for sb in np.unique(s):
            i = (s == sb) & ok
            vc[i] = v[i] - v[i].mean()
        beta, *_ = np.linalg.lstsq(Xi[ok], vc[ok], rcond=None)
        r = np.full(len(v), np.nan); r[ok] = vc[ok] - Xi[ok] @ beta
        out[c] = r
    return out


def famA(df, names, signs, seed, n_perm=N_PERM, n_boot=N_BOOT):
    y, s, lab = arrays(df)
    F = np.column_stack([df[n].astype(float).values if n in df else np.full(len(df), np.nan) for n in names])
    return S.family_a(F, names, signs, y, s, lab, n_perm=n_perm, n_boot=n_boot, seed=seed)


# ------------------------------------------------------------------ Study 3
def study3_score(df, model, keys=None):
    keys = keys or [f"{k}__ft" for k in model["feature_keys"]]
    X = np.column_stack([df[k].astype(float).values - df[kf].astype(float).values if kf.endswith("__ft")
                         else df[kf].astype(float).values for k, kf in zip(model["feature_keys"], keys)])
    s = df.subj.values; Z = np.zeros_like(X)
    for sb in np.unique(s):
        i = s == sb
        mu = np.nanmean(X[i], 0); sd = np.nanstd(X[i], 0); sd = np.where(sd > 0, sd, np.inf)
        Z[i] = (X[i] - mu) / sd
    Z = np.nan_to_num(Z, nan=0.0)
    return model["intercept"] + Z @ np.array(model["coef"])


def study3_surr_score(df, model, kind):
    """Gate: features replaced by the second-draw surrogate excess m__s3x_<kind> (already excess values)."""
    X = np.column_stack([df[f"{k}__s3x_{kind}"].astype(float).values for k in model["feature_keys"]])
    s = df.subj.values; Z = np.zeros_like(X)
    for sb in np.unique(s):
        i = s == sb
        mu = np.nanmean(X[i], 0); sd = np.nanstd(X[i], 0); sd = np.where(sd > 0, sd, np.inf)
        Z[i] = (X[i] - mu) / sd
    Z = np.nan_to_num(Z, nan=0.0)
    return model["intercept"] + Z @ np.array(model["coef"])


def study3(df1, dfd, base, model, rng):
    y, s, lab = arrays(df1)
    sc = study3_score(df1, model)
    kb = S.keep_both(y, s)
    P = S.PairAUC(y[kb], s[kb], lab[kb])
    a = P.auc(sc[kb])
    Y = P.perm_labels(N_PERM, rng)
    null = P.perm_aucs(sc[kb], Y)
    out = {"killed_in_fit": model["killed"], "outer_auc_fit": model["outer_auc"], "auc": a,
           "p_one_sided": float((1 + np.sum(null >= a - 1e-12)) / (1 + N_PERM)),
           "ci95": P.boot_ci(sc[kb], P.boot_draws(N_BOOT, rng)),
           "per_lab": {l: S.PairAUC(y[kb][lab[kb] == l], s[kb][lab[kb] == l]).auc(sc[kb][lab[kb] == l])
                       for l in np.unique(lab[kb])}}
    # frozen ΔAUC: models fitted on discovery rows only
    cols = base + ["clock", "aw_idx"]
    yd, sd_, _ = arrays(dfd)
    Xd = S.centre_z(dfd[cols].astype(float).values, sd_); scd = S.centre_z(study3_score(dfd, model), sd_)
    X1 = S.centre_z(df1[cols].astype(float).values, s); sc1 = S.centre_z(sc, s)
    w0 = S.logit_fit(Xd, yd); w1 = S.logit_fit(np.c_[Xd, scd], yd)
    p0 = w0[0] + X1 @ w0[1:]; p1 = w1[0] + np.c_[X1, sc1] @ w1[1:]
    n0, n1 = P.num_s(p0[kb]), P.num_s(p1[kb])
    out["delta"] = float((n1.sum() - n0.sum()) / P.den_s.sum())
    draws = P.boot_draws(N_BOOT, rng)
    bd = [(n1[d].sum() - n0[d].sum()) / P.den_s[d].sum() for d in draws]
    out["delta_ci95"] = (float(np.percentile(bd, 2.5)), float(np.percentile(bd, 97.5)))
    g = {}
    for kind in ("ft", "iaaft"):
        ss = study3_surr_score(df1, model, kind)
        g["auc_" + kind] = P.auc(ss[kb])
        g["share_" + kind] = (g["auc_" + kind] - 0.5) / (a - 0.5) if a != 0.5 else float("inf")   # AUC 0.5: gate fails
    g["pass"] = bool(g["share_ft"] <= 0.5 and g["share_iaaft"] <= 0.5)
    out["gate"] = g
    rr = residualise(df1.assign(s3=sc), ["s3"])
    out["auc_arousal_adjusted"] = S.PairAUC(y[kb], s[kb]).auc(rr["s3"].values[kb])
    return out


# ------------------------------------------------------------------ amendment 3: spectral headline
def spectral_headline(dB, cols, test_labs, rng, n_perm=N_PERM, n_boot=N_BOOT_B):
    """Held-out experience AUC of a logistic model on `cols` only (leave one test lab out; all other rows,
    including any training-only labs, in training). One-sided within-subject label permutation p (refit),
    95% CI from the within-lab subject bootstrap (refit)."""
    y, s, lab = arrays(dB)
    X = S.centre_z(dB[cols].astype(float).values, s)
    te = np.isin(lab, list(test_labs))
    P = S.PairAUC(y[te], s[te], lab[te])
    a = P.auc(S.lolo_pred(X, y, lab, test_labs)[te])
    grp = [np.flatnonzero(s == sb) for sb in np.unique(s)]
    null = np.empty(n_perm)
    for p in range(n_perm):
        yp = y.copy()
        for g in grp:
            yp[g] = y[g][rng.permutation(len(g))]
        null[p] = S.PairAUC(yp[te], s[te]).auc(S.lolo_pred(X, yp, lab, test_labs)[te])
    sub_ids = np.unique(s); sub_lab = np.array([lab[s == sb][0] for sb in sub_ids])
    rows_of = {sb: np.flatnonzero(s == sb) for sb in sub_ids}
    bs = []
    for _ in range(n_boot):
        pick, ns = [], []
        for l in np.unique(sub_lab):
            for k, sb in enumerate(rng.choice(sub_ids[sub_lab == l], (sub_lab == l).sum(), replace=True)):
                pick.append(rows_of[sb]); ns.append(np.full(len(rows_of[sb]), f"{sb}#{k}", object))
        pk = np.concatenate(pick); nsb = np.concatenate(ns); tb = te[pk]
        q = S.lolo_pred(X[pk], y[pk], lab[pk], test_labs)[tb]
        bs.append(S.PairAUC(y[pk][tb], nsb[tb]).auc(q))
    return {"auc": a, "p_one_sided": float((1 + np.sum(null >= a - 1e-12)) / (1 + n_perm)),
            "ci95": (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))), "columns": cols,
            "test_labs": sorted(test_labs), "n_test": int(te.sum())}


def reading(R):
    """Amendment 3 §2: how each outcome is read, fixed before unblinding."""
    sp = R["spectral_headline_tier1"]
    SP = sp["ci95"][0] > 0.50 and sp["p_one_sided"] < 0.05
    s3 = R["study3"]
    adds = [m for m in FAM_B if R["B_tier1"][m]["holm_sig"] and R["B_tier1"][m]["delta"] >= 0.03
            and R["B_tier1"][m]["ci95"][0] > 0]
    if (not s3["killed_in_fit"]) and s3["p_one_sided"] < 0.05 and s3["delta"] >= 0.03 and s3["delta_ci95"][0] > 0:
        adds.append("study3")
    none_adds = all(R["B_tier1"][m]["ci95"][1] < 0.03 for m in FAM_B) and s3["delta_ci95"][1] < 0.03
    a2 = [k for k, v in R["A2_correlate"].items() if v["achieved"]]
    if a2:
        r = "R2/R4: arousal-free, spectrum-free correlate (A2): " + ", ".join(a2)
    elif SP and none_adds and R["K1_pass"]:
        r = ("R1 + A1: the named markers are bounded (A1) yet the full frozen spectrum predicts report; " if
             R["A1_double_dissociation"]["achieved"] else "") + "R1: spectrum-sufficient. The frozen spectrum predicts report at fixed stage in held-out labs, and no marker adds to it (all increments bounded below 0.03). Publishable."
    elif (not SP) and R["A1_double_dissociation"]["achieved"]:
        r = "R3: clean double dissociation (A1). Publishable."
    elif SP and adds:
        r = "R5a: spectrum predicts and some marker adds, but short of the A2 marks: atlas, no paper."
    else:
        r = "R5: messy middle: atlas and ledger, no paper."
    return {"spectrum_predicts": bool(SP), "markers_adding": adds, "no_marker_adds_bounded": bool(none_adds), "reading": r}


# ------------------------------------------------------------------ main
def main():
    pc, pl = guards()
    model = json.load(open(os.path.join(HERE, "study3_model.json")))
    p2 = json.load(open(os.path.join(HERE, "p2.json")))
    rng = np.random.default_rng(20261119)
    R = {"guards": "sealed hashes OK; P1 a/b/c passed; no PC1 fault flag", "K4": "discovery labs in Family B training"}
    df = fill_subject_mean(load(), ["clock", "aw_idx", "arousal_idx"])
    base, trig = baseline_cols(df)
    R["baseline"] = {"columns": base, "lowpass_rule": trig}
    d1 = df[df.lab.isin(TIER1)].copy(); d2 = df.copy(); dd = df[df.lab.isin(DISC)].copy()
    for d in (d1, d2, dd):
        kb = S.keep_both(d.y.values, d.subj.values); d.drop(d.index[~kb], inplace=True)

    def counts(d):
        labs = {l: int(g.subj.nunique()) for l, g in d.groupby("lab")}
        return {"n": int(len(d)), "n_exp": int(d.y.sum()), "n_no": int((1 - d.y).sum()),
                "n_subj": int(d.subj.nunique()), "subjects_per_lab": labs}
    R["counts"] = {"tier1": counts(d1), "tier2": counts(d2), "discovery": counts(dd)}
    c1 = R["counts"]["tier1"]
    R["K1_pass"] = bool(c1["n"] >= 300 and c1["n_no"] >= 120 and len(c1["subjects_per_lab"]) >= 3)
    R["K2_pass"] = bool(p2["power_auc060_holm8"] >= 0.80)
    signs = [DIRECTION[m] for m in M.PRIMARY]

    # Family A
    R["A_tier1"] = famA(d1, M.PRIMARY, signs, 1)
    R["A_tier2"] = famA(d2, M.PRIMARY, signs, 2)
    R["A_tier2_noTononi_1_3"] = famA(d2[d2.lab != "Tononi"], ["post_delta", "exponent"], [-1, 1], 3, n_perm=0)
    R["C_tier1"] = famA(d1, SEC, [1] * len(SEC), 4, n_perm=N_PERM)
    R["C_tier2"] = famA(d2, SEC, [1] * len(SEC), 5, n_perm=0)
    r1 = residualise(d1, M.PRIMARY + SEC); r2 = residualise(d2, M.PRIMARY + SEC)
    R["A_tier1_arousal_adj"] = famA(r1, M.PRIMARY, signs, 6, n_perm=0)
    R["A_tier2_arousal_adj"] = famA(r2, M.PRIMARY, signs, 7, n_perm=0)
    R["C_tier2_arousal_adj"] = famA(r2, SEC, [1] * len(SEC), 8, n_perm=0)

    # Family B (Tier 1 test labs; discovery labs in training: K4)
    dB = pd.concat([d1, dd])
    y, s, lab = arrays(dB)
    X0 = S.centre_z(dB[base + ["clock", "aw_idx"]].astype(float).values, s)
    Mb = np.column_stack([S.centre_z(dB[m].astype(float).values, s)[:, 0] if np.isfinite(dB[m].astype(float)).all()
                          else _cz_nan(dB[m].astype(float).values, s) for m in FAM_B])
    R["B_tier1"] = S.family_b(X0, Mb, FAM_B, y, s, lab, set(TIER1), n_perm=N_PERM, n_boot=N_BOOT_B, seed=9)

    # amendment 3: the frozen spectrum's own experience AUC (headline), and with covariates (model 0)
    R["spectral_headline_tier1"] = spectral_headline(dB, base, set(TIER1), np.random.default_rng(31))
    R["model0_tier1"] = spectral_headline(dB, base + ["clock", "aw_idx"], set(TIER1), np.random.default_rng(32), n_perm=0)
    R["spectral_headline_tier2_lolo7"] = spectral_headline(d2, base, set(TIER2), np.random.default_rng(33), n_perm=0)

    # gate for anything significant in A or B (Tier 1)
    y1, s1, _ = arrays(d1)
    R["gate"] = {}
    for m in NONSPEC:
        if R["A_tier1"][m]["holm_sig"] or (m in FAM_B and R["B_tier1"][m]["holm_sig"]):
            R["gate"][m] = S.gate(d1[m].astype(float).values, d1[m + "__ft"].astype(float).values,
                                  d1[m + "__iaaft"].astype(float).values, DIRECTION[m], y1, s1)

    # Study 3
    R["study3"] = study3(d1, dd, base, model, rng)

    # sensitivity and secondary analyses (§8, C6, C7)
    d1n19 = d1[d1.lab != "Set19"]
    R["A_tier1_without_set19"] = famA(d1n19, M.PRIMARY, signs, 10)
    R["study3_without_set19"] = study3(d1n19, dd, base, model, np.random.default_rng(11))
    R["A_tier1_window_last20"] = famA(d1, [m + "__w0" for m in M.PRIMARY], signs, 12)
    R["A_tier1_window_minus10"] = famA(d1, [m + "__w10" for m in M.PRIMARY], signs, 13)
    R["A_rome_only"] = famA(d1[d1.lab == "Rome"], M.PRIMARY, signs, 14, n_perm=0)
    R["A_other_tier1"] = famA(d1[d1.lab != "Rome"], M.PRIMARY, signs, 15, n_perm=0)
    dk = d1.copy(); dk["subj"] = dk["subj_set"]
    dk = dk[S.keep_both(dk.y.values, dk.subj.values)]
    R["A_tier1_aamodt_set_key"] = famA(dk, M.PRIMARY, signs, 16, n_perm=0)
    rem = fill_subject_mean(load("REM"), ["clock", "aw_idx", "arousal_idx"]); rem = rem[rem.lab.isin(TIER1)]
    rem = rem[S.keep_both(rem.y.values, rem.subj.values)]
    R["A_REM_tier1"] = famA(rem, M.PRIMARY, signs, 17); R["counts"]["REM_tier1"] = counts(rem)
    n3 = fill_subject_mean(load("N3"), ["clock", "aw_idx", "arousal_idx"]); n3 = n3[n3.lab == "DATA1"]
    n3 = n3[S.keep_both(n3.y.values, n3.subj.values)]
    R["A_N3_DATA1"] = famA(n3, M.PRIMARY, signs, 18) if len(n3) else None
    wr = fill_subject_mean(load("N2", ("Without recall",)), ["clock", "aw_idx", "arousal_idx"]); wr = wr[wr.lab.isin(TIER1)]
    wr = wr[S.keep_both(wr.y.values, wr.subj.values)]
    R["A_without_recall_vs_none_tier1"] = famA(wr, M.PRIMARY, signs, 19, n_perm=0) if len(wr) else None

    # ---------------------------------------------------------- outcomes
    tracking = {m: pc["verdict"][m]["arousal_tracking"] for m in M.PRIMARY}
    inside = lambda ci: ci[0] > 0.40 and ci[1] < 0.60
    a1_measures = [m for m in M.PRIMARY if tracking[m] and inside(R["A_tier2"][m]["ci95"])
                   and 0.40 <= R["A_tier1"][m]["auc"] <= 0.60 and inside(R["A_tier2_arousal_adj"][m]["ci95"])]
    c2 = R["counts"]["tier2"]
    labs_ok = sum(1 for v in c2["subjects_per_lab"].values() if v >= 2)
    A1 = {"measures_bounded_and_tracking": a1_measures, "n": len(a1_measures),
          "no_holm_sig": not any(R["A_tier1"][m]["holm_sig"] or R["A_tier2"][m]["holm_sig"] for m in M.PRIMARY),
          "labs_with_2_subjects": labs_ok, "tier2_n": c2["n"]}
    A1["achieved"] = bool(A1["n"] >= 6 and A1["no_holm_sig"] and labs_ok >= 5 and c2["n"] >= 600 and R["K1_pass"])
    A1["every_marker_bounded"] = bool(all(inside(R["A_tier2"][m]["ci95"]) for m in M.PRIMARY)
                                      and all(inside(R["C_tier2"][m]["ci95"]) for m in SEC))
    R["A1_double_dissociation"] = A1

    A2 = {}
    for m in FAM_B:
        a, b = R["A_tier1"][m], R["B_tier1"][m]
        g = R["gate"].get(m, {"pass": False})
        signs_ok = sum(1 for v in a["per_lab"].values() if v > 0.5)
        A2[m] = {"auc": a["auc"], "holm_A": a["holm_sig"], "holm_B": b["holm_sig"], "delta": b["delta"],
                 "delta_ci95": b["ci95"], "gate": g["pass"], "auc_arousal_adj": R["A_tier1_arousal_adj"][m]["auc"],
                 "labs_same_sign": signs_ok}
        A2[m]["achieved"] = bool(a["auc"] >= 0.65 and a["holm_sig"] and b["holm_sig"] and b["delta"] >= 0.03
                                 and b["ci95"][0] > 0 and g["pass"] and A2[m]["auc_arousal_adj"] >= 0.60
                                 and signs_ok >= 4 and R["K1_pass"] and R["K2_pass"])
    s3 = R["study3"]
    s3_signs = sum(1 for v in s3["per_lab"].values() if v > 0.5)
    A2["study3"] = {"auc": s3["auc"], "p": s3["p_one_sided"], "delta": s3["delta"], "delta_ci95": s3["delta_ci95"],
                    "gate": s3["gate"]["pass"], "auc_arousal_adj": s3["auc_arousal_adjusted"], "labs_same_sign": s3_signs,
                    "killed_in_fit": s3["killed_in_fit"]}
    A2["study3"]["achieved"] = bool(not s3["killed_in_fit"] and s3["auc"] >= 0.65 and s3["p_one_sided"] < 0.05
                                    and s3["delta"] >= 0.03 and s3["delta_ci95"][0] > 0 and s3["gate"]["pass"]
                                    and s3["auc_arousal_adjusted"] >= 0.60 and s3_signs >= 4
                                    and R["K1_pass"] and R["K2_pass"])
    R["A2_correlate"] = A2
    R["set19_dependence"] = {
        "A1_without_set19_note": "A1 uses Tier 2 bounds; Tier 1 point estimates without set 19 are in A_tier1_without_set19",
        "study3_auc_without_set19": R["study3_without_set19"]["auc"]}
    R["outcome"] = ("A1 clean double dissociation" if A1["achieved"] else
                    "A2 arousal-free, spectrum-free correlate: " + ", ".join(k for k, v in A2.items() if v["achieved"])
                    if any(v["achieved"] for v in A2.values()) else "messy middle (atlas and ledger, no paper)")
    R["reading_amendment3"] = reading(R)
    out = os.path.join(HERE, "results.json")
    json.dump(R, open(out, "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print("OUTCOME:", R["outcome"])
    sp = R["spectral_headline_tier1"]
    print(f"HEADLINE spectrum-only AUC (Tier 1, held-out labs): {sp['auc']:.3f} [{sp['ci95'][0]:.3f},{sp['ci95'][1]:.3f}] "
          f"p {sp['p_one_sided']:.4f}")
    print("READING:", R["reading_amendment3"]["reading"])
    print("counts", R["counts"]["tier1"], R["counts"]["tier2"]["n"])
    for m in M.PRIMARY:
        a1, a2 = R["A_tier1"][m], R["A_tier2"][m]
        print(f"{m:11s} T1 {a1['auc']:.3f} [{a1['ci95'][0]:.3f},{a1['ci95'][1]:.3f}] holm {a1['p_holm']:.4f} | "
              f"T2 {a2['auc']:.3f} [{a2['ci95'][0]:.3f},{a2['ci95'][1]:.3f}] | arousal-tracking {tracking[m]}")
    print("study3", {k: s3[k] for k in ("auc", "p_one_sided", "delta", "delta_ci95")}, "gate", s3["gate"])
    print("results sha256", hashlib.sha256(open(out, "rb").read()).hexdigest())


def _cz_nan(v, s):
    """centre_z for a column with missing values (missing stays NaN; dropped per measure in family_b)."""
    out = np.full(len(v), np.nan); ok = np.isfinite(v)
    out[ok] = S.centre_z(v[ok], s[ok])[:, 0]
    return out


if __name__ == "__main__":
    main()
