"""No-report bifurcation: planted kill test (synthetic only; no real EEG is read).

  .venv/bin/python -I experiments/bifurcation/kill_planted.py [n_rep]  -> kill_planted.json

Question: at the real no-report trial counts of Cohen et al. 2024 (Cereb Cortex, doi:10.1093/cercor/bhae415)
and Sergent et al. 2021 (Nat Commun, doi:10.1038/s41467-021-21393-z), can a single-trial two-state test at
fixed stimulus strength tell a bimodal (two-state) score from graded unimodal alternatives?

Pipeline: identical to the T4 P1 pipeline (experiments/our_theory/t4_planted/p1_decidability.py; its fitting
and scoring functions are imported unchanged): per subject, z-score by the low-state reference, remove
within-block trial drift, 5-fold held-out log-likelihood of a mixture (low state N(0,1) fixed) against the
better of a normal and a bounded skew-normal per level; PASS = patient-bootstrap 95% CI lower bound > 0,
beta rises with strength, 0.1 <= beta at the threshold level <= 0.7.

Designs (two near-threshold levels per subject; reference = no-stimulus trials):
  cohen:   40 subjects (25 confirmatory + 15 pilot, both analysed in the paper's exploratory decoding),
           ~135 face trials per SOA per condition (paper: 960 trials per condition; trials per SOA not stated,
           estimated), levels 50 ms (58% seen) and 67 ms (89% seen); reference = mask-only trials (~160).
  sergent: 20 subjects, ~150 trials per level after rejection (paper: 160 per level, 94% kept),
           levels with ~50% and ~85% audibility; reference = noise-alone trials (~150).
Kill rule (coordinator): power < 80% at the separation the data plausibly have kills the test.
Plausible separation: Sergent's report-prediction AUC > 0.75 (250-700 ms) implies d' ~ 0.95; T4's Stockart
iEEG estimate was ~1.2.
"""
import json
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "our_theory", "t4_planted"))
import p1_decidability as T4  # noqa: E402  (fit/score functions reused unchanged)

rng = np.random.default_rng(20261120)
T4.rng = rng
DESIGNS = {"cohen": dict(n_subj=40, n_per=135, n_ref=160, b=(0.58, 0.89)),
           "sergent": dict(n_subj=20, n_per=150, n_ref=150, b=(0.50, 0.85))}


def layout(n_per, n_blocks=8):
    k = np.r_[np.zeros(n_per), np.ones(n_per)].astype(int); rng.shuffle(k)
    blk = np.arange(len(k)) * n_blocks // len(k); idx = np.arange(len(k)) - np.searchsorted(blk, blk)
    return k, blk, idx


def noise(n, kind="normal"):
    if kind == "t5":
        return stats.t.rvs(5, size=n, random_state=rng) / np.sqrt(5 / 3)
    if kind == "skew":
        a = 4; dl = a / np.sqrt(1 + a * a); m = dl * np.sqrt(2 / np.pi)
        return (stats.skewnorm.rvs(a, size=n, random_state=rng) - m) / np.sqrt(1 - m * m)
    return rng.normal(size=n)


def gen_mix(D, d, nk="normal"):
    k, blk, idx = layout(D["n_per"])
    dd = max(0.2, d + rng.normal(0, 0.25))
    b0, b1 = D["b"]
    beta = np.where(k == 0, np.clip(b0 + rng.normal(0, 0.1), .05, .95), np.clip(b1 + rng.normal(0, 0.05), .05, .98))
    hi = rng.random(len(k)) < beta
    late = np.where(hi, dd * np.where(k == 0, 1.0, 1.15) + noise(len(k), nk), noise(len(k), nk))
    return late, noise(D["n_ref"], nk), k, blk, idx


