"""Item 2b: is the fixed-SOA VAN graded evidence, arousal, or two-state? Report x RT-speed interaction (SOA 50, report).
Prereg: docs/prereg/2026-11-24_cohen_van_rt_gradient.md

    python -I rt_gradient.py power   # RT shuffled within class (real VAN noise) + planted patterns -> out/rt_power.json
    python -I rt_gradient.py run     # real RT; refuses unless sealed -> out/rt_result.json

Per subject and class (seen / unseen), trials are split at the class's median RT into fast and slow.
  g_seen   = VAN(fast seen)   - VAN(slow seen)      graded evidence predicts < 0 (fast seen = more evidence = more negative)
  g_unseen = VAN(fast unseen) - VAN(slow unseen)    graded evidence predicts > 0 (fast unseen = least evidence)
  I = g_seen - g_unseen   (crossover; graded predicts < 0)      S = (g_seen + g_unseen) / 2   (arousal predicts < 0)
"""
import json, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cohen_killtest as ck  # noqa: E402

OUT = HERE / "out"
PREREG = HERE.parents[1] / "docs" / "prereg" / "2026-11-24_cohen_van_rt_gradient.md"
SEED = 20261126
RUNS = 500
G = 0.4          # planted within-class fast-slow VAN difference, uV
BOUND = 0.5      # FLAT needs both CIs inside +-BOUND
MIN_CELL = 10


def tq(n):
    from scipy.stats import t
    return float(t.ppf(0.975, n - 1))


def per_subject(van, seen, rt, rng=None, shuffle=False):
    out = {}
    for cls, m in (("seen", seen), ("unseen", ~seen)):
        r = rt[m].copy()
        v = van[m]
        if shuffle:
            r = rng.permutation(r)
        fast = r < np.median(r)
        slow = r > np.median(r)
        if fast.sum() < MIN_CELL or slow.sum() < MIN_CELL:
            return None
        out[cls] = (v[fast].mean() - v[slow].mean(), fast, slow, m)
    return out


def stats(gs, gu):
    gs, gu = np.array(gs), np.array(gu)
    n = len(gs)
    res = {}
    for name, x in (("I", gs - gu), ("S", (gs + gu) / 2), ("g_seen", gs), ("g_unseen", gu)):
        se = x.std(ddof=1) / np.sqrt(n)
        res[name] = dict(mean=float(x.mean()), ci95=[float(x.mean() - tq(n) * se), float(x.mean() + tq(n) * se)])
    res["n"] = n
    return res


def decide(r):
    I, S = r["I"]["ci95"], r["S"]["ci95"]
    if I[1] < 0 and r["g_seen"]["mean"] < 0 and r["g_unseen"]["mean"] > 0:
        return "GRADED"
    if S[1] < 0 and I[0] <= 0 <= I[1]:
        return "AROUSAL-LIKE"
    if -BOUND < I[0] and I[1] < BOUND and -BOUND < S[0] and S[1] < BOUND:
        return "FLAT"
    return "INCONCLUSIVE"


def collect(D, subs, rng, shuffle, plant=None):
    gs, gu = [], []
    for s in subs:
        seen = D[s]["resp"] == 1
        van = D[s]["VAN"].copy()
        p = per_subject(van, seen, D[s]["rt"], rng, shuffle)
        if p is None:
            continue
        if plant:
            # rebuild fast/slow on the (shuffled) RT and add the planted pattern
            for cls in ("seen", "unseen"):
                _, fast, slow, m = p[cls]
                idx = np.where(m)[0]
                sign = {"crossover": (-1 if cls == "seen" else 1), "arousal": -1}[plant]
                van[idx[fast]] += sign * G / 2
                van[idx[slow]] -= sign * G / 2
            gs.append(van[np.where(p["seen"][3])[0][p["seen"][1]]].mean() - van[np.where(p["seen"][3])[0][p["seen"][2]]].mean())
            gu.append(van[np.where(p["unseen"][3])[0][p["unseen"][1]]].mean() - van[np.where(p["unseen"][3])[0][p["unseen"][2]]].mean())
        else:
            gs.append(p["seen"][0])
            gu.append(p["unseen"][0])
    return stats(gs, gu)


def power():
    D = ck.load()
    subs = ck.eligible("confirm") + ck.eligible("pilot")
    rng = np.random.default_rng(SEED)
    tally = {w: {} for w in ("null", "crossover", "arousal")}
    se = []
    for k in range(RUNS):
        for w in tally:
            r = collect(D, subs, rng, True, None if w == "null" else w)
            v = decide(r)
            tally[w][v] = tally[w].get(v, 0) + 1
            if w == "null":
                se.append((r["I"]["ci95"][1] - r["I"]["ci95"][0]) / (2 * tq(r["n"])))
    res = dict(subjects=len(subs), runs=RUNS, plant_uv=G, bound=BOUND,
               rates={w: {v: n / RUNS for v, n in t.items()} for w, t in tally.items()},
               null_se_I=float(np.mean(se)))
    r = res["rates"]
    res["false_graded"] = r["null"].get("GRADED", 0)
    res["false_arousal"] = r["null"].get("AROUSAL-LIKE", 0)
    res["power_crossover"] = r["crossover"].get("GRADED", 0)
    res["power_arousal"] = r["arousal"].get("AROUSAL-LIKE", 0)
    res["PASS"] = bool(res["false_graded"] <= 0.05 and res["false_arousal"] <= 0.05 and
                       res["power_crossover"] >= 0.8 and res["power_arousal"] >= 0.8)
    (OUT / "rt_power.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


def run():
    from evidence import require_sealed
    for f in (PREREG, Path(__file__), OUT / "rt_power.json"):
        require_sealed(str(f))
    assert json.loads((OUT / "rt_power.json").read_text())["PASS"], "power check failed: no run"
    D = ck.load()
    rng = np.random.default_rng(SEED)
    res = {}
    for grp in ("confirm", "pilot"):
        r = collect(D, ck.eligible(grp), rng, False)
        r["verdict"] = decide(r)
        res[grp] = r
    (OUT / "rt_result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    {"power": power, "run": run}[sys.argv[1]]()
