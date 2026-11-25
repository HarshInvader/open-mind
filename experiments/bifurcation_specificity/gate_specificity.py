"""Round 17 #3: why did the 5-model comparison lose specificity at 38 subjects? (simulation only, zero data)
Prereg: docs/prereg/2026-11-25_bifurcation_gate_specificity.md

Follow-up 3 found G_jitter_hi (graded, jittered threshold: the exact family of model J) called bifurcation
(Model 3 pxp > 0.95 among 5) in 0.18 of studies at 38 subjects with real per-level counts, vs 0.007 at 20 subjects
x 150 per level (RESULTS.md). Two candidate causes:
  (a) sample size: random-effects BMS turns a small consistent per-subject edge into a confident call as N grows;
  (b) fit quality: the sealed fits stop at MATLAB's fminsearch budget (200*n evaluations; ~31% of fits report no
      convergence), so the true model J may be under-fit and lose out of sample to Model 3.
Design: Sergent's 150 trials per level (the real counts were close: median 128-154, min 115), N in {20, 38, 76}, so
subject count varies alone (no Cohen-derived counts). Sealed N = 20 outputs already show unprotected xp(M3) > 0.95 in
0.10 of G_jitter_hi studies, held to 0.007 by the omnibus-risk protection (BOR median 0.16): so BOR, xp and pxp are
all stored here.
Each simulated subject is fitted twice on the same data:
  STD  the sealed procedure (one fminsearch run per model and fold; identical to extended.subject_lme5);
  RST  each model's fit restarted from its own end point while fminsearch reports no convergence, at most MAX_RUNS
       runs in total, keeping the best training fit (same rule for all 5 models).
Descriptive (G_jitter_hi only): ORC, J also fitted from the generating parameters (with restarts); the better
TRAINING fit of RST-J and ORC-J is used. Real data has no oracle; this only asks whether RST-J is at its optimum.

    python -I gate_specificity.py check   # STD == extended.subject_lme5 for one subject (prints only the match)
    python -I gate_specificity.py pilot   # timing only
    python -I gate_specificity.py run     # sealed run -> out_gs/<cell>_n<N>.json (resume: finished files kept)
    python -I gate_specificity.py summary # verdicts -> out_gs/summary.json
"""
import json, sys, time
from pathlib import Path
from multiprocessing import Pool

import numpy as np
from scipy.stats import norm, t as tdist

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "rules"))
import audit as A  # noqa: E402
import extended as E  # noqa: E402

OUT = HERE / "out_gs"
PREREG = HERE.parents[1] / "docs" / "prereg" / "2026-11-25_bifurcation_gate_specificity.md"
# run order: primary cell first; G_jitter_hi N = 76 is secondary and is the first thing dropped by the fallback
CELLS_N = [("G_jitter_hi", 38), ("B_bifurcation", 38), ("G_jitter_hi", 20), ("G_jitter_hi", 76)]
CELL_IDX = {"G_jitter_hi": 0, "B_bifurcation": 1}
STUDIES = 100                 # fallbacks (prereg section 0): drop N = 76 if > 8 h; then 60 studies; > 14 h: stop
CHUNK = 20                    # studies per resume file
DROP_76 = False
BOR_CAP = 0.0625              # pxp3 can exceed 0.95 only if BOR < 0.0625 (pxp = (1 - BOR) xp + BOR / 5)
CONV_BAR = 0.95
WORKERS = 4
SEED = 20261737
MAX_RUNS = 4
CALL = 0.95
SPEC_BAR = 0.10               # the gate's specificity bar (graded call rate <= 0.10)
RECALL_BAR = 0.80             # the gate's recall bar
ORACLE_J = [A.X0, A.KM, A.DMAX, 1e-3, 1.5, 1.0]   # G_jitter_hi generating values for J: x0, k, L, c, tau, s


def neg(fn, y, x, usex):
    return (lambda p: -fn(p, y, x)) if usex else (lambda p: -fn(p, y))


def restart_fit(g, p, ok):
    """Continue from p while not converged; at most MAX_RUNS runs in total (p counts as run 1). Best training fit."""
    best, bv, runs = p, g(p), 1
    while not ok and runs < MAX_RUNS:
        p, ok = A.fminsearch(g, best)
        runs += 1
        v = g(p)
        if v < bv:
            best, bv = p, v
    return best, ok, runs


