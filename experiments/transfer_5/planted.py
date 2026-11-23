"""Planted-signal gate for the sealed REM-placement analysis. Uses Sleep-EDF W and N3 epochs only (no REM, no HMC).

Subjects are split in half (seeded). Cutoffs are fitted on half A. In half B pseudo-"REM" sets are built per subject
from real epochs: 17 W + 3 N3 (mix 0.83), 10 + 10 (0.5) or 3 + 17 (0.17). Attempt 3 (after Fable's pre-seal review)
checks the normalised REM position and the verdict itself:
  1. placement: 0.83 -> "wake side", 0.17 -> "N3 side", for every eligible measure;
  2. position recovers the mix within 0.05 for every eligible measure;
  3. purely spectral measures (exponent, band powers, spectral entropy, baseline) get surrogate "same";
  4. positive control: pseudo-REM paired with surrogates of the opposite mix -> surrogate "different" for every
     eligible measure;
  5. verdict() on the pure mixtures (0.83, 0.5, 0.17) starts "one axis";
  6. verdict() when one measure's (lz) pseudo-REM values are swapped for its values in the opposite mix starts
     "measures disagree" and names lz (run for mixes 0.83 and 0.17).
Gate passes if 1-6 hold and at least 3 viable measures are eligible in half B.
Attempts 1-2 (planted_attempt1.json, planted_attempt2.json) used raw wake fractions; see the prereg.
"""
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse as A  # noqa: E402
import measures as M  # noqa: E402

SPECTRAL = ["exponent", "rel_delta", "rel_alpha", "rel_beta", "spectral_entropy", "baseline"]


def pseudo(rows_b, mix, rng, n=20):
    out = []
    by = {}
    for r in rows_b:
        by.setdefault(r["subject"], {"W": [], "N3": []})[r["stage"]].append(r)
    for s, d in sorted(by.items()):
        kw = int(round(mix * n))
        if len(d["W"]) < kw or len(d["N3"]) < n - kw:
            continue
        pick = [d["W"][i] for i in rng.choice(len(d["W"]), kw, replace=False)] + \
               [d["N3"][i] for i in rng.choice(len(d["N3"]), n - kw, replace=False)]
        out += [dict(p, stage="R") for p in pick]
    return out


def main():
    if not os.path.exists(os.path.join(HERE, "feats_sedf_wn.jsonl")):
        A.extract("sedf_wn")
    rows = A.load("sedf_wn")
    subs = sorted({r["subject"] for r in rows})
    rng = np.random.default_rng(5)
    half = set(rng.choice(subs, len(subs) // 2, replace=False))
    ra = [r for r in rows if r["subject"] in half]
    rb = [r for r in rows if r["subject"] not in half]
    # Phase-surrogate features for half B (same epochs, same order).
    sp = os.path.join(HERE, "feats_planted_surr.jsonl")
    if not os.path.exists(sp):
        files = [f for f in sorted(os.listdir(A.SEDF_RAW)) if f[:-4] not in half]
        with Pool(3) as pool, open(sp, "w") as fh:
            for rr in pool.imap(A._one, [(os.path.join(A.SEDF_RAW, f), "sleepedf_surr", ["W", "N3"], True) for f in files]):
                for r in rr:
                    fh.write(json.dumps(r) + "\n")
    surr = [json.loads(l) for l in open(sp)]
    skey = {(r["subject"], r["epoch"]): r for r in surr}
    out = {"half_A": sorted(half), "mixes": {}}
    ok = True
    sets = {}
    for mix in (0.83, 0.5, 0.17):
        pr = pseudo(rb, mix, np.random.default_rng(int(mix * 100)))
        sets[mix] = (pr, [dict(skey[(r["subject"], r["epoch"])], stage="R") for r in pr if (r["subject"], r["epoch"]) in skey])
    for mix, want in ((0.83, "wake side"), (0.5, "in between"), (0.17, "N3 side")):
        pr, ps = sets[mix]
        res = A.summarise(ra, rb + pr, ps, np.random.default_rng(A.SEED))
        v_pure = A.verdict(res)
        el = [m for m in A.NAMES if res["measures"][m]["eligible"]]
        chk = {m: dict(placement=res["measures"][m]["placement"], pos=round(res["measures"][m]["rem_position"], 3),
                       surrogate=res["measures"][m]["surrogate"], vs=res["measures"][m].get("vs_comparator"))
               for m in el}
        rec = dict(eligible=el, checks=chk, verdict_pure=v_pure,
                   test_ba={m: round(res["measures"][m]["test_ba"], 3) for m in A.NAMES})
        good = len([m for m in el if m != "baseline"]) >= 3 and v_pure.startswith("one axis")
        good &= all(abs(c["pos"] - mix) <= 0.05 for c in chk.values())
        if mix != 0.5:
            opp = sets[round(1 - mix, 2)]
            ctrl = A.summarise(ra, rb + pr, opp[1], np.random.default_rng(A.SEED))
            rec["ctrl_surrogate"] = {m: ctrl["measures"][m]["surrogate"] for m in el}
            # planted shift: lz's pseudo-REM values replaced by lz values from the opposite mix (same subjects, order)
            lzmap = {}
            for r in opp[0]:
                lzmap.setdefault(r["subject"], []).append(r["lz"])
            shifted, k = [], {}
            for r in pr:                      # subjects present in both mixes only
                if r["subject"] not in lzmap:
                    continue
                i = k.get(r["subject"], 0); k[r["subject"]] = i + 1
                shifted.append(dict(r, lz=lzmap[r["subject"]][i]))
            ps_sh = [q for q in ps if q["subject"] in lzmap]
            v_shift = A.verdict(A.summarise(ra, rb + shifted, ps_sh, np.random.default_rng(A.SEED)))
            rec["verdict_shift_lz"] = v_shift
            good &= all(c["placement"] == want for c in chk.values())
            good &= all(c["surrogate"] == "same" for m, c in chk.items() if m in SPECTRAL)
            good &= all(s == "different" for s in rec["ctrl_surrogate"].values())
            good &= v_shift.startswith("measures disagree") and "lz (" in v_shift
        rec["pass_"] = bool(good)
        ok &= good
        out["mixes"][str(mix)] = rec
        print(mix, json.dumps(rec), flush=True)
    out["gate_pass"] = bool(ok)
    print("PLANTED GATE", "PASS" if ok else "FAIL", flush=True)
    json.dump(out, open(os.path.join(HERE, "planted.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
