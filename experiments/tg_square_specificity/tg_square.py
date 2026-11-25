"""Is a temporal-generalisation "square" specific to a sustained code? (simulation, zero data)
Prereg: docs/prereg/2026-11-25_tg_square_specificity.md

Hutchinson, Dehaene, Slagter & Pitts (2026, bioRxiv) read a seen-vs-unseen TG "square" at about 200-400 ms in
no-report EEG as "a single neural code ... sustained and stabilised over time". They raise trial-to-trial latency
jitter of a brief evoked response as an alternative and reject it in words ("We ultimately find this interpretation
unlikely"); there is no simulation and no quantitative square criterion.

Here: simulated EEG (64 channels, volume-conducted latent sources, pink background) with known ground truth.
  SUS        one code, sustained 200-400 ms (the reading Hutchinson et al. give); SUS_j60 same, onset SD 60 ms
  NULL       no signal (false-positive check for the square criterion)
  J1_s<sd>   one brief code (50 ms) whose latency jitters across trials, SD in {0, 25, 50, 75} ms
  CH4_s<sd>  a chain of four distinct brief codes (50 ms each, 190-390 ms), common latency jitter, same SDs
Seen trials carry the signal; unseen trials are noise only. Pipeline as theirs: causal 0.1 Hz high-pass on a long
padded epoch, baseline -100 to 0 ms, 250 Hz then decimated to 125 Hz for TG, per-time LDA (Ledoit-Wolf shrinkage),
5-fold CV, AUC.

Measures per study (group of 20 simulated subjects):
  SQ    square index = mean(AUC-0.5) over the 200-400 x 200-400 block / mean(AUC-0.5) on its diagonal
  SPAN  ms of contiguous test times around the 300 ms training time with group t > t_crit (one-sided, p < .05)
  CPL   single-trial coupling: for the decoder trained at 250 ms, the correlation across trials between its decision
        values averaged over 230-270 ms and over 330-370 ms, seen minus unseen (Fisher z), group mean and t.
        A sustained code predicts > 0; a brief jittered code predicts < 0.

    python -I tg_square.py calibrate   # amplitude per cell -> out/calibration.json (separate seeds)
    python -I tg_square.py run         # -> out/<cell>.json (skips finished cells)
    python -I tg_square.py summary     # -> out/summary.json
"""
import json, os, sys, time
from pathlib import Path
from multiprocessing import Pool

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import numpy as np  # noqa: E402
from scipy.signal import butter, lfilter  # noqa: E402
from scipy.stats import t as tdist  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
PREREG = HERE.parents[1] / "docs" / "prereg" / "2026-11-25_tg_square_specificity.md"
sys.path.insert(0, str(HERE.parents[0] / "rules"))

FS = 250
PAD = 5.0                       # s of padding before the epoch (about 3 time constants of the 0.1 Hz high-pass)
T0, T1 = -0.2, 0.8              # analysed epoch (s)
DEC = 2                         # TG at 125 Hz (8 ms)
N_CH, N_LAT = 64, 24            # channels, latent sources
N_SUB, N_TR = 20, 150           # subjects, trials per class
FOLDS = 5
STUDIES = 40
CAL_STUDIES = 4
WORKERS = 3
SEED = 20261203
SDS = [0, 25, 50, 75]           # latency jitter SD (ms)
TARGET_AUC = 0.58               # calibration target: group-mean MEAN diagonal AUC over the 200-400 ms block
CAL_TOL = 0.004
AMP_LO, AMP_HI, CAL_STEPS = 0.05, 100.0, 16
AMP_CV = 0.5                    # trial-to-trial amplitude variability (gamma), same for every generator
CELLS = ["SUS", "SUS_j60", "NULL"] + [f"J1_s{s}" for s in SDS] + [f"CH4_s{s}" for s in SDS]
SQ_MIN, SPAN_MIN = 0.80, 150.0  # a study is "square" if SQ >= SQ_MIN and SPAN >= SPAN_MIN
W = (0.200, 0.400)              # square block
T_TRAIN_SPAN = 0.300            # training time for SPAN: the block centre (a 200 ms anchor sits on SUS's onset edge)
T_CPL_TRAIN = 0.250             # coupling: decoder trained at 250 ms ...
T_CPL_WIN = ((0.230, 0.270), (0.330, 0.370))   # ... its decision values averaged over these two test windows

