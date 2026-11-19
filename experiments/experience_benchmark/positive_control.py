"""Arousal positive controls for task #42 (prereg §7 PC1/PC2; amendment 1, C3). No DREAM data is read.

  .venv/bin/python -I experiments/experience_benchmark/positive_control.py [sleepedf|boas|all]

Inputs (fetched by seeded, label-free epoch choice):
  experiments/nonequilibrium/raw/SC4xx1.npz       Sleep-EDF, Fpz-Cz + Pz-Oz, 100 Hz, 30 s epochs (fetch_sleepedf.py)
  experiments/experience_benchmark/raw_boas/*.npz BOAS ds005555, F3 F4 C3 C4 O1 O2, 256 Hz (fetch_boas.py)

Rules (fixed before any feature below was computed):
- Window: the middle 20 s of each 30 s epoch (5-25 s).
- Bad channel: SD < 0.5 uV or > 200 uV, or |x| > 1000 uV in the window (prereg §3.4). A window is dropped
  if < 60% of its channels are good (Sleep-EDF: both channels must be good).
- Native branch, measures.native on the posterior ROI:
    Sleep-EDF: Pz-Oz at 100 Hz, no notch possible, post_hf = 20-40 Hz (prereg table, row 2);
    BOAS: good channels of O1, O2 at 256 Hz, 50 Hz notch, post_hf = 20-45 Hz.
- 100 Hz branch, measures.m100 on lz_slope.features.preprocess of the good channels (BOAS resampled
  256 -> 100 Hz with resample_poly 25/64 first, as in extract.py). Pairwise measures on all good channels
  (Sleep-EDF: 1 pair, tc undefined). Secondary measures included.
- Statistic: within-subject pair AUC (prereg §5), pairs pooled over subjects, oriented by the prereg
  direction with wake (or REM) standing in for "experience". 95% CI from 2,000 subject-bootstrap draws
  (percentile). Secondary measures have no prereg direction: their raw AUC (class 1 > N3) is reported.
- Contrasts: W vs N3 (PC1, and C3 on BOAS) and REM vs N3 (PC2). A subject enters a contrast only if it has
  both classes after exclusion.
- Verdicts: PC1 flags AUC < 0.75 as a possible fault (§7). Arousal-tracking per amendment C3 needs the
  95% lower bound >= 0.85 in BOTH Sleep-EDF and BOAS (wSMI and tc: BOAS only, as Sleep-EDF has one pair).
Outputs: pc_features_<ds>.jsonl (per window), positive_control.json.
"""
import json
import os
import sys
import zlib
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction

import numpy as np
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measures as M  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
SEDF = os.path.join(REPO, "experiments", "nonequilibrium", "raw")
BOAS = os.path.join(HERE, "raw_boas")
DIRECTION = {"post_delta": -1, "post_hf": 1, "exponent": 1, "lz": 1, "pe": 1, "hfd": 1, "wsmi": 1, "tc": -1}
N_BOOT = 2000


def good_channels(x):
    sd = x.std(1)
    return (sd >= 0.5) & (sd <= 200) & (np.abs(x).max(1) <= 1000)


def one_window(job):
    ds, sub, k, stage, x, fs, chans = job
    rng = np.random.default_rng(zlib.crc32(f"{ds}|{sub}|{k}".encode()))
    rec = {"ds": ds, "sub": str(sub), "k": int(k), "stage": str(stage)}
    try:
        a = int(5 * fs); x = np.asarray(x, float)[:, a:a + int(20 * fs)]
        g = good_channels(x)
        rec["n_good"] = int(g.sum())
        if g.mean() < 0.6 or (ds == "sleepedf" and not g.all()):
            rec["dropped"] = "bad channels"; return rec
        if ds == "sleepedf":
            rec.update(M.native(x[1:2], fs, None, hf_hi=40.0))
            x100 = x
        else:
            roi = [i for i, c in enumerate(chans) if c in ("PSG_O1", "PSG_O2") and g[i]]
            if not roi:
                rec["dropped"] = "empty ROI"; return rec
            rec.update(M.native(x[roi], fs, 50.0, hf_hi=45.0))
            fr = Fraction(100, int(round(fs)))
            x100 = resample_poly(x, fr.numerator, fr.denominator, axis=-1)
        xp = M.preprocess(x100[g])
        rec.update(M.m100(xp, xp, rng, True))
    except Exception as e:  # logged, never silently dropped
        rec["dropped"] = f"error {type(e).__name__}: {e}"
    return rec


def jobs(ds):
    if ds == "sleepedf":
        for fn in sorted(os.listdir(SEDF)):
            if fn.endswith(".npz"):
                z = np.load(os.path.join(SEDF, fn), allow_pickle=False)
                for k, (x, st) in enumerate(zip(z["eeg"], z["stage"])):
                    yield ("sleepedf", str(z["subject"]), k, str(st), x, 100.0, ["Fpz-Cz", "Pz-Oz"])
    else:
        for fn in sorted(os.listdir(BOAS)):
            if fn.endswith(".npz"):
                z = np.load(os.path.join(BOAS, fn), allow_pickle=False)
                for k, (x, st) in enumerate(zip(z["eeg"], z["stage"])):
                    yield ("boas", str(z["subject"]), k, str(st), x, float(z["fs"]), list(z["channels"]))