def subject(y, x, block, oracle):
    i0, i2, i3 = A.inits(y, x)
    ij, it = E.inits_ext(y, x)
    fits = [(A.llh_null, i0, False), (A.llh_2b, i2, True), (A.llh_3, i3, True), (E.llh_j, ij, True), (E.llh_t, it, True)]
    std, rst = np.zeros(5), np.zeros(5)
    orc = 0.0
    cs, cr, nr = np.zeros(5), np.zeros(5), np.zeros(5)
    for f in range(5):
        te = (block >= 4 * f) & (block < 4 * f + 4)
        tr = ~te
        pj = None
        for m, (fn, ini, usex) in enumerate(fits):
            g = neg(fn, y[tr], x[tr], usex)
            ev = neg(fn, y[te], x[te], usex)
            p1, ok1 = A.fminsearch(g, ini)
            std[m] -= ev(p1)
            cs[m] += ok1
            pr, okr, runs = restart_fit(g, p1, ok1)
            rst[m] -= ev(pr)
            cr[m] += okr
            nr[m] += runs
            if m == 3:
                pj = pr
        if oracle:
            g = neg(E.llh_j, y[tr], x[tr], True)
            po, oko = A.fminsearch(g, ORACLE_J)
            po, _, _ = restart_fit(g, po, oko)
            best = po if g(po) < g(pj) else pj
            orc += E.llh_j(best, y[te], x[te])
    return std / 5, rst / 5, cs / 5, cr / 5, nr / 5, (orc / 5 if oracle else np.nan)


def bms(lme, seed):
    """Full spm_bms output with a fresh stream per arm (paired arms get identical draws)."""
    if not np.all(np.isfinite(lme)):
        return None
    b = A.spm_bms(lme, np.random.default_rng(seed))
    return dict(pxp=[float(v) for v in b["pxp"]], xp=[float(v) for v in b["xp"]],
                freq=[float(v) for v in b["freq"]], bor=float(b["bor"]))


def one_study(args):
    cell, n_sub, seed = args
    rng = np.random.default_rng(seed)
    S, R, O, CS, CR, NR = [], [], [], [], [], []
    for _ in range(n_sub):
        y, x, block = A.gen(cell, rng)
        s_, r_, cs, cr, nr, o = subject(y, x, block, oracle=(cell == "G_jitter_hi"))
        S.append(s_); R.append(r_); O.append(o); CS.append(cs); CR.append(cr); NR.append(nr)
    S, R, O = np.array(S), np.array(R), np.array(O)
    out = dict(std=bms(S, seed + 1), rst=bms(R, seed + 1),
               conv_std=np.mean(CS, 0).tolist(), conv_rst=np.mean(CR, 0).tolist(), runs=np.mean(NR, 0).tolist(),
               lme_std=S.round(4).tolist(), lme_rst=R.round(4).tolist())
    if cell == "G_jitter_hi":
        RO = R.copy()
        RO[:, 3] = O
        out.update(orc=bms(RO, seed + 1), lme_orc_j=O.round(4).tolist())
    return out


def name(cell, n):
    return f"{cell}_n{n}"


def run_cell(cell, n):
    ss = np.random.SeedSequence([SEED, CELL_IDX[cell], n])
    seeds = [int(q.generate_state(1)[0]) for q in ss.spawn(STUDIES)]
    for c0 in range(0, STUDIES, CHUNK):
        f = OUT / f"{name(cell, n)}_{c0:03d}.json"
        if f.exists():
            continue
        t0 = time.time()
        with Pool(WORKERS) as p:
            res = p.map(one_study, [(cell, n, q) for q in seeds[c0:c0 + CHUNK]])
        r = dict(cell=cell, n=n, first=c0, studies=len(res), seconds=round(time.time() - t0), runs=res)
        tmp = f.with_suffix(".tmp")
        tmp.write_text(json.dumps(r) + "\n")
        tmp.rename(f)
        print(name(cell, n), c0, r["seconds"], "s", flush=True)


