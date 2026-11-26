"""Round 19 #3 kill test (label-free; DESIGN.md §4). Reads ../ds006171_van/out/prep/<sub>.npz and per-subject COUNTS
of hit / miss / CR from events.tsv (behaviour only; no EEG trial is paired with an answer).

    python -I killtest.py        # -> out/killtest.json
"""
import csv, json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "datasets" / "local" / "r19_ds006171" / "files"
PREP = ROOT / "experiments" / "ds006171_van" / "out" / "prep"
WIN = (0.180, 0.280)
GABOR, CATCH = {11, 12, 21, 22}, {31, 32}
HM, DZ = -0.69, 0.46                       # reanalysis bilateral seen - unseen (uV) and its dz
PLANTS, CUT = (0.0, 0.32, 0.40), 0.20
NRUN, NBOOT, SEED = 200, 2000, 20261127
MIN_CR, MIN_HM = 20, 30


def counts(sub):
    """Hits, misses, CRs: each stimulus code's next 124/125 before the next stimulus code."""
    rows = list(csv.DictReader(open(RAW / sub / "eeg" / f"{sub}_task-nocue_events.tsv"), delimiter="\t"))
    h = m = cr = fa = 0
    cur = None
    for r in rows:
        k = int(r["trial_type"])
        if k in GABOR or k in CATCH:
            cur = k
        elif k in (124, 125) and cur is not None:
            if cur in GABOR:
                h += k == 124; m += k == 125
            else:
                fa += k == 124; cr += k == 125
            cur = None
    return h, m, cr, fa


def boot(num_s, den_s, rng):
    n = len(num_s)
    I = rng.integers(0, n, (NBOOT, n))
    with np.errstate(divide="ignore", invalid="ignore"):
        r = num_s[I].mean(axis=1) / den_s[I].mean(axis=1)
    return num_s.mean() / den_s.mean(), *np.percentile(r, [2.5, 97.5])


def call(lo, hi):
    return "AON" if hi < CUT else ("GRADED" if lo > CUT else "INC")


def main():
    rng = np.random.default_rng(SEED)
    S, beh = {}, {}
    for f in sorted(PREP.glob("sub-*.npz")):
        s = f.stem
        d = np.load(f)
        t = d["times"]
        w = (t >= WIN[0]) & (t <= WIN[1])
        x = d["bil"][:, w].mean(axis=1)
        code, keep = d["code"], d["keep"]
        g, c = x[keep & np.isin(code, list(GABOR))], x[keep & np.isin(code, list(CATCH))]
        h, m, cr, fa = counts(s)
        beh[s] = dict(hit=h, miss=m, cr=cr, fa=fa, kept_gabor=len(g), kept_catch=len(c))
        nh = int(round(len(g) * h / (h + m))); ncr = int(round(len(c) * cr / (cr + fa)))
        if ncr < MIN_CR or nh < MIN_HM or len(g) - nh < MIN_HM:
            continue
        S[s] = (g - g.mean(), c - c.mean(), nh, ncr)
    # sampling variance of the synthetic hit - miss difference, to set sd_true so total SD matches the sourced dz
    v = np.mean([np.var(g, ddof=1) * (1 / nh + 1 / (len(g) - nh)) for g, _, nh, _ in S.values()])
    sd_true = float(np.sqrt(max(0.0, (abs(HM) / DZ) ** 2 - v)))
    out = dict(n_used=len(S), n_prepped=len(beh), behaviour=beh, sd_true=sd_true, sampling_sd=float(np.sqrt(v)),
               median_cr=float(np.median([v_[3] for v_ in S.values()])), plants={})
    print(f"used {len(S)}/{len(beh)}; median pseudo-CR {out['median_cr']}; sd_true {sd_true:.2f}, sampling sd {np.sqrt(v):.2f}",
          flush=True)
    for R in PLANTS:
        calls, hw = [], []
        for _ in range(NRUN):
            num, den = [], []
            for g, c, nh, ncr in S.values():
                hm = rng.normal(HM, sd_true)
                D = hm / (1 - R)
                p = rng.permutation(len(g))
                hit, miss = g[p[:nh]] + D, g[p[nh:]] + R * D
                crv = rng.choice(c, ncr, replace=False)
                num.append(miss.mean() - crv.mean()); den.append(hit.mean() - crv.mean())
            est, lo, hi = boot(np.array(num), np.array(den), rng)
            calls.append(call(lo, hi)); hw.append((hi - lo) / 2)
        want = "AON" if R == 0 else "GRADED"
        wrong = "GRADED" if R == 0 else "AON"
        out["plants"][str(R)] = dict(correct=calls.count(want) / NRUN, wrong=calls.count(wrong) / NRUN,
                                     inconclusive=calls.count("INC") / NRUN, median_halfwidth=float(np.median(hw)))
        print(R, out["plants"][str(R)], flush=True)
    P = out["plants"]
    out["PASS"] = bool(P["0.0"]["median_halfwidth"] <= 0.12 and all(P[k]["correct"] >= 0.80 and P[k]["wrong"] <= 0.05
                                                                      for k in P))
    print("KILLTEST", "PASS" if out["PASS"] else "FAIL")
    (HERE / "out").mkdir(exist_ok=True)
    json.dump(out, open(HERE / "out" / "killtest.json", "w"), indent=1)


if __name__ == "__main__":
    main()
