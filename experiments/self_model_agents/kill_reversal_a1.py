"""Amendment 1 run: optimised vs fixed-floor controllers. See docs/prereg/2026-11-20_self_model_kill_reversal_amendment1.md."""
import json, math

S_GRID = [i / 20 for i in range(21)]
THETAS = [-1 + i * 0.01 for i in range(401)]


def up(theta, mu, sigma):
    return 0.5 * (1 - math.erf((theta - mu) / (sigma * math.sqrt(2))))


def D(kind, s, theta, sigma, k, e, g):
    p = s ** g
    if kind == "N":
        return p
    if kind == "step":
        return p if s < 0.3 else p * (1 - e) + k
    if kind in ("S", "F"):
        q = up(theta, s, sigma)
        return p * (1 - e * q) + k * q
    q0 = up(theta, 0.0, sigma)
    q1 = up(theta, 1.0 if kind == "A1" else s, sigma)
    return p * (1 - e * q1) + k * (p * q1 + (1 - p) * q0)


def curve(kind, sigma, k, e, g):
    if kind in ("N", "step"):
        th = None
    elif kind in ("F", "FA"):
        th = 0.3
    else:
        th = min(THETAS, key=lambda t: sum(D(kind, s, t, sigma, k, e, g) for s in S_GRID))
    kk = "A2" if kind == "FA" else kind
    return th, [D(kk, s, th, sigma, k, e, g) for s in S_GRID]


def rev(d):
    i = max(range(len(d)), key=lambda j: d[j])
    r = d[i] - d[-1]
    return round(r, 4), S_GRID[i], (r > 0.05 and S_GRID[i] < 0.9)


kinds = ("N", "step", "S", "A1", "A2", "F", "FA")
cells = []
for e in (0.7, 0.8, 0.95):
    for g in (0.5, 1, 2):
        for sigma in (0.1, 0.3):
            for k in (0.02, 0.1):
                c = {"e": e, "g": g, "sigma": sigma, "k": k}
                for kd in kinds:
                    th, d = curve(kd, sigma, k, e, g)
                    r, pk, sh = rev(d)
                    c[kd] = {"theta": th, "reversal": r, "peak_s": pk, "shows": sh}
                c["step_expected"] = (0.25 ** g - ((1 - e) + k)) > 0.05
                cells.append(c)
count = {kd: sum(c[kd]["shows"] for c in cells) for kd in kinds}
p1 = count["N"] == 0
p2 = all(c["step"]["shows"] for c in cells if c["step_expected"])
ok = p1 and p2
sup = ok and all(count[k] <= 3 for k in ("S", "A1", "A2")) and all(count[k] >= 18 for k in ("F", "FA"))
verdict = "void" if not ok else ("supported" if sup else "not supported")
json.dump({"P1": p1, "P2": p2, "counts_of_36": count, "verdict": verdict, "cells": cells},
          open("kill_reversal_a1.json", "w"), indent=1)
print("P1", p1, "P2", p2, "step cells expected", sum(c["step_expected"] for c in cells))
print("cells showing reversal (of 36):", count, "->", verdict)
print("max reversal, optimised:", max(c[k]["reversal"] for c in cells for k in ("S", "A1", "A2")))
print("median reversal F / FA:", sorted(c["F"]["reversal"] for c in cells)[18], sorted(c["FA"]["reversal"] for c in cells)[18])
