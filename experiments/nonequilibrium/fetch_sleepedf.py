"""Copy of experiments/lz_slope/fetch.py (same seeded epoch selection), writing to this folder. Only change: this line.

For each subject (first available night), downloads the hypnogram (a few KB)
and the PSG header, picks up to N_PER_STAGE epochs per stage (W within the
sleep period, N3 = R&K stages 3+4, REM) with a fixed seed, and fetches only
those 30-s data records (18 KB each). Saves raw/<rec>.npz with EEG Fpz-Cz,
Pz-Oz, EOG (100 Hz) and submental EMG envelope (1 Hz), in physical units.
Resumable: skips subjects already saved. Untrusted data: only parsed, never executed.

Usage: .venv/bin/python -I experiments/lz_slope/fetch.py [max_subjects]
"""
import http.client
import json
import os
import re
import sys
import tempfile
import time
import urllib.request

import mne
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
HOST = "physionet-open.s3.amazonaws.com"
BASE = "/sleep-edfx/1.0.0/sleep-cassette/"
INDEX = "https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/"
N_PER_STAGE = 40
WAKE_MARGIN = 60          # epochs (30 min) either side of the sleep period
STAGE_MAP = {"Sleep stage W": "W", "Sleep stage 1": "N1", "Sleep stage 2": "N2",
             "Sleep stage 3": "N3", "Sleep stage 4": "N3", "Sleep stage R": "R"}
KEEP = ["EEG Fpz-Cz", "EEG Pz-Oz", "EOG horizontal", "EMG submental"]

os.makedirs(RAW, exist_ok=True)
_conn = None


def get_range(path, start, end):
    global _conn
    for attempt in range(5):
        try:
            if _conn is None:
                _conn = http.client.HTTPSConnection(HOST, timeout=60)
            _conn.request("GET", path, headers={"Range": f"bytes={start}-{end}"})
            r = _conn.getresponse()
            data = r.read()
            if r.status in (200, 206) and len(data) == end - start + 1:
                return data
            raise IOError(f"status {r.status} len {len(data)}")
        except Exception as e:  # reconnect and retry
            _conn = None
            time.sleep(2 * (attempt + 1))
            err = e
    raise err


def parse_header(b):
    ns = int(b[252:256])
    h = {"start": b[168:184].decode("ascii"), "hdr_bytes": int(b[184:192]),
         "n_rec": int(b[236:244]), "rec_dur": float(b[244:252]), "ns": ns}
    off = 256

    def field(width):
        nonlocal off
        vals = [b[off + i * width: off + (i + 1) * width].decode("ascii", "replace").strip() for i in range(ns)]
        off += width * ns
        return vals
    h["labels"] = field(16); field(80); field(8)
    h["pmin"] = list(map(float, field(8))); h["pmax"] = list(map(float, field(8)))
    h["dmin"] = list(map(float, field(8))); h["dmax"] = list(map(float, field(8)))
    field(80)
    h["spr"] = list(map(int, field(8)))
    return h


