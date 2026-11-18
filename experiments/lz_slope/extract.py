"""Compute measures on real epochs and on one phase-randomised surrogate per epoch.

Reads raw/<rec>.npz, appends rows to features.jsonl (resumable by rec).
Run through the gate:  board/run.sh .venv/bin/python -I experiments/lz_slope/extract.py
"""
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from features import all_measures, phase_surrogate, preprocess, psd  # noqa: E402

OUT = os.path.join(HERE, "features.jsonl")


def done_recs():
    if not os.path.exists(OUT):
        return set()
    return {json.loads(l)["rec"] for l in open(OUT)}


def psd_err(x, s):
    f, p1 = psd(x)
    _, p2 = psd(s)
    m = (f >= 1) & (f <= 40)
    return float(np.median(np.abs(np.log10(p1[:, m]) - np.log10(p2[:, m]))))


def main():
    done = done_recs()
    for fn in sorted(glob.glob(os.path.join(HERE, "raw", "*.npz"))):
        d = np.load(fn)
        rec, subj = str(d["rec"]), str(d["subject"])
        if rec in done:
            continue
        rng = np.random.default_rng(1000 + int(subj))
        rows = []
        for i in range(len(d["stage"])):
            x = preprocess(d["eeg"][i])
            ptp = np.ptp(x, axis=-1)
            sd = x.std(-1)
            clean = bool((ptp.max() <= 500) and (sd.min() >= 1))
            base = {"rec": rec, "subject": subj, "stage": str(d["stage"][i]),
                    "epoch": int(d["epoch"][i]), "clean": clean,
                    "emg": float(np.log(np.mean(d["emg"][i]) + 1e-6)),
                    "eog": float(np.log(np.var(d["eog"][i]) + 1e-6))}
            if not clean:
                rows.append({**base, "kind": "real"})
                continue
            rows.append({**base, "kind": "real", **all_measures(x, rng)})
            s = phase_surrogate(x, rng)
            rows.append({**base, "kind": "surr", "psd_err": psd_err(x, s), **all_measures(s, rng)})
        with open(OUT, "a") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        print(rec, len(rows), flush=True)


if __name__ == "__main__":
    main()
