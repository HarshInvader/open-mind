"""Planted-answer checks for every piece of the task #9 pipeline.

Each check has a known answer; the run prints PASS/FAIL and writes planted.json.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phi_lib as L

rng = np.random.default_rng(7)
res = {}


def check(name, ok, detail):
    res[name] = {"pass": bool(ok), "detail": detail}
    print(("PASS " if ok else "FAIL ") + name + ": " + detail)


# 1. Gaussian lagged MI vs analytic AR(1): I = -0.5 log(1 - a^2)
a, T = 0.7, 200_000
x = np.zeros(T)
e = rng.normal(size=T)
for t in range(1, T):
    x[t] = a * x[t - 1] + e[t]
mi = L.gauss_mi_lag(x[:, None], [0])
true = -0.5 * np.log(1 - a ** 2)
check("gauss_mi_ar1", abs(mi - true) < 0.01, f"est {mi:.4f} vs analytic {true:.4f}")

# 2. Granger: x -> y only
T = 50_000
X = np.zeros((T, 3))
E = rng.normal(size=(T, 3))
for t in range(1, T):
    X[t, 0] = 0.5 * X[t - 1, 0] + E[t, 0]
    X[t, 1] = 0.5 * X[t - 1, 1] + 0.6 * X[t - 1, 0] + E[t, 1]
    X[t, 2] = 0.5 * X[t - 1, 2] + E[t, 2]
cd_coupled = L.causal_density(X)
cd_indep = L.causal_density(np.column_stack([X[:, 0], rng.permutation(X[:, 1]), X[:, 2]]))
check("causal_density_planted", cd_coupled > 0.03 and cd_indep < 0.002,
      f"coupled {cd_coupled:.4f}, independent {cd_indep:.5f}")

# 3. Phi_E: independent AR channels ~ 0; ring-coupled channels > 0
Xi = np.zeros((T, 4))
Xc = np.zeros((T, 4))
E = rng.normal(size=(T, 4))
for t in range(1, T):
    Xi[t] = 0.6 * Xi[t - 1] + E[t]
    Xc[t] = 0.3 * Xc[t - 1] + 0.5 * np.roll(Xc[t - 1], 1) + E[t]
pi, pc = L.phi_wms(Xi), L.phi_wms(Xc)
check("phi_wms_planted", abs(pi) < 0.005 and pc > 0.05, f"independent {pi:.4f}, coupled {pc:.4f}")

# 4. Integration and TSE: zero for independent, positive for correlated
Z = rng.normal(size=(T, 4))
Zc = Z @ np.array([[1, .5, .5, .5], [0, 1, .5, .5], [0, 0, 1, .5], [0, 0, 0, 1]])
check("integration_planted", L.integration(Z) < 0.002 and L.integration(Zc) > 0.1,
      f"indep {L.integration(Z):.4f}, corr {L.integration(Zc):.4f}")
check("tse_planted", abs(L.tse_complexity(Z)) < 0.005 and L.tse_complexity(Zc) > 0.05,
      f"indep {L.tse_complexity(Z):.4f}, corr {L.tse_complexity(Zc):.4f}")

# 5. LZ: iid binary normalised ~1; periodic far below
Bi = rng.integers(0, 2, (10_000, 5)).astype(np.int8)
Bp = np.tile(np.array([[0, 1, 0, 1, 1], [1, 0, 1, 0, 0]], dtype=np.int8), (5_000, 1))
li, lp = L.lzc_multi(Bi, rng), L.lzc_multi(Bp, rng)
check("lzc_planted", 0.95 < li < 1.05 and lp < 0.1, f"iid {li:.3f}, periodic {lp:.4f}")

# 6. PyPhi truth: feedforward and disconnected networks have phi_s = 0 in every state;
#    a recurrent network has phi_s > 0 in some state.
out = {}
for fam in ("FF", "DISC", "DENSE"):
    W = L.make_W(fam, np.random.default_rng(11))
    tpm = L.tpm_from_W(W, np.zeros(L.N), 1.0)
    cm = (W != 0).astype(int)
    vals = L.phi_by_state(tpm, cm, np.ones(2 ** L.N), min_w=0)
    out[fam] = float(np.nanmax(vals))
check("pyphi_structural_zero", out["FF"] == 0 and out["DISC"] == 0 and out["DENSE"] > 0,
      f"max phi_s: FF {out['FF']}, DISC {out['DISC']}, DENSE {out['DENSE']:.4f}")

# 7. Plug-in phi: on a long clean binary series of a recurrent network it must
#    approach the true stationary-weighted phi_s (relative error < 25%).
W = L.make_W("DENSE", np.random.default_rng(3))
tpm = L.tpm_from_W(W, np.zeros(L.N), 1.0)
pi = L.stationary(tpm)
true = L.weighted_mean(L.phi_by_state(tpm, (W != 0).astype(int), pi), pi)
x = L.simulate(tpm, 100_000, np.random.default_rng(4))
est = L.phi_plugin(x)
check("phi_plugin_converges", abs(est - true) / true < 0.25, f"plug-in {est:.4f} vs true {true:.4f}")

# 8. Stationary distribution matches simulated state frequencies
pow2 = 2 ** np.arange(L.N)
freq = np.bincount(x @ pow2, minlength=2 ** L.N) / len(x)
tv = 0.5 * np.abs(freq - pi).sum()
check("stationary_matches_sim", tv < 0.02, f"total variation {tv:.4f}")

json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "planted.json"), "w"), indent=1)
print("ALL PASS" if all(v["pass"] for v in res.values()) else "SOME FAILED")
