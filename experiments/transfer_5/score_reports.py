"""Task #5b (sealed before any labels): do report-confirmed experience awakenings under propofol fall on the N3 side
of the frozen Sleep-EDF exponent cutoff?

Usage:
  .venv/bin/python -I experiments/transfer_5/score_reports.py gate                 # planted/power gate, no labels
  .venv/bin/python -I experiments/transfer_5/score_reports.py classes LABELS.csv   # step 1: distinct class strings only
  .venv/bin/python -I experiments/transfer_5/score_reports.py score LABELS.csv CLASSMAP.json   # step 2

LABELS.csv: the authors' table converted to columns subject, run, class (their class string verbatim).
CLASSMAP.json: {class string: "experience" | "no_experience" | "unarousable" | "exclude"}, written from the output of
step 1 alone (class strings, no subjects or runs), under the sealed mapping rule in the prereg, and committed before
step 2 runs.
Input run map: ds005620_runmap.json (label-free, made by make_runmap.py and committed before sealing).
"""
import csv
import json
import os
import sys

import numpy as np
from scipy.stats import beta, mannwhitneyu

HERE = os.path.dirname(os.path.abspath(__file__))
MIN_EXP = 16          # stop check: fewer than 16 experience awakenings on clean runs -> not testable
ALPHA = 0.05


def cp(k, n):
    lo = 0.0 if k == 0 else beta.ppf(ALPHA / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - ALPHA / 2, k + 1, n - k)
    return float(lo), float(hi)


def call(k, n):
    lo, hi = cp(k, n)
    if lo > 0.5:
        return "N3-like despite report"
    if hi < 0.5:
        return "wake-like with report"
    return "inconclusive"


def runmap():
    d = json.load(open(os.path.join(HERE, "ds005620_runmap.json")))
    return d, {(r["subject"], int(r["run"])): r for r in d["runs"]}


def gate():
    d, rm = runmap()
    runs = d["runs"]
    n3 = np.array([not r["exponent_wake_side"] for r in runs])
    out = {"binomial": {}, "resampled_real_runs": {}}
    for n in (16, 20, 24):
        for p in (0.30, 0.50, 0.68, 0.80):
            ks = np.arange(n + 1)
            from scipy.stats import binom
            w = binom.pmf(ks, n, p)
            calls = [call(k, n) for k in ks]
            out["binomial"][f"n{n}_p{p}"] = {c: round(float(w[[x == c for x in calls]].sum()), 3)
                                             for c in ("N3-like despite report", "inconclusive", "wake-like with report")}
    rng = np.random.default_rng(55)
    for n in (16, 20, 24):
        res = {"N3-like despite report": 0, "inconclusive": 0, "wake-like with report": 0}
        for _ in range(5000):
            pick = rng.choice(len(runs), n, replace=False)
            res[call(int(n3[pick].sum()), n)] += 1
        out["resampled_real_runs"][f"n{n}"] = {k: v / 5000 for k, v in res.items()}
    # planted pass rule (sealed): at p = 0.5 the false "N3-like" rate must be <= 0.05 for every n, and at p = 0.80
    # the "N3-like" rate must be >= 0.80 at n = 24.
    ok = all(out["binomial"][f"n{n}_p0.5"]["N3-like despite report"] <= 0.05 for n in (16, 20, 24))
    ok &= out["binomial"]["n24_p0.8"]["N3-like despite report"] >= 0.80
    out["gate_pass"] = bool(ok)
    json.dump(out, open(os.path.join(HERE, "reports_gate.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


def read_labels(path):
    lab = []
    for r in csv.DictReader(open(path)):
        sub = r["subject"].strip()
        sub = sub if sub.startswith("sub-") else "sub-" + sub
        lab.append(dict(subject=sub, run=int(str(r["run"]).strip()), cls=r["class"].strip()))
    return lab


def classes(path):
    print(json.dumps(sorted({r["cls"] for r in read_labels(path)}), indent=1))


def score(path, classmap_path):
    d, rm = runmap()
    cmap = json.load(open(classmap_path))
    lab = read_labels(path)
    res = {"n_label_rows": len(lab)}
    stop = []
    missing_cls = sorted({r["cls"] for r in lab} - set(cmap))
    if missing_cls:
        stop.append(f"class strings not in CLASSMAP: {missing_cls}")
    assert set(cmap.values()) <= {"experience", "no_experience", "unarousable", "exclude"}, cmap
    keys = [(r["subject"], r["run"]) for r in lab]
    dups = sorted({k for k in keys if keys.count(k) > 1})
    if dups:
        stop.append(f"duplicate (subject, run) rows: {dups}")
    unknown = [k for k in keys if k[0] not in d["available_sed2"] and k[0] != "sub-1037"
               or (k[0] in d["available_sed2"] and k[1] not in d["available_sed2"][k[0]])]
    if unknown:
        stop.append(f"not mappable: (subject, run) not among release sed2 files: {unknown}")
    if stop:
        res["verdict"] = "STOP: " + " | ".join(stop)
        json.dump(res, open(os.path.join(HERE, "reports_result.json"), "w"), indent=1)
        print("VERDICT:", res["verdict"]); return
    rows, unclean, excluded = [], [], []
    for r in lab:
        rep = cmap[r["cls"]]
        key = (r["subject"], r["run"])
        if rep == "exclude":
            excluded.append(dict(subject=key[0], run=key[1], cls=r["cls"]))
        elif key in rm:
            rows.append(dict(rm[key], report=rep))
        else:   # sub-1037 (excluded from the release analysis) or a run that failed the amplitude check
            unclean.append(dict(subject=key[0], run=key[1], report=rep))
    exp = [r for r in rows if r["report"] == "experience"]
    res.update(n_matched_clean=len(rows), unclean_or_excluded_subject=unclean, excluded_class=excluded,
               n_experience_clean=len(exp))
    if len(exp) < MIN_EXP:
        res["verdict"] = f"STOP: only {len(exp)} experience awakenings on clean runs (< {MIN_EXP}); not testable"
    else:
        for m in ("exponent", "baseline"):
            k = sum(not r[f"{m}_wake_side"] for r in exp)
            res[m] = dict(k_n3_side=k, n=len(exp), frac=k / len(exp), ci=cp(k, len(exp)), call=call(k, len(exp)))
        res["verdict"] = res["exponent"]["call"]
        # secondary, descriptive: other classes, and exponent values experience vs unarousable
        for cls in ("no_experience", "unarousable"):
            g = [r for r in rows if r["report"] == cls]
            res[f"secondary_{cls}"] = dict(n=len(g), k_n3_side=sum(not r["exponent_wake_side"] for r in g))
        un = [r["exponent"] for r in rows if r["report"] == "unarousable"]
        if len(un) >= 5:
            u = mannwhitneyu([r["exponent"] for r in exp], un)
            res["secondary_exp_vs_unarousable"] = dict(U=float(u.statistic), p=float(u.pvalue),
                                                      median_exp=float(np.median([r["exponent"] for r in exp])),
                                                      median_unarousable=float(np.median(un)))
    json.dump(res, open(os.path.join(HERE, "reports_result.json"), "w"), indent=1)
    print("VERDICT:", res["verdict"])
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    {"gate": lambda: gate(), "classes": lambda: classes(sys.argv[2]),
     "score": lambda: score(sys.argv[2], sys.argv[3])}[sys.argv[1]]()
