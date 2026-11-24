"""Study 4 design, part 2: offset-robust statistics (simulated data only; reads report-trial parameters from out/prep.npz).

Why: study4_sim.py showed (a) the shape-based mixture share cannot tell AWARE from REPORT, (b) the position statistic
moves by ~0.75 axis units per 1 uV block offset, (c) the covariation statistic is fake-positive under REPORT because
m_NR - e0 and pi*(e1 - e0) share the noise of e0.

Candidates here (D_s = no-report mean minus all-report-trial mean at SOA 50; no labels in D_s):
  S4 slope: regress D_s on pi_s * Dhat_s across subjects. AWARE -> slope 0, REPORT -> slope -1. Offsets add noise only.
  DD double difference: (NR face50 - NR mask-only) - (R face50 - R mask-only), group mean, scaled by -mean(pi*Dhat).
     AWARE -> 0, REPORT -> 1. Block offset cancels if it is the same for face and mask-only trials; tau_int is the
     part that is not. Needs mask-only trials from both blocks (extra bytes).
    python -I study4_sim2.py   # -> out/study4_sim2.json
"""
import json
from pathlib import Path
import numpy as np
from scipy import stats
import sys; sys.path.insert(0, str(Path(__file__).resolve().parent))
import study4_sim as s4

RNG = np.random.default_rng(7)
OUT = Path(__file__).resolve().parent / "out"


def one(P, world, beta, tau, tau_int, n_mask):
    gd = np.mean([p["mu1"] - p["mu0"] for p in P])
    D, X, dd = [], [], []
    for p in P:
        sd, pi, n = p["sd"], p["pi"], p["nnr"]
        d = gd * (0.5 if world == "HALF" else 1.0)
        y = RNG.random(p["n0"] + p["n1"]) < pi              # report trials (re-drawn labels)
        r = RNG.normal(p["mu0"] + gd * y, sd)
        dhat = r[y].mean() - r[~y].mean()
        b = RNG.normal(beta, tau)
        z = (RNG.random(n) < pi) if world != "REPORT" else np.zeros(n, bool)
        x = RNG.normal(p["mu0"] + b + d * z, sd)
        D.append(x.mean() - r.mean())
        X.append(pi * dhat)
        m_nr = RNG.normal(b + RNG.normal(0, tau_int), sd, n_mask).mean()   # mask-only, relative baseline 0
        m_r = RNG.normal(0, sd, n_mask).mean()
        dd.append((x.mean() - m_nr) - (r.mean() - m_r))
    D, X, dd = map(np.array, (D, X, dd))
    sl = stats.linregress(X, D)
    scale = -X.mean()
    ddn = dd / scale
    return sl.slope, sl.stderr, ddn.mean(), ddn.std(ddof=1) / np.sqrt(len(ddn))


def main():
    P = s4.params()
    res = {}
    for world in ("AWARE", "HALF", "REPORT"):
        for beta, tau, tau_int in ((0, 1, 0.3), (1, 1, 0.3), (1, 1, 0.6)):
            for n_mask in (60, 150):
                s = np.array([one(P, world, beta, tau, tau_int, n_mask) for _ in range(500)])
                k = f"{world}|beta{beta}|tau{tau}|tauint{tau_int}|mask{n_mask}"
                res[k] = dict(S4_slope=float(s[:, 0].mean()), S4_se=float(s[:, 1].mean()),
                              DD_mean=float(s[:, 2].mean()), DD_se=float(s[:, 3].mean()),
                              DD_ci_hi_below_0p5=float((s[:, 2] + 1.96 * s[:, 3] < 0.5).mean()),
                              DD_ci_lo_above_0p5=float((s[:, 2] - 1.96 * s[:, 3] > 0.5).mean()))
                print(k, {a: round(v, 3) for a, v in res[k].items()}, flush=True)
    (OUT / "study4_sim2.json").write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    main()
