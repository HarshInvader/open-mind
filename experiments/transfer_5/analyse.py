"""Task #5 redesigned (sealed): where does each measure place REM sleep, using wake-vs-N3 cutoffs frozen on Sleep-EDF?
See docs/prereg/2026-11-23_transfer5_rem_placement.md.

  extract  : features for Sleep-EDF (W, N3, R) and HMC (W, N3, R, plus phase-surrogate R)  -> feats_*.jsonl
  analyse  : the sealed analysis -> results.json
"""
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measures as M  # noqa: E402

SEDF_RAW = os.path.join(HERE, "..", "nonequilibrium", "raw")
HMC_RAW = os.path.join(HERE, "raw_hmc")
N_BOOT = 2000
SEED = 20261123
ELIG_BA = 0.80          # eligibility: frozen cutoff balanced accuracy on HMC W vs N3
SAME_BAND = 0.10        # "places REM like X" if the paired 95% CI of the difference lies inside +-0.10
MIN_REM = 10            # subjects need >= 10 clean REM epochs to enter the REM fraction
MIN_WN = 5              # ... and >= 5 clean W and N3 epochs to enter eligibility
NAMES = M.MEASURES + ["baseline"]


# ------------------------------------------------------------------ extraction
def _one(args):
    path, dataset, stages, surrogate = args
    d = np.load(path, allow_pickle=True)
    keep = np.isin(d["stage"], stages)
    subj = str(d["rec"]) if "rec" in d.files else os.path.basename(path)[:-4]
    rng = np.random.default_rng(int("".join(c for c in subj if c.isdigit()) or 0) + (7 if surrogate else 0))
    return M.epoch_rows(d["eeg"][keep], d["stage"][keep], subj, dataset, rng=rng, surrogate=surrogate)


def extract(which):
    jobs = []
    if which == "sedf_wn":       # Sleep-EDF W and N3 only (cutoff fitting; used by the planted gate before sealing)
        jobs = [(os.path.join(SEDF_RAW, f), "sleepedf", ["W", "N3"], False) for f in sorted(os.listdir(SEDF_RAW))]
    elif which == "sedf_r":      # Sleep-EDF REM (secondary; computed only after sealing)
        jobs = [(os.path.join(SEDF_RAW, f), "sleepedf", ["R"], False) for f in sorted(os.listdir(SEDF_RAW))]
    elif which == "hmc":
        jobs = [(os.path.join(HMC_RAW, f), "hmc", ["W", "N3", "R"], False) for f in sorted(os.listdir(HMC_RAW))]
    elif which == "hmc_surr":
        jobs = [(os.path.join(HMC_RAW, f), "hmc_surr", ["R"], True) for f in sorted(os.listdir(HMC_RAW))]
    out = os.path.join(HERE, f"feats_{which}.jsonl")
    with Pool(3) as pool, open(out, "w") as fh:
        for rows in pool.imap(_one, jobs):
            for r in rows:
                fh.write(json.dumps(r) + "\n")
    print("wrote", out, flush=True)


def load(which):
    return [json.loads(l) for l in open(os.path.join(HERE, f"feats_{which}.jsonl"))]


# ------------------------------------------------------------------ cutoffs
def fit(rows):
    """Per measure: sign and Youden-optimal cutoff on pooled W vs N3 epochs. Baseline: LDA on the
    exponent plus six log relative band powers, standardised on the training data, equal priors."""
    y = np.array([r["stage"] == "W" for r in rows])
    cut = {}
    for m in M.MEASURES:
        x = np.array([r[m] for r in rows])
        sign = 1 if np.median(x[y]) > np.median(x[~y]) else -1
        s = sign * x
        cand = np.unique(np.quantile(s, np.linspace(0.005, 0.995, 400)))
        ba = [0.5 * (np.mean(s[y] >= c) + np.mean(s[~y] < c)) for c in cand]
        cut[m] = dict(sign=sign, thr=float(cand[int(np.argmax(ba))]), train_ba=float(np.max(ba)),
                      prior_sign=M.PRIOR_SIGN[m])
    X = np.array([[r[f] for f in M.BASELINE_FEATS] for r in rows])
    mu, sd = X.mean(0), X.std(0) + 1e-12
    Z = (X - mu) / sd
    m1, m0 = Z[y].mean(0), Z[~y].mean(0)
    S = 0.5 * (np.cov(Z[y].T) + np.cov(Z[~y].T)) + 1e-6 * np.eye(Z.shape[1])
    w = np.linalg.solve(S, m1 - m0)
    b = -0.5 * (m1 + m0) @ w
    sc = Z @ w + b
    cut["baseline"] = dict(mu=mu.tolist(), sd=sd.tolist(), w=w.tolist(), b=float(b),
                           train_ba=float(0.5 * (np.mean(sc[y] >= 0) + np.mean(sc[~y] < 0))))
    return cut