def load(cell, n):
    runs = []
    for c0 in range(0, STUDIES, CHUNK):
        r = json.loads((OUT / f"{name(cell, n)}_{c0:03d}.json").read_text())
        assert r["cell"] == cell and r["n"] == n and r["first"] == c0 and r["studies"] == min(CHUNK, STUDIES - c0)
        runs += r["runs"]
    assert len(runs) == STUDIES
    return runs


# ------------------------------------------------------------------ statistics
Z = norm.ppf(0.95)            # one-sided 95%


def wilson(k, n):
    p = k / n
    c = (p + Z * Z / (2 * n)) / (1 + Z * Z / n)
    h = Z * np.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / (1 + Z * Z / n)
    return c - h, c + h


def newcombe_lower(k1, n1, k0, n0):
    """One-sided 95% lower bound of p1 - p0 (Newcombe hybrid score, independent samples)."""
    l1, u1 = wilson(k1, n1)
    l0, u0 = wilson(k0, n0)
    p1, p0 = k1 / n1, k0 / n0
    return (p1 - p0) - np.sqrt((p1 - l1) ** 2 + (u0 - p0) ** 2)


def mcnemar_p(b, c):
    """Exact one-sided p that STD calls exceed RST calls: b = called STD only, c = called RST only."""
    from scipy.stats import binom
    return float(binom.sf(b - 1, b + c, 0.5)) if b + c else 1.0


def called(r, arm):
    return r.get(arm) is not None and r[arm]["pxp"][2] > CALL


def arm_stats(runs, arm, lkey):
    ok = [r for r in runs if r.get(arm) is not None]
    k = sum(called(r, arm) for r in runs)
    lo, hi = wilson(k, STUDIES)
    d = []
    for r in ok:
        L = np.array(r[lkey])
        if arm == "orc":
            L = np.array(r["lme_rst"]); L[:, 3] = r["lme_orc_j"]
        d.append(float(np.mean(L[:, 2] - L[:, 3])))
    xp_hi = sum(r[arm]["xp"][2] > CALL for r in ok)
    bor_lo = sum(r[arm]["bor"] < BOR_CAP for r in ok)
    return dict(calls=k, rate=k / STUDIES, wilson_lo95=float(lo), wilson_hi95=float(hi), nonfinite=STUDIES - len(ok),
                rate_xp3_gt_095=xp_hi / STUDIES, rate_bor_lt_cap=bor_lo / STUDIES,
                rate_both=sum(r[arm]["xp"][2] > CALL and r[arm]["bor"] < BOR_CAP for r in ok) / STUDIES,
                bor_median=float(np.median([r[arm]["bor"] for r in ok])) if ok else None,
                d_m3_minus_j=tint(d) if len(d) > 1 else None)


def cell_stats(runs, cell):
    row = {a: arm_stats(runs, a, f"lme_{a}" if a != "orc" else "lme_rst")
           for a in (("std", "rst", "orc") if cell == "G_jitter_hi" else ("std", "rst"))}
    so = sum(called(r, "std") and not called(r, "rst") for r in runs)
    ro = sum(called(r, "rst") and not called(r, "std") for r in runs)
    row.update(paired_std_only=so, paired_rst_only=ro, mcnemar_p_std_gt_rst=mcnemar_p(so, ro))
    row["conv_std_by_model"] = np.mean([r["conv_std"] for r in runs], 0).tolist()
    row["conv_rst_by_model"] = np.mean([r["conv_rst"] for r in runs], 0).tolist()
    row["runs_by_model"] = np.mean([r["runs"] for r in runs], 0).tolist()
    row["heldout_gain_rst_minus_std_by_model"] = np.mean(
        [np.mean(np.array(r["lme_rst"]) - np.array(r["lme_std"]), 0) for r in runs], 0).tolist()
    for a in ("std", "rst"):
        row[f"best_{a}"] = np.sum([np.bincount(np.argmax(np.array(r[f"lme_{a}"]), 1), minlength=5) for r in runs],
                                  0).tolist()
    if cell == "G_jitter_hi":
        row["j_heldout_gain_orc_vs_rst"] = tint([np.mean(np.array(r["lme_orc_j"]) - np.array(r["lme_rst"])[:, 3])
                                                 for r in runs])
    return row


