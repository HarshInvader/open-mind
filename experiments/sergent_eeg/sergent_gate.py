"""Item 2 design gate: is the 5-model comparison specific and sensitive at Sergent et al. 2021's own design?
Design: experiments/sergent_eeg/DESIGN.md. Synthetic data only; runs BEFORE any Sergent EEG is streamed.

Same generators, fitting, CV and spm_BMS as the sealed audit.py / extended.py (imported, not edited). Only the design
changes: 20 subjects, per-level counts 168 (18 subjects) or 176 (2 subjects), inferred exactly from their Fig 1D, scaled
by 150/168 to the paper's post-rejection size; signal size DMAX 0.89 reproduces their published max-level AUC (0.731).

    python -I sergent_gate.py run [KT ...]   # -> out_gate/<tag>_<cell>.json (skips finished files); optional item-1 k*tau cells
    python -I sergent_gate.py summary        # -> out_gate/summary.json with the tier per signal size

Tiers (DESIGN.md section 4): 1 = recall >= 0.80 and every graded cell <= 0.10; 2 = recall < 0.80, graded all <= 0.10
(stream; one-sided reading); 3 = some graded cell > 0.10 (do not stream for the 5-model question).
"""
import json, sys, time
from pathlib import Path
from multiprocessing import Pool

import numpy as np
from scipy.special import expit

HERE = Path(__file__).resolve().parent
BIF = HERE.parents[0] / "bifurcation_specificity"
sys.path.insert(0, str(BIF))
import audit as A  # noqa: E402
import extended as E  # noqa: E402

OUT = HERE / "out_gate"
GRADED = ["G_jitter_mid", "G_jitter_hi", "G_heavy", "H_jitter_t", "H_gain"]
CELLS = ["B_bifurcation"] + GRADED
COUNTS = [168] * 18 + [176] * 2                      # per level, before rejection (Fig 1D)
RETAIN = 150 / 168
D_DECIDE, HET_SD = 0.89, 0.35
# (tag, dmax, heterogeneous, cells), in run order
PLAN = [("d0.89", 0.89, False, CELLS), ("het0.89", 0.89, True, CELLS),
        ("d1.0", 1.0, False, ["B_bifurcation"]), ("d1.25", 1.25, False, ["B_bifurcation"])]
STUDIES = 100
WORKERS = 4
SEED = 20261203


def counts():
    return [int(round(c * RETAIN)) for c in COUNTS]


_N = [None]


def design_counts(rng):
    x = np.repeat(A.LEVELS, _N[0])
    block = np.empty(len(x), int)
    for l in A.LEVELS:
        idx = np.where(x == l)[0]
        block[idx] = rng.permutation(np.arange(len(idx)) % A.N_BLOCK)
    return x, block


def gen(cell, rng):
    if cell.startswith("G_jitter_kt"):                # item-1 cell: jittered threshold at a fitted k*tau (KM per level)
        tau_lv = float(cell[len("G_jitter_kt"):]) / A.KM
        x, block = A.design(rng)
        th = A.X0 + rng.normal(0, tau_lv, len(x))
        return A.DMAX * expit(A.KM * (x - th)) + rng.normal(0, 1, len(x)), x, block
    return E.gen_ext(cell, rng)


def one_study(args):
    cell, seed, dmax, het = args
    A.design = design_counts                          # generators look these globals up at call time
    rng = np.random.default_rng(seed)
    lme = []
    for n in counts():
        _N[0] = n
        A.DMAX = dmax * np.exp(rng.normal(0, HET_SD) - HET_SD ** 2 / 2) if het else dmax
        y, x, block = gen(cell, rng)
        l, _, _ = E.subject_lme5(y, x, block)
        lme.append(l)
    lme = np.array(lme)
    if not np.all(np.isfinite(lme)):
        return dict(pxp3=float("nan"), winner=-1)
    pxp = A.spm_bms(lme, rng)["pxp"]
    return dict(pxp3=float(pxp[2]), winner=int(np.argmax(pxp)))


def run(kts):
    OUT.mkdir(exist_ok=True)
    plan = list(PLAN)
    if kts:                                           # item-1 cells go right after the deciding signal size
        plan.insert(1, ("d0.89", 0.89, False, [f"G_jitter_kt{k:g}" for k in kts]))
    for tag, dmax, het, cells in plan:
        for cell in cells:
            f = OUT / f"{tag}_{cell}.json"
            if f.exists():
                continue
            key = [SEED, int(round(dmax * 100)), int(het), sum(map(ord, cell))]
            seeds = [int(s.generate_state(1)[0]) for s in np.random.SeedSequence(key).spawn(STUDIES)]
            t = time.time()
            with Pool(WORKERS) as p:
                res = p.map(one_study, [(cell, s, dmax, het) for s in seeds])
            pxp3 = np.array([r["pxp3"] for r in res])
            call = np.where(np.isnan(pxp3), False, pxp3 > 0.95)
            r = dict(tag=tag, dmax=dmax, heterogeneous=het, cell=cell, studies=STUDIES, counts=counts(),
                     rate_call=float(call.mean()),
                     winner_counts=np.bincount([r["winner"] + 1 for r in res], minlength=6).tolist(),
                     nonfinite=int(np.isnan(pxp3).sum()), seconds=round(time.time() - t))
            f.write_text(json.dumps(r) + "\n")
            print(tag, cell, r["rate_call"], r["winner_counts"], r["seconds"], "s", flush=True)


def summary():
    S = {}
    for f in sorted(OUT.glob("*_*.json")):
        if f.name == "summary.json":
            continue
        r = json.loads(f.read_text())
        S.setdefault(r["tag"], {})[r["cell"]] = r["rate_call"]
    for tag, v in S.items():
        g = [c for c in v if c != "B_bifurcation"]
        if "B_bifurcation" in v and all(c in v for c in GRADED):
            spec = all(v[c] <= 0.10 for c in g)
            v["TIER"] = 1 if (spec and v["B_bifurcation"] >= 0.80) else (2 if spec else 3)
    (OUT / "summary.json").write_text(json.dumps(S, indent=1) + "\n")
    print(json.dumps(S, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run([float(k) for k in sys.argv[2:]])
    else:
        summary()
