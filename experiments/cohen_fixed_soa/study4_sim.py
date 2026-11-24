"""Study 4 kill-test design on simulated data: can no-report SOA-50 trials reveal a seen/unseen mixture on the VAN?

Nothing here reads no-report EEG (none is on disk). Per-subject parameters come from the report SOA-50 trials
(out/prep.npz, the spent and sealed contrast): seen and unseen VAN means, pooled trial SD, seen rate, plus the
no-report SOA-50 trial count from trials.csv.

Simulated worlds for the no-report block (each subject also gets a block offset b_s ~ N(beta, tau)):
  AWARE   no-report trials are a mixture: a seen-like share pi_s (the subject's report seen rate) at the seen mean,
          the rest at the unseen mean.
  REPORT  the seen/unseen VAN difference needs report: every no-report trial sits at the unseen mean.
  HALF    a mixture at half the report separation.

Candidate statistics:
  S1 shape: per-subject two-component mixture share with known separation and SD but free location (grid ML).
            Identifiable only through shape.
  S2 position: pooled position of the no-report mean on the report unseen->seen axis,
            sum(m_NR - mu0) / sum(mu1 - mu0). It is shifted by any block offset.
  S3 covariation: across-subject Spearman r between (m_NR - mu0) and pi_s * (mu1 - mu0). It is immune to a common
            offset but needs between-subject variation in pi.

    python -I study4_sim.py     # -> out/study4_sim.json
"""
import csv, json
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
RNG = np.random.default_rng(20261124)


def params():
    z = np.load(OUT / "prep.npz")
    subs = sorted({k.split("|")[0] for k in z.files})
    nnr = {}
    for r in csv.DictReader(open(HERE / "trials.csv")):
        if r["block"] == "noreport" and r["kind"] == "face" and r["soa"] == "50":
            nnr[r["sub"]] = nnr.get(r["sub"], 0) + 1
    P = []
    for s in subs:
        v, y = z[f"{s}|VAN"], z[f"{s}|resp"] == 1
        if y.sum() < 10 or (~y).sum() < 10:
            continue
        P.append(dict(sub=s, mu1=v[y].mean(), mu0=v[~y].mean(), sd=np.sqrt((v[y].var() * y.sum() + v[~y].var() * (~y).sum()) / len(v)),
                      pi=y.mean(), n1=int(y.sum()), n0=int((~y).sum()), nnr=nnr.get(s, 0)))
    return P


def shape_share(x, d, sd):
    """ML share of the 'seen' component (at location+d) with free location, on a grid. d < 0 for the VAN."""
    pis = np.linspace(0, 1, 21)[:, None, None]
    locs = np.linspace(x.mean() - abs(d) - 1, x.mean() + abs(d) + 1, 41)[None, :, None]
    f0 = stats.norm.pdf(x[None, None, :], locs, sd)
    f1 = stats.norm.pdf(x[None, None, :], locs + d, sd)
    ll = np.log((1 - pis) * f0 + pis * f1 + 1e-300).sum(-1)
    return float(pis.ravel()[np.unravel_index(ll.argmax(), ll.shape)[0]])


def simulate(P, world, beta, tau, true_delta_scale=1.0):
    """Returns S1 (mean shape share), S2 (pooled position), S3 (Spearman r, p one-sided)."""
    # true per-subject means: shrink the noisy report estimates towards the group mean difference
    gd = np.mean([p["mu1"] - p["mu0"] for p in P])
    s1, num, den, a, bb = [], 0.0, 0.0, [], []
    for p in P:
        mu0, d, sd = p["mu0"], gd * true_delta_scale, p["sd"]
        # the analyst re-estimates mu0, mu1 from simulated report trials (same counts as real)
        e0 = RNG.normal(mu0, sd, p["n0"]).mean()
        e1 = RNG.normal(mu0 + gd, sd, p["n1"]).mean()
        b = RNG.normal(beta, tau)
        n = p["nnr"]
        if world == "REPORT":
            x = RNG.normal(mu0 + b, sd, n)
        else:
            z = RNG.random(n) < p["pi"]
            x = RNG.normal(mu0 + b + d * z, sd, n)
        s1.append(shape_share(x, e1 - e0, sd))
        num += x.mean() - e0
        den += e1 - e0
        a.append(x.mean() - e0)
        bb.append(p["pi"] * (e1 - e0))
    r, pv = stats.spearmanr(bb, a)
    return float(np.mean(s1)), float(num / den), float(r), float(pv / 2 if r > 0 else 1 - pv / 2)


def main():
    P = params()
    pis = np.array([p["pi"] for p in P])
    summary = dict(subjects=len(P), mean_seen_rate=float(pis.mean()), sd_seen_rate=float(pis.std()),
                   mean_delta_uv=float(np.mean([p["mu1"] - p["mu0"] for p in P])),
                   mean_trial_sd_uv=float(np.mean([p["sd"] for p in P])),
                   mean_nr_trials=float(np.mean([p["nnr"] for p in P])))
    res = {}
    for world, scale in (("AWARE", 1.0), ("HALF", 0.5), ("REPORT", 1.0)):
        for beta in (0.0, 1.0):
            sims = [simulate(P, world if world != "HALF" else "AWARE", beta, 1.0, scale) for _ in range(100)]
            s = np.array(sims)
            res[f"{world}_offset{beta:+.0f}uv"] = dict(
                S1_shape_share_mean=float(s[:, 0].mean()), S1_sd=float(s[:, 0].std()),
                S2_position_mean=float(s[:, 1].mean()), S2_sd=float(s[:, 1].std()),
                S3_r_mean=float(s[:, 2].mean()), S3_power_p05=float((s[:, 3] < 0.05).mean()))
            print(world, beta, {k: round(v, 3) for k, v in res[f"{world}_offset{beta:+.0f}uv"].items()}, flush=True)
    (OUT / "study4_sim.json").write_text(json.dumps(dict(params=summary, worlds=res), indent=1) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
