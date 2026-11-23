"""Design check for the AI2 amendment (no training). Exact expected loss D(s) for scripted agents.

Task (as in kill_trained.py): s uniform on {0, .05, ..., 1}; x = s + N(0, sigma); suppress costs k;
capture with prob s^g; captured and unsuppressed costs 1, suppression removes a fraction e.
Expected loss at s for a policy with suppress-probability P(s) = Pr(suppress | s):
    D(s) = s^g * (1 - e * P(s)) + k * P(s)

Agents:
- BAYES: Bayes-optimal stimulus-only agent. Suppresses iff E[e*s^g - k | x] > 0 (posterior over the 21 levels).
- BLANKET: always suppresses.
- FLOOR(f): the Bayes agent, but its ACTION is forced to "no suppress" whenever x < f (action-gated floor).
Reversal = max_s D(s) - D(1); "shows" if > 0.05 with the peak at s < 0.9 (the sealed metric).
"""
import json, itertools
import numpy as np
from scipy.stats import norm

S = np.arange(21) / 20.0
XG = np.linspace(-1.5, 2.5, 8001)  # x grid for the decision regions
DX = XG[1] - XG[0]


def bayes_region(e, g, sigma, k):
    lik = norm.pdf((XG[:, None] - S[None, :]) / sigma)  # x by s
    post = lik / lik.sum(1, keepdims=True)
    gain = post @ (e * S ** g - k)
    return gain > 0


def D_of(region, e, g, sigma, k):
    dens = norm.pdf((XG[:, None] - S[None, :]) / sigma) / sigma * DX  # x by s
    P = (dens * region[:, None]).sum(0) / dens.sum(0)
    return S ** g * (1 - e * P) + k * P


def rev(D):
    i = int(np.argmax(D))
    r = D[i] - D[-1]
    return float(r), float(S[i]), bool(r > 0.05 and S[i] < 0.9)


def crossover(e, g, k):
    return (k / e) ** (1 / g) if k < e else None


def main():
    out = []
    es, gs, sigmas, ks = [0.8, 0.95], [0.5, 1.0], [0.1, 0.3], [0.02, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    for e, g, sigma, k in itertools.product(es, gs, sigmas, ks):
        reg = bayes_region(e, g, sigma, k)
        row = dict(cell=[e, g, sigma, k], s_star=crossover(e, g, k))
        row["BAYES"] = rev(D_of(reg, e, g, sigma, k))
        row["BLANKET"] = rev(D_of(np.ones_like(reg), e, g, sigma, k))
        for f in (0.3, 0.5, 0.7):
            row[f"FLOOR{f}"] = rev(D_of(reg & (XG >= f), e, g, sigma, k))
        out.append(row)
    n_bayes = sum(r["BAYES"][2] for r in out)
    print("cells", len(out), "BAYES shows in", n_bayes, "max BAYES reversal", max(r["BAYES"][0] for r in out))
    for r in out:
        print(r["cell"], "s*", None if r["s_star"] is None else round(r["s_star"], 3),
              "BAYES %.3f" % r["BAYES"][0], "BLANKET %.3f" % r["BLANKET"][0],
              "F.3 %.3f%s" % (r["FLOOR0.3"][0], "*" if r["FLOOR0.3"][2] else ""),
              "F.5 %.3f%s" % (r["FLOOR0.5"][0], "*" if r["FLOOR0.5"][2] else ""),
              "F.7 %.3f%s" % (r["FLOOR0.7"][0], "*" if r["FLOOR0.7"][2] else ""))
    json.dump(out, open(__file__.replace(".py", ".json"), "w"), indent=1)


if __name__ == "__main__":
    main()