T_FULL = np.arange(int(round((T0 - PAD) * FS)), int(round(T1 * FS))) / FS
KEEP = T_FULL >= T0 - 1e-9
TIMES = T_FULL[KEEP]
TT = TIMES[::DEC]


def hann_bump(t, centre, width):
    x = (t - centre) / width
    return np.where(np.abs(x) < 0.5, np.cos(np.pi * x) ** 2, 0.0)


def boxcar(t, on, off, ramp=0.02):
    up = np.clip((t - on) / ramp, 0, 1)
    down = np.clip((off - t) / ramp, 0, 1)
    return np.sin(np.pi / 2 * np.minimum(up, down)) ** 2


def subject_model(rng):
    """Per-subject head: mixing matrix (volume conduction), signal patterns (latent-space orthogonal)."""
    A = rng.standard_normal((N_CH, N_LAT))
    A = A @ np.diag(np.linspace(1.5, 0.5, N_LAT))                          # a few dominant sources
    q, _ = np.linalg.qr(rng.standard_normal((N_LAT, N_LAT)))
    pats = (A @ q[:, :4]).T                                                # 4 latent-orthogonal codes, sensor space
    pats /= np.linalg.norm(pats, axis=1, keepdims=True)
    return A, pats


def pink(rng, n_series, n_t):
    f = np.fft.rfftfreq(n_t, 1 / FS)
    spec = (rng.standard_normal((n_series, f.size)) + 1j * rng.standard_normal((n_series, f.size)))
    spec /= np.sqrt(np.maximum(f, 0.5))
    x = np.fft.irfft(spec, n=n_t, axis=1)
    return x / x.std(axis=1, keepdims=True)


def time_courses(cell, n, rng):
    """(n, n_codes, T) time courses of the codes on seen trials."""
    amp = rng.gamma(1 / AMP_CV ** 2, AMP_CV ** 2, n)                       # mean 1, CV AMP_CV
    t = T_FULL
    if cell == "NULL":
        return np.zeros((n, 1, t.size))
    if cell in ("SUS", "SUS_j60"):
        sh = rng.normal(0, 0.020 if cell == "SUS" else 0.060, n)
        tc = np.stack([boxcar(t - s, *W) for s in sh])[:, None, :]
    else:
        kind, s = cell.split("_s")
        sh = rng.normal(0, int(s) / 1000, n)
        if kind == "J1":
            tc = np.stack([hann_bump(t - x, 0.300, 0.100) for x in sh])[:, None, :]        # 50 ms FWHM
        else:
            cs = [0.215, 0.265, 0.315, 0.365]
            tc = np.stack([np.stack([hann_bump(t - x, c, 0.100) for c in cs]) for x in sh])
    return tc * amp[:, None, None]


def simulate_subject(cell, amp, rng):
    A, pats = subject_model(rng)
    nT = T_FULL.size
    X = np.empty((2 * N_TR, N_CH, nT))
    for i in range(2 * N_TR):
        X[i] = A @ pink(rng, N_LAT, nT) / np.sqrt(N_LAT) + 0.5 * rng.standard_normal((N_CH, nT))
    tc = time_courses(cell, N_TR, rng)                                     # seen = first N_TR trials
    X[:N_TR] += amp * np.einsum("nkt,kc->nct", tc, pats[: tc.shape[1]])
    b, a = butter(1, 0.1 / (FS / 2), "highpass")                           # causal, like an online hardware filter
    X = lfilter(b, a, X, axis=2)[:, :, KEEP]
    X -= X[:, :, (TIMES >= -0.1) & (TIMES < 0)].mean(axis=2, keepdims=True)
    y = np.r_[np.ones(N_TR), np.zeros(N_TR)]
    return X[:, :, ::DEC], y


