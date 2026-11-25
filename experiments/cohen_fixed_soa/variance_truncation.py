"""DROPPED BEFORE SEALING (see prereg header). Round 15 item 4: are seen trials less variable than a graded brain would make them? (Cohen et al. 2024, report, SOA 50)
Prereg: docs/prereg/2026-11-25_cohen_variance_truncation.md

Graded-truncation null: the single-trial amplitude a and a graded visibility variable z are bivariate normal (corr rho);
"seen" means z is above the subject's own threshold (set by their seen rate p). Selection alone then changes the variance
of each class. From p, the class-mean gap and the pooled variance it predicts each class's variance, with no free
parameter. Excess = observed log(var_seen / var_unseen) - predicted. Variability quenching beyond selection = excess < 0.

    python -I variance_truncation.py design     # label-free amplitude statistics -> out/var_design.json
    python -I variance_truncation.py calibrate  # fake labels on real amplitudes + synthetic -> out/var_calibration.json
    python -I variance_truncation.py run        # real labels; refuses unless sealed and PASS -> out/var_result.json
"""
import csv, json, sys
from pathlib import Path

import numpy as np
from scipy.stats import norm, t as tdist, skew, kurtosis

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
PREREG = HERE.parents[1] / "docs" / "prereg" / "2026-11-25_cohen_variance_truncation.md"
PRIMARY = ["VAN", "P3b"]
DESCRIPTIVE = ["P1", "N2"]
SEED = 20261131
RUNS = 300
ALPHA = 0.05 / len(PRIMARY)       # Bonferroni over the two primary components: 97.5% intervals
BOUND = 0.15                      # MATCHES NULL needs the CI inside +-0.15 (log variance ratio)
PLANT = np.log(0.80)              # planted quenching: seen-class variance x 0.80 beyond selection
RHO = (0.10, 0.50)                # calibration: per-subject |corr(a, z)| ~ U(0.10, 0.50)
MC = 500                          # Monte Carlo label sets per subject (fallback F1 only)


def load():
    z = np.load(OUT / "prep.npz")
    subs = [r["sub"] for r in csv.DictReader(open(OUT / "eligibility.csv")) if r["eligible"] == "1"]
    return {s: {k: z[f"{s}|{k}"] for k in PRIMARY + DESCRIPTIVE + ["resp"]} for s in subs}


def moments_pred(p, gap, var_tot):
    """Predicted log(var_seen/var_unseen) under the graded-truncation null.
    z ~ N(0,1), seen iff z > c with P(seen) = p; a = mu + b*z + e, e independent of z.
    Class means of z: l1 = phi(c)/(1-Phi(c)), l0 = -phi(c)/Phi(c); class variances V = 1 + c*l - l^2.
    gap = b*(l1 - l0); var_tot = b^2 + var(e). Class variance of a = b^2 * V + var(e)."""
    c = norm.ppf(1 - p)
    l1 = norm.pdf(c) / norm.sf(c)
    l0 = -norm.pdf(c) / norm.cdf(c)
    v1, v0 = 1 + c * l1 - l1 ** 2, 1 + c * l0 - l0 ** 2
    b2 = (gap / (l1 - l0)) ** 2
    ve = max(var_tot - b2, 1e-9 * var_tot)                       # b^2 cannot exceed total variance
    b2 = min(b2, var_tot)
    return float(np.log((b2 * v1 + ve) / (b2 * v0 + ve)))


def excess(a, seen, method="moments", rng=None):
    """Observed log variance ratio (seen/unseen, ddof 1) minus the null prediction. Moments method: the observed ratio is
    first corrected for the small-sample bias of log(sample variance), E = log(var) - 1/(n-1) (to first order)."""
    a1, a0 = a[seen], a[~seen]
    obs = np.log(a1.var(ddof=1) / a0.var(ddof=1))
    p = seen.mean()
    gap = a1.mean() - a0.mean()
    if method == "moments":
        n1, n0 = len(a1), len(a0)
        obs = obs + 1 / (n1 - 1) - 1 / (n0 - 1)                    # small-sample bias of log sample variance
        return obs - moments_pred(p, gap, a.var(ddof=1))
    return obs - mc_pred(a, int(seen.sum()), gap, rng)


