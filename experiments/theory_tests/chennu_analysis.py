"""T-ENT analysis: entropic brain on Chennu propofol (baseline vs moderate).

Prereg: docs/prereg/2026-11-18_theory_entropic_propofol.md
  .venv/bin/python -I experiments/theory_tests/chennu_analysis.py planted   # baseline only
  .venv/bin/python -I experiments/theory_tests/chennu_analysis.py real
"""
import itertools
import json
import os
import sys

import numpy as np
import pandas as pd
import scipy.io as sio
from scipy.stats import spearmanr, wilcoxon

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "experiments", "rules"))
sys.path.insert(0, HERE)
from evidence import require_sealed  # noqa: E402
from dream_analysis import auc, cv_oof  # noqa: E402

PREREG = os.path.join(REPO, "docs", "prereg", "2026-11-18_theory_entropic_propofol.md")
MEAS = ["lz", "pnlz", "slope", "perm_entropy", "lz_surr", "pnlz_surr"]


def load():
    ep = pd.DataFrame([json.loads(l) for l in open(os.path.join(HERE, "features", "chennu_epochs.jsonl"))])
    ep = ep[~ep.bad].copy()
    ep["pnlz_surr"] = ep.lz_surr * ep.pnlz / ep.lz
    return ep


def per_rec(ep):
    g = ep.groupby(["subject", "level"])
    rec = g[MEAS].median()
    rec["n_clean"] = g.size()
    rec = rec[rec.n_clean >= 6].reset_index()
    return rec


def paired(a, b):
    """one-sided tests that b < a (b = moderate). Returns dict."""
    d = b - a
    w = wilcoxon(d, alternative="less")
    n = len(d)
    # exact sign-flip permutation on the mean difference
    if n <= 16:
        flips = np.array(list(itertools.product([1, -1], repeat=n)))
    else:
        flips = np.random.default_rng(0).choice([1, -1], size=(10000, n))
    null = (flips * np.abs(d)).mean(1)
    p_perm = (1 + (null <= d.mean()).sum()) / (len(null) + 1)
    rng = np.random.default_rng(0)
    boots = [np.median(rng.choice(d, n)) for _ in range(2000)]
    rpos = np.sum(np.argsort(np.argsort(np.abs(d)))[d > 0] + 1)
    rneg = np.sum(np.argsort(np.argsort(np.abs(d)))[d < 0] + 1)
    return {"n": int(n), "median_diff": float(np.median(d)), "ci95": np.percentile(boots, [2.5, 97.5]).tolist(),
            "wilcoxon_p_less": float(w.pvalue), "signflip_p_less": float(p_perm),
            "rank_biserial": float((rpos - rneg) / (rpos + rneg)) if (rpos + rneg) else 0.0,
            "d_z": float(d.mean() / (d.std(ddof=1) + 1e-12)),
            "wilcoxon_p_greater": float(wilcoxon(d, alternative="greater").pvalue)}


def planted():
    ep = load()
    b = ep[ep.level == 1]
    rec = b.groupby("subject")[MEAS].median()
    # P1: real vs own surrogate (pnLZ must differ; exponent identical by construction)
    p1 = wilcoxon(rec.pnlz - rec.pnlz_surr)
    out = {"P1_pnlz_real_minus_surr_median": float(np.median(rec.pnlz - rec.pnlz_surr)), "P1_p": float(p1.pvalue),
           "P1_n": int(len(rec))}
    # P2: first vs second half of baseline
    h1 = b[b.epoch < 6].groupby("subject").pnlz.median()
    h2 = b[b.epoch >= 6].groupby("subject").pnlz.median()
    s = h1.index.intersection(h2.index)
    out["P2"] = paired(h1[s].values, h2[s].values)
    out["P1_pass"] = bool(out["P1_p"] < 0.05)
    out["P2_pass"] = bool(out["P2"]["wilcoxon_p_less"] > 0.05)
    json.dump(out, open(os.path.join(HERE, "planted_chennu.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


def real():
    print("sealed:", require_sealed(PREREG))
    pl = json.load(open(os.path.join(HERE, "planted_chennu.json")))
    ep = load()
    rec = per_rec(ep)
    wide = rec.pivot(index="subject", columns="level")
    wide = wide.dropna()
    out = {"subjects": int(len(wide)), "planted": pl}
    for m in MEAS:
        out[m] = paired(wide[(m, 1)].values, wide[(m, 3)].values)
    # surrogate gate: does surrogate LZ reproduce the LZ drop?
    out["surrogate_gate"] = {"lz_real_drop": out["lz"]["median_diff"], "lz_surrogate_drop": out["lz_surr"]["median_diff"]}
    # H3: subject-held-out AUC exponent vs exponent + LZ / + pnLZ
    r = rec[rec.subject.isin(wide.index)].copy()
    r["y"] = (r.level == 1).astype(int)  # 1 = baseline (less sedated)
    r["dataset"] = "chennu"
    r["subject"] = "chennu:" + r.subject
    r = r.reset_index(drop=True)
    pa = cv_oof(r, ["slope"])
    for extra in ("lz", "pnlz"):
        pb = cv_oof(r, ["slope", extra])
        out[f"H3_{extra}"] = {"auc_exponent": float(auc(pa, r.y.values)), "auc_plus": float(auc(pb, r.y.values))}
    out["single_auc"] = {m: float(max(auc(r[m].values, r.y.values), 1 - auc(r[m].values, r.y.values))) for m in MEAS}
    # H4: behaviour
    info = sio.loadmat(os.path.join(HERE, "raw", "meta", "chennu_datainfo.mat"), squeeze_me=True)["datainfo"]
    hits = {(str(x[0])[:2], int(x[1])): float(x[4]) for x in info}
    dl = wide[("lz", 3)] - wide[("lz", 1)]
    dh = pd.Series({s: hits[(s, 3)] - hits[(s, 1)] for s in wide.index})
    rho, p = spearmanr(dl.values, dh[wide.index].values)
    out["H4_lz_change_vs_hits_change"] = {"rho": float(rho), "p_one_sided": float(p / 2 if rho > 0 else 1 - p / 2)}
    dpn = wide[("pnlz", 3)] - wide[("pnlz", 1)]
    rho2, p2 = spearmanr(dpn.values, dh[wide.index].values)
    out["H4_pnlz_change_vs_hits_change"] = {"rho": float(rho2), "p_one_sided": float(p2 / 2 if rho2 > 0 else 1 - p2 / 2)}
    h2 = out["pnlz"]
    passed = h2["wilcoxon_p_less"] < 0.05 and h2["median_diff"] < 0
    if not pl.get("P1_pass", False):
        verdict = "uninformative (planted check P1 failed)"
    elif passed:
        verdict = "passed this test"
    else:
        verdict = "failed this test"
        if out["lz"]["wilcoxon_p_less"] < 0.05:
            out["sub_verdict"] = "LZ falls but only through the spectrum"
        else:
            out["sub_verdict"] = "no entropy drop"
        if h2["wilcoxon_p_greater"] < 0.05:
            out["sub_verdict"] += "; pnLZ moves in the opposite direction"
    out["verdict_ENT"] = verdict
    wide.columns = [f"{a}_L{b}" for a, b in wide.columns]
    wide.to_csv(os.path.join(HERE, "features", "chennu_subject_measures.csv"))
    json.dump(out, open(os.path.join(HERE, "chennu_results.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"planted": planted, "real": real}[sys.argv[1]]()
