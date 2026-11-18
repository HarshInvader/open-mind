"""Chennu 2016 propofol: fetch the first 120 s of baseline (level 1) and moderate (level 3) recordings,
compute LZ, pnLZ, spectral exponent, permutation entropy and one-surrogate LZ per 10-s epoch.

Prereg: docs/prereg/2026-11-18_theory_entropic_propofol.md
Run: board/run.sh .venv/bin/python -I experiments/theory_tests/chennu_features.py
Output: features/chennu_epochs.jsonl (resumable). Mode fetch saves the first 120 s as raw/chennu/*.npy; mode compute reads each, saves features, deletes it.

Layout (inferred from member sizes and the dataset paper; .set is MATLAB v7.3 and h5py is not
installable on this Python): 91 channels, 250 Hz, 10-s epochs of 2500 samples, float32,
channel-fastest order (EEGLAB .fdt). Every .fdt size is a multiple of 91*4*2500 bytes.
"""
import json
import os
import sys

import mne
import numpy as np
import scipy.io as sio

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "experiments", "lz_slope"))
from ziprange import RemoteZip  # noqa: E402
from features import (lz, perm_entropy, phase_surrogate, pnlz, preprocess,  # noqa: E402
                      spectral_exponent)

URL = "https://api.repository.cam.ac.uk/server/api/core/bitstreams/e94a6722-da5b-4e53-8673-5e8ec106e0f7/content"
SIZE = 3694326663
NCH, SF, EP, NEP = 91, 250.0, 2500, 12
OUT = os.path.join(HERE, "features", "chennu_epochs.jsonl")
RAWDIR = os.path.join(HERE, "raw", "chennu")
MODE = sys.argv[1] if len(sys.argv) > 1 else "compute"   # fetch (network only) | compute (via board/run.sh)


def main():
    info = sio.loadmat(os.path.join(HERE, "raw", "meta", "chennu_datainfo.mat"), squeeze_me=True)["datainfo"]
    rows = [(str(r[0]), int(r[1])) for r in info if int(r[1]) in (1, 3)]
    done = set()
    if os.path.exists(OUT):
        for ln in open(OUT):
            r = json.loads(ln)
            done.add(r["file"])
    os.makedirs(RAWDIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    z = RemoteZip(URL, SIZE)
    for name, level in rows:
        if name in done:
            continue
        member = f"Sedation-RestingState/{name}.fdt"
        usz = z.members[member][2]
        n_avail = usz // (NCH * 4 * EP)
        nep = min(NEP, n_avail)
        cache = os.path.join(RAWDIR, name.replace(" ", "_") + ".npy")
        if MODE == "fetch":
            if not os.path.exists(cache):
                raw = z.read(member, max_out=nep * NCH * 4 * EP)
                np.save(cache, np.frombuffer(raw, dtype="<f4").reshape(-1, NCH).T)
                print("fetched", name, round(z.bytes_fetched / 1e6, 1), "MB total", flush=True)
            continue
        x = np.load(cache).astype(np.float64)  # (ch, samples)
        x = x - x.mean(0, keepdims=True)                     # average reference
        x = mne.filter.resample(x, up=100.0 / SF, verbose=False)  # anti-aliased, 100 Hz
        subj = name[:2]
        rng = np.random.default_rng(0)
        recs = []
        for k in range(nep):
            e = preprocess(x[:, k * 1000:(k + 1) * 1000])
            ptp = e.max(1) - e.min(1)
            rec = {"file": name, "subject": subj, "level": level, "epoch": k,
                   "bad": bool((ptp > 500).any()), "max_ptp": float(ptp.max())}
            if not rec["bad"]:
                rec.update(lz=lz(e), pnlz=pnlz(e, rng), slope=spectral_exponent(e),
                           perm_entropy=perm_entropy(e), lz_surr=lz(phase_surrogate(e, rng)))
            recs.append(rec)
        os.remove(cache)
        with open(OUT, "a") as fh:
            for r in recs:
                fh.write(json.dumps(r) + "\n")
        print(name, level, nep, "epochs", sum(not r["bad"] for r in recs), "clean",
              "fetched MB", round(z.bytes_fetched / 1e6, 1), flush=True)


if __name__ == "__main__":
    main()
