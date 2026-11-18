"""Fetch DREAM N2 (and REM, descriptive) awakenings and save per-channel PSDs. Labels are NOT read here.

Prereg: docs/prereg/2026-11-18_theory_iit_posterior_dream.md (sections 2-4).
Run: board/run.sh .venv/bin/python -I experiments/theory_tests/dream_features.py
Output: experiments/theory_tests/features/dream_psd.npz  (+ dream_fetch_log.jsonl, resumable)
Raw EDFs are written to raw/dream/, read, then deleted.
"""
import json
import os
import sys

import mne
import numpy as np
import pandas as pd
from scipy.signal import detrend, welch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ziprange import RemoteZip  # noqa: E402

mne.set_log_level("ERROR")
SETS = {
    "zhang": dict(url="https://ndownloader.figshare.com/files/39504757",
                  prefix="Zhang & Wamsley 2019/Data/PSG/", records="raw/meta/zhang_Records.csv"),
    "youngadults": dict(url="https://ndownloader.figshare.com/files/39673915",
                        prefix="Dream_YoungAdults/Data/PSG/", records="raw/meta/ya_Records.csv"),
}
# 17 shared scalp channels (10-10 names; YoungAdults T3/T4 map to T7/T8)
SHARED = ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "C3", "Cz", "C4", "P3", "Pz", "P4", "O1", "O2", "T7", "T8"]
FS = 100.0
OUT = os.path.join(HERE, "features")
RAW = os.path.join(HERE, "raw", "dream")
LOG = os.path.join(OUT, "dream_fetch_log.jsonl")


def clean_name(ch):
    c = ch.replace("-REF", "").replace("EEG ", "").strip()
    c = {"T3": "T7", "T4": "T8"}.get(c, c)
    return c[:1].upper() + c[1:].lower() if c.lower() not in ("fp1", "fp2") else c[:2].capitalize() + c[2:]


def features_from_edf(path, dataset):
    raw = mne.io.read_raw_edf(path, preload=True)
    names = {ch: clean_name(ch) for ch in raw.ch_names}
    raw.rename_channels(names)
    have = raw.ch_names
    if dataset == "zhang":
        if not ("A1" in have and "A2" in have):
            return None, "no mastoids"
        ref = raw.get_data(picks=["A1", "A2"]).mean(0)
    missing = [c for c in SHARED if c not in have]
    if missing:
        return None, f"missing {missing}"
    x = raw.get_data(picks=SHARED) * 1e6  # uV
    if dataset == "zhang":
        x = x - ref[None, :] * 1e6
    sf = raw.info["sfreq"]
    n = x.shape[1]
    a, b = n - int(22 * sf), n - int(2 * sf)
    if a < 0:
        return None, "too short"
    x = x[:, a:b]
    x = mne.filter.filter_data(x, sf, None, 30.0, verbose=False)
    x = mne.filter.resample(x, up=FS / sf, verbose=False) if sf != FS else x
    x = detrend(x, axis=-1)
    seg = int(4 * FS)
    psds, n_ok = [], 0
    for k in range(x.shape[1] // seg):
        s = x[:, k * seg:(k + 1) * seg]
        ptp = s.max(1) - s.min(1)
        if (ptp > 500).any() or (s.std(1) < 0.5).any():
            continue
        f, p = welch(s, fs=FS, nperseg=int(2 * FS), noverlap=int(FS), window="hann", axis=-1)
        psds.append(p)
        n_ok += 1
    if n_ok < 3:
        return None, f"only {n_ok} clean segments"
    return (f, np.mean(psds, 0), n_ok), "ok"


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(RAW, exist_ok=True)
    done = {}
    if os.path.exists(LOG):
        for ln in open(LOG):
            r = json.loads(ln)
            done[(r["dataset"], r["file"])] = r
    fetched = 0
    for ds, cfg in SETS.items():
        rec = pd.read_csv(os.path.join(HERE, cfg["records"]))
        # stage filter only (2 = N2); Experience column untouched here
        rec = rec[rec["Last sleep stage"] == 2]
        z = RemoteZip(cfg["url"])
        for fn in rec["Filename"]:
            if (ds, fn) in done:
                continue
            member = cfg["prefix"] + fn
            if member not in z.members:
                r = {"dataset": ds, "file": fn, "status": "not in zip"}
            else:
                try:
                    data = z.read(member)
                except Exception as e:  # noqa: BLE001  (YoungAdults DG05.edf is corrupt in the deposit)
                    with open(LOG, "a") as fh:
                        fh.write(json.dumps({"dataset": ds, "file": fn, "status": f"corrupt member: {e}"}) + "\n")
                    print(ds, fn, "corrupt", flush=True)
                    continue
                fetched += len(data)
                p = os.path.join(RAW, os.path.basename(fn))
                open(p, "wb").write(data)
                try:
                    res, status = features_from_edf(p, ds)
                except Exception as e:  # noqa: BLE001
                    res, status = None, f"error {e}"
                os.remove(p)
                r = {"dataset": ds, "file": fn, "status": status, "bytes": len(data)}
                if res is not None:
                    f, P, n_ok = res
                    np.save(os.path.join(OUT, f"psd_{ds}_{os.path.basename(fn)}.npy"), P.astype(np.float32))
                    r["n_seg"] = n_ok
            with open(LOG, "a") as fh:
                fh.write(json.dumps(r) + "\n")
            print(ds, fn, r["status"], flush=True)
        print(ds, "compressed bytes fetched (this run, incl. other sets):", fetched, flush=True)
    f = np.fft.rfftfreq(int(2 * FS), 1 / FS)
    np.save(os.path.join(OUT, "psd_freqs.npy"), f)
    json.dump(SHARED, open(os.path.join(OUT, "psd_channels.json"), "w"))


if __name__ == "__main__":
    main()
