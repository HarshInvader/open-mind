"""Item 2 analysis on the streamed decoder outputs. Prereg: docs/prereg/2026-11-25_sergent_eeg_five_models.md.

    python -I analyse.py measure   # once, after streaming finished: measured DMAX, its across-subject log-SD, real counts
    python -I analyse.py fit       # after measure: 3- and 5-model LMEs, all 53 windows, both solvers (Pool(4))
    python -I analyse.py readout   # R1 replication -> R2 5-model verdict ('meas' tier) -> puzzle tests (a)(b)(c)

Model fits are the sealed audit.subject_lme / extended.subject_lme5, unchanged; x = snr - 1 (their coding), fold = 4
consecutive blocks (block - 1, 0-based). spm_BMS = audit.spm_bms with fixed seeds. Nothing here re-decodes the EEG.
Primary solver = liblinear ('win'); lbfgs ('win_lbfgs') enters R1 as a descriptive line only.
"""
import json, sys
from pathlib import Path
from multiprocessing import Pool

import numpy as np
from scipy.stats import kurtosis

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "bifurcation_specificity"))
sys.path.insert(0, str(HERE))
import audit as A  # noqa: E402
import extended as E  # noqa: E402
import sergent_gate as G  # noqa: E402
from sergent_gate import bimod, fold_z, flips  # noqa: E402

DEC = HERE.parents[1] / "datasets" / "local" / "sergent2021_decoded"
OUT = HERE / "out_real"
GATE = HERE / "out_gate"
PRIMARY = list(range(23, 29))          # 1-based windows 23..28 = 360..540 ms: their Fig 3E run of Model 3 pxp > 0.95
N_SUB, MIN_SUBJ, NEED = 20, 18, 4
MIN_LEVEL = 60                         # trials per level; fewer -> subject excluded
SEED = 20261205
KURT_BAR = 0.5                         # heavy tails also need median level-0 excess kurtosis > 0.5 (t(16)-like)
H1_HI, H1_LO = 0.80, 0.30


def require_seal():
    G.require_seal()                                  # prereg + sergent_gate.py
    from evidence import require_sealed
    require_sealed(str(Path(__file__)))