def mc_pred(a, n1, gap, rng):
    """Fallback F1: Monte Carlo null from the subject's own amplitudes. Fake z = r*std(a) + sqrt(1-r^2)*N(0,1); the
    top n1 trials are 'seen'. r is set so that the expected gap matches the observed gap (bisection on a grid)."""
    s = (a - a.mean()) / a.std()
    E = rng.standard_normal((MC, len(a)))
    sgn = np.sign(gap) if gap != 0 else 1.0

    def stats(r):
        zz = sgn * r * s[None, :] + np.sqrt(1 - r ** 2) * E
        top = np.argsort(-zz, axis=1)[:, :n1]
        m = np.zeros_like(zz, bool)
        np.put_along_axis(m, top, True, axis=1)
        A = np.broadcast_to(a, m.shape)
        g = (np.where(m, A, 0).sum(1) / n1) - (np.where(~m, A, 0).sum(1) / (len(a) - n1))
        v1 = np.where(m, (A - (np.where(m, A, 0).sum(1, keepdims=True) / n1)) ** 2, 0).sum(1) / (n1 - 1)
        v0 = np.where(~m, (A - (np.where(~m, A, 0).sum(1, keepdims=True) / (len(a) - n1))) ** 2, 0).sum(1) / (len(a) - n1 - 1)
        return np.abs(g).mean(), np.log(v1 / v0).mean()

    lo, hi = 0.0, 0.99
    for _ in range(12):
        mid = (lo + hi) / 2
        if stats(mid)[0] < abs(gap):
            lo = mid
        else:
            hi = mid
    return float(stats((lo + hi) / 2)[1])


def group(x):
    x = np.asarray(x, float)
    n = len(x)
    se = x.std(ddof=1) / np.sqrt(n)
    q = tdist.ppf(1 - ALPHA / 2, n - 1)
    lo, hi = x.mean() - q * se, x.mean() + q * se
    if hi < 0:
        v = "QUENCHED"
    elif lo > 0:
        v = "WIDENED"
    elif -BOUND < lo and hi < BOUND:
        v = "MATCHES NULL"
    else:
        v = "INCONCLUSIVE"
    return dict(n=n, mean=float(x.mean()), ci=[float(lo), float(hi)], ci_level=1 - ALPHA, verdict=v)


