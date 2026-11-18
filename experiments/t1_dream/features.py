"""Fetch the last 12 s of each Tononi Serial Awakenings EDF and save posterior/frontal ROI signals.

LABEL-BLIND: reads tononi_members.csv (file names, sizes, offsets) only. No report labels.
Raw EDF bytes are held in memory only; nothing raw is written to disk.
Per awakening it saves roi/<file>.npz: post (9 x 1536), front (9 x 1536) at 128 Hz, file time [-12, 0] s,
and the list of good ROI channels. Log: fetch_log.jsonl (resumable; bytes fetched per file).
Run: board/run.sh .venv/bin/python -I experiments/t1_dream/features.py
"""
import csv
import json
import os
import sys
from fractions import Fraction

import numpy as np
from scipy.signal import butter, resample_poly, sosfiltfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tailzip import parse_edf_header, read_tail  # noqa: E402
from ziprange import RemoteZip  # noqa: E402

BUDGET = 0.95e9          # hard cap on bytes fetched by this task
TAIL_S = 12              # seconds read from the end of each file
ROI = {
    "post": ["E98", "E87", "E86", "E101", "E100", "E129", "E152", "E153", "E162"],   # P3, Pz, P4
    "front": ["E35", "E39", "E40", "E22", "E14", "E21", "E3", "E4", "E223"],         # F3, Fz, F4
}
OUT = os.path.join(HERE, "roi")
LOG = os.path.join(HERE, "fetch_log.jsonl")


def scalp_channels():
    """Channels within 90 deg of the vertex (Cz) on the package's own .sfp layout: the average reference set."""
    rows = [l.split() for l in open(os.path.join(HERE, "raw", "HydroCelGSN256v10.sfp"))]
    P = np.array([[float(v) for v in r[1:4]] for r in rows])
    A = np.c_[2 * P, np.ones(len(P))]
    c = np.linalg.lstsq(A, (P ** 2).sum(1), rcond=None)[0][:3]
    V = P - c
    cz = V[-1] / np.linalg.norm(V[-1])
    ang = np.degrees(np.arccos(np.clip((V / np.linalg.norm(V, axis=1, keepdims=True)) @ cz, -1, 1)))
    return [i for i in range(len(P)) if ang[i] <= 90]   # indices 0..256 (256 = Cz, the recording reference)


def process(data_tail, pos0, h, scalp):
    ns, n = h["ns"], int(h["nsamp"][0])
    if not (h["nsamp"] == n).all():
        return None, "unequal sampling"
    fs = n / h["recdur"]
    recb = ns * n * 2
    nrec = (h["usize"] - h["hbytes"]) // recb
    first = nrec - int(round(TAIL_S / h["recdur"]))
    off = h["hbytes"] + first * recb - pos0
    if off < 0:
        return None, "tail too short"
    raw = np.frombuffer(data_tail[off:off + (nrec - first) * recb], "<i2").reshape(nrec - first, ns, n)
    x = raw.transpose(1, 0, 2).reshape(ns, -1).astype(float)
    x = x * h["gain"][:, None] + h["offs"][:, None]
    if h["units"][0].lower() in ("v",):
        x *= 1e6
    sos = butter(4, [0.3, 45.0], btype="band", fs=fs, output="sos")
    xf = sosfiltfilt(sos, x, axis=-1)
    sd = xf.std(1)
    good = (sd >= 0.5) & (sd <= 200)
    good[ns - 1] = True  # Cz reference channel is ~0 by construction
    ref_set = [i for i in scalp if good[i]]
    xf = xf - xf[ref_set].mean(0, keepdims=True)
    fr = Fraction(128, int(round(fs))).limit_denominator(1000)
    out, chans = {}, {}
    names = [f"E{i + 1}" for i in range(ns - 1)] + ["Cz"]
    for roi, lst in ROI.items():
        idx = [names.index(c) for c in lst if good[names.index(c)]]
        chans[roi] = [names[i] for i in idx]
        if len(idx) < 5:
            return None, f"{roi} ROI has {len(idx)} good channels"
        y = resample_poly(xf[idx], fr.numerator, fr.denominator, axis=-1)
        y = y[:, -int(TAIL_S * 128):]
        out[roi] = y.astype(np.float32)
    big = max(float(np.abs(out[r].mean(0)).max()) for r in out)
    if big > 400:
        return None, f"ROI-mean exceeds 400 uV ({big:.0f})"
    return dict(**out, chans=json.dumps(chans), n_ref=len(ref_set), fs=fs), "ok"


def main():
    os.makedirs(OUT, exist_ok=True)
    done, spent = set(), 0
    if os.path.exists(LOG):
        for ln in open(LOG):
            r = json.loads(ln)
            done.add(r["file"])
            spent += r.get("bytes", 0)
    scalp = scalp_channels()
    members = list(csv.DictReader(open(os.path.join(HERE, "tononi_members.csv"))))
    zips = {}
    for m in members:
        if m["file"] in done:
            continue
        if spent > BUDGET:
            print("BUDGET reached, stopping", spent, flush=True)
            break
        url = m["url"]
        if url not in zips:
            zips[url] = RemoteZip(url, size=int(m["zipsize"]))
        z = zips[url]
        rec = dict(file=m["file"])
        try:
            b0 = z.bytes_fetched
            hdr = z.read(m["member"], max_out=257 * 256 + 256, chunk=40 * 1024)
            h = parse_edf_header(hdr)
            h["usize"] = int(m["usize"])
            recb = int(h["nsamp"].sum()) * 2
            pos0, data, taint, fetched = read_tail(url, int(m["offset"]), int(m["csize"]), int(m["usize"]),
                                                   TAIL_S * recb + 65536)
            rec["bytes"] = fetched + (z.bytes_fetched - b0) + 30
            rec["tainted_bytes"] = int(taint.sum())
            last_t = int(np.nonzero(taint)[0].max()) + 1 if taint.any() else 0
            res, status = process(data[last_t:], pos0 + last_t, h, scalp)
            rec["status"] = status
            if res is not None:
                np.savez_compressed(os.path.join(OUT, m["file"].replace(".edf", ".npz")), **res)
                rec["n_ref"] = res["n_ref"]
                rec["fs"] = res["fs"]
        except Exception as e:  # noqa: BLE001
            rec["status"] = f"error {type(e).__name__}: {e}"
            rec.setdefault("bytes", 0)
        spent += rec.get("bytes", 0)
        with open(LOG, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(m["file"], rec["status"], round(spent / 1e6, 1), "MB", flush=True)
    print("total fetched MB", round(spent / 1e6, 1))


if __name__ == "__main__":
    main()
