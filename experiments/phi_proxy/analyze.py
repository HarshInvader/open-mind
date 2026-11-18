"""Task #9 analysis: pre-registered pass marks (docs/prereg/phi_proxy_recovery.md)."""
import csv
import json
import os
import sys

import numpy as np
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "experiments", "rules"))
from evidence import ledger_rows_write  # noqa: E402

PROXIES = ["phi_wms", "causal_density", "integration", "tse_complexity", "lzc", "phi_plugin"]
BASELINES = ["base_local_pred", "base_mean_corr"]
rng = np.random.default_rng(99)
NB, NP = 2000, 5000

recs = [json.loads(l) for l in open(os.path.join(HERE, "out", "networks.jsonl"))]
n = len(recs)
truth = np.array([r["true_phi"] for r in recs])
szero = np.array([r["structural_zero"] for r in recs])
rec_pos = (~szero) & (truth >= np.median(truth[~szero]))  # top half of recurrent networks


def rho(a, b):
    return spearmanr(a, b).statistic


def auc(score, lab):
    pos, neg = score[lab], score[~lab]
    gt = (pos[:, None] > neg[None, :]).mean()
    eq = (pos[:, None] == neg[None, :]).mean()
    return gt + 0.5 * eq


boot_idx = [rng.integers(0, n, n) for _ in range(NB)]
out = {"n_networks": n, "n_structural_zero": int(szero.sum()), "n_recurrent_top_half": int(rec_pos.sum()),
       "truth_summary": {"min": float(truth.min()), "median": float(np.median(truth)), "max": float(truth.max()),
                         "structural_zero_max": float(truth[szero].max())},
       "conditions": {}}
ledger = []
for cond in ("C1", "C0"):
    vals = {p: np.array([r[cond][p] for r in recs]) for p in PROXIES + BASELINES}
    base_rho = {b: rho(vals[b], truth) for b in BASELINES}
    best_base = max(BASELINES, key=lambda b: base_rho[b])
    res = {}
    for p in PROXIES + BASELINES:
        v = vals[p]
        r0 = rho(v, truth)
        bs = np.array([rho(v[i], truth[i]) for i in boot_idx])
        perm = np.array([rho(v, rng.permutation(truth)) for _ in range(NP if cond == "C1" else 1000)])
        pval = (1 + np.sum(perm >= r0)) / (1 + len(perm))
        lab = rec_pos[szero | rec_pos]
        a = auc(v[szero | rec_pos], lab)
        rr = rho(v[~szero], truth[~szero])
        d = None
        if p in PROXIES:
            bb = vals[best_base]
            diffs = np.array([rho(v[i], truth[i]) - rho(bb[i], truth[i]) for i in boot_idx])
            d = {"vs": best_base, "diff": float(r0 - base_rho[best_base]),
                 "ci": [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))]}
        passed = None
        if p in PROXIES:
            passed = bool(r0 >= 0.6 and np.percentile(bs, 2.5) > 0.3 and a >= 0.8 and d["ci"][0] > 0)
        res[p] = {"rho": float(r0), "rho_ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                  "p_perm": float(pval), "auc_zero_vs_pos": float(a), "rho_recurrent_only": float(rr),
                  "vs_best_baseline": d, "pass": passed}
    # Holm over the 6 proxies (primary condition only is the confirmatory family)
    ps = sorted((res[p]["p_perm"], p) for p in PROXIES)
    for k, (pv, p) in enumerate(ps):
        res[p]["p_holm"] = float(min(1.0, max(pv * (len(ps) - j) for j, (pv, _) in enumerate(ps[:k + 1]))))
    out["conditions"][cond] = {"best_baseline": best_base, "results": res}
    for p in PROXIES:
        r = res[p]
        ledger.append({
            "id": f"phi9_{cond}_{p}", "claim": f"{p} ranks known-phi networks ({'EEG-like' if cond == 'C1' else 'clean'} obs)",
            "area": "phi_proxy", "file": "experiments/phi_proxy/RESULTS.md",
            "statistic": f"spearman rho {r['rho']:.3f}; AUC {r['auc_zero_vs_pos']:.3f}; rho-best_base {r['vs_best_baseline']['diff']:+.3f}",
            "p_value": f"{r['p_perm']:.4g}", "p_source": "permutation", "ci": f"[{r['rho_ci'][0]:.3f}, {r['rho_ci'][1]:.3f}]",
            "n": n, "distinct_subjects": "", "split": "synthetic",
            "mode": "method_check", "family": f"phi_proxy_{cond}", "family_size": len(PROXIES),
            "replicated_independently": "no", "readme_claim": "planted answer gate (M4)", "ground_truth": "synthetic",
            "q_global": "", "q_area": "", "q_hier": "", "q_all": f"{r['p_holm']:.4g}",
            "note": ("PASS" if r["pass"] else "FAIL") + (" (primary)" if cond == "C1" else " (secondary, clean)"),
        })

# Effect of beta: is phi non-monotonic in coupling? (descriptive)
by_beta = {}
for b in sorted({r["beta"] for r in recs}):
    m = np.array([r["beta"] == b for r in recs]) & ~szero
    by_beta[str(b)] = {"true_phi_mean": float(truth[m].mean()),
                       **{p: float(np.mean([recs[i]["C1"][p] for i in np.where(m)[0]])) for p in PROXIES + BASELINES}}
out["by_beta_recurrent"] = by_beta
out["rho_true_phi_vs_beta_recurrent"] = float(rho(np.array([r["beta"] for r in recs])[~szero], truth[~szero]))
json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1)
ledger_rows_write(os.path.join(HERE, "ledger_rows.csv"), ledger)
for cond in ("C1", "C0"):
    print(cond, "best baseline", out["conditions"][cond]["best_baseline"])
    for p, r in out["conditions"][cond]["results"].items():
        print(f"  {p:16s} rho {r['rho']:+.3f} [{r['rho_ci'][0]:+.2f},{r['rho_ci'][1]:+.2f}] AUC {r['auc_zero_vs_pos']:.3f} "
              f"rec-only {r['rho_recurrent_only']:+.3f} p {r['p_perm']:.4f} "
              + (f"d {r['vs_best_baseline']['diff']:+.3f} [{r['vs_best_baseline']['ci'][0]:+.2f},{r['vs_best_baseline']['ci'][1]:+.2f}] PASS={r['pass']}" if r['pass'] is not None else ""))
print(json.dumps(by_beta, indent=0)[:1500])
print(out["truth_summary"], out["n_recurrent_top_half"])
