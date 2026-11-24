"""Robustness check of the sealed VAN result (Cohen et al. 2024, report block, SOA 50): does seen - unseen VAN survive
trial-wise arousal / attention covariates? Prereg: docs/prereg/2026-11-24_cohen_van_arousal_control.md

    python -I arousal_control.py covars     # covariates per kept trial -> out/arousal_covars.npz (small)
    python -I arousal_control.py calibrate  # fake labels only: null, planted direct effect, planted confound -> out/arousal_calibration.json
    python -I arousal_control.py run        # real labels; refuses unless prereg + this script + calibration are sealed

Covariates (named before any adjusted statistic was computed, all from data on disk):
  local  : attention state. Mean of (seen - expected seen at that SOA) over the 10 report face trials before and the 10
           after this one (all SOAs, current trial excluded), from trials.csv.
  prev   : the same residual for the previous report face trial.
  order  : time on task (rank of the trial in the session).
  p1     : P1 amplitude (100-140 ms, sealed posterior channels): early sensory gain. The sealed P1 control was flagged.
  prestd : prestimulus posterior SD (-100..0 ms, VAN + P1 channels): prestimulus state / alpha.
Model per subject: VAN = a + b*seen + sum_k c_k * z(cov_k) (OLS). b_adj is averaged over subjects.
"""
import csv, json, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cohen_killtest as ck  # noqa: E402

ROOT = HERE.parents[1]
OUT = HERE / "out"
PREREG = ROOT / "docs" / "prereg" / "2026-11-24_cohen_van_arousal_control.md"
COVS = ["local", "prev", "order", "p1", "prestd"]
NBR = 10
B = 10000
SEED = 20261125
RETAIN = 0.5            # ROBUST needs the retained fraction's CI lower bound >= this
PLANT_UV = 1.16         # the sealed confirmatory effect size
RUNS = 300
MAX_FALSE = 0.05


def residual_seen():
    """(sub, onset) -> (local, prev): residual seen rate around each report face trial."""
    by = {}
    for r in csv.DictReader(open(HERE / "trials.csv")):
        if r["block"] == "report" and r["kind"] == "face" and r["resp"] in ("1", "2") and r["soa"]:
            by.setdefault(r["sub"], []).append((int(r["onset"]), r["soa"], r["resp"] == "1"))
    out = {}
    for s, rows in by.items():
        rows.sort()
        soa = np.array([x[1] for x in rows])
        y = np.array([x[2] for x in rows], float)
        exp = np.array([y[soa == q].mean() for q in soa])
        res = y - exp
        for i, (on, _, _) in enumerate(rows):
            nb = np.r_[res[max(0, i - NBR):i], res[i + 1:i + 1 + NBR]]
            out[(s, on)] = (float(nb.mean()), float(res[i - 1]) if i else 0.0)
    return out


def covars():
    from scipy.signal import butter, filtfilt
    RS = residual_seen()
    D = ck.load()
    store = {}
    chs = sorted(set(ck.COMP["VAN"][0] + ck.COMP["P1"][0]))
    bb, aa = butter(4, ck.LOWPASS / (ck.FS / 2))
    for s in D:
        p = ck.preprocess(s)
        k = p["keep"]
        d = np.load(ck.EP / f"{s}.npz")
        x = filtfilt(bb, aa, d["X"][k][:, [c - 1 for c in chs + [ck.LMAST]], :].astype(np.float64) * float(d["scale_uv"]),
                     axis=2, padlen=100)
        sc = x[:, :-1, :] - x[:, -1:, :] / 2
        pre = sc[:, :, :ck.samp(0)]
        bad = set(p["bad"])
        use = [i for i, c in enumerate(chs) if c not in bad]
        prestd = pre[:, use, :].std(axis=2).mean(axis=1)
        on = D[s]["onset"]
        assert len(on) == k.sum() and np.array_equal(on, p["onset"][k])
        lp = np.array([RS[(s, int(o))] for o in on])
        store[f"{s}|local"], store[f"{s}|prev"] = lp[:, 0], lp[:, 1]
        store[f"{s}|order"] = np.argsort(np.argsort(on)).astype(float)
        store[f"{s}|p1"] = D[s]["P1"]
        store[f"{s}|prestd"] = prestd
    np.savez_compressed(OUT / "arousal_covars.npz", **store)
    print("covariates for", len(D), "subjects")


