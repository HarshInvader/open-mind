"""T-IIT and T-GNWT analysis on DREAM N2 awakenings.

Preregs: docs/prereg/2026-11-18_theory_iit_posterior_dream.md, ..._gnwt_frontal_dream.md
  .venv/bin/python -I experiments/theory_tests/dream_analysis.py planted   # random labels, must pass first
  .venv/bin/python -I experiments/theory_tests/dream_analysis.py real
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.linear_model import LogisticRegression

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "experiments", "rules"))
from evidence import Recording, check_split, require_sealed, subject_folds  # noqa: E402

FEAT = os.path.join(HERE, "features")
PREREGS = [os.path.join(REPO, "docs", "prereg", p) for p in
           ("2026-11-18_theory_iit_posterior_dream.md", "2026-11-18_theory_gnwt_frontal_dream.md")]
POST = ["P3", "Pz", "P4", "O1", "O2"]
FRONT = ["F3", "Fz", "F4"]
RECORDS = {"zhang": "raw/meta/zhang_Records.csv", "youngadults": "raw/meta/ya_Records.csv"}


def load(with_labels):
    f = np.load(os.path.join(FEAT, "psd_freqs.npy"))
    chans = json.load(open(os.path.join(FEAT, "psd_channels.json")))
    log = [json.loads(ln) for ln in open(os.path.join(FEAT, "dream_fetch_log.jsonl"))]
    rows, psds = [], []
    for r in log:
        if r["status"] != "ok":
            continue
        P = np.load(os.path.join(FEAT, f"psd_{r['dataset']}_{os.path.basename(r['file'])}.npy")).astype(float)
        rows.append({"dataset": r["dataset"], "file": r["file"]})
        psds.append(P)
    df = pd.DataFrame(rows)
    rec = pd.concat([pd.read_csv(os.path.join(HERE, p)).assign(dataset=d) for d, p in RECORDS.items()])
    rec = rec.rename(columns={"Filename": "file", "Subject ID": "subject"})
    cols = ["dataset", "file", "subject"] + (["Experience"] if with_labels else [])
    df = df.merge(rec[cols], on=["dataset", "file"], how="left")
    df["subject"] = df["dataset"] + ":" + df["subject"].astype(str)
    if with_labels:
        df = df[df["Experience"].isin([0, 2])].copy()
        keep = df.index.values
        psds = [psds[i] for i in keep]
        df = df.reset_index(drop=True)
        df["y"] = (df["Experience"] == 2).astype(int)
    return f, chans, np.array(psds), df


def measures(f, chans, psds, df, exponent=True):
    ci = {c: i for i, c in enumerate(chans)}
    d = (f >= 1) & (f <= 4)
    m = (f >= 1) & (f <= 30)
    delta = np.log10(psds[:, :, d].sum(-1))          # (n, ch)
    lf = np.log10(f[m])
    if exponent:
        A = np.vstack([lf, np.ones_like(lf)]).T
        Lp = np.log10(psds[:, :, m]).reshape(-1, m.sum()).T
        slopes = np.linalg.lstsq(A, Lp, rcond=None)[0][0].reshape(psds.shape[0], psds.shape[1]).mean(1)
    else:
        slopes = np.zeros(len(df))
    out = df.copy()
    out["D_post"] = delta[:, [ci[c] for c in POST]].mean(1)
    out["D_front"] = delta[:, [ci[c] for c in FRONT]].mean(1)
    out["exponent"] = slopes
    for c in ("D_post", "D_front", "exponent"):
        out[c + "_raw"] = out[c]
        out[c] = out.groupby("dataset")[c].transform(lambda v: (v - v.mean()) / v.std())
    return out


def auc(s, y):
    r = rankdata(s)
    n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def perm_p(s, y, strata, n=5000, seed=0):
    rng = np.random.default_rng(seed)
    obs = auc(s, y)
    r = rankdata(s)
    n1 = y.sum(); n0 = len(y) - n1
    idx = [np.flatnonzero(strata == k) for k in np.unique(strata)]
    Y = np.tile(y, (n, 1))
    for ii in idx:
        order = np.argsort(rng.random((n, len(ii))), axis=1)
        Y[:, ii] = y[ii][order]
    null = ((Y * r).sum(1) - n1 * (n1 + 1) / 2) / (n1 * n0)
    return obs, (1 + (null >= obs).sum()) / (n + 1)


def cluster_boot(df, fn, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    out = []
    groups = {ds: {s: g.index.values for s, g in d.groupby("subject")} for ds, d in df.groupby("dataset")}
    for _ in range(n):
        idx = np.concatenate([np.concatenate([gs[s] for s in rng.choice(list(gs), len(gs))])
                              for gs in groups.values()])
        b = df.loc[idx]
        if b.y.nunique() < 2:
            continue
        out.append(fn(b))
    return np.percentile(out, [2.5, 97.5]).tolist()


def cv_oof(df, feats, seed=0):
    subs = sorted(df.subject.unique())
    recs = [Recording(s, s, s.split(":")[0], s.split(":")[0]) for s in subs]
    folds = subject_folds(recs, k=5, seed=seed)
    pred = np.full(len(df), np.nan)
    for tr, te in folds:
        check_split([recs[i] for i in tr], [recs[i] for i in te])
        s_tr = {subs[i] for i in tr}
        fit = df[df.subject.isin(s_tr)]
        X = fit[feats].values
        mu, sd = X.mean(0), X.std(0) + 1e-12
        clf = LogisticRegression(C=1.0, class_weight="balanced").fit((X - mu) / sd, fit.y.values)
        ii = np.flatnonzero(~df.subject.isin(s_tr).values)
        pred[ii] = clf.predict_proba((df.iloc[ii][feats].values - mu) / sd)[:, 1]
    return pred


def transfer(df, feats):
    out = {}
    for tr_ds in df.dataset.unique():
        tr, te = df[df.dataset == tr_ds], df[df.dataset != tr_ds]
        check_split([Recording(s, s, tr_ds, tr_ds) for s in tr.subject.unique()],
                    [Recording(s, s, d, d) for s, d in te[["subject", "dataset"]].drop_duplicates().values],
                    mode="transfer")
        clf = LogisticRegression(C=1.0, class_weight="balanced").fit(tr[feats].values, tr.y.values)
        out[f"train_{tr_ds}"] = auc(clf.predict_proba(te[feats].values)[:, 1], te.y.values)
    return out


def planted():
    f, chans, psds, df = load(with_labels=True)  # labels used ONLY for per-dataset counts
    counts = df.groupby("dataset").y.agg(["sum", "count"]).to_dict("index")
    df = df.drop(columns=["y", "Experience"])
    ci = {c: i for i, c in enumerate(chans)}
    band = (f >= 1) & (f <= 4)
    rng = np.random.default_rng(1)
    res = {}
    for roi_name, roi in (("posterior", POST), ("frontal", FRONT)):
        for a in (1.0, 0.85, 0.75):
            ps, aucs = [], []
            for rep in range(200):
                y = np.zeros(len(df), int)
                for ds, c in counts.items():
                    ii = np.flatnonzero(df.dataset.values == ds)
                    y[rng.choice(ii, c["sum"], replace=False)] = 1
                P = psds.copy()
                for c in roi:
                    P[np.ix_(y == 1, [ci[c]], np.flatnonzero(band))] *= a ** 2
                m = measures(f, chans, P, df, exponent=False)
                col = "D_post" if roi_name == "posterior" else "D_front"
                o, p = perm_p(-m[col].values, y, m.dataset.values, n=1000, seed=rep)
                ps.append(p); aucs.append(o)
            res[f"{roi_name}_a{a}"] = {"power_at_0.025": float(np.mean(np.array(ps) < 0.025)),
                                       "mean_auc": float(np.mean(aucs))}
            print(roi_name, a, res[f"{roi_name}_a{a}"], flush=True)
    ok = all(res[f"{r}_a1.0"]["power_at_0.025"] <= 0.09 and res[f"{r}_a0.75"]["power_at_0.025"] >= 0.8
             for r in ("posterior", "frontal"))
    res["pass"] = bool(ok)
    json.dump(res, open(os.path.join(HERE, "planted_dream.json"), "w"), indent=1)
    print("PLANTED PASS" if ok else "PLANTED FAIL")


def real():
    for p in PREREGS:
        print("sealed:", require_sealed(p))
    pl = json.load(open(os.path.join(HERE, "planted_dream.json")))
    assert pl["pass"], "planted check failed; real results would not count"
    f, chans, psds, df = load(with_labels=True)
    m = measures(f, chans, psds, df)
    m.to_csv(os.path.join(FEAT, "dream_measures.csv"), index=False)
    y, strata = m.y.values, m.dataset.values
    out = {"n": int(len(m)), "n_exp": int(y.sum()), "n_noexp": int((1 - y).sum()),
           "n_subjects": int(m.subject.nunique()),
           "per_dataset": m.groupby("dataset").y.agg(["sum", "count"]).to_dict("index")}
    for name, col in (("posterior", "D_post"), ("frontal", "D_front"), ("exponent_steeper_is_noexp", "exponent")):
        s = -m[col].values if col != "exponent" else m[col].values
        o, p = perm_p(s, y, strata)
        cib = cluster_boot(m, lambda b, col=col: auc(-b[col].values if col != "exponent" else b[col].values, b.y.values))
        per = {ds: float(auc(-g[col].values if col != "exponent" else g[col].values, g.y.values))
               for ds, g in m.groupby("dataset")}
        out[name] = {"auc": float(o), "p_one_sided": float(p), "ci95": cib, "per_dataset": per}
    out["dAUC_post_minus_front"] = {
        "value": float(auc(-m.D_post.values, y) - auc(-m.D_front.values, y)),
        "ci95": cluster_boot(m, lambda b: auc(-b.D_post.values, b.y.values) - auc(-b.D_front.values, b.y.values))}
    for name, feats in (("posterior", ["exponent", "D_post"]), ("frontal", ["exponent", "D_front"])):
        pa = cv_oof(m, ["exponent"]); pb = cv_oof(m, feats)
        mm = m.assign(pa=pa, pb=pb)
        out[f"H3_{name}"] = {"auc_exponent": float(auc(pa, y)), "auc_plus": float(auc(pb, y)),
                             "dAUC": float(auc(pb, y) - auc(pa, y)),
                             "ci95": cluster_boot(mm, lambda b: auc(b.pb.values, b.y.values) - auc(b.pa.values, b.y.values)),
                             "transfer_plus": transfer(m, feats), "transfer_exponent": transfer(m, ["exponent"])}
    # verdicts per prereg
    iit = out["posterior"]["p_one_sided"] < 0.025 and out["dAUC_post_minus_front"]["ci95"][0] > 0 \
        and out["H3_posterior"]["ci95"][0] > 0
    gnwt = out["frontal"]["p_one_sided"] < 0.025 and out["H3_frontal"]["ci95"][0] > 0
    out["verdict_IIT"] = "passed this test" if iit else "failed this test"
    out["verdict_GNWT"] = "passed this test" if gnwt else "failed this test"
    out["surrogate_note"] = "delta power is spectrum-determined; phase-randomised surrogates return identical values by construction"
    json.dump(out, open(os.path.join(HERE, "dream_results.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"planted": planted, "real": real}[sys.argv[1]]()