def gen_graded(D, d, kind="normal", drift=0.0):
    """Unimodal: every trial shifted by a graded amount; mean matched to the mixture's mean shift."""
    k, blk, idx = layout(D["n_per"])
    dd = max(0.2, d + rng.normal(0, 0.25)); b0, b1 = D["b"]
    mu = np.where(k == 0, b0 * dd, b1 * dd * 1.15)
    late = mu + noise(len(k), kind) + drift * (idx / idx.max() - 0.5)
    return late, noise(D["n_ref"], kind), k, blk, idx


def gen_accum(D, d, bound=None):
    """Leaky accumulator of noisy evidence, read out at a late time; optional absorbing bound."""
    k, blk, idx = layout(D["n_per"])
    dd = max(0.2, d + rng.normal(0, 0.25)); b0, b1 = D["b"]
    drift = np.where(k == 0, b0, b1 * 1.15) * dd / 10
    x = np.zeros(len(k)); hit = np.zeros(len(k), bool)
    for _ in range(30):
        x = x + drift - 0.05 * x + rng.normal(0, 0.25, len(k))
        if bound is not None:
            hit |= x > bound * dd; x = np.where(hit, bound * dd, x)
    late = (x - x.mean()) / x.std() * 1.0 + np.where(k == 0, b0, b1) * dd
    return late, noise(D["n_ref"]), k, blk, idx


def run(gen, D, n_rep):
    res = []
    for _ in range(n_rep):
        out = [T4.patient(*gen()) for _ in range(D["n_subj"])]
        eff = np.array([o[0] for o in out]); bt = np.array([o[1] for o in out])
        boot = np.array([eff[rng.integers(0, len(eff), len(eff))].mean() for _ in range(2000)])
        lo = np.quantile(boot, 0.025); b0, b1 = bt[:, 0].mean(), bt[:, 1].mean()
        res.append(bool(lo > 0 and b1 > b0 and 0.1 <= b0 <= 0.7))
    return float(np.mean(res))


def scenarios():
    S = []
    for name, D in DESIGNS.items():
        for d in (1.0, 1.5, 2.0, 2.5, 3.0):
            S.append((f"{name} MIX d={d}", name, ("mix", d)))
        S.append((f"{name} MIX d=2.0 t5", name, ("mix_t5", 2.0)))
        for d in (1.0, 2.0):
            S.append((f"{name} NULL graded d={d}", name, ("graded", d)))
        S.append((f"{name} NULL graded-skew d=2.0", name, ("graded_skew", 2.0)))
        S.append((f"{name} NULL graded-t5 d=2.0", name, ("graded_t5", 2.0)))
        S.append((f"{name} NULL graded+drift d=1.0", name, ("drift", 1.0)))
        S.append((f"{name} NULL leaky-accumulator d=1.5", name, ("accum", 1.5)))
        S.append((f"{name} AMBIG accumulator-to-bound d=1.5", name, ("bound", 1.5)))
    return S


def one(args):
    label, dname, (kind, d), n_rep, seed = args
    global rng
    rng = np.random.default_rng(seed); T4.rng = rng
    D = DESIGNS[dname]
    g = {"mix": lambda: gen_mix(D, d), "mix_t5": lambda: gen_mix(D, d, "t5"),
         "graded": lambda: gen_graded(D, d), "graded_skew": lambda: gen_graded(D, d, "skew"),
         "graded_t5": lambda: gen_graded(D, d, "t5"), "drift": lambda: gen_graded(D, d, drift=0.8),
         "accum": lambda: gen_accum(D, d), "bound": lambda: gen_accum(D, d, 0.8)}[kind]
    return label, run(g, D, n_rep)


def main():
    from concurrent.futures import ProcessPoolExecutor
    n_rep = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    jobs = [(l, dn, sc, n_rep, 1000 + i) for i, (l, dn, sc) in enumerate(scenarios())]
    out = {}
    with ProcessPoolExecutor(max_workers=3) as ex:
        for label, rate in ex.map(one, jobs):
            out[label] = rate; print(label, rate, flush=True)
    json.dump({"n_rep": n_rep, "pass_rate": out}, open(os.path.join(HERE, "kill_planted.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
