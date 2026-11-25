"""Round 17 #1: are blink trials more alpha-band phase-locked at T2 than no-blink trials?

Claim tested (Zauner et al. 2012, doi:10.1016/j.neuroimage.2012.06.075): entrainment "during the time
window of T2 presentation - is larger for AB than NoAB trials"; "alpha entrainment may be considered the
critical factor underlying the attentional blink phenomenon" (14 subjects).

Data: ds001810 (OpenNeuro, CC0) T2-locked epochs on disk, lag 3, T1 correct, pre-tDCS blocks only.
y = 1 T2 correct (no blink), y = 0 T2 incorrect (blink). Preprocessing and block eligibility are the
sealed hypothesis-generator ones (experiments/hypothesis_generator/ab_killtest.py), imported unchanged.

Modes:
  calib  shuffled labels only (pre-seal): null verdict rates + planted checks -> out/calibration.json
  gate   label-free: alpha-band phase-locking at T2 must be present at all  -> out/gate.json
  run    real labels, once, only after GATE PASS                          -> out/subjects.json, out/summary.json
Run with: nice -n 20 .venv/bin/python -I experiments/rhythm_blink/rhythm_blink.py <mode>
"""
import hashlib, json, sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
sys.path.insert(0, str(ROOT / "experiments" / "hypothesis_generator"))
sys.path.insert(0, str(ROOT / "experiments" / "rules"))
import ab_killtest as AB  # noqa: E402  (preprocess + eligible_blocks; importing reads no data)

PREREG = ROOT / "docs" / "prereg" / "2026-11-25_rhythm_blink.md"
SCRIPT = Path(__file__).resolve()

F_STREAM = 1000.0 / 91.7          # 10.905 Hz: one letter per 91.7 ms, no gap (Reteig 2022)
N_CYC = 3.0                        # sigma_t = 3/(2 pi f) = 43.8 ms; support +/-3 sigma = +/-131 ms; passes ~7-15 Hz
SIGMA_T = N_CYC / (2 * np.pi * F_STREAM)
WIN = (-50.0, 50.0)                # Zauner's peri-T2 window (centres), ms
COURSE = np.arange(-50.0, 661.0, 20.0)   # descriptive centres; +660 + 131 < 799 ms epoch end
# Zauner's PLI effects: central, centro-parietal, parietal (largest at P4); not occipital
ROI = ["C1", "Cz", "C2", "CP1", "CPz", "CP2", "P3", "Pz", "P4"]
MIN_ROI = 6
DRAWS = 100                        # count-matching subsamples per block
SEED = 20261725
EQ = 0.02                          # equivalence bound on the ITC difference (see prereg section 5)
ALPHA = 0.05
GATE_RHO = 0.10                    # median subject debiased all-trial phase-locking must reach this
MAX_DROP = 3                       # more non-finite subjects than this -> UNRESOLVED
N_NULL, N_PLANT = 200, 25
ADD_PLANTS = [(uv, ph) for uv in (1.0, 2.0) for ph in (0.0, 0.5 * np.pi, np.pi, 1.5 * np.pi)]
CONC_PLANTS = (0.05, 0.10)         # phase-spread shrink factor in "blink" trials, amplitude preserved

MORE = "BLINK TRIALS MORE ALPHA-BAND PHASE-LOCKED AT T2"
LESS = "BLINK TRIALS LESS ALPHA-BAND PHASE-LOCKED AT T2"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ------------------------------------------------------------------ measure
def wavelet_matrix(t_ms, centres_ms):
    """Rows: conjugated complex Morlet at F_STREAM centred on each centre; X @ W.T gives coefficients."""
    tau = (t_ms[None, :] - centres_ms[:, None]) / 1000.0
    w = np.exp(-2j * np.pi * F_STREAM * tau) * np.exp(-tau ** 2 / (2 * SIGMA_T ** 2))
    w[np.abs(tau) > 3 * SIGMA_T] = 0.0
    assert centres_ms.min() - 3000 * SIGMA_T >= t_ms[0] and centres_ms.max() + 3000 * SIGMA_T <= t_ms[-1], \
        "wavelet support leaves the epoch"
    return w