def design():
    D = load()
    res = {}
    for c in PRIMARY + DESCRIPTIVE:
        a = [D[s][c] for s in D]
        res[c] = dict(median_sd_uv=float(np.median([x.std() for x in a])),
                      median_skew=float(np.median([skew(x) for x in a])),
                      median_excess_kurtosis=float(np.median([kurtosis(x) for x in a])))
    res["subjects"] = len(D)
    res["median_trials"] = float(np.median([len(D[s]["resp"]) for s in D]))
    (OUT / "var_design.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


# ------------------------------------------------------------------ calibration (no real label touches an amplitude)
def labels_from(a, n1, rho, rng, sign):
    """Graded null on the REAL amplitudes: z = sign*rho*std(a) + sqrt(1-rho^2)*N(0,1); top n1 trials are 'seen'."""
    s = (a - a.mean()) / a.std()
    z = sign * rho * s + np.sqrt(1 - rho ** 2) * rng.standard_normal(len(a))
    seen = np.zeros(len(a), bool)
    seen[np.argsort(-z)[:n1]] = True
    return seen


def synth_skewed(n, n1, rho, sd, rng):
    """Synthetic graded null with a SKEWED latent: z = standardised gamma(4) (skew 1), a = rho*z + sqrt(1-rho^2)*e."""
    g = rng.gamma(4.0, 1.0, n)
    z = (g - 4.0) / 2.0
    a = sd * (rho * z + np.sqrt(1 - rho ** 2) * rng.standard_normal(n))
    seen = np.zeros(n, bool)
    seen[np.argsort(-z)[:n1]] = True
    return a, seen


def plant(a, seen, rng):
    """Planted quenching: shrink seen trials' deviations from the seen mean so their variance is x0.80."""
    a = a.copy()
    m = a[seen].mean()
    a[seen] = m + (a[seen] - m) * np.sqrt(np.exp(PLANT))
    return a


def calibrate(method="moments", seed=SEED, out_name="var_calibration.json"):
    D = load()
    rng = np.random.default_rng(seed)
    cells = {"null_real_amp": {}, "null_skewed_latent": {}, "planted": {}}
    means = {k: [] for k in cells}
    for _ in range(RUNS):
        ex = {k: {c: [] for c in PRIMARY} for k in cells}
        for s, d in D.items():
            n1 = int((d["resp"] == 1).sum())                       # the subject's own seen count (rate only)
            for c in PRIMARY:
                a = d[c]
                rho = rng.uniform(*RHO)
                sign = rng.choice([-1.0, 1.0])
                sn = labels_from(a, n1, rho, rng, sign)
                ex["null_real_amp"][c].append(excess(a, sn, method, rng))
                a2, s2 = synth_skewed(len(a), n1, rho, a.std(), rng)
                ex["null_skewed_latent"][c].append(excess(a2, s2, method, rng))
                sp = labels_from(a, n1, rho, rng, sign)
                ex["planted"][c].append(excess(plant(a, sp, rng), sp, method, rng))
        for k in cells:
            for c in PRIMARY:
                g = group(ex[k][c])
                cells[k].setdefault(c, {})
                cells[k][c][g["verdict"]] = cells[k][c].get(g["verdict"], 0) + 1
                means[k].append(g["mean"])
    rates = {k: {c: {v: n / RUNS for v, n in cells[k][c].items()} for c in PRIMARY} for k in cells}
    false = {k: {c: rates[k][c].get("QUENCHED", 0) + rates[k][c].get("WIDENED", 0) for c in PRIMARY}
             for k in ("null_real_amp", "null_skewed_latent")}
    power = {c: rates["planted"][c].get("QUENCHED", 0) for c in PRIMARY}
    ok = all(v <= 0.05 for k in false for v in false[k].values()) and all(v >= 0.80 for v in power.values())
    res = dict(method=method, seed=seed, runs=RUNS, plant_log_ratio=PLANT, bound=BOUND, rho_range=RHO, rates=rates,
               false_call=false, power=power, mean_excess={k: float(np.mean(v)) for k, v in means.items()}, PASS=bool(ok))
    (OUT / out_name).write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


# ------------------------------------------------------------------ the one real run
def run():
    sys.path.insert(0, str(HERE.parents[0] / "rules"))
    from evidence import require_sealed
    for f in (PREREG, Path(__file__), OUT / "var_calibration.json"):
        require_sealed(str(f))
    cal = json.loads((OUT / "var_calibration.json").read_text())
    method = "moments"
    if not cal["PASS"]:
        f1 = OUT / "var_calibration_f1.json"                        # fallback F1 (prereg section 4)
        require_sealed(str(f1))
        assert json.loads(f1.read_text())["PASS"], "calibration and fallback F1 both failed: no run"
        method = "mc"
    D = load()
    rng = np.random.default_rng(SEED + 1)
    res = dict(method=method, primary={}, descriptive={}, per_subject={})
    for c in PRIMARY + DESCRIPTIVE:
        ex, obs, pred = [], [], []
        for s, d in D.items():
            seen = d["resp"] == 1
            a = d[c]
            e = excess(a, seen, method, rng)
            o = float(np.log(a[seen].var(ddof=1) / a[~seen].var(ddof=1)))
            ex.append(e)
            obs.append(o)
            pred.append(o - e)
        g = group(ex)
        g.update(observed_log_ratio_mean=float(np.mean(obs)), predicted_log_ratio_mean=float(np.mean(pred)),
                 subjects_excess_below_0=int(np.sum(np.array(ex) < 0)))
        if c in PRIMARY:
            res["primary"][c] = g
        else:
            res["descriptive"][c] = {k: v for k, v in g.items() if k != "verdict"}
        res["per_subject"][c] = [round(float(x), 4) for x in ex]
    (OUT / "var_result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "per_subject"}, indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "calibrate_f1":
        calibrate("mc", SEED + 7, "var_calibration_f1.json")
    else:
        {"design": design, "calibrate": calibrate, "run": run}[cmd]()