def subjects(key="win"):
    out, excl = {}, {}
    for f in sorted(DEC.glob("S*.npz")):
        if ".tmp" in f.name:
            continue
        d = np.load(f)
        info = d["trialinfo"]
        block, snr = info[:, 0].astype(int), info[:, 1].astype(int)
        cnt = np.bincount(snr - 1, minlength=6)
        if cnt.min() < MIN_LEVEL:
            excl[f.stem] = f"level counts {cnt.tolist()}"; continue
        if any(((block - 1) // 4 == k).sum() == 0 for k in range(5)):
            excl[f.stem] = "empty CV fold"; continue
        if not np.all(np.isfinite(d[key][:, [j - 1 for j in PRIMARY]])):
            excl[f.stem] = "non-finite primary window (F10)"; continue
        out[f.stem] = dict(win=d[key].astype(float), diag=d["diag"].astype(float), x=snr - 1, block=block - 1,
                           fold=d["fold"], time=d["time"])
    return out, excl


def auc(a, b):
    """P(a > b) + 0.5 P(tie), Mann-Whitney."""
    r = np.argsort(np.argsort(np.r_[a, b])) + 1
    return (r[:len(a)].sum() - len(a) * (len(a) + 1) / 2) / (len(a) * len(b))


def stream_complete():
    log = DEC / "stream_log.jsonl"
    recs = [json.loads(l) for l in log.read_text().splitlines() if l.strip()] if log.exists() else []
    return {r["sub"] for r in recs} == set(range(1, N_SUB + 1))


def measure():
    require_seal()
    f = OUT / "measured.json"
    assert not f.exists(), "measured.json is frozen once written"
    assert stream_complete(), "streaming has not finished every subject (ok or skip)"
    S, excl = subjects()
    if len(S) < MIN_SUBJ:
        raise SystemExit(f"{len(S)} usable subjects < {MIN_SUBJ}: INVALID (F1); no gate re-run")
    dm = {}
    for s, d in S.items():
        w = d["win"][:, [j - 1 for j in PRIMARY]]
        l0, l5 = w[d["x"] == 0], w[d["x"] == 5]
        dm[s] = float(np.mean((l5.mean(0) - l0.mean(0)) / l0.std(0, ddof=1)))     # mean over the primary windows
    v = np.array(list(dm.values()))
    pos = v[v > 0]                    # log-SD over subjects with positive DMAX; the number excluded is reported
    r = dict(n_subjects=len(S), excluded=excl, dmax_per_subject=dm, dmax_median=float(np.median(v)),
             log_sd=float(np.std(np.log(pos), ddof=1)), n_nonpositive_dmax=int((v <= 0).sum()),
             counts={s: np.bincount(d["x"], minlength=6).tolist() for s, d in S.items()})
    OUT.mkdir(exist_ok=True)
    f.write_text(json.dumps(r, indent=1) + "\n")
    print(f"{len(S)} subjects; measured DMAX median {r['dmax_median']:.3f}, log-SD {r['log_sd']:.3f}")


def _fit(args):
    s, j, y, x, block = args
    if not np.all(np.isfinite(y)):
        return s, j, np.full(3, np.nan), np.full(5, np.nan), np.nan
    l3, _ = A.subject_lme(y, x, block)
    l5, _, kj = E.subject_lme5(y, x, block)
    return s, j, l3, l5, kj


def fit():
    require_seal()
    assert (OUT / "measured.json").exists(), "run measure first (it freezes the measured size before any model fit)"
    res = {}
    for key, wins in (("win", range(53)), ("win_lbfgs", [j - 1 for j in PRIMARY])):
        f = OUT / f"lme_{key}.npz"
        if f.exists():
            continue
        S, _ = subjects(key)
        names = sorted(S)
        jobs = [(s, j, S[s]["win"][:, j], S[s]["x"], S[s]["block"]) for j in wins for s in names]
        L3 = np.full((53, len(names), 3), np.nan); L5 = np.full((53, len(names), 5), np.nan)
        KJ = np.full((53, len(names)), np.nan)
        with Pool(4) as p:
            for s, j, l3, l5, kj in p.imap_unordered(_fit, jobs, chunksize=4):
                i = names.index(s); L3[j, i], L5[j, i], KJ[j, i] = l3, l5, kj
        np.savez(f, L3=L3, L5=L5, KJ=KJ, names=np.array(names))
        res[key] = L3.shape
    print("fit done", res)


def bms(lme, seed):
    """F4: drop non-finite subjects; no outcome if more than 2 are dropped."""
    ok = np.all(np.isfinite(lme), axis=1)
    if ok.sum() < len(lme) - 2:
        return None
    return A.spm_bms(lme[ok], np.random.default_rng(seed))["pxp"]


def gate_file(tag, cell):
    f = GATE / f"{tag}_{cell}.json"
    return json.loads(f.read_text()) if f.exists() else None


def readout():
    require_seal()
    assert not (OUT / "result.json").exists(), "the first result.json is final"
    G.summary()                                       # the tier is always recomputed from the gate files on disk
    S, excl = subjects()
    d = np.load(OUT / "lme_win.npz")
    L3, L5, KJ, names = d["L3"], d["L5"], d["KJ"], list(d["names"])
    res = dict(n_subjects=len(names), excluded=excl, primary_windows=PRIMARY)
    # ---- R1: replication of their 3-model result
    p3 = [bms(L3[j], SEED + j) for j in range(53)]
    p5 = [bms(L5[j], SEED + 100 + j) for j in range(53)]
    res["pxp3_M3"] = [None if p is None else float(p[2]) for p in p3]
    res["pxp5"] = [None if p is None else [float(v) for v in p] for p in p5]
    called3 = [j for j in PRIMARY if p3[j - 1] is not None and p3[j - 1][2] > 0.95]
    res["replication"] = dict(windows_M3_gt_095=len(called3), passed=len(called3) >= NEED)
    if (OUT / "lme_win_lbfgs.npz").exists():          # descriptive only
        Lb = np.load(OUT / "lme_win_lbfgs.npz")["L3"]
        pb = [bms(Lb[j - 1], SEED + j - 1) for j in PRIMARY]
        res["replication_lbfgs_descriptive"] = sum(1 for p in pb if p is not None and p[2] > 0.95)
    # ---- R2: 5-model verdict, tier from the gate re-run at the measured size
    gs = json.loads((GATE / "summary.json").read_text()) if (GATE / "summary.json").exists() else {}
    tier = gs.get("meas", {}).get("TIER")
    res["tier"] = tier
    surv = sum(1 for j in PRIMARY if p5[j - 1] is not None and p5[j - 1][2] > 0.95)
    rival = sum(1 for j in PRIMARY if p5[j - 1] is not None and max(p5[j - 1][3], p5[j - 1][4]) > 0.95)
    res["five_model_windows"] = dict(M3=surv, J_or_T=rival)
    if len(names) < MIN_SUBJ:
        res["result"] = f"INVALID: {len(names)} usable subjects (< {MIN_SUBJ}); descriptives and puzzle tests only"
    elif not res["replication"]["passed"]:
        res["result"] = "PORT DOES NOT REPRODUCE their 3-model result; 5-model reported descriptively, no verdict"
    elif tier is None:
        res["result"] = "NO 5-MODEL VERDICT: the measured-size gate ('meas') is missing or incomplete"
    elif tier == 3:
        res["result"] = "NO 5-MODEL VERDICT: gate tier 3 at the measured size (not specific at this design)"
    elif surv >= NEED:
        res["result"] = "TWO-STATE SURVIVES fair graded rivals"
    elif tier == 2:
        res["result"] = "UNRESOLVED (tier 2, low power): not evidence against two states"
    elif rival >= NEED:
        res["result"] = "GRADED RIVAL WINS"
    elif surv <= NEED - 2:
        res["result"] = "TWO-STATE LOST ITS EDGE"
    else:
        res["result"] = "UNRESOLVED"
    # ---- puzzle tests (every tier, whatever R1 says)
    P = {}
    meas = json.loads((OUT / "measured.json").read_text())
    gB, gH = gate_file("meas", "B_bifurcation"), gate_file("meas_het", "B_bifurcation")
    # (a) H1: is the window-level signal strong enough for their 3-model call to be routine?
    a_s, a_w = [], []
    for s in names:
        dd = S[s]
        t_ms = np.round(dd["time"] * 1000, 3)
        m = (t_ms >= 360) & (t_ms <= 540)
        l0, l5 = dd["x"] == 0, dd["x"] == 5
        a_s.append(np.mean([auc(dd["diag"][l5, t], dd["diag"][l0, t]) for t in np.where(m)[0]]))
        a_w.append(np.mean([auc(dd["win"][l5, j - 1], dd["win"][l0, j - 1]) for j in PRIMARY]))
    rB = None if gB is None else gB["rate_call_3model"]
    pf = HERE.parents[1] / "datasets" / "local" / "sergent2021_source" / "csv" / "Figure_3_Panel_F.csv"
    their_w = None
    if pf.exists():                                   # descriptive: their per-subject window AUC (Fig 3F), primary mean
        import csv
        rows = [r for r in csv.reader(open(pf)) if len(r) >= 53 and r[0][:1].isdigit()]
        their_w = float(np.mean([[float(v) for v in r[:53]] for r in rows], axis=0)[[j - 1 for j in PRIMARY]].mean())
    P["a"] = dict(auc_sample_mean=float(np.mean(a_s)), auc_window_mean=float(np.mean(a_w)), their_fig3f_window_auc=their_w,
                  dmax_measured=meas["dmax_median"], meas_B_3model_call_rate=rB,
                  H1=("not assessable (meas gate missing)" if rB is None else
                      "EXPLAINS" if rB >= H1_HI else "DOES NOT EXPLAIN" if rB < H1_LO else "EXPLAINS IN PART"),
                  per_subject_sample=dict(zip(names, map(float, a_s))), per_subject_window=dict(zip(names, map(float, a_w))))
    # (b) H2: does the real call rest on fewer subjects than a homogeneous population's call would?
    b = {}
    for j in called3:
        lm = L3[j - 1]
        lm = lm[np.all(np.isfinite(lm), axis=1)]            # as F4 and the gate: drop non-finite subjects
        loo = [float(A.spm_bms(np.delete(lm, i, 0), np.random.default_rng(SEED))["pxp"][2]) for i in range(len(lm))]
        b[j] = dict(loo_min=min(loo), loo_flips=int(sum(v <= 0.95 for v in loo)), greedy_flip=flips(lm))
    ref = None if gB is None else gB["flips_3model_calls"]
    if ref is None or len(ref) < 20:
        h2 = "not assessable (fewer than 20 calling studies in the meas B gate)"
    elif len(b) < NEED:
        h2 = f"not assessable ({len(b)} called primary windows < {NEED})"
    elif float(np.percentile(ref, 5)) <= 1:
        h2 = "not assessable (floor: the reference 5th percentile is <= 1, and a called window always needs >= 1 drop)"
    else:
        p5_ref = float(np.percentile(ref, 5))
        low = sum(1 for v in b.values() if v["greedy_flip"] < p5_ref)
        h2 = "SUPPORTED" if low >= NEED else "NOT SUPPORTED"
        b["ref_p5"] = p5_ref
    P["b"] = dict(per_window=b, H2=h2, meas_B_3model_rate=rB,
                  meas_het_B_3model_rate=None if gH is None else gH["rate_call_3model"],
                  dmax_log_sd=meas["log_sd"], n_nonpositive_dmax=meas["n_nonpositive_dmax"])
    # (c) H3: shape after within-decoder-fold standardisation, median over the 6 windows, then over subjects
    k0, bc5, f0 = [], [], []
    for s in names:
        dd = S[s]
        W = dd["win"][:, [j - 1 for j in PRIMARY]]
        i0, i5 = dd["x"] == 0, dd["x"] == 5
        k0.append(np.median([kurtosis(fold_z(W[i0, i], dd["fold"][i0])) for i in range(len(PRIMARY))]))
        bc5.append(np.median([bimod(fold_z(W[i5, i], dd["fold"][i5])) for i in range(len(PRIMARY))]))
        f0.append(dd["fold"][i0])
    rng = np.random.default_rng(SEED)            # null: Gaussian, same fold sizes, one window per subject (conservative)
    null = np.array([np.median([kurtosis(fold_z(rng.normal(size=len(f)), f)) for f in f0]) for _ in range(1000)])
    k_med = float(np.median(k0))
    bc_ref = None if gB is None else gB["bc5_p95"]
    P["c"] = dict(kurt0_median=k_med, kurt0_null_p95=float(np.percentile(null, 95)), kurt_bar=KURT_BAR,
                  heavy_tails=bool(k_med > np.percentile(null, 95) and k_med > KURT_BAR),
                  bc5_median=float(np.median(bc5)), bc5_B_generator_p95=bc_ref,
                  separated_high_states=None if bc_ref is None else bool(np.median(bc5) > bc_ref),
                  kj_median_primary=float(np.nanmedian(KJ[[j - 1 for j in PRIMARY]])))
    res["puzzle"] = P
    OUT.mkdir(exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(res["result"])
    print(json.dumps({k: res[k] for k in ("replication", "tier", "five_model_windows")}))
    print("H1", P["a"]["H1"], "| H2", P["b"]["H2"], "| heavy tails", P["c"]["heavy_tails"],
          "| separated high states", P["c"]["separated_high_states"])


if __name__ == "__main__":
    {"measure": measure, "fit": fit, "readout": readout}[sys.argv[1]]()