def block_coefs(b):
    """Complex coefficients (trials, roi_channels, centres) for the primary window and the course."""
    t = b["t"]
    idx = [b["ch"].index(c) for c in ROI if c in b["ch"]]
    X = b["X"][:, idx, :]
    win = t[(t >= WIN[0]) & (t <= WIN[1])]
    return dict(win=X @ wavelet_matrix(t, win).T, course=X @ wavelet_matrix(t, COURSE).T, n_roi=len(idx), t=t)


def unit(c):
    return c / np.maximum(np.abs(c), 1e-12)


def itc(u, rows):
    """Mean over channels and centres of |mean over the selected trials of unit phasors|."""
    return float(np.abs(u[rows].mean(0)).mean())


def block_stats(c, y, rng):
    """Count-matched blink - no-blink: ITC (primary), ITC course, log evoked amplitude; plus log power."""
    uw, uc = unit(c["win"]), unit(c["course"])
    ib, inb = np.flatnonzero(y == 0), np.flatnonzero(y == 1)
    m = min(len(ib), len(inb))
    d, dc, ev = [], [], []
    for _ in range(DRAWS):
        sb = rng.choice(ib, m, replace=False)
        snb = rng.choice(inb, m, replace=False)
        d.append(itc(uw, sb) - itc(uw, snb))
        dc.append(np.abs(uc[sb].mean(0)).mean(0) - np.abs(uc[snb].mean(0)).mean(0))
        ev.append(np.log(np.abs(c["win"][sb].mean(0)).mean()) - np.log(np.abs(c["win"][snb].mean(0)).mean()))
    pw = np.log(np.mean(np.abs(c["win"][ib]) ** 2)) - np.log(np.mean(np.abs(c["win"][inb]) ** 2))
    return dict(delta=float(np.mean(d)), course=np.mean(dc, 0), log_evoked=float(np.mean(ev)),
                logpow=float(pw), m=int(m), n_blink=int(len(ib)), n_noblink=int(len(inb)))


def rho2_all(c):
    """Label-free, count-independent: debiased squared phase-locking over ALL trials, (n R^2 - 1)/(n - 1)."""
    u = unit(c["win"])
    n = u.shape[0]
    R2 = np.abs(u.mean(0)) ** 2
    return float(((n * R2 - 1) / (n - 1)).mean())


# ------------------------------------------------------------------ data
def load():
    per, _ = AB.eligible_blocks()
    data = {}
    for sub in sorted(per):
        bl = [(b["stem"], block_coefs(b), b["y"].astype(int)) for b in per[sub]]
        bl = [x for x in bl if x[1]["n_roi"] >= MIN_ROI]
        if bl:
            data[sub] = bl
    return data


def subjects(data, labels=None, plant=None, seed=SEED):
    """Per-subject means over eligible blocks. labels: {stem: y} override. plant: f(stem, coefs, y) -> coefs."""
    out = {}
    for si, sub in enumerate(sorted(data)):
        rows = []
        for bi, (stem, c, y) in enumerate(data[sub]):
            yy = labels[stem] if labels is not None else y
            cc = plant(stem, c, yy) if plant is not None else c
            rows.append(block_stats(cc, yy, np.random.default_rng([seed, si, bi])))
        out[sub] = dict(delta=float(np.mean([r["delta"] for r in rows])),
                        course=np.mean([r["course"] for r in rows], 0).tolist(),
                        log_evoked=float(np.mean([r["log_evoked"] for r in rows])),
                        logpow=float(np.mean([r["logpow"] for r in rows])),
                        blink_rate=float(sum(r["n_blink"] for r in rows) /
                                         sum(r["n_blink"] + r["n_noblink"] for r in rows)),
                        blocks=len(rows), m=[r["m"] for r in rows])
    return out


