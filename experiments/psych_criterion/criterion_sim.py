"""Is "the signal tracks the psychometric curve" a specific test of an awareness correlate? (Cohen et al. 2024 rule)
Prereg: docs/prereg/2026-11-25_psych_criterion_sim.md   (Fable round 16, item 3; zero new bytes)

Simulates per-subject SOA means for 25 subjects at SOAs 17/33/50/67/83 ms, using each subject's real report-block
seen rates and trial counts (experiments/cohen_fixed_soa/trial_counts.csv; behaviour only, no EEG), and applies:

  RULE  Cohen et al.'s pre-registered four-part bifurcation rule (paired t, two-sided alpha .05, df 24):
        (i) 17 vs 33 n.s.; (ii) 33 < 50 significant; (iii) 50 < 67 significant; (iv) 67 vs 83 n.s.
  MSE   their post hoc test: per-subject linear vs nonlinear regression on the 5 SOA means, paired t on the MSEs;
        "nonlinear" if nonlinear MSE is lower and p < .05. Their model and MSE definition are unstated, so four
        variants: (4-parameter logistic | quadratic) x (uncorrected SSE/5 | df-corrected SSE/(5 - parameters)).

    python -I criterion_sim.py calibrate   # -> out/calibration.json
    python -I criterion_sim.py run         # -> out/<cell>.json, out/summary.json (verdict)
    python -I criterion_sim.py pilot       # unsealed timing only
"""
import csv, json, os, sys, time
from pathlib import Path
from multiprocessing import Pool

os.environ.setdefault("OMP_NUM_THREADS", "1")
import warnings  # noqa: E402
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402
from scipy.optimize import curve_fit, OptimizeWarning  # noqa: E402
warnings.simplefilter("ignore", OptimizeWarning)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "rules"))
OUT = HERE / "out"
PREREG = ROOT / "docs" / "prereg" / "2026-11-25_psych_criterion_sim.md"
COUNTS = ROOT / "experiments" / "cohen_fixed_soa" / "trial_counts.csv"

SOAS = [17, 33, 50, 67, 83]
K = np.arange(5, dtype=float)              # linear stimulus regressor (equal SOA steps)
NSUB = 25
ALPHA = 0.05
AMP_CV = 0.5                               # between-subject CV of each effect size (gamma)
TARGET_T = 4.49                            # Cohen's no-report N2, 33 vs 50 ms (reference strength)
AW_TARGETS = [3.0, 4.49, 6.0, 7.5]         # pure-awareness strength sweep (median part-(ii) t)
CAL_TOL = 0.15
CAL_STUDIES = 400
STUDIES = 1000
RATIOS = [0.05, 0.1, 0.15, 0.2, 0.3, 0.5]  # per-SOA-step stimulus effect / awareness effect (MIX cells)
SAT_MIX = [0.25, 0.5, 1.0]                 # saturating stimulus effect (full size at 50 ms) / awareness effect
WORKERS = 4
SEED = 20261206


def sealed():
    from evidence import require_sealed
    for f in (PREREG, Path(__file__)):
        require_sealed(str(f))
    OUT.mkdir(exist_ok=True)


def subjects():
    rows = []
    for r in csv.DictReader(open(COUNTS)):
        seen = np.array([int(r[f"soa{s}_seen"]) for s in SOAS])
        uns = np.array([int(r[f"soa{s}_unseen"]) for s in SOAS])
        rows.append((seen + uns, seen / np.maximum(seen + uns, 1)))
    return rows


SUBS = subjects()
PGROUP = np.mean([p for _, p in SUBS], axis=0)


def gam(rng, n):
    return rng.gamma(1 / AMP_CV ** 2, AMP_CV ** 2, n)


def study(cell, B, rng):
    """Per-subject SOA means (25 x 5). Trial noise SD 1; seen counts drawn per trial from the subject's seen rate."""
    idx = rng.integers(0, len(SUBS), NSUB)
    M = np.empty((NSUB, 5))
    for j, i in enumerate(idx):
        n, p = SUBS[i]
        share = rng.binomial(n, p) / n
        ga, gs = gam(rng, 1)[0], gam(rng, 1)[0]
        kind, r = cell
        if kind == "NULL":
            mu = np.zeros(5)
        elif kind == "AW":
            mu = B * ga * share
        elif kind == "MIX":
            mu = B * ga * share + r * B * gs * K
        elif kind == "AWSAT":                                           # awareness + saturating stimulus
            mu = B * ga * share + r * B * gs * np.minimum(K, 2) / 2
        elif kind == "LIN":
            mu = B * gs * K
        elif kind == "SAT":                                             # sensory, rises to 50 ms then flat (P1-like)
            mu = B * gs * np.minimum(K, 2) / 2
        elif kind == "SIG":                                             # sensory sigmoid = group psychometric shape,
            mu = B * gs * PGROUP                                        # no awareness term
        M[j] = mu + rng.normal(0, 1, 5) / np.sqrt(n)
    return M


