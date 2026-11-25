"""Design gate for the real-data prereg (docs/prereg/2026-11-25_bifurcation_real_data_cohen.md), run BEFORE any fetch.
Question for the owner's byte decision: at the Cohen report-block design, is the 5-model comparison specific?
Two byte options: FULL (each eligible subject's real per-level trial counts) and HALF (64 per level), 38 subjects.

Signal size: the prereg measures it as (SOA 83 - mask only) / SD(mask only) on the decoder output. Neither level is on
disk (only SOA 50 is), so it cannot be estimated yet. The gate is therefore run on a grid of max-level signal sizes,
DMAX in {2, 1, 3} noise SDs (2 = the sealed simulation's value), in that order so the reference size finishes first.

Same models, fitting, CV, spm_BMS and generators as the sealed extended.py/audit.py (imported, not edited); only the
trial counts, the number of subjects and DMAX change. Gate PASS per (option, DMAX): B_bifurcation >= 0.80 and every
graded cell <= 0.10 (the sealed rule).

    python -I gate_design.py run       # -> out_gate/<option>_d<DMAX>_<cell>.json (skips finished files)
    python -I gate_design.py summary   # -> out_gate/summary.json
"""
import csv, json, sys, time
from pathlib import Path
from multiprocessing import Pool

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audit as A  # noqa: E402
import extended as E  # noqa: E402

OUT = HERE / "out_gate"
COH = HERE.parents[0] / "cohen_fixed_soa"
CELLS = ["B_bifurcation", "G_jitter_mid", "G_jitter_hi", "G_heavy", "H_jitter_t", "H_gain"]
GRADED = CELLS[1:]
DMAXES = [2.0, 1.0, 3.0]
OPTIONS = ["full", "half"]
STUDIES = 100
WORKERS = 9
SEED = 20261201
HALF_N = 64


def real_counts():
    """Per eligible subject: report-block trial counts at levels 0..5 (mask only, SOA 17/33/50/67/83), from trials.csv.
    Counts are before artefact rejection (median rejection is small), so they slightly overstate the real design."""
    el = [r["sub"] for r in csv.DictReader(open(COH / "out" / "eligibility.csv")) if r["eligible"] == "1"]
    lev = {"150": 0, "17": 1, "33": 2, "50": 3, "67": 4, "83": 5}
    C = {s: np.zeros(6, int) for s in el}
    for r in csv.DictReader(open(COH / "trials.csv")):
        if r["sub"] in C and r["block"] == "report":
            k = "150" if r["kind"] == "150" else (r["soa"] if r["kind"] == "face" and r["soa"] else None)
            if k in lev:
                C[r["sub"]][lev[k]] += 1
    return [C[s] for s in el]


_COUNTS = [None]


def design_counts(rng):
    n = _COUNTS[0]
    x = np.repeat(A.LEVELS, n)
    block = np.empty(len(x), int)
    for l in A.LEVELS:
        idx = np.where(x == l)[0]
        block[idx] = rng.permutation(np.arange(len(idx)) % A.N_BLOCK)
    return x, block


def one_study(args):
    cell, seed, dmax, counts = args
    A.design = design_counts                         # generators look these globals up at call time
    A.DMAX = dmax
    rng = np.random.default_rng(seed)
    lme = []
    for c in counts:
        _COUNTS[0] = c
        y, x, block = E.gen_ext(cell, rng)
        l, _, _ = E.subject_lme5(y, x, block)
        lme.append(l)
    lme = np.array(lme)
    if not np.all(np.isfinite(lme)):
        return dict(pxp3=float("nan"), winner=-1)
    pxp = A.spm_bms(lme, rng)["pxp"]
    return dict(pxp3=float(pxp[2]), winner=int(np.argmax(pxp)))


def run():
    OUT.mkdir(exist_ok=True)
    rc = real_counts()
    designs = {"full": rc, "half": [np.full(6, HALF_N) for _ in rc]}
    for d in DMAXES:
        for opt in OPTIONS:
            for cell in CELLS:
                f = OUT / f"{opt}_d{d:g}_{cell}.json"
                if f.exists():
                    continue
                ss = np.random.SeedSequence([SEED, OPTIONS.index(opt), int(d * 10), CELLS.index(cell)])
                seeds = [int(s.generate_state(1)[0]) for s in ss.spawn(STUDIES)]
                t = time.time()
                with Pool(WORKERS) as p:
                    res = p.map(one_study, [(cell, s, d, designs[opt]) for s in seeds])
                pxp3 = np.array([r["pxp3"] for r in res])
                call = np.where(np.isnan(pxp3), False, pxp3 > 0.95)
                r = dict(option=opt, dmax=d, cell=cell, studies=STUDIES, subjects=len(rc), rate_call=float(call.mean()),
                         winner_counts=np.bincount([r["winner"] + 1 for r in res], minlength=6).tolist(),
                         nonfinite=int(np.isnan(pxp3).sum()), seconds=round(time.time() - t))
                f.write_text(json.dumps(r) + "\n")
                print(opt, d, cell, r["rate_call"], r["winner_counts"], r["seconds"], "s", flush=True)


def summary():
    S = {}
    for f in sorted(OUT.glob("*_d*_*.json")):
        r = json.loads(f.read_text())
        S.setdefault(f"{r['option']}_d{r['dmax']:g}", {})[r["cell"]] = r["rate_call"]
    for k, v in S.items():
        if len(v) == len(CELLS):
            v["PASS"] = bool(v["B_bifurcation"] >= 0.80 and all(v[c] <= 0.10 for c in GRADED))
    (OUT / "summary.json").write_text(json.dumps(S, indent=1) + "\n")
    print(json.dumps(S, indent=1))


if __name__ == "__main__":
    {"run": run, "summary": summary}[sys.argv[1]]()