def verdict(deltas):
    d = np.asarray(deltas, float)
    dropped = int((~np.isfinite(d)).sum())
    d = d[np.isfinite(d)]
    n = len(d)
    if dropped > MAX_DROP or n < 3:
        return dict(verdict="UNRESOLVED", n=n, dropped=dropped)
    se = d.std(ddof=1) / np.sqrt(n)
    t = d.mean() / se
    p = 2 * stats.t.sf(abs(t), n - 1)
    p_lo = stats.t.sf((d.mean() + EQ) / se, n - 1)       # H0: mean <= -EQ
    p_hi = stats.t.cdf((d.mean() - EQ) / se, n - 1)      # H0: mean >= +EQ
    if p < ALPHA and t > 0:
        v = MORE
    elif p < ALPHA and t < 0:
        v = LESS
    elif max(p_lo, p_hi) < ALPHA:
        v = f"NO DIFFERENCE: EQUIVALENT WITHIN +/-{EQ}"
    else:
        v = "INCONCLUSIVE"
    q = stats.t.ppf(.975, n - 1)
    return dict(verdict=v, n=n, dropped=dropped, mean=float(d.mean()), se=float(se), t=float(t), p=float(p),
                tost_p=float(max(p_lo, p_hi)), ci95=[float(d.mean() - q * se), float(d.mean() + q * se)],
                significant_but_within_bound=bool(p < ALPHA and abs(d.mean()) < EQ))


def gate_from(data):
    r2 = np.array([np.mean([rho2_all(c) for (_, c, _) in data[s]]) for s in sorted(data)])
    n = len(r2)
    t = r2.mean() / (r2.std(ddof=1) / np.sqrt(n))
    rho = np.sqrt(np.maximum(r2, 0))
    ok = bool(t > stats.t.ppf(1 - ALPHA, n - 1) and np.median(rho) >= GATE_RHO)
    return dict(gate="PASS" if ok else "METHOD BLIND", n=n, t=float(t), mean_rho2=float(r2.mean()),
                median_rho=float(np.median(rho)), script_sha=sha(SCRIPT), prereg_sha=sha(PREREG))


# ------------------------------------------------------------------ plants (calibration only)
def add_plant(data, uv, phase):
    """Additive: uv * cos(2 pi F t + phase) * exp(-t^2/(2*100^2)) on every ROI channel of 'blink' trials."""
    sig = {}
    for sub in data:
        for (stem, c, _) in data[sub]:
            t = c["t"]
            s = uv * np.cos(2 * np.pi * F_STREAM * t / 1000.0 + phase) * np.exp(-(t ** 2) / (2 * 100.0 ** 2))
            win = t[(t >= WIN[0]) & (t <= WIN[1])]
            sig[stem] = (s @ wavelet_matrix(t, win).T, s @ wavelet_matrix(t, COURSE).T)

    def f(stem, c, y):
        bl = (y == 0)[:, None, None].astype(float)
        sw, sc = sig[stem]
        return dict(win=c["win"] + bl * sw[None, None, :], course=c["course"] + bl * sc[None, None, :])
    return f


def conc_plant(kappa):
    """Amplitude-preserving: in 'blink' trials shrink each phase's deviation from the block's all-trial
    circular mean phase (per channel and centre) by the factor kappa; |coefficient| unchanged."""
    def shrink(z, bl):
        mu = np.angle(unit(z).mean(0))[None]
        dev = np.angle(z * np.exp(-1j * mu))
        z2 = np.abs(z) * np.exp(1j * (mu + (1 - kappa) * dev))
        return np.where(bl, z2, z)

    def f(stem, c, y):
        bl = (y == 0)[:, None, None]
        return dict(win=shrink(c["win"], bl), course=shrink(c["course"], bl))
    return f


# ------------------------------------------------------------------ modes
def require_seal():
    from evidence import require_sealed
    for f in (PREREG, SCRIPT, ROOT / "experiments" / "hypothesis_generator" / "ab_killtest.py",
              OUT / "calibration.json"):
        require_sealed(str(f))


