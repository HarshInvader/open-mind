"""P1 synthetic planted checks for the NE measures (prereg section 'Planted checks'). No real data.

  .venv/bin/python -I experiments/nonequilibrium/planted.py      -> planted.json

P1a  Gaussian linear process (AR(2), alpha peak): |mean tra_x| < 0.01 and |mean ptir_x| < 0.01.
P1b  Planted asymmetric (sawtooth) alpha with a wandering frequency, k = 0, 0.25, 0.5, 1:
     tra_x rises monotonically, |tra_x| < 0.01 at k = 0, tra_x > 0.05 at k = 1; tra_x of a phase
     surrogate of the k = 1 signal is within +-0.01 of 0.
P1c  2-channel linear VAR with one-way lagged coupling (Gaussian, non-equilibrium): ne2 at least 5x
     the symmetric-coupling value; multichannel phase surrogates keep ne2 within 25%; |tra_x| < 0.01.
"""
import json
import os
import sys

import numpy as np
from scipy.signal import lfilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "experiments", "lz_slope"))
from features import phase_surrogate, preprocess  # noqa: E402
from ne_measures import ne2, ne_measures  # noqa: E402

FS, N, REPS = 100, 1000, 40


def ar_alpha(rng, n_ch=2):
    r, f = 0.97, 10 / FS
    a = [1, -2 * r * np.cos(2 * np.pi * f), r * r]
    return np.stack([lfilter([1], a, rng.normal(size=N + 500))[500:] for _ in range(n_ch)])


def wander_saw(rng):
    """Sawtooth (fast rise 15% of the cycle, slow fall) whose frequency wanders around 10 Hz."""
    f = 10 + np.cumsum(rng.normal(0, 0.05, N)); f = np.clip(f, 8, 12)
    ph = 2 * np.pi * np.cumsum(f) / FS + rng.uniform(0, 2 * np.pi)
    u = (ph / (2 * np.pi)) % 1.0
    return np.where(u < 0.15, u / 0.15, (1 - u) / 0.85) * 2 - 1


def m(x, rng):
    return ne_measures(x, rng, phase_surrogate)


def main():
    rng = np.random.default_rng(7)
    out = {}
    g = [m(preprocess(ar_alpha(rng)), rng) for _ in range(REPS)]
    out["P1a"] = {k: float(np.mean([r[k] for r in g])) for k in ("tra", "tra_x", "ptir", "ptir_x")}
    out["P1a"]["PASS"] = bool(abs(out["P1a"]["tra_x"]) < 0.01 and abs(out["P1a"]["ptir_x"]) < 0.01)

    res = {}
    for k in (0, 0.25, 0.5, 1):
        rv, sv = [], []
        for _ in range(REPS):
            x = ar_alpha(rng); x = x / x.std(1, keepdims=True)
            x = preprocess(x + k * wander_saw(rng)[None, :])
            rv.append(m(x, rng)["tra_x"])
            if k == 1:
                sv.append(m(phase_surrogate(x, rng), rng)["tra_x"])
        res[str(k)] = {"tra_x": float(np.mean(rv))}
        if k == 1:
            res[str(k)]["surr_tra_x"] = float(np.mean(sv))
    vals = [res[k]["tra_x"] for k in ("0", "0.25", "0.5", "1")]
    out["P1b"] = res
    out["P1b"]["PASS"] = bool(all(np.diff(vals) > 0) and abs(vals[0]) < 0.01 and vals[-1] > 0.05
                              and abs(res["1"]["surr_tra_x"]) < 0.01)

    def var2(c12, c21):
        e = rng.normal(size=(2, N + 500)); x = np.zeros_like(e)
        for i in range(3, N + 500):
            x[0, i] = 0.6 * x[0, i - 1] + c12 * x[1, i - 3] + e[0, i]
            x[1, i] = 0.6 * x[1, i - 1] + c21 * x[0, i - 3] + e[1, i]
        return preprocess(x[:, 500:])
    asym = [var2(0.0, 0.5) for _ in range(REPS)]
    sym = [var2(0.25, 0.25) for _ in range(REPS)]
    a, s = np.mean([ne2(x) for x in asym]), np.mean([ne2(x) for x in sym])
    a_s = np.mean([ne2(phase_surrogate(x, rng)) for x in asym])
    tr = np.mean([m(x, rng)["tra_x"] for x in asym])
    out["P1c"] = {"ne2_asym": float(a), "ne2_sym": float(s), "ne2_asym_surr": float(a_s), "tra_x_asym": float(tr)}
    out["P1c"]["PASS"] = bool(a > 5 * s and abs(a_s / a - 1) < 0.25 and abs(tr) < 0.01)
    out["ALL_PASS"] = bool(out["P1a"]["PASS"] and out["P1b"]["PASS"] and out["P1c"]["PASS"])
    json.dump(out, open(os.path.join(HERE, "planted.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