def load():
    D = ck.load()
    z = np.load(OUT / "arousal_covars.npz")
    for k in z.files:
        s, c = k.split("|")
        D[s][c] = z[k]
    return D


def zs(v):
    sd = v.std()
    return (v - v.mean()) / sd if sd > 0 else v * 0


def subject_betas(van, seen, C):
    """Returns (unadjusted diff, adjusted b) for one subject. C: trials x covariates (z-scored)."""
    y = seen.astype(float)
    raw = van[seen].mean() - van[~seen].mean()
    X = np.column_stack([np.ones(len(y)), y, C])
    b = np.linalg.lstsq(X, van, rcond=None)[0]
    return raw, b[1]


class _T(dict):
    def __missing__(self, n):
        from scipy.stats import t
        return float(t.ppf(0.975, n - 1))


TQ = _T()


def group(raws, adjs, rng):
    raws, adjs = np.array(raws), np.array(adjs)
    n = len(raws)
    idx = rng.integers(0, n, size=(B, n))
    br, ba = raws[idx].mean(axis=1), adjs[idx].mean(axis=1)
    ratio = ba / br
    return dict(n=n, unadjusted_uv=float(raws.mean()), adjusted_uv=float(adjs.mean()),
                adjusted_ci95=[float(adjs.mean() - TQ[n] * adjs.std(ddof=1) / np.sqrt(n)),
                               float(adjs.mean() + TQ[n] * adjs.std(ddof=1) / np.sqrt(n))],   # t-interval over subjects
                retained=float(adjs.mean() / raws.mean()),
                retained_ci95=[float(np.percentile(ratio, 2.5)), float(np.percentile(ratio, 97.5))],
                subjects_adjusted_negative=int(np.sum(adjs < 0)))


def decide(g):
    lo_a, hi_a = g["adjusted_ci95"]
    lo_r, hi_r = g["retained_ci95"]
    if hi_a < 0 and lo_r >= RETAIN:
        return "ROBUST"
    if hi_a < 0:
        return "REDUCED"
    if hi_r < RETAIN:
        return "EXPLAINED"
    return "INCONCLUSIVE"


def analyse(D, subs, labels, van=None, rng=None):
    raws, adjs = [], []
    for s in subs:
        C = np.column_stack([zs(D[s][c]) for c in COVS])
        v = D[s]["VAN"] if van is None else van[s]
        r, a = subject_betas(v, labels[s], C)
        raws.append(r)
        adjs.append(a)
    g = group(raws, adjs, rng)
    g["verdict"] = decide(g)
    return g


def fake_labels(D, s, rng, w=0.5):
    """Labels driven by the covariates (logistic, weight w per z-scored covariate), with the subject's real seen rate."""
    C = np.column_stack([zs(D[s][c]) for c in COVS])
    sgn = np.array([1, 1, -1, -1, -1])                      # seeing up with local/prev rate, down with time, P1, prestd
    eta = C @ (w * sgn) + rng.logistic(size=len(C))
    rate = (D[s]["resp"] == 1).mean()
    return eta > np.quantile(eta, 1 - rate)


