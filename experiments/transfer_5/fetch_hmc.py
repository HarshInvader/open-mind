"""Fetch a seeded epoch sample from the HMC sleep staging database (PhysioNet, CC BY 4.0, v1.1).

Same selection rule as the Sleep-EDF fetch (experiments/lz_slope/fetch.py): up to 40 epochs each of W (within
30 min of the sleep period), N3 and R, fixed seed per subject. Only those 30-s stretches are range-downloaded.
Derivations: F4-C4 = (F4-M1) - (C4-M1) and C4-O2 = (C4-M1) - (O2-M1), resampled 256 -> 100 Hz (polyphase,
anti-aliased). Saves raw_hmc/<SNxxx>.npz with eeg (n, 2, 3000) in microvolts and stage.
Untrusted data: only parsed, never executed.

Usage: .venv/bin/python -I experiments/transfer_5/fetch_hmc.py [max_subjects]
"""
import http.client
import json
import os
import re
import sys
import time
import urllib.request

import numpy as np
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw_hmc")
HOST = "physionet-open.s3.amazonaws.com"
BASE = "/hmc-sleep-staging/1.1/recordings/"
UA = {"User-Agent": "open-research-site/1.0"}
N_PER_STAGE = 40
WAKE_MARGIN = 60
STAGE_MAP = {"Sleep stage W": "W", "Sleep stage N1": "N1", "Sleep stage N2": "N2", "Sleep stage N3": "N3",
             "Sleep stage R": "R"}
os.makedirs(RAW, exist_ok=True)
_conn = None


def get(path, rng=None):
    global _conn
    err = None
    for attempt in range(5):
        try:
            if _conn is None:
                _conn = http.client.HTTPSConnection(HOST, timeout=60)
            h = dict(UA)
            if rng:
                h["Range"] = f"bytes={rng[0]}-{rng[1]}"
            _conn.request("GET", path, headers=h)
            r = _conn.getresponse()
            data = r.read()
            if r.status in (200, 206) and (rng is None or len(data) == rng[1] - rng[0] + 1):
                return data
            raise IOError(f"status {r.status} len {len(data)}")
        except Exception as e:
            _conn = None
            err = e
            time.sleep(2 * (attempt + 1))
    raise err


def header(b):
    ns = int(b[252:256])
    off = 256

    def field(w):
        nonlocal off
        v = [b[off + i * w: off + (i + 1) * w].decode("ascii", "replace").strip() for i in range(ns)]
        off += w * ns
        return v
    lab = field(16); field(80); dim = field(8)
    pmin = list(map(float, field(8))); pmax = list(map(float, field(8)))
    dmin = list(map(float, field(8))); dmax = list(map(float, field(8)))
    field(80); spr = list(map(int, field(8)))
    return dict(ns=ns, hdr=int(b[184:192]), nrec=int(b[236:244]), dur=float(b[244:252]), labels=lab, dim=dim,
                pmin=pmin, pmax=pmax, dmin=dmin, dmax=dmax, spr=spr)


def main(max_subjects=None):
    recs = sorted(set(re.findall(r"SN\d{3}", urllib.request.urlopen(urllib.request.Request(
        "https://physionet.org/files/hmc-sleep-staging/1.1/RECORDS", headers=UA), timeout=60).read().decode())))
    if max_subjects:
        recs = recs[:int(max_subjects)]
    log = []
    for rec in recs:
        out = os.path.join(RAW, rec + ".npz")
        if os.path.exists(out):
            continue
        try:
            txt = get(BASE + rec + "_sleepscoring.txt").decode("utf-8", "replace")
            h = header(get(BASE + rec + ".edf", (0, 4095)))
            assert h["dur"] == 1.0 and len(set(h["spr"])) == 1, (h["dur"], h["spr"])
            fs = h["spr"][0]
            ch = {l: i for i, l in enumerate(h["labels"])}
            need = ["EEG F4-M1", "EEG C4-M1", "EEG O2-M1"]
            assert all(n in ch for n in need), h["labels"]
            n_ep = h["nrec"] // 30
            lab = np.array(["?"] * n_ep, dtype=object)
            for line in txt.splitlines()[1:]:
                p = [s.strip() for s in line.split(",")]
                if len(p) >= 5 and p[4] in STAGE_MAP:
                    i0 = int(round(float(p[2]) / 30))
                    if 0 <= i0 < n_ep:
                        lab[i0] = STAGE_MAP[p[4]]
            sleep = np.flatnonzero(np.isin(lab, ["N1", "N2", "N3", "R"]))
            lo, hi = max(sleep[0] - WAKE_MARGIN, 0), min(sleep[-1] + WAKE_MARGIN, n_ep - 1)
            rng = np.random.default_rng(int(rec[2:]))
            pick = {}
            for st in ["W", "N3", "R"]:
                cand = np.flatnonzero(lab == st)
                if st == "W":
                    cand = cand[(cand >= lo) & (cand <= hi)]
                pick[st] = np.sort(rng.choice(cand, min(N_PER_STAGE, cand.size), replace=False)) if cand.size else []
            rec_bytes = 2 * sum(h["spr"])
            gain = [(h["pmax"][i] - h["pmin"][i]) / (h["dmax"][i] - h["dmin"][i]) for i in range(h["ns"])]
            scale = [1e3 if h["dim"][i].lower() == "mv" else (1e6 if h["dim"][i].lower() == "v" else 1.0)
                     for i in range(h["ns"])]
            eeg, stages = [], []
            for st, idxs in pick.items():
                for e in idxs:
                    # 2-s margin either side (clipped at the file ends) so resampling edges fall outside the epoch.
                    r0, r1 = max(e * 30 - 2, 0), min((e + 1) * 30 + 2, h["nrec"])
                    b = get(BASE + rec + ".edf", (h["hdr"] + r0 * rec_bytes, h["hdr"] + r1 * rec_bytes - 1))
                    a = np.frombuffer(b, "<i2").reshape(r1 - r0, h["ns"], fs)
                    sig = {}
                    for n in need:
                        i = ch[n]
                        d = a[:, i, :].reshape(-1).astype(float)
                        sig[n] = ((d - h["dmin"][i]) * gain[i] + h["pmin"][i]) * scale[i]
                    x = np.stack([sig["EEG F4-M1"] - sig["EEG C4-M1"], sig["EEG C4-M1"] - sig["EEG O2-M1"]])
                    y = resample_poly(x, 100, fs, axis=-1, padtype="line")
                    k0 = int(round((e * 30 - r0) * 100))
                    eeg.append(y[:, k0:k0 + 3000])
                    stages.append(st)
            np.savez_compressed(out, eeg=np.array(eeg, np.float32), stage=np.array(stages), rec=rec,
                                fs_orig=fs, units=str([h["dim"][ch[n]] for n in need]))
            log.append({"rec": rec, "n": {s: int(np.sum(np.array(stages) == s)) for s in pick}})
        except Exception as ex:  # skipped and listed, per the prereg
            log.append({"rec": rec, "skip": repr(ex)[:200]})
        print(json.dumps(log[-1]), flush=True)
    with open(os.path.join(HERE, "fetch_hmc_log.jsonl"), "a") as fh:
        for r in log:
            fh.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main(*(sys.argv[1:2]))