def lw_lda(Xtr, ytr):
    m1, m0 = Xtr[ytr == 1].mean(0), Xtr[ytr == 0].mean(0)
    Z = np.r_[Xtr[ytr == 1] - m1, Xtr[ytr == 0] - m0]
    n, p = Z.shape
    S = Z.T @ Z / n
    mu = np.trace(S) / p
    d2 = np.sum((S - mu * np.eye(p)) ** 2)
    b2 = min(d2, (np.sum(np.sum(Z ** 2, axis=1) ** 2) - n * np.sum(S ** 2)) / n ** 2)
    sh = b2 / d2 if d2 > 0 else 1.0
    C = sh * mu * np.eye(p) + (1 - sh) * S
    w = np.linalg.solve(C, m1 - m0)
    return w, -w @ (m1 + m0) / 2


def auc_cols(d, y):
    """AUC of each column of d (n_trials, ...) for labels y, via ranks."""
    from scipy.stats import rankdata
    r = rankdata(d, axis=0)
    n1, n0 = (y == 1).sum(), (y == 0).sum()
    return (r[y == 1].sum(0) - n1 * (n1 + 1) / 2) / (n1 * n0)


def tg_subject(X, y, rng):
    n, c, T = X.shape
    folds = np.empty(n, int)
    for lab in (0, 1):
        idx = np.where(y == lab)[0]
        folds[idx] = rng.permutation(np.arange(idx.size) % FOLDS)
    D = np.empty((n, T, T))                                                # decision values [trial, train t, test t]
    for f in range(FOLDS):
        tr, te = folds != f, folds == f
        for ti in range(T):
            w, b0 = lw_lda(X[tr, :, ti], y[tr])
            D[te, ti, :] = np.einsum("ncT,c->nT", X[te], w) + b0
    auc = auc_cols(D, y)                                                   # (T, T)
    i1 = int(np.argmin(np.abs(TT - T_CPL_TRAIN)))
    w1, w2 = [(TT >= a - 1e-9) & (TT <= b + 1e-9) for a, b in T_CPL_WIN]
    z = []
    for lab in (1, 0):
        a, bb = D[y == lab, i1][:, w1].mean(1), D[y == lab, i1][:, w2].mean(1)
        z.append(np.arctanh(np.clip(np.corrcoef(a, bb)[0, 1], -0.999, 0.999)))
    return auc, z[0] - z[1]


def study(cell, amp, seed):
    rng = np.random.default_rng(seed)
    aucs, cpl = [], []
    for _ in range(N_SUB):
        X, y = simulate_subject(cell, amp, rng)
        a, c = tg_subject(X, y, rng)
        aucs.append(a)
        cpl.append(c)
    return np.array(aucs), np.array(cpl)


def measures(aucs, cpl):
    m = aucs.mean(0) - 0.5
    w = (TT >= W[0] - 1e-9) & (TT <= W[1] + 1e-9)
    diag = np.diag(m)
    sq = float(m[np.ix_(w, w)].mean() / diag[w].mean()) if diag[w].mean() > 0 else float("nan")
    tcrit = tdist.ppf(0.95, N_SUB - 1)
    ti = int(np.argmin(np.abs(TT - T_TRAIN_SPAN)))
    tv = (aucs[:, ti, :] - 0.5).mean(0) / ((aucs[:, ti, :]).std(0, ddof=1) / np.sqrt(N_SUB))
    lo = hi = ti
    if tv[ti] > tcrit:
        while lo > 0 and tv[lo - 1] > tcrit:
            lo -= 1
        while hi < len(TT) - 1 and tv[hi + 1] > tcrit:
            hi += 1
        span = float((TT[hi] - TT[lo]) * 1000 + 1000 * DEC / FS)
    else:
        span = 0.0
    mdiag = float(np.diag(aucs.mean(0))[w].mean())
    c = float(cpl.mean())
    ct = float(c / (cpl.std(ddof=1) / np.sqrt(N_SUB)))
    return dict(sq=sq, span_ms=span, mean_diag_auc=mdiag, cpl=c, cpl_t=ct)