def calib():
    """Shuffled labels only. Never reads the real label-outcome association."""
    OUT.mkdir(exist_ok=True)
    data = load()
    rng = np.random.default_rng([SEED, 999])

    def shuffled():
        return {stem: rng.permutation(y) for sub in data for (stem, _, y) in data[sub]}

    counts, nulls = {}, []
    for k in range(N_NULL):
        v = verdict([s["delta"] for s in subjects(data, shuffled(), seed=SEED + 1000 + k).values()])
        counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1
        nulls.append(v["mean"])
    planted = {}
    cells = [(f"add_{uv}uV_phase{ph / np.pi:.1f}pi", add_plant(data, uv, ph)) for uv, ph in ADD_PLANTS]
    cells += [(f"conc_kappa{k}", conc_plant(k)) for k in CONC_PLANTS]
    for ci, (name, f) in enumerate(cells):
        vs = [verdict([s["delta"] for s in subjects(data, shuffled(), plant=f,
                                                         seed=SEED + 5000 + 100 * ci + k).values()])
              for k in range(N_PLANT)]
        planted[name] = dict(detect_more=float(np.mean([v["verdict"] == MORE for v in vs])),
                             mean_delta=float(np.mean([v["mean"] for v in vs])))
        print(name, planted[name], flush=True)
    res = dict(null_runs=N_NULL, null_verdicts=counts, null_mean_sd=float(np.std(nulls)), eq_bound=EQ,
               plant_runs=N_PLANT, planted=planted, subjects=len(data),
               blocks=sum(len(v) for v in data.values()))
    (OUT / "calibration.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


def gate():
    require_seal()
    OUT.mkdir(exist_ok=True)
    g = gate_from(load())
    (OUT / "gate.json").write_text(json.dumps(g, indent=1) + "\n")
    print(json.dumps(g, indent=1))


def run():
    require_seal()
    if (OUT / "summary.json").exists():
        raise SystemExit("summary.json exists: the real-label run happens once")
    g = json.loads((OUT / "gate.json").read_text())
    if g.get("script_sha") != sha(SCRIPT) or g.get("prereg_sha") != sha(PREREG):
        raise SystemExit("gate.json was not produced by the sealed script and prereg")
    if g["gate"] != "PASS":
        raise SystemExit(f"gate {g['gate']}: real labels not analysed")
    data = load()
    subj = subjects(data)
    v = verdict([s["delta"] for s in subj.values()])
    keys = sorted(subj)
    lp = np.array([subj[s]["logpow"] for s in keys])
    le = np.array([subj[s]["log_evoked"] for s in keys])
    br = np.array([subj[s]["blink_rate"] for s in keys])
    r2 = np.array([np.mean([rho2_all(c) for (_, c, _) in data[s]]) for s in keys])
    r, pr = stats.pearsonr(r2, br)
    course = np.array([subj[s]["course"] for s in keys])

    def one(x):
        tt = stats.ttest_1samp(x, 0)
        return dict(mean=float(x.mean()), t=float(tt.statistic), p=float(tt.pvalue))
    summ = dict(primary=v, gate=g, log_power_ratio=one(lp), log_evoked_amplitude_ratio=one(le),
                secondary_between_subject=dict(r=float(r), p=float(pr), n=len(br),
                                               note="label-free all-trial rho^2 vs blink rate (no verdict)"),
                course=dict(centres_ms=COURSE.tolist(), mean=course.mean(0).tolist(),
                            se=(course.std(0, ddof=1) / np.sqrt(len(course))).tolist()))
    (OUT / "subjects.json").write_text(json.dumps(subj, indent=1) + "\n")
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1) + "\n")
    print(json.dumps({k: summ[k] for k in ("primary", "log_power_ratio", "log_evoked_amplitude_ratio",
                                           "secondary_between_subject")}, indent=1))


if __name__ == "__main__":
    {"calib": calib, "gate": gate, "run": run}[sys.argv[1] if len(sys.argv) > 1 else ""]()