def q2_verdict(g, b):
    if g["std"]["wilson_lo95"] <= SPEC_BAR:
        return "NOT APPLICABLE: NO SPECIFICITY LOSS SHOWN AT THIS N"
    p = g["mcnemar_p_std_gt_rst"]
    if g["rst"]["wilson_hi95"] <= SPEC_BAR and p < 0.05:
        return ("FIT-BUDGET ARTEFACT: RESTARTS RESTORE SPECIFICITY" if b["rst"]["rate"] >= RECALL_BAR
                else "FIT-BUDGET ARTEFACT, BUT RESTARTS COST RECALL")
    if g["rst"]["wilson_lo95"] > SPEC_BAR:
        optimum = (g.get("orc") is not None and g["orc"]["wilson_lo95"] > SPEC_BAR
                   and g["conv_rst_by_model"][2] >= CONV_BAR and g["conv_rst_by_model"][3] >= CONV_BAR)
        if p < 0.05:
            return "PARTIAL: RESTARTS REDUCE BUT DO NOT REMOVE THE LOSS"
        return ("NOT A FIT-BUDGET ARTEFACT: SPECIFICITY STILL LOST WITH RESTARTS" if optimum
                else "UNRESOLVED: OPTIMUM NOT SHOWN")
    return "UNRESOLVED"


def summary():
    sealed()
    cells = [(c, n) for c, n in CELLS_N if not (DROP_76 and n == 76)]
    R = {(c, n): load(c, n) for c, n in cells}
    tab = {name(c, n): cell_stats(R[(c, n)], c) for c, n in cells}
    k = {n: tab[f"G_jitter_hi_n{n}"]["std"]["calls"] for c, n in cells if c == "G_jitter_hi"}
    q1_lo = float(newcombe_lower(k[38], STUDIES, k[20], STUDIES))
    q1 = "STD CALL RATE RISES FROM 20 TO 38 SUBJECTS" if q1_lo > 0 else "NO DETECTABLE RISE FROM 20 TO 38 SUBJECTS"
    b = tab["B_bifurcation_n38"]
    S = dict(q1=dict(verdict=q1, newcombe_lo95_onesided=q1_lo,
                     lo95_76_vs_38=float(newcombe_lower(k[76], STUDIES, k[38], STUDIES)) if 76 in k else None),
             q2_primary_n38=dict(verdict=q2_verdict(tab["G_jitter_hi_n38"], b)),
             q2_secondary_n76=dict(verdict=q2_verdict(tab["G_jitter_hi_n76"], b)) if 76 in k else None,
             recall_b_n38=dict(std=b["std"]["rate"], rst=b["rst"]["rate"]), cells=tab, drop_76=DROP_76, studies=STUDIES)
    (OUT / "summary.json").write_text(json.dumps(S, indent=1) + "\n")
    print(q1, "|", S["q2_primary_n38"]["verdict"], "|", S["q2_secondary_n76"])
    for kk, v in tab.items():
        print(kk, {a: (v[a]["calls"], v[a]["rate_xp3_gt_095"], v[a]["rate_bor_lt_cap"]) for a in ("std", "rst", "orc") if a in v})


# ------------------------------------------------------------------ entry points
def sealed():
    from evidence import require_sealed
    for f in (PREREG, Path(__file__), HERE / "audit.py", HERE / "extended.py"):
        require_sealed(str(f))
    OUT.mkdir(exist_ok=True)


def check():
    """STD must equal the sealed extended.subject_lme5 on the same subject; prints only the match and timing."""
    rng = np.random.default_rng(1)
    y, x, block = A.gen("G_jitter_mid", rng)
    t0 = time.time()
    ref, _, _ = E.subject_lme5(y, x, block)
    std, *_ = subject(y, x, block, oracle=True)
    print("STD == subject_lme5:", bool(np.allclose(std, ref, rtol=0, atol=1e-9)), "| seconds", round(time.time() - t0, 1))


def pilot():
    t0 = time.time()
    one_study(("G_jitter_hi", 20, 12345))          # output discarded; only the time is printed
    print("one G_jitter_hi study at 20 subjects (STD + RST + ORC), seconds:", round(time.time() - t0, 1))


def run():
    sealed()
    for c, n in CELLS_N:
        if DROP_76 and n == 76:
            continue
        run_cell(c, n)


if __name__ == "__main__":
    {"check": check, "pilot": pilot, "run": run, "summary": summary}[sys.argv[1]]()
