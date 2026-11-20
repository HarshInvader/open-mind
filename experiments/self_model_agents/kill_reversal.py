"""Kill test: is the Tsushima reversal diagnostic of an attention model?
Exact expected-loss calculation; see docs/prereg/2026-11-20_self_model_kill_reversal.md."""
import json, math

E = 0.9
S_GRID = [i / 20 for i in range(21)]
THETAS = [-1 + i * 0.01 for i in range(401)]  # -1 .. 3


def up(theta, mu, sigma):  # P(N(mu, sigma) > theta)
    return 0.5 * (1 - math.erf((theta - mu) / (sigma * math.sqrt(2))))


def disruption(kind, s, theta, sigma, k):
    if kind == "N":
        return s
    if kind == "step":
        return s if s < 0.3 else s * (1 - E) + k
    if kind == "S":
        q = up(theta, s, sigma)
        return s * (1 - E * q) + k * q
    q0 = up(theta, 0.0, sigma)
    q1 = up(theta, 1.0 if kind == "A1" else s, sigma)
    return s * (1 - E * q1) + k * (s * q1 + (1 - s) * q0)


def curve(kind, sigma, k):
    if kind in ("N", "step"):
        return None, [disruption(kind, s, 0, sigma, k) for s in S_GRID]
    best = min(THETAS, key=lambda t: sum(disruption(kind, s, t, sigma, k) for s in S_GRID))
    return best, [disruption(kind, s, best, sigma, k) for s in S_GRID]


def reversal(d):
    peak = max(range(len(d)), key=lambda i: d[i])
    r = d[peak] - d[-1]
    return r, S_GRID[peak], (r > 0.05 and S_GRID[peak] < 0.9)


rows = []
for sigma in (0.1, 0.2, 0.3, 0.5):
    for k in (0.02, 0.05, 0.1, 0.2):
        cell = {"sigma": sigma, "k": k}
        for kind in ("N", "step", "S", "A1", "A2"):
            th, d = curve(kind, sigma, k)
            r, pk, shows = reversal(d)
            cell[kind] = {"theta": th, "reversal": round(r, 4), "peak_s": pk, "shows": shows,
                          "D": [round(x, 4) for x in d]}
        rows.append(cell)

p1 = all(not c["N"]["shows"] for c in rows)
p2 = all(c["step"]["shows"] for c in rows if c["k"] < 0.3)
disagree = sum(1 for c in rows if c["S"]["shows"] != c["A1"]["shows"] or c["S"]["shows"] != c["A2"]["shows"])
disagree_S_A2 = sum(1 for c in rows if c["S"]["shows"] != c["A2"]["shows"])
disagree_S_A1 = sum(1 for c in rows if c["S"]["shows"] != c["A1"]["shows"])
verdict = "void (planted check failed)" if not (p1 and p2) else ("diagnostic" if disagree >= 4 else "not diagnostic")
out = {"P1": p1, "P2": p2, "cells_S_vs_any_A_disagree": disagree, "cells_S_vs_A1": disagree_S_A1,
       "cells_S_vs_A2": disagree_S_A2, "verdict": verdict, "cells": rows}
json.dump(out, open("kill_reversal.json", "w"), indent=1)
print(f"P1 {p1} P2 {p2} | S-vs-A1 {disagree_S_A1}/16, S-vs-A2 {disagree_S_A2}/16 | verdict: {verdict}")
for c in rows:
    print(c["sigma"], c["k"], *(f'{kd}:{c[kd]["reversal"]:+.3f}@{c[kd]["peak_s"]}{"*" if c[kd]["shows"] else ""}' for kd in ("S", "A1", "A2")))