def _study_level(args):
    cell, amp, seed = args
    a, c = study(cell, amp, seed)
    return measures(a, c)["mean_diag_auc"]


def calibrate():
    """Bisection on log amplitude (same seeds at every step) so that the mean over CAL_STUDIES of the group-mean
    diagonal AUC over 200-400 ms is TARGET_AUC +- CAL_TOL. The closest step is kept. NULL is not calibrated (amp 0).
    A cell that cannot reach the target within [AMP_LO, AMP_HI] is marked UNCALIBRATED (prereg section 4)."""
    sealed()
    f = OUT / "calibration.json"
    cal = json.loads(f.read_text()) if f.exists() else {}
    for cell in CELLS:
        if cell in cal:
            continue
        if cell == "NULL":
            cal[cell] = dict(amp=0.0, level=None, ok=True, history=[])
            f.write_text(json.dumps(cal, indent=1) + "\n")
            continue
        seeds = [int(s.generate_state(1)[0]) for s in
                 np.random.SeedSequence([SEED, 1, CELLS.index(cell)]).spawn(CAL_STUDIES)]
        lo, hi, hist = np.log(AMP_LO), np.log(AMP_HI), []
        with Pool(WORKERS) as p:
            for _ in range(CAL_STEPS):
                mid = (lo + hi) / 2
                lv = float(np.mean(p.map(_study_level, [(cell, float(np.exp(mid)), s) for s in seeds])))
                hist.append([float(np.exp(mid)), lv])
                if abs(lv - TARGET_AUC) <= CAL_TOL:
                    break
                lo, hi = (mid, hi) if lv < TARGET_AUC else (lo, mid)
        amp, lv = min(hist, key=lambda h: abs(h[1] - TARGET_AUC))
        cal[cell] = dict(amp=amp, level=lv, ok=abs(lv - TARGET_AUC) <= CAL_TOL, history=hist)
        f.write_text(json.dumps(cal, indent=1) + "\n")
        print("cal", cell, round(amp, 4), round(lv, 4), cal[cell]["ok"], flush=True)


def _study_measures(args):
    cell, amp, seed = args
    a, c = study(cell, amp, seed)
    r = measures(a, c)
    r["seed"] = seed
    return r


def run():
    sealed()
    cal = json.loads((OUT / "calibration.json").read_text())
    for cell in CELLS:
        f = OUT / f"{cell}.json"
        if f.exists() or not cal[cell]["ok"]:                             # UNCALIBRATED cells are not run
            continue
        seeds = [int(s.generate_state(1)[0]) for s in
                 np.random.SeedSequence([SEED, 2, CELLS.index(cell)]).spawn(STUDIES)]
        t = time.time()
        with Pool(WORKERS) as p:
            res = p.map(_study_measures, [(cell, cal[cell]["amp"], s) for s in seeds])
        r = dict(cell=cell, amp=cal[cell]["amp"], studies=STUDIES, runs=res, seconds=round(time.time() - t))
        tmp = f.with_suffix(".tmp")
        tmp.write_text(json.dumps(r) + "\n")
        tmp.rename(f)
        print("run", cell, "sq", round(float(np.nanmedian([x["sq"] for x in res])), 3),
              "span", np.median([x["span_ms"] for x in res]), "cpl", round(np.median([x["cpl"] for x in res]), 3),
              r["seconds"], "s", flush=True)


