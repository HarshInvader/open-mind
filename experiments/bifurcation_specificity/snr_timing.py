"""Is "early unimodal, late bifurcated" (Sergent et al. 2021) what weak true two-state data would show anyway?
Prereg: docs/prereg/2026-11-25_bifurcation_snr_timing.md

Sergent et al. report that the unimodal model (2B) "showed the highest probability" from 0 to 250 ms and again from
700 to 900 ms, and that Model 3 won from 250 to 700 ms. The signal is weaker in the early and late periods. Here: true
two-state data (their Model 3 shape, B_bifurcation) on a grid of signal sizes, analysed with their comparison
(models 0, 2B, 3) and, as a secondary, the extended set (0, 2B, 3, J, T). Which model wins as the signal shrinks?

Same generators, fitting, CV and spm_BMS as the sealed audit.py / extended.py (imported, not edited); only DMAX changes.
The max-level decoder separation of each grid point is reported as an AUC (level 5 vs level 0), so the result can be
read against published decoding curves.

    python -I snr_timing.py run3        # primary: 3-model comparison -> out_snr/m3_<cell>_d<DMAX>.json
    python -I snr_timing.py run5        # secondary: 5-model comparison, B only -> out_snr/m5_B_bifurcation_d<DMAX>.json
    python -I snr_timing.py summary     # verdict -> out_snr/summary.json
"""
import json, sys, time
from pathlib import Path
from multiprocessing import Pool

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "rules"))
import audit as A  # noqa: E402
import extended as E  # noqa: E402

OUT = HERE / "out_snr"
PREREG = HERE.parents[1] / "docs" / "prereg" / "2026-11-25_bifurcation_snr_timing.md"
DMAXES = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0]
CELLS3 = ["B_bifurcation", "M2_unimodal"]
STUDIES = 100
WORKERS = 3
SEED = 20261202
AUC_INFORMATIVE = 0.60     # verdict thresholds on the max-level AUC (prereg section 2)
AUC_BLIND = 0.69       # DMAX 0.75 gives AUC 0.699; the bound sits just below it so that grid point counts


def max_level_auc(cell, dmax, rng, n=200_000):
    """AUC of level 5 vs level 0 for the generator at this DMAX (label-free property of the generator)."""
    old_design, old_dmax = A.design, A.DMAX
    try:
        A.DMAX = dmax
        ys = {}
        for lev in (0, 5):
            A.design = lambda r, lev=lev: (np.full(n, lev), np.zeros(n, int))
            y, _, _ = A.gen(cell, rng)
            ys[lev] = y
    finally:
        A.design, A.DMAX = old_design, old_dmax
    from scipy.stats import mannwhitneyu
    u = mannwhitneyu(ys[5], ys[0]).statistic
    return float(u / (n * n))


def one_study(args):
    cell, seed, dmax, five = args
    A.DMAX = dmax
    rng = np.random.default_rng(seed)
    lme = []
    for _ in range(A.N_SUB):
        y, x, block = A.gen(cell, rng)
        if five:
            l, _, _ = E.subject_lme5(y, x, block)
        else:
            l, _ = A.subject_lme(y, x, block)
        lme.append(l)
    lme = np.array(lme)
    if not np.all(np.isfinite(lme)):
        return dict(finite=False)
    out = dict(finite=True)
    b3 = A.spm_bms(lme[:, :3], rng)["pxp"]
    out.update(pxp3=[float(v) for v in b3], win3=int(np.argmax(b3)))
    if five:
        b5 = A.spm_bms(lme, rng)["pxp"]
        out.update(pxp5=[float(v) for v in b5], win5=int(np.argmax(b5)))
    return out


