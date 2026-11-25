"""Item 2 design gate: is the 5-model comparison specific and sensitive at Sergent et al. 2021's own design?
Design: experiments/sergent_eeg/DESIGN.md. Synthetic data only; runs BEFORE any Sergent EEG is streamed.

Same generators, fitting, CV and spm_BMS as the sealed audit.py / extended.py (imported, not edited). Only the design
changes: 20 subjects, per-level counts 168 (18 subjects) or 176 (2 subjects), inferred exactly from their Fig 1D, scaled
by 150/168 to the paper's post-rejection size; signal size DMAX 0.89 reproduces their published max-level AUC (0.731).

    python -I sergent_gate.py run [KT ...]   # -> out_gate/<tag>_<cell>.json (skips finished files); optional item-1 k*tau cells
    python -I sergent_gate.py rerun          # after streaming: tag 'meas' at the measured DMAX and real per-subject,
                                             # per-level counts (out_real/measured.json), with the k*tau cells fixed
                                             # at the first run (out_gate/kt.json); plus B with the measured
                                             # across-subject log-SD of DMAX ('meas_het'). The 'meas' tier decides.
    python -I sergent_gate.py summary        # -> out_gate/summary.json with the tier per signal size

Tiers (DESIGN.md section 4): 1 = recall >= 0.80 and every graded cell <= 0.10; 2 = recall < 0.80, graded all <= 0.10
(stream; one-sided reading); 3 = some graded cell > 0.10 (do not stream for the 5-model question).
"""
import json, sys, time
from pathlib import Path
from multiprocessing import Pool

import numpy as np
from scipy.special import expit
from scipy.stats import kurtosis, skew

HERE = Path(__file__).resolve().parent
BIF = HERE.parents[0] / "bifurcation_specificity"
sys.path.insert(0, str(BIF))
import audit as A  # noqa: E402
import extended as E  # noqa: E402

OUT = HERE / "out_gate"
KTF = OUT / "kt.json"
PREREG = HERE.parents[1] / "docs" / "prereg" / "2026-11-25_sergent_eeg_five_models.md"
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


def bimod(v):
    """Sarle's bimodality coefficient."""
    n = len(v)
    return (skew(v) ** 2 + 1) / (kurtosis(v) + 3 * (n - 1) ** 2 / ((n - 2) * (n - 3)))


def fold_z(v, fold):
    """Standardise within decoder fold (removes fold-to-fold mean and scale differences of the decoder; prereg §5c)."""
    out = np.empty(len(v))
    for f in np.unique(fold):
        m = fold == f
        out[m] = (v[m] - v[m].mean()) / v[m].std(ddof=1)
    return out


def flips(lme, k=2, thr=0.95, seed=20261205):
    """Greedy: drop the subject with the largest log-evidence advantage for model k until pxp[k] <= thr.
    Returns the number dropped (len(lme) if it never flips; 0 if pxp[k] <= thr already)."""
    keep = list(range(len(lme)))
    for n in range(len(lme) - 2):
        p = A.spm_bms(lme[keep], np.random.default_rng(seed))["pxp"]
        if p[k] <= thr:
            return n
        adv = [lme[i, k] - np.delete(lme[i], k).max() for i in keep]
        keep.pop(int(np.argmax(adv)))
    return len(lme)


def drop_nonfinite(lme):
    """F4 parity with the real data: drop non-finite subjects; None if more than 2."""
    ok = np.all(np.isfinite(lme), axis=1)
    return lme[ok] if ok.sum() >= len(lme) - 2 else None


def one_study(args):
    cell, seed, dmax, het, cnts, want_flips = args
    A.design = design_counts                          # generators look these globals up at call time
    rng = np.random.default_rng(seed)
    lme, bc5 = [], []
    for n in cnts:
        _N[0] = n                                     # scalar (same per level) or a 6-list of per-level counts
        sd = het if isinstance(het, float) else (HET_SD if het else 0.0)
        A.DMAX = dmax * np.exp(rng.normal(0, sd) - sd ** 2 / 2) if sd else dmax
        y, x, block = gen(cell, rng)
        l, _, _ = E.subject_lme5(y, x, block)
        lme.append(l)
        y5 = y[x == 5]
        bc5.append(bimod(fold_z(y5, np.arange(len(y5)) % 10)))   # same within-fold standardisation as the real data
    lme = drop_nonfinite(np.array(lme))
    if lme is None:
        return dict(pxp3=float("nan"), pxp3_3m=float("nan"), winner=-1, bc5=float(np.median(bc5)), flip=None)
    pxp = A.spm_bms(lme, rng)["pxp"]
    pxp_3m = A.spm_bms(lme[:, :3], rng)["pxp"]       # columns 0..2 are exactly the 3-model (null, 2B, M3) LMEs
    flip = flips(lme[:, :3]) if (want_flips and pxp_3m[2] > 0.95) else None
    return dict(pxp3=float(pxp[2]), pxp3_3m=float(pxp_3m[2]), winner=int(np.argmax(pxp)), bc5=float(np.median(bc5)),
                flip=flip)


