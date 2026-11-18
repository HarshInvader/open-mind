"""Finish task #4 after analyse.py main crashed in the descriptive block (NaN EMG).
H1-H4 observed deltas and permutation p-values come from main.log (1000 Freedman-Lane
permutations each); observed deltas are recomputed here as a check. Adds bootstrap CIs,
Holm correction and the descriptives; the arousal model drops epochs with NaN EMG."""
import ast, json, os, re, sys
import numpy as np
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from analyse import load, CV, CONTRASTS, BP, boot_delta, holm, auc

df = load()
logged = {}
for ln in open(os.path.join(HERE, "main.log")):
    m = re.match(r"(H\d) (C\d_\w+) (\{.*\})", ln.strip())
    if m:
        logged[(m.group(1), m.group(2))] = ast.literal_eval(m.group(3))
SPEC = {"H1": (["slope"], "lz"), "H2": (["slope"], "pnlz"), "H3": (["slope"] + BP, "lz"), "H4": (["slope"] + BP, "pnlz")}
rng = np.random.default_rng(0)
tests = []
for c in ("C1_W_vs_N3", "C2_R_vs_N3"):
    cv = CV(df, *CONTRASTS[c])
    for h, (base, add) in SPEC.items():
        r = dict(logged[(h, c)]); r["hyp"], r["contrast"] = h, c
        chk = cv.auc(np.column_stack([cv.d[base].values, cv.d[add].values])) - cv.auc(cv.d[base].values)
        assert abs(chk - r["delta"]) < 1e-9, (h, c, chk, r["delta"])
        r["ci_delta"] = boot_delta(cv, cv.d[base].values, cv.d[add].values, 1000, rng)
        tests.append(r)
adj = holm([t["p"] for t in tests])
res = {"n_subjects": int(df.subject.nunique()), "n_epochs": df.stage.value_counts().to_dict(), "tests": {}, "single": {}}
for t, a in zip(tests, adj):
    t["p_holm"] = float(a); t["verdict"] = "adds" if (a < 0.05 and t["delta"] >= 0.01) else "does not add"
    res["tests"][f"{t['hyp']}_{t['contrast']}"] = t
for c, (pos, neg) in CONTRASTS.items():
    res["single"][c] = {}
    for key, cols in [(m, [m]) for m in ["lz", "pnlz", "slope", "perm_entropy"] + BP] + \
                     [("spectral_baseline", ["slope"] + BP), ("arousal_emg_eog", ["emg", "eog"])]:
        d = df.dropna(subset=cols)
        cv = CV(d, pos, neg)
        res["single"][c][key] = {"cv_auc": cv.auc(cv.d[cols].values),
                                 "n_dropped_nan": int(len(df) - len(d))}
res["rho"] = {m: {"median_within_subject_rho_vs_slope": float(np.median([spearmanr(g[m], g["slope"])[0] for _, g in df.groupby("subject")])),
                  "pooled_rho": float(spearmanr(df[m], df["slope"])[0])} for m in ("lz", "pnlz", "perm_entropy")}
res["planted1"] = json.load(open(os.path.join(HERE, "planted1.json")))
res["planted1b"] = json.load(open(os.path.join(HERE, "planted1b.json")))
res["planted2"] = json.load(open(os.path.join(HERE, "planted2.json")))
json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1)
for k, t in res["tests"].items():
    print(k, round(t["auc_base"], 4), round(t["auc_full"], 4), round(t["delta"], 4), t["ci_delta"], t["p"], round(t["p_holm"], 4), t["verdict"])
print(json.dumps(res["single"], indent=0)); print(res["rho"])