def wake_side(rows, cut, name):
    if name == "baseline":
        c = cut["baseline"]
        X = np.array([[r[f] for f in M.BASELINE_FEATS] for r in rows])
        return ((X - np.array(c["mu"])) / np.array(c["sd"])) @ np.array(c["w"]) + c["b"] >= 0
    c = cut[name]
    return c["sign"] * np.array([r[name] for r in rows]) >= c["thr"]


# ------------------------------------------------------------------ per-subject summaries
def by_subject(rows, cut, stage, min_n):
    """{subject: share of `stage` epochs on the wake side} for every measure, subjects with >= min_n epochs."""
    rs = [r for r in rows if r["stage"] == stage]
    subs = sorted({r["subject"] for r in rs})
    out = {}
    for name in NAMES:
        ws = wake_side(rs, cut, name) if rs else np.array([])
        sj = np.array([r["subject"] for r in rs])
        out[name] = {s: float(ws[sj == s].mean()) for s in subs if np.sum(sj == s) >= min_n}
    return out


def boot_mean(vals, rng):
    v = np.array(vals)
    b = [rng.choice(v, v.size).mean() for _ in range(N_BOOT)]
    return float(v.mean()), [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def ci(x):
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def three_way(c):
    """Equivalence call on a 95% CI of a difference: same / different / inconclusive."""
    if -SAME_BAND < c[0] and c[1] < SAME_BAND:
        return "same"
    if c[0] > SAME_BAND or c[1] < -SAME_BAND:
        return "different"
    return "inconclusive"


def placement(c):
    if c[0] > 0.5:
        return "wake side"
    if c[1] < 0.5:
        return "N3 side"
    return "in between"


def summarise(train, test, test_surr, rng):
    """Normalised REM position per measure: pos = (REM - N3) / (W - N3), where each term is the subject-mean share
    of epochs on the wake side of the frozen cutoff (0 = like N3, 1 = like W). Raw wake fractions depend on each
    measure's accuracy; pos does not (a W/N3 mixture with share m gives pos = m whatever the accuracy).
    All CIs come from one joint subject bootstrap, so differences are paired."""
    cut = fit(train)
    w = by_subject(test, cut, "W", MIN_WN)
    n3 = by_subject(test, cut, "N3", MIN_WN)
    rem = by_subject(test, cut, "R", MIN_REM)
    rem_s = by_subject(test_surr, cut, "R", MIN_REM) if test_surr else None
    subs = sorted(set.intersection(*[set(d[n]) for d in (w, n3, rem) for n in NAMES]))
    if rem_s is not None:
        subs = [s for s in subs if all(s in rem_s[n] for n in NAMES)]
    S = len(subs)
    A = {n: np.array([[w[n][s], n3[n][s], rem[n][s]] for s in subs]) for n in NAMES}
    As = {n: np.array([rem_s[n][s] for s in subs]) for n in NAMES} if rem_s is not None else None
    idx = [rng.integers(0, S, S) for _ in range(N_BOOT)] if S else []

    def pos(a, i=None, rem_col=None):
        a = a if i is None else a[i]
        W, N, R = a[:, 0].mean(), a[:, 1].mean(), (a[:, 2] if rem_col is None else rem_col).mean()
        return (R - N) / (W - N) if W - N > 1e-9 else np.nan

    res = {"cutoffs": cut, "n_subjects": S, "measures": {}}
    bpos = {n: np.array([pos(A[n], i) for i in idx]) for n in NAMES}
    for n in NAMES:
        allsub = sorted(set(w[n]) & set(n3[n]))
        ba = float(np.mean([0.5 * (w[n][s] + 1 - n3[n][s]) for s in allsub])) if allsub else float("nan")
        viable = cut[n]["train_ba"] >= ELIG_BA
        r = dict(train_ba=cut[n]["train_ba"], test_ba=ba, n_subjects_ba=len(allsub), viable_in_dataset=bool(viable),
                 eligible=bool(viable and ba >= ELIG_BA))
        if n != "baseline":
            r["fitted_sign"], r["prior_sign"] = cut[n]["sign"], cut[n]["prior_sign"]
            r["sign_mismatch"] = cut[n]["sign"] != cut[n]["prior_sign"]
        if S:
            r["wake_frac_W"], r["wake_frac_N3"], r["wake_frac_REM"] = [float(v) for v in A[n].mean(0)]
            r["rem_position"], r["rem_position_ci"] = float(pos(A[n])), ci(bpos[n])
            r["placement"] = placement(r["rem_position_ci"])
            if As is not None:
                d = np.array([pos(A[n], i) - pos(A[n], i, As[n][i]) for i in idx])
                r["surr_rem_position"] = float(pos(A[n], None, As[n]))
                r["surr_diff"], r["surr_diff_ci"] = float(r["rem_position"] - r["surr_rem_position"]), ci(d)
                r["surrogate"] = three_way(r["surr_diff_ci"])
                r["spectral"] = r["surrogate"] == "same"
        res["measures"][n] = r
    # Comparator: the baseline if it is eligible, else the exponent if eligible, else none (rule 4).
    comp = "baseline" if res["measures"]["baseline"]["eligible"] else (
        "exponent" if res["measures"]["exponent"]["eligible"] else None)
    res["comparator"] = comp
    for n in M.MEASURES:
        if comp and n != comp and S:
            d = bpos[n] - bpos[comp]
            r = res["measures"][n]
            r["vs_comparator_diff"] = float(r["rem_position"] - res["measures"][comp]["rem_position"])
            r["vs_comparator_ci"] = ci(d)
            r["vs_comparator"] = three_way(r["vs_comparator_ci"])
    return res


def verdict(res):
    ms = res["measures"]
    viable = [m for m in M.MEASURES if ms[m]["viable_in_dataset"]]
    el = [m for m in viable if ms[m]["eligible"]]
    if len(el) < 3:
        return f"killed: only {len(el)} of {len(viable)} in-dataset-viable measures transfer from Sleep-EDF to HMC (hardware-bound)"
    comp = res["comparator"]
    if comp is None:
        return "killed: neither the spectral baseline nor the exponent transfers to HMC"
    others = [m for m in el if m != comp]
    calls = {m: ms[m]["vs_comparator"] for m in others}
    if any(c == "different" for c in calls.values()):
        return f"measures disagree on REM (vs {comp}): " + ", ".join(
            f"{m} ({ms[m]['placement']}, surrogate {ms[m].get('surrogate')})" for m, c in calls.items() if c == "different")
    if all(c == "same" for c in calls.values()):
        return f"one axis, spectral: every eligible measure places REM where the {comp} does"
    return f"inconclusive: no eligible measure differs from the {comp}, but " + ", ".join(
        m for m, c in calls.items() if c == "inconclusive") + " cannot be called the same"


def main():
    rng = np.random.default_rng(SEED)
    train = load("sedf_wn")
    test = load("hmc")
    surr = load("hmc_surr")
    res = {"primary": summarise(train, test, surr, rng)}
    res["primary"]["verdict"] = verdict(res["primary"])
    res["primary"]["n_epochs"] = {"train": len(train), "test": len(test), "surr": len(surr)}
    # Secondary: Sleep-EDF REM with its own (in-sample) cutoffs.
    sedf = train + load("sedf_r")
    res["secondary_sleepedf_rem"] = summarise(train, sedf, None, rng)
    p = os.path.join(HERE, "ds005620_feats.jsonl")
    if os.path.exists(p):   # Secondary replication on propofol (awake EC vs sed2); see extract_ds.py
        ds = [json.loads(l) for l in open(p)]
        cut = res["primary"]["cutoffs"]
        rep = {}
        for name in NAMES:
            o = {}
            for st in ("awake", "sed2"):
                v = by_subject(ds, cut, st, 1)[name]
                if v:
                    o[st] = boot_mean(list(v.values()), rng) + (len(v),)
            rep[name] = o
        el = [m for m in M.MEASURES if res["primary"]["measures"][m]["eligible"]
              and "sed2" in rep[m] and "rem_position" in res["primary"]["measures"][m]]
        if len(el) >= 3:
            from scipy.stats import spearmanr
            rho = spearmanr([res["primary"]["measures"][m]["rem_position"] for m in el],
                            [rep[m]["sed2"][0] for m in el])
            rep["ranking_spearman"] = dict(rho=float(rho.statistic), p=float(rho.pvalue), measures=el)
        res["secondary_ds005620"] = rep
    json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    P = res["primary"]
    print("VERDICT:", P["verdict"], "| comparator:", P["comparator"], "| subjects:", P["n_subjects"])
    for name in NAMES:
        r = P["measures"][name]
        print(f"{name:17s} trainBA {r['train_ba']:.3f} testBA {r['test_ba']:.3f} elig {r['eligible']!s:5s} "
              f"REMpos {r.get('rem_position', float('nan')):+.3f} {r.get('rem_position_ci')} {r.get('placement')} "
              f"surr {r.get('surrogate')} vs_comp {r.get('vs_comparator')} {r.get('vs_comparator_ci')} "
              f"sign_mismatch {r.get('sign_mismatch')}")

if __name__ == "__main__":
    if sys.argv[1] == "extract":
        extract(sys.argv[2])
    else:
        main()