def main(max_subjects=None):
    # Amendment 2026-11-18 (before any outcome was computed): the HTML index and
    # SHA256SUMS list only 102 of 153 cassette nights. Take PSGs from RECORDS and
    # find each hypnogram by probing the S3 key for suffix letters A-Z.
    recs_txt = urllib.request.urlopen(INDEX.replace("sleep-cassette/", "RECORDS"), timeout=60).read().decode()
    psgs = sorted(set(re.findall(r"(SC4\d{3}[A-Z]0)-PSG\.edf", recs_txt)))
    hyps = {}

    def find_hyp(rec, P="E"):
        global _conn
        for L in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            for attempt in range(3):
                try:
                    if _conn is None:
                        _conn = http.client.HTTPSConnection(HOST, timeout=60)
                    _conn.request("HEAD", f"{BASE}{rec}{P}{L}-Hypnogram.edf")
                    r = _conn.getresponse(); r.read()
                    break
                except Exception:
                    _conn = None; time.sleep(2)
            if r.status == 200:
                return f"{rec}{P}{L}"
        return None
    # first available night per subject
    first = {}
    for p in psgs:
        subj = p[3:5]
        first.setdefault(subj, p)
    subjects = sorted(first)
    if max_subjects:
        subjects = subjects[:int(max_subjects)]
    log = []
    for subj in subjects:
        rec = first[subj][:6]
        out = os.path.join(RAW, rec + ".npz")
        if os.path.exists(out):
            continue
        hyp = find_hyp(rec, first[subj][6])
        if hyp is None:
            log.append({"rec": rec, "skip": "no hypnogram"}); continue
        with tempfile.TemporaryDirectory() as d:
            hp = os.path.join(d, "h.edf")
            with urllib.request.urlopen(f"https://{HOST}{BASE}{hyp}-Hypnogram.edf", timeout=60) as r:
                open(hp, "wb").write(r.read())
            ann = mne.read_annotations(hp)
            hyp_start = open(hp, "rb").read(256)[168:184].decode("ascii")
        b = get_range(BASE + first[subj] + "-PSG.edf", 0, 4095)
        h = parse_header(b)
        kk = int(round(h["rec_dur"] / 30.0))      # 30-s epochs per data record (1 or 2)
        assert kk * 30.0 == h["rec_dur"], h["rec_dur"]
        n_ep = h["n_rec"] * kk
        if h["start"] != hyp_start:
            log.append({"rec": rec, "skip": f"start mismatch {h['start']} vs {hyp_start}"}); continue
        lab = np.array(["?"] * n_ep, dtype=object)
        for on, du, de in zip(ann.onset, ann.duration, ann.description):
            s = STAGE_MAP.get(de, "?")
            i0, n = int(round(on / 30)), int(round(du / 30))
            lab[i0:min(i0 + n, n_ep)] = s
        sleep = np.flatnonzero(np.isin(lab, ["N1", "N2", "N3", "R"]))
        lo, hi = max(sleep[0] - WAKE_MARGIN, 0), min(sleep[-1] + WAKE_MARGIN, n_ep - 1)
        rng = np.random.default_rng(int(subj))
        pick = {}
        for st in ["W", "N3", "R"]:
            cand = np.flatnonzero(lab == st)
            if st == "W":
                cand = cand[(cand >= lo) & (cand <= hi)]
            pick[st] = np.sort(rng.choice(cand, min(N_PER_STAGE, len(cand)), replace=False)) if len(cand) else np.array([], int)
        spr = h["spr"]
        rec_bytes = 2 * sum(spr)
        idx = {k: h["labels"].index(k) for k in KEEP}
        offs = np.concatenate([[0], np.cumsum(spr)])
        data = {k: [] for k in KEEP}
        stages, epochs = [], []
        for st in ["W", "N3", "R"]:
            for e in pick[st]:
                st0 = h["hdr_bytes"] + (int(e) // kk) * rec_bytes
                sub = int(e) % kk
                raw = np.frombuffer(get_range(BASE + first[subj] + "-PSG.edf", st0, st0 + rec_bytes - 1), "<i2")
                for k in KEEP:
                    i = idx[k]
                    n30 = spr[i] // kk
                    dig = raw[offs[i] + sub * n30: offs[i] + (sub + 1) * n30].astype(np.float64)
                    g = (h["pmax"][i] - h["pmin"][i]) / (h["dmax"][i] - h["dmin"][i])
                    data[k].append(((dig - h["dmin"][i]) * g + h["pmin"][i]).astype(np.float32))
                stages.append(st); epochs.append(int(e))
        np.savez_compressed(out, eeg=np.stack([np.array(data["EEG Fpz-Cz"]), np.array(data["EEG Pz-Oz"])], 1),
                            eog=np.array(data["EOG horizontal"]), emg=np.array(data["EMG submental"]),
                            stage=np.array(stages), epoch=np.array(epochs), subject=subj, rec=rec)
        log.append({"rec": rec, "n": {s: int(len(v)) for s, v in pick.items()}})
        print(log[-1], flush=True)
    with open(os.path.join(HERE, "fetch_log.jsonl"), "a") as f:
        for r in log:
            f.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
