"""Task #9 main run: known-Phi networks -> time series -> proxies. Resumable.

Writes one JSON line per network to out/networks.jsonl; skips finished ids.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import phi_lib as L

FAMILIES = ["FF", "DISC", "DENSE", "SPARSE", "RING"]
BETAS = [0.3, 0.6, 1.0, 2.0, 4.0]
REPS = 3
T = 20_000
SEED = 2026

os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
path = os.path.join(HERE, "out", "networks.jsonl")
done = set()
if os.path.exists(path):
    for line in open(path):
        done.add(json.loads(line)["id"])

jobs = [(f, b, r) for f in FAMILIES for b in BETAS for r in range(REPS)]
for k, (fam, beta, rep) in enumerate(jobs):
    nid = f"{fam}_b{beta}_r{rep}"
    if nid in done:
        continue
    t0 = time.time()
    rng = np.random.default_rng([SEED, k])
    W = L.make_W(fam, rng)
    h = rng.normal(0, 0.3, L.N)
    tpm = L.tpm_from_W(W, h, beta)
    cm = (W != 0).astype(int)
    pi = L.stationary(tpm)
    phis = L.phi_by_state(tpm, cm, pi)
    truth = L.weighted_mean(phis, pi)
    x = L.simulate(tpm, T, rng)
    rec = {
        "id": nid, "family": fam, "beta": beta, "rep": rep,
        "structural_zero": fam in ("FF", "DISC"),
        "true_phi": truth,
        "true_phi_max": float(np.nanmax(phis)),
        "frac_states_phi_pos": float(np.nansum((phis > 0) * pi) / np.nansum(pi * ~np.isnan(phis))),
        "mean_activity": float(x.mean()),
    }
    rec["C0"] = L.all_proxies(x.astype(float), x, rng)
    eeg = L.observe_eeg(x, rng)
    rec["C1"] = L.all_proxies(eeg, L.binarize(eeg), rng)
    rec["sec"] = round(time.time() - t0, 1)
    with open(path, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(nid, f"phi={truth:.4f}", f"{rec['sec']}s", flush=True)
print("done", len(jobs))
