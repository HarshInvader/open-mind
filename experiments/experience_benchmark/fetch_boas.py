"""Fetch the BOAS (OpenNeuro ds005555, CC0) epochs for the arousal positive control (amendment 1, C3).

Network only, no analysis. Rules fixed before any BOAS EEG was read:
- Subjects: participants.tsv sorted by numeric sub-N; the first night per person (`pid`) is kept;
  the first 30 distinct persons are used.
- Stages from `stage_hum` (human consensus; 0 W, 1 N1, 2 N2, 3 N3, 4 REM) in the PSG events file.
- Epoch choice copies experiments/nonequilibrium/fetch_sleepedf.py: up to 40 epochs per stage
  (W within 60 epochs of the sleep period, N3, REM), numpy default_rng(subject number).
- Only the EDF data records covering each chosen 30 s epoch are fetched (HTTP range reads).
- Saved: raw_boas/<sub>.npz with the 6 PSG EEG channels (F3 F4 C3 C4 O1 O2, M1 reference) at 256 Hz, in uV.
Untrusted data: only parsed, never executed.

  .venv/bin/python -I experiments/experience_benchmark/fetch_boas.py
"""
import http.client
import io
import json
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw_boas")
HOST = "s3.amazonaws.com"
BASE = "/openneuro.org/ds005555/"
UA = {"User-Agent": "open-research-site/1.0"}
N_SUBJ, N_PER_STAGE, WAKE_MARGIN = 30, 40, 60
EEG = ["PSG_F3", "PSG_F4", "PSG_C3", "PSG_C4", "PSG_O1", "PSG_O2"]
CODES = {0: "W", 1: "N1", 2: "N2", 3: "N3", 4: "R"}
_conn = None


def get(path, rng_bytes=None):
    global _conn
    err = None
    for attempt in range(5):
        try:
            if _conn is None:
                _conn = http.client.HTTPSConnection(HOST, timeout=60)
            h = dict(UA)
            if rng_bytes:
                h["Range"] = f"bytes={rng_bytes[0]}-{rng_bytes[1]}"
            _conn.request("GET", path, headers=h)
            r = _conn.getresponse(); data = r.read()
            if r.status in (200, 206) and (not rng_bytes or len(data) == rng_bytes[1] - rng_bytes[0] + 1):
                return data
            raise IOError(f"status {r.status} len {len(data)}")
        except Exception as e:
            _conn = None; err = e; time.sleep(2 * (attempt + 1))
    raise err


def parse_header(b):
    ns = int(b[252:256])
    h = {"hdr_bytes": int(b[184:192]), "n_rec": int(b[236:244]), "rec_dur": float(b[244:252]), "ns": ns}
    off = 256

    def field(width):
        nonlocal off
        v = [b[off + i * width: off + (i + 1) * width].decode("ascii", "replace").strip() for i in range(ns)]
        off += width * ns
        return v
    h["labels"] = field(16); field(80); h["units"] = field(8)
    h["pmin"] = list(map(float, field(8))); h["pmax"] = list(map(float, field(8)))
    h["dmin"] = list(map(float, field(8))); h["dmax"] = list(map(float, field(8)))
    field(80); h["spr"] = list(map(int, field(8)))
    return h


def main():
    os.makedirs(RAW, exist_ok=True)
    rows = [l.rstrip("\r").split("\t") for l in get(BASE + "participants.tsv").decode().strip().split("\n")]
    hd = rows[0]; rows = [dict(zip(hd, r)) for r in rows[1:]]
    rows.sort(key=lambda r: int(r["participant_id"].split("-")[1]))
    chosen, seen = [], set()
    for r in rows:
        if r["pid"] not in seen:
            seen.add(r["pid"]); chosen.append(r["participant_id"])
        if len(chosen) == N_SUBJ:
            break
    log = []
    for sub in chosen:
        out = os.path.join(RAW, sub + ".npz")
        if os.path.exists(out):
            continue
        stem = f"{BASE}{sub}/eeg/{sub}_task-Sleep_acq-psg"
        ev = [l.rstrip("\r") for l in get(stem + "_events.tsv").decode().strip().split("\n")]
        evh = ev[0].split("\t"); ev = [dict(zip(evh, l.split("\t"))) for l in ev[1:]]
        lab = np.array([CODES.get(int(float(e["stage_hum"])), "?") if e["stage_hum"] not in ("n/a", "") else "?" for e in ev], dtype=object)
        beg = np.array([int(e["begsample"]) - 1 for e in ev])          # 0-based first sample of each epoch
        hb = get(stem + "_eeg.edf", (0, 255))
        hb = get(stem + "_eeg.edf", (0, int(hb[184:192]) - 1))
        h = parse_header(hb)
        idx = [h["labels"].index(k) for k in EEG]
        fs = h["spr"][idx[0]] / h["rec_dur"]
        assert all(h["spr"][i] == h["spr"][idx[0]] for i in idx) and abs(fs - 256) < 1e-6, (h["spr"], h["rec_dur"])
        assert all(h["units"][i].lower() in ("uv", "µv") for i in idx), h["units"]
        spr = h["spr"]; rec_bytes = 2 * sum(spr); offs = np.concatenate([[0], np.cumsum(spr)])
        sleep = np.flatnonzero(np.isin(lab, ["N1", "N2", "N3", "R"]))
        if len(sleep) == 0:
            log.append({"sub": sub, "skip": "no sleep"}); continue
        lo, hi = max(sleep[0] - WAKE_MARGIN, 0), min(sleep[-1] + WAKE_MARGIN, len(lab) - 1)
        rng = np.random.default_rng(int(sub.split("-")[1]))
        pick = {}
        for st in ["W", "N3", "R"]:
            cand = np.flatnonzero(lab == st)
            if st == "W":
                cand = cand[(cand >= lo) & (cand <= hi)]
            pick[st] = np.sort(rng.choice(cand, min(N_PER_STAGE, len(cand)), replace=False)) if len(cand) else np.array([], int)
        n30 = int(round(30 * fs)); data, stages, epochs = [], [], []
        for st in ["W", "N3", "R"]:
            for e in pick[st]:
                s0 = beg[e]; s1 = s0 + n30
                r0, r1 = s0 // spr[idx[0]], (s1 - 1) // spr[idx[0]]
                if r1 >= h["n_rec"]:
                    continue
                raw = np.frombuffer(get(stem + "_eeg.edf", (h["hdr_bytes"] + r0 * rec_bytes,
                                                            h["hdr_bytes"] + (r1 + 1) * rec_bytes - 1)), "<i2")
                raw = raw.reshape(r1 - r0 + 1, sum(spr))
                chans = []
                for i in idx:
                    dig = raw[:, offs[i]:offs[i + 1]].reshape(-1).astype(np.float64)
                    g = (h["pmax"][i] - h["pmin"][i]) / (h["dmax"][i] - h["dmin"][i])
                    phys = (dig - h["dmin"][i]) * g + h["pmin"][i]
                    a = s0 - r0 * spr[i]
                    chans.append(phys[a:a + n30])
                data.append(np.array(chans, np.float32)); stages.append(st); epochs.append(int(e))
        np.savez_compressed(out, eeg=np.stack(data), stage=np.array(stages), epoch=np.array(epochs),
                            subject=sub, fs=fs, channels=np.array(EEG))
        log.append({"sub": sub, "n": {s: int((np.array(stages) == s).sum()) for s in pick}})
        print(log[-1], flush=True)
    with open(os.path.join(HERE, "fetch_boas_log.jsonl"), "a") as f:
        for r in log:
            f.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()