def ptest(a, b):
    t, p = stats.ttest_rel(b, a)
    return float(t), float(p)


def rule(M):
    t1, p1 = ptest(M[:, 0], M[:, 1])
    t2, p2 = ptest(M[:, 1], M[:, 2])
    t3, p3 = ptest(M[:, 2], M[:, 3])
    t4, p4 = ptest(M[:, 3], M[:, 4])
    ok = p1 >= ALPHA and p2 < ALPHA and t2 > 0 and p3 < ALPHA and t3 > 0 and p4 >= ALPHA
    return bool(ok), [t1, t2, t3, t4]


def part_met(ts, j):
    """Whether part j of the rule holds, from its t value (df 24, two-sided)."""
    tc = stats.t.ppf(1 - ALPHA / 2, NSUB - 1)
    return abs(ts[j]) < tc if j in (0, 3) else ts[j] > tc


def logistic(x, lo, hi, m, s):
    return lo + (hi - lo) / (1 + np.exp(-(x - m) / s))


NPAR = {"lin": 2, "quad": 3, "logistic": 4}


def sse_lin(y):
    c = np.polyfit(K, y, 1)
    return float(np.sum((y - np.polyval(c, K)) ** 2))


def sse_quad(y):
    c = np.polyfit(K, y, 2)
    return float(np.sum((y - np.polyval(c, K)) ** 2))


def sse_logistic(y):
    """4-parameter logistic, least squares; best of 18 fixed starts."""
    best = np.inf
    lo0, hi0 = y.min(), y.max()
    for m0 in (1.0, 2.0, 3.0):
        for s0 in (0.3, 1.0, 3.0):
            for sign in (1, -1):
                p0 = [lo0, hi0, m0, s0] if sign > 0 else [hi0, lo0, m0, s0]
                try:
                    with np.errstate(all="ignore"):
                        p, _ = curve_fit(logistic, K, y, p0=p0, maxfev=2000)
                        e = float(np.sum((y - logistic(K, *p)) ** 2))
                    if np.isfinite(e):
                        best = min(best, e)
                except (RuntimeError, ValueError):
                    pass
    return best


def mse_tests(M):
    """Their post hoc test in four variants: nonlinear model (logistic, quadratic) x MSE (uncorrected SSE/5, or
    df-corrected SSE/(5 - parameters)). Returns {variant: (called_nonlinear, t)} and the logistic failure count."""
    lin = np.array([sse_lin(y) for y in M])
    nls = {"logistic": np.array([sse_logistic(y) for y in M]), "quad": np.array([sse_quad(y) for y in M])}
    bad = int((~np.isfinite(nls["logistic"])).sum())
    out = {}
    for name, nl in nls.items():
        ok = np.isfinite(nl)
        for corr in (False, True):
            key = f"{name}_{'dfcorr' if corr else 'raw'}"
            if (~ok).sum() >= 3:
                out[key] = (False, float("nan"))
                continue
            a = lin[ok] / (5 - NPAR["lin"] if corr else 5)
            b = nl[ok] / (5 - NPAR[name] if corr else 5)
            t, p = stats.ttest_rel(a, b)
            out[key] = (bool(t > 0 and p < ALPHA), float(t))
    return out, bad


# ------------------------------------------------------------------ calibration
def med_t2(cell, B, seed):
    rng = np.random.default_rng([SEED, 999, seed])
    return float(np.median([rule(study(cell, B, rng))[1][1] for _ in range(CAL_STUDIES)]))


def calibrate_one(args):
    cell, target = args
    lo, hi = np.log(1e-3), np.log(10.0)
    best = None
    for _ in range(30):
        mid = (lo + hi) / 2
        t = med_t2(cell, np.exp(mid), 1)
        if best is None or abs(t - target) < abs(best[1] - target):
            best = (float(np.exp(mid)), t)
        if abs(t - target) <= CAL_TOL / 3:
            break
        lo, hi = (mid, hi) if t < target else (lo, mid)
    return dict(B=best[0], target=target, median_t2=best[1], calibrated=bool(abs(best[1] - target) <= CAL_TOL))


CAL_CELLS = {f"AW_{t}": (("AW", 0), t) for t in AW_TARGETS}
CAL_CELLS.update({c: ((c, 0), TARGET_T) for c in ("LIN", "SAT", "SIG")})
REQUIRED = [f"AW_{TARGET_T}", "LIN", "SAT", "SIG"]