def calibrate():
    D = load()
    subs = ck.eligible("confirm")
    rng = np.random.default_rng(SEED)
    tally = {w: {} for w in ("null_shuffled", "planted_direct_clean", "planted_direct_coupled", "planted_confound")}
    fit, cpl = [], []
    for k in range(RUNS):
        # null: labels shuffled, no effect
        lab = {s: rng.permutation(D[s]["resp"] == 1) for s in subs}
        v = analyse(D, subs, lab, rng=rng)["verdict"]
        tally["null_shuffled"][v] = tally["null_shuffled"].get(v, 0) + 1
        # direct, clean: shuffled labels plus a direct -1.16 uV effect (power for ROBUST)
        van = {s: D[s]["VAN"] - PLANT_UV * lab[s] for s in subs}
        v = analyse(D, subs, lab, van=van, rng=rng)["verdict"]
        tally["planted_direct_clean"][v] = tally["planted_direct_clean"].get(v, 0) + 1
        # direct, coupled (descriptive): labels from covariates plus the direct effect. The real VAN's own covariate
        # link then adds to the raw difference, so the true retained fraction is below 1 here by construction.
        lab = {s: fake_labels(D, s, rng) for s in subs}
        van = {s: D[s]["VAN"] - PLANT_UV * lab[s] for s in subs}
        g = analyse(D, subs, lab, van=van, rng=rng)
        cpl.append((g["unadjusted_uv"], g["adjusted_uv"]))
        tally["planted_direct_coupled"][g["verdict"]] = tally["planted_direct_coupled"].get(g["verdict"], 0) + 1
        # confound: labels from covariates; the VAN gets a covariate-driven shift that makes seen - unseen about
        # -1.16 uV with no direct effect of the label
        van = {}
        for s in subs:
            C = np.column_stack([zs(D[s][c]) for c in COVS])
            u = C @ np.array([1, 1, -1, -1, -1]) / np.sqrt(5)
            d = u[lab[s]].mean() - u[~lab[s]].mean()
            van[s] = D[s]["VAN"] - PLANT_UV * u / max(d, 1e-6)
        g = analyse(D, subs, lab, van=van, rng=rng)
        fit.append(g["unadjusted_uv"])
        tally["planted_confound"][g["verdict"]] = tally["planted_confound"].get(g["verdict"], 0) + 1
    res = dict(subjects=len(subs), runs=RUNS, plant_uv=PLANT_UV, retain_bar=RETAIN,
               rates={w: {v: n / RUNS for v, n in t.items()} for w, t in tally.items()},
               confound_mean_unadjusted_uv=float(np.mean(fit)),
               coupled_mean_unadjusted_uv=float(np.mean([c[0] for c in cpl])),
               coupled_mean_adjusted_uv=float(np.mean([c[1] for c in cpl])))
    r = res["rates"]
    res["false_robust_null"] = r["null_shuffled"].get("ROBUST", 0) + r["null_shuffled"].get("REDUCED", 0)
    res["false_robust_confound"] = r["planted_confound"].get("ROBUST", 0)
    res["power_direct"] = r["planted_direct_clean"].get("ROBUST", 0)
    res["PASS"] = bool(res["false_robust_null"] <= MAX_FALSE and res["false_robust_confound"] <= MAX_FALSE)
    (OUT / "arousal_calibration.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


def run():
    from evidence import require_sealed
    for f in (PREREG, Path(__file__), OUT / "arousal_calibration.json", OUT / "arousal_covars.npz"):
        require_sealed(str(f))
    cal = json.loads((OUT / "arousal_calibration.json").read_text())
    assert cal["PASS"], "calibration failed: no real-label run"
    D = load()
    rng = np.random.default_rng(SEED)
    res = {}
    for grp in ("confirm", "pilot"):
        subs = ck.eligible(grp)
        lab = {s: D[s]["resp"] == 1 for s in subs}
        g = analyse(D, subs, lab, rng=rng)
        # descriptive: how each covariate differs between seen and unseen (z units), and leave-one-covariate-in
        g["covariate_seen_minus_unseen_z"] = {c: float(np.mean([zs(D[s][c])[lab[s]].mean() - zs(D[s][c])[~lab[s]].mean()
                                                                for s in subs])) for c in COVS}
        one = {}
        for c in COVS:
            adj = []
            for s in subs:
                adj.append(subject_betas(D[s]["VAN"], lab[s], zs(D[s][c])[:, None])[1])
            one[c] = float(np.mean(adj))
        g["adjusted_uv_one_covariate"] = one
        res[grp] = g
    res["verdict_from"] = "confirm"
    (OUT / "arousal_result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    {"covars": covars, "calibrate": calibrate, "run": run}[sys.argv[1]]()