def extract(ds):
    out = os.path.join(HERE, f"pc_features_{ds}.jsonl")
    done = set()
    if os.path.exists(out):
        done = {(r["sub"], r["k"]) for r in map(json.loads, open(out))}
    todo = [j for j in jobs(ds) if (j[1], j[2]) not in done]
    with ProcessPoolExecutor(max_workers=2) as ex, open(out, "a") as f:
        for i, r in enumerate(ex.map(one_window, todo, chunksize=8)):
            f.write(json.dumps(r) + "\n")
            if i % 200 == 0:
                f.flush(); print(ds, i, "/", len(todo), flush=True)
    return [json.loads(l) for l in open(out)]


def pair_auc(v, y, s, subjects):
    num = den = 0.0
    for sb in subjects:
        m = s == sb
        a, b = v[m & (y == 1)], v[m & (y == 0)]
        if len(a) == 0 or len(b) == 0:
            continue
        d = a[:, None] - b[None, :]
        num += (d > 0).sum() + 0.5 * (d == 0).sum(); den += d.size
    return num / den if den else np.nan


def contrast(rows, cls1, measure, sign, rng):
    rr = [r for r in rows if "dropped" not in r and r["stage"] in (cls1, "N3") and np.isfinite(r.get(measure, np.nan))]
    v = np.array([r[measure] for r in rr], float) * sign
    y = np.array([r["stage"] == cls1 for r in rr], int); s = np.array([r["sub"] for r in rr])
    subs = [sb for sb in np.unique(s) if (y[s == sb] == 1).any() and (y[s == sb] == 0).any()]
    if len(subs) < 2:
        return {"auc": None, "n_subjects": len(subs)}
    auc = pair_auc(v, y, s, subs)
    # bootstrap: resample subjects with replacement (a subject drawn twice counts twice)
    idx = {sb: np.flatnonzero(s == sb) for sb in subs}
    boots = []
    for _ in range(N_BOOT):
        draw = rng.choice(len(subs), len(subs), replace=True)
        num = den = 0.0
        for d in draw:
            ii = idx[subs[d]]; a, b = v[ii][y[ii] == 1], v[ii][y[ii] == 0]
            dd = a[:, None] - b[None, :]
            num += (dd > 0).sum() + 0.5 * (dd == 0).sum(); den += dd.size
        boots.append(num / den)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"auc": round(float(auc), 4), "lo95": round(float(lo), 4), "hi95": round(float(hi), 4),
            "n_subjects": len(subs), "n1": int(sum((y == 1) & np.isin(s, subs))), "n0": int(sum((y == 0) & np.isin(s, subs)))}


def summarise(rows, ds):
    rng = np.random.default_rng(zlib.crc32(ds.encode()))
    res = {"n_windows": len(rows), "dropped": {}}
    for r in rows:
        if "dropped" in r:
            key = r["dropped"].split(":")[0]; res["dropped"][key] = res["dropped"].get(key, 0) + 1
    for cls1, name in (("W", "wake_vs_N3"), ("R", "rem_vs_N3")):
        res[name] = {}
        for m in M.PRIMARY:
            res[name][m] = contrast(rows, cls1, m, DIRECTION[m], rng)
        for m in M.SECONDARY:
            res[name][m + " (raw, no direction)"] = contrast(rows, cls1, m, 1, rng)
    return res


def verdict(R):
    out = {}
    for m in M.PRIMARY:
        se = R.get("sleepedf", {}).get("wake_vs_N3", {}).get(m, {})
        bo = R.get("boas", {}).get("wake_vs_N3", {}).get(m, {})
        flag = se.get("auc") is not None and se["auc"] < 0.75 and m not in ("wsmi", "tc")
        ok_se = m in ("wsmi", "tc") or (se.get("lo95") is not None and se["lo95"] >= 0.85)
        ok_bo = bo.get("lo95") is not None and bo["lo95"] >= 0.85
        out[m] = {"pc1_fault_flag": bool(flag), "arousal_tracking": bool(ok_se and ok_bo)}
    out["n_arousal_tracking"] = sum(v["arousal_tracking"] for v in out.values() if isinstance(v, dict))
    return out


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    path = os.path.join(HERE, "positive_control.json")
    R = json.load(open(path)) if os.path.exists(path) else {}
    for ds in (["sleepedf", "boas"] if which == "all" else [which]):
        rows = extract(ds)
        R[ds] = summarise(rows, ds)
        print(ds, json.dumps(R[ds]["wake_vs_N3"], indent=0)[:3000], flush=True)
    R["verdict"] = verdict(R)
    json.dump(R, open(path, "w"), indent=1)
    print(json.dumps(R["verdict"], indent=1))


if __name__ == "__main__":
    main()
