"""Engineering check of tailzip.read_tail against a full download of ONE member.

Reads no labels. Also prints the EDF header and per-second signal summaries of the
last 15 s (to place the analysis window away from the alarm), so the window can be
fixed in the pre-registration before any label is joined to EEG.
Output: method_check.json
"""
import json
import os
import sys
import time
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tailzip import member_data_range, parse_edf_header, read_tail  # noqa: E402
from ziprange import _get  # noqa: E402

URL = "https://ndownloader.figshare.com/files/41090870"
NAME = "Tononi Serial Awakenings/Data/PSG/s01_ep01.edf"


def main():
    import csv
    m = [r for r in csv.DictReader(open(os.path.join(HERE, "tononi_members.csv"))) if r["member"] == NAME][0]
    off, csz, usz = int(m["offset"]), int(m["csize"]), int(m["usize"])
    a, b = member_data_range(URL, off, csz)
    full = zlib.decompress(_get(URL, a, b), -15)
    assert len(full) == usz
    h = parse_edf_header(full[:256 * 258])
    rec = int(h["nsamp"].sum()) * 2
    need = 14 * rec
    t0 = time.time()
    pos0, data, taint, fetched = read_tail(URL, off, csz, usz, need)
    dt = time.time() - t0
    ref = np.frombuffer(full[pos0:], np.uint8)
    got = np.frombuffer(data, np.uint8)
    clean = ~taint
    res = dict(usize=usz, csize=csz, fetched_tail=fetched, seconds=round(dt, 1), pos0=pos0,
               n_out=len(data), n_tainted=int(taint.sum()),
               last_tainted_from_end=int(len(data) - np.nonzero(taint)[0].max()) if taint.any() else 0,
               clean_bytes_mismatch=int((ref[clean] != got[clean]).sum()),
               tainted_bytes_actually_wrong=int((ref[taint] != got[taint]).sum()),
               header=dict(ns=h["ns"], nrec=h["nrec"], recdur=h["recdur"], hbytes=h["hbytes"],
                           nsamp=sorted(set(h["nsamp"].tolist())), units=sorted(set(h["units"])),
                           gain_range=[float(h["gain"].min()), float(h["gain"].max())],
                           labels_first_last=[h["labels"][:3], h["labels"][-3:]]))
    # per-second signal summary of the last 15 s (no labels involved)
    ns, n = h["ns"], int(h["nsamp"][0])
    x = np.frombuffer(full[h["hbytes"]:], "<i2").reshape(h["nrec"], ns, n).astype(float)
    x = x * h["gain"][None, :, None] + h["offs"][None, :, None]
    sig = np.concatenate(list(x), axis=1) if False else x.transpose(1, 0, 2).reshape(ns, -1)
    sig = sig - sig[:256].mean(0, keepdims=True)  # average reference, scalp channels
    fs = n / h["recdur"]
    per_s = []
    for s in range(15, 0, -1):
        seg = sig[:256, -int(s * fs): -int((s - 1) * fs) or None]
        per_s.append(dict(t=-s, median_sd_uV=round(float(np.median(seg.std(1))), 2),
                          p95_ptp_uV=round(float(np.percentile(seg.max(1) - seg.min(1), 95)), 1)))
    res["last15s"] = per_s
    res["ch257_sd"] = float(x[:, 256].std())
    json.dump(res, open(os.path.join(HERE, "method_check.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