def run_cell(tag, cell, dmax, five):
    f = OUT / f"{tag}_{cell}_d{dmax:g}.json"
    if f.exists():                                             # resume rule: finished files kept
        return
    ss = np.random.SeedSequence([SEED, int(five), CELLS3.index(cell), int(dmax * 100)])
    seeds = [int(s.generate_state(1)[0]) for s in ss.spawn(STUDIES)]
    t = time.time()
    with Pool(WORKERS) as p:
        res = p.map(one_study, [(cell, s, dmax, five) for s in seeds])
    fin = [r for r in res if r["finite"]]
    r = dict(cell=cell, dmax=dmax, models=5 if five else 3, studies=STUDIES, nonfinite=STUDIES - len(fin),
             auc_max_level=max_level_auc(cell, dmax, np.random.default_rng(SEED)),
             win3=np.bincount([x["win3"] for x in fin], minlength=3).tolist(),
             call3=float(np.mean([x["finite"] and x["pxp3"][2] > 0.95 for x in res])),
             call2b_3=float(np.mean([x["finite"] and x["pxp3"][1] > 0.95 for x in res])),
             seconds=round(time.time() - t))
    if five:
        r.update(win5=np.bincount([x["win5"] for x in fin], minlength=5).tolist(),
                 call5=float(np.mean([x["finite"] and x["pxp5"][2] > 0.95 for x in res])))
    r["runs"] = res
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(r) + "\n")
    tmp.rename(f)
    print(tag, cell, dmax, round(r["auc_max_level"], 3), r["win3"], r.get("win5"), r["nonfinite"], r["seconds"], "s",
          flush=True)


def sealed():
    from evidence import require_sealed
    for f in (PREREG, Path(__file__), HERE / "audit.py", HERE / "extended.py"):
        require_sealed(str(f))
    OUT.mkdir(exist_ok=True)


def run3():
    sealed()
    for d in DMAXES:
        for c in CELLS3:
            run_cell("m3", c, d, False)


def run5():
    sealed()
    for d in DMAXES:
        run_cell("m5", "B_bifurcation", d, True)


def summary():
    R = {}
    for f in sorted(OUT.glob("m3_*.json")):
        r = json.loads(f.read_text())
        R.setdefault(r["cell"], {})[r["dmax"]] = r
    B = R["B_bifurcation"]
    rows = []
    for d in DMAXES:
        r = B[d]
        n = STUDIES                                            # shares over all studies; non-finite counts for no model
        rows.append(dict(dmax=d, auc=r["auc_max_level"], share_m3_top=r["win3"][2] / n, share_2b_top=r["win3"][1] / n,
                         share_null_top=r["win3"][0] / n, nonfinite=r["nonfinite"], call3=r["call3"],
                         call2b=r["call2b_3"]))
    valid = B[2.0]["win3"][2] / STUDIES >= 0.80                # must reproduce the sealed audit (prereg section 3)
    informative = all(x["share_m3_top"] >= 0.80 for x in rows if x["auc"] >= AUC_INFORMATIVE)
    blind = any(x["share_2b_top"] > 0.50 for x in rows if x["auc"] >= AUC_BLIND)
    if not valid:
        verdict = "INVALID"
    elif informative:
        verdict = "SEES WEAK TWO-STATE SIGNALS"
    elif blind:
        verdict = "BLIND ZONE REACHES AUC 0.70"
    else:
        verdict = "NEITHER CONDITION MET"
    first = [x["auc"] for x in rows if x["share_m3_top"] >= 0.80]
    s = dict(verdict=verdict, rows=rows, auc_where_m3_first_top_in_80pct=min(first) if first else None,
             m2_unimodal={d: dict(auc=R["M2_unimodal"][d]["auc_max_level"], win3=R["M2_unimodal"][d]["win3"])
                          for d in DMAXES if d in R.get("M2_unimodal", {})},
             five_model={json.loads(f.read_text())["dmax"]: dict(win5=json.loads(f.read_text())["win5"],
                                                                  call5=json.loads(f.read_text())["call5"])
                         for f in sorted(OUT.glob("m5_*.json"))})
    (OUT / "summary.json").write_text(json.dumps(s, indent=1) + "\n")
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    {"run3": run3, "run5": run5, "summary": summary}[sys.argv[1]]()