def summary():
    sealed()
    cal = json.loads((OUT / "calibration.json").read_text())
    tc = tdist.ppf(0.95, N_SUB - 1)
    rows, R = {}, {}
    for c in CELLS:
        f = OUT / f"{c}.json"
        if not cal.get(c, {}).get("ok"):
            rows[c] = dict(status="UNCALIBRATED", amp=cal.get(c, {}).get("amp"))
            continue
        if not f.exists():
            rows[c] = dict(status="MISSING")
            continue
        runs = json.loads(f.read_text())["runs"]
        R[c] = runs
        sq = np.array([x["sq"] for x in runs], float)
        span = np.array([x["span_ms"] for x in runs])
        cpt = np.array([x["cpl_t"] for x in runs])
        lvl = float(np.median([x["mean_diag_auc"] for x in runs]))
        square = np.where(np.isnan(sq), False, sq >= SQ_MIN) & (span >= SPAN_MIN)
        rows[c] = dict(status="OK", amp=cal[c]["amp"], run_median_level=lvl,
                       level_ok=(c == "NULL") or abs(lvl - TARGET_AUC) <= 0.01,
                       sq_median=float(np.nanmedian(sq)) if np.isfinite(sq).any() else None,
                       sq_nan=int(np.isnan(sq).sum()), span_median=float(np.median(span)),
                       cpl_median=float(np.median([x["cpl"] for x in runs])),
                       share_square=float(square.mean()), share_cpl_pos=float(np.mean(cpt > tc)),
                       share_cpl_neg=float(np.mean(cpt < -tc)))
    ok = lambda c: rows[c].get("status") == "OK" and rows[c]["level_ok"]
    ch = [f"CH4_s{s}" for s in SDS]
    problems = []
    for c in ("SUS", "SUS_j60", "NULL"):
        if not ok(c):
            problems.append(f"{c} not usable")
    if not problems:
        if rows["SUS"]["share_square"] < 0.80 or (rows["SUS"]["sq_median"] or 0) < SQ_MIN:
            problems.append("SUS not square in >= 80%")
        if rows["NULL"]["share_square"] > 0.10:
            problems.append("NULL square in > 10%")
    if not any(ok(c) for c in ch if int(c.split("_s")[1]) <= 50):
        problems.append("no usable CH4 cell with SD <= 50")
    if any(rows[c].get("status") == "OK" and not rows[c]["level_ok"] for c in CELLS):
        problems.append("a run's median level is off target by > 0.01")
    hit = lambda maxsd: [c for c in ch if ok(c) and int(c.split("_s")[1]) <= maxsd and rows[c]["share_square"] >= 0.50]
    if problems:
        verdict, sq_cells, cpl = "INVALID", [], None
    else:
        verdict = ("SQUARE NOT SPECIFIC (jitter <= 50 ms)" if hit(50) else
                   "SQUARE NOT SPECIFIC ONLY AT LARGE JITTER (75 ms)" if hit(75) else "SQUARE SPECIFIC IN THIS MODEL")
        sq_cells = hit(75) + [c for c in CELLS if c.startswith("J1") and ok(c) and rows[c]["share_square"] >= 0.50]
        if not sq_cells:
            cpl = None
        elif rows["SUS"]["share_cpl_pos"] < 0.80 or rows["SUS_j60"]["share_cpl_pos"] < 0.80:
            cpl = "CPL UNINFORMATIVE"
        elif all(rows[c]["share_cpl_neg"] >= 0.80 for c in sq_cells):
            cpl = "COUPLING SEPARATES"
        else:
            cpl = "COUPLING DOES NOT SEPARATE"
    s = dict(verdict=verdict, problems=problems, square_cells=sq_cells, coupling=cpl, rows=rows)
    (OUT / "summary.json").write_text(json.dumps(s, indent=1) + "\n")
    print(json.dumps(s, indent=1))


def sealed():
    from evidence import require_sealed
    for f in (PREREG, Path(__file__)):
        require_sealed(str(f))
    OUT.mkdir(exist_ok=True)


def pilot():
    """Unsealed smoke test: runtime and finiteness only (no measures are printed), writes nothing to out/."""
    global N_SUB
    N_SUB = 2
    for cell in ("SUS", "CH4_s50"):
        t = time.time()
        a, c = study(cell, 0.5, 1)
        print(cell, "finite", bool(np.isfinite(a).all() and np.isfinite(c).all()), "shape", a.shape,
              round((time.time() - t) / N_SUB, 1), "s per subject", flush=True)


if __name__ == "__main__":
    {"calibrate": calibrate, "run": run, "summary": summary, "pilot": pilot}[sys.argv[1]]()