def require_seal():
    sys.path.insert(0, str(HERE.parents[0] / "rules"))
    from evidence import require_sealed
    require_sealed(str(PREREG)); require_sealed(str(Path(__file__)))


def kt_cells():
    return [f"G_jitter_kt{k:g}" for k in json.loads(KTF.read_text())["kt"]]


def run(kts, plan=None, cnts=None, stamp=None):
    require_seal()
    OUT.mkdir(exist_ok=True)
    if plan is None:
        if KTF.exists():                              # the item-1 values are fixed at the first run (prereg §6)
            assert json.loads(KTF.read_text())["kt"] == kts, f"k*tau must match {KTF.name}"
        else:
            KTF.write_text(json.dumps(dict(kt=kts)) + "\n")
        plan = list(PLAN)
        if kts:                                       # item-1 cells go right after the deciding signal size
            plan.insert(1, ("d0.89", 0.89, False, kt_cells()))
    cnts = cnts or counts()
    for tag, dmax, het, cells in plan:
        for cell in cells:
            f = OUT / f"{tag}_{cell}.json"
            if f.exists():
                if stamp is not None:
                    old = json.loads(f.read_text())
                    assert old.get("stamp") == stamp, f"{f.name} was made at another measured size or counts: stale"
                continue
            key = [SEED, int(round(dmax * 100)), int(round(float(het) * 1000)), sum(map(ord, tag)), sum(map(ord, cell))]
            seeds = [int(s.generate_state(1)[0]) for s in np.random.SeedSequence(key).spawn(STUDIES)]
            want = tag.startswith("meas") and cell == "B_bifurcation"
            t = time.time()
            with Pool(WORKERS) as p:
                res = p.map(one_study, [(cell, s, dmax, het, cnts, want) for s in seeds])
            pxp3 = np.array([r["pxp3"] for r in res])
            call = np.where(np.isnan(pxp3), False, pxp3 > 0.95)
            p3m = np.array([r["pxp3_3m"] for r in res])
            fl = [r["flip"] for r in res if r["flip"] is not None]
            r = dict(tag=tag, dmax=dmax, heterogeneous=het, cell=cell, studies=STUDIES, counts=cnts, stamp=stamp,
                     rate_call=float(call.mean()),
                     rate_call_3model=float(np.where(np.isnan(p3m), False, p3m > 0.95).mean()),
                     bc5_median=float(np.median([r["bc5"] for r in res])),
                     bc5_p95=float(np.percentile([r["bc5"] for r in res], 95)),
                     flips_3model_calls=fl,
                     winner_counts=np.bincount([r["winner"] + 1 for r in res], minlength=6).tolist(),
                     nonfinite=int(np.isnan(pxp3).sum()), seconds=round(time.time() - t))
            f.write_text(json.dumps(r) + "\n")
            print(tag, cell, r["rate_call"], r["rate_call_3model"], r["winner_counts"], r["seconds"], "s", flush=True)


def rerun():
    m = json.loads((HERE / "out_real" / "measured.json").read_text())
    d = round(m["dmax_median"], 3)
    cnts = list(m["counts"].values())
    stamp = dict(dmax=d, log_sd=round(m["log_sd"], 3), counts=cnts)
    cells = CELLS[:1] + kt_cells() + CELLS[1:]
    run(None, plan=[("meas", d, False, cells), ("meas_het", d, round(m["log_sd"], 3), ["B_bifurcation"])],
        cnts=cnts, stamp=stamp)


def summary():
    S = {}
    for f in sorted(OUT.glob("*_*.json")):
        if f.name in ("summary.json", KTF.name):
            continue
        r = json.loads(f.read_text())
        S.setdefault(r["tag"], {})[r["cell"]] = r["rate_call"]
    need = GRADED + (kt_cells() if KTF.exists() else [])
    for tag, v in S.items():
        if tag in ("d0.89", "meas"):                  # the two tags with a tier; every graded and item-1 cell required
            if "B_bifurcation" in v and all(c in v for c in need):
                spec = all(v[c] <= 0.10 for c in need)
                v["TIER"] = 1 if (spec and v["B_bifurcation"] >= 0.80) else (2 if spec else 3)
            else:
                v["TIER"] = None
                v["missing"] = [c for c in ["B_bifurcation"] + need if c not in v]
    (OUT / "summary.json").write_text(json.dumps(S, indent=1) + "\n")
    print(json.dumps(S, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run([float(k) for k in sys.argv[2:]])
    elif sys.argv[1] == "rerun":
        rerun()
    else:
        summary()