def calibrate():
    sealed()
    with Pool(WORKERS) as p:
        res = dict(zip(CAL_CELLS, p.map(calibrate_one, CAL_CELLS.values())))
    (OUT / "calibration.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


# ------------------------------------------------------------------ run
CELL_IDS = (["NULL"] + list(CAL_CELLS) + [f"MIX_{r}" for r in RATIOS] + [f"AWSAT_{c}" for c in SAT_MIX])


def one(args):
    name, cell, B, k = args
    rng = np.random.default_rng([SEED, CELL_IDS.index(name), k])
    M = study(cell, B, rng)
    ok, ts = rule(M)
    mt, bad = mse_tests(M)
    return name, ok, ts, mt, bad


def cells_from(cal):
    out = {"NULL": (("NULL", 0), 0.0)}
    for n, (cell, _) in CAL_CELLS.items():
        if cal[n]["calibrated"]:
            out[n] = (cell, cal[n]["B"])
    Bref = cal[f"AW_{TARGET_T}"]["B"]
    for r in RATIOS:
        out[f"MIX_{r}"] = (("MIX", r), Bref)
    for c in SAT_MIX:
        out[f"AWSAT_{c}"] = (("AWSAT", c), Bref)
    return out


def run():
    sealed()
    cal = json.loads((OUT / "calibration.json").read_text())
    if not all(cal[c]["calibrated"] for c in REQUIRED):
        summ = dict(verdict="INVALID", reason="a required cell missed calibration tolerance", calibration=cal)
        (OUT / "summary.json").write_text(json.dumps(summ, indent=1) + "\n")
        print(json.dumps(summ, indent=1))
        return
    cells = cells_from(cal)
    jobs = [(n, c, B, k) for n, (c, B) in cells.items() for k in range(STUDIES)]
    t0 = time.time()
    with Pool(WORKERS) as p:
        res = p.map(one, jobs, chunksize=50)
    rows = {}
    variants = ["logistic_raw", "logistic_dfcorr", "quad_raw", "quad_dfcorr"]
    for n in cells:
        r = [x for x in res if x[0] == n]
        ts = np.array([x[2] for x in r])
        rows[n] = dict(rule_pass=float(np.mean([x[1] for x in r])),
                       share_each_part_met=[float(np.mean([part_met(x[2], j) for x in r])) for j in range(4)],
                       median_t=[float(v) for v in np.median(ts, axis=0)],
                       mse_nonlinear_rate={v: float(np.mean([x[3][v][0] for x in r])) for v in variants},
                       mse_median_t={v: float(np.nanmedian([x[3][v][1] for x in r])) for v in variants},
                       logistic_fit_failures=int(sum(x[4] for x in r)))
        (OUT / f"{n}.json").write_text(json.dumps(dict(rows[n], rule=[x[1] for x in r], t=[x[2] for x in r],
                                                       mse=[x[3] for x in r]), indent=0) + "\n")
    aw = [(t, rows[f"AW_{t}"]["rule_pass"]) for t in AW_TARGETS if f"AW_{t}" in rows]
    fails = [t for t, pr in aw if pr < 0.5]
    rv = ("RULE PASSES PURE AWARENESS SIGNALS AT EVERY TESTED STRENGTH" if not fails else
          f"RULE REJECTS A PURE AWARENESS SIGNAL AT STRENGTH t = {min(fails)}")
    mv = {v: ("NON-SPECIFIC" if rows["LIN"]["mse_nonlinear_rate"][v] >= 0.5 else "SPECIFIC TO LINEAR TRUTH")
          for v in variants}
    r50 = next((r for r in RATIOS if rows[f"MIX_{r}"]["rule_pass"] < 0.5), None)
    summ = dict(rule_verdict=rv, aw_sweep_pass=dict(aw), uncalibrated_sweep_points=[n for n in CAL_CELLS if n not in cells],
                mse_verdict_by_variant=mv, mix_ratio_where_rule_pass_below_half=r50,
                awsat_pass={c: rows[f"AWSAT_{c}"]["rule_pass"] for c in SAT_MIX},
                sensory_sigmoid_pass=rows["SIG"]["rule_pass"], calibration=cal, cells=rows,
                seconds=round(time.time() - t0))
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1) + "\n")
    print(json.dumps(summ, indent=1))


def pilot():
    """Unsealed: timing of one study (all tests) at an arbitrary scale; prints timing only."""
    rng = np.random.default_rng(1)
    t = time.time()
    M = study(("MIX", 0.2), 0.5, rng)
    rule(M), mse_tests(M)
    print("one study", round(time.time() - t, 3), "s; subjects in pool", len(SUBS))


if __name__ == "__main__":
    {"calibrate": calibrate, "run": run, "pilot": pilot}[sys.argv[1]]()
