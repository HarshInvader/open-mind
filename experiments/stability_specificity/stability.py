"""Is "seen trials are more stable" (Schurger et al. 2015) explained by evoked amplitude? (Cohen 2024 SOA-50 epochs)
Prereg: docs/prereg/2026-11-25_stability_specificity.md   (Fable round 16, item 5; zero new bytes)

Measure (Schurger 2015): within a 100 ms window, dva = 1 - || mean_t( v_t / ||v_t|| ) ||, v_t = the sensor vector at
sample t (average reference). Lower dva = more stable. Computed per trial, then averaged over trials (primary,
"within-trial"); and once on the trial-mean vectors of each window ("across-trial", secondary).

Kill test (split-half, no trial scored by the ERP it was injected with): add the subject's seen-minus-unseen ERP
(from half A) to the unseen trials of half B. If the stability difference is a property of evoked amplitude, the
injected unseen trials become as stable as the seen ones.

    python -I stability.py gate     # synthetic, label-free: can injection tell amplitude from stability? -> out/gate.json
    python -I stability.py run      # only on GATE PASS -> out/subjects.json, out/summary.json (verdict)
    python -I stability.py pilot    # unsealed: timing on one subject with permuted labels; prints timing only
"""
import json, os, sys, time
from pathlib import Path
from multiprocessing import Pool

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "latency_spread"))
sys.path.insert(0, str(ROOT / "experiments" / "rules"))
import latency_spread as L  # noqa: E402  (load_subject and eligible only: same preprocessing as the sealed studies)

OUT = HERE / "out"
PREREG = ROOT / "docs" / "prereg" / "2026-11-25_stability_specificity.md"
FS, TMIN, NS = L.FS, L.TMIN, L.NS
WINS = [(0.300, 0.400), (0.400, 0.500)]           # primary: mean over these two 100 ms windows
COURSE = [(c - 0.05, c + 0.05) for c in np.arange(0.0, 0.55, 0.02)]   # descriptive time course (centres 0-540 ms)
SPLITS = 20
NBOOT = 5000
WORKERS = 4
SEED = 20261207


def sealed():
    from evidence import require_sealed
    for f in (PREREG, Path(__file__)):
        require_sealed(str(f))
    OUT.mkdir(exist_ok=True)


def idx(w):
    return int(round((w[0] - TMIN) * FS)), int(round((w[1] - TMIN) * FS))


def dva_trials(X, w):
    """Within-trial dva per trial (trials x chans x samples) in window w."""
    a, b = idx(w)
    V = X[:, :, a:b]
    U = V / np.linalg.norm(V, axis=1, keepdims=True)
    return 1 - np.linalg.norm(U.mean(axis=2), axis=1)


def dva_across(X, w):
    """Across-trial dva: each trial's window-mean vector, normalised; 1 - norm of their mean."""
    a, b = idx(w)
    m = X[:, :, a:b].mean(axis=2)
    m = m / np.linalg.norm(m, axis=1, keepdims=True)
    return float(1 - np.linalg.norm(m.mean(axis=0)))


def prim(X, fn):
    return float(np.mean([np.mean(fn(X, w)) for w in WINS]))


def subject_stats(sub, y_override=None):
    X, y, _, _ = L.subject(sub)
    if y_override is not None:
        y = y_override
    return sub, stats_from(X, y, np.random.default_rng([SEED, int(sub)]))


def stats_from(X, y, rng):
    X = X - X.mean(axis=1, keepdims=True)                      # average reference
    S, U = X[y == 1], X[y == 0]
    n = min(len(S), len(U))
    acc = {k: [] for k in ("seen", "unseen", "inj", "injnoise", "across_seen", "across_unseen", "across_inj")}
    course = {k: [] for k in ("seen", "unseen", "inj")}
    for _ in range(SPLITS):
        ps, pu = rng.permutation(len(S)), rng.permutation(len(U))
        hs, hu = len(S) // 2, len(U) // 2
        for A in (0, 1):
            sA = S[ps[:hs]] if A == 0 else S[ps[hs:]]
            sB = S[ps[hs:]] if A == 0 else S[ps[:hs]]
            uA = U[pu[:hu]] if A == 0 else U[pu[hu:]]
            uB = U[pu[hu:]] if A == 0 else U[pu[:hu]]
            m = min(len(sB), len(uB), n)                         # equal trial counts in the scored half
            sB = sB[rng.permutation(len(sB))[:m]]
            uB = uB[rng.permutation(len(uB))[:m]]
            d = sA.mean(0) - uA.mean(0)                          # half-A ERP difference (all samples, channels)
            inj = uB + d
            rs = (sA - sA.mean(0)).std()                         # broadband residual SD, half A
            ru = (uA - uA.mean(0)).std()
            injn = (uB - uB.mean(0)) * (rs / ru) + uB.mean(0) + d
            acc["seen"].append(prim(sB, dva_trials))
            acc["unseen"].append(prim(uB, dva_trials))
            acc["inj"].append(prim(inj, dva_trials))
            acc["injnoise"].append(prim(injn, dva_trials))
            acc["across_seen"].append(float(np.mean([dva_across(sB, w) for w in WINS])))
            acc["across_unseen"].append(float(np.mean([dva_across(uB, w) for w in WINS])))
            acc["across_inj"].append(float(np.mean([dva_across(inj, w) for w in WINS])))
            for k, Z in (("seen", sB), ("unseen", uB), ("inj", inj)):
                course[k].append([float(np.mean(dva_trials(Z, w))) for w in COURSE])
    out = {k: float(np.mean(v)) for k, v in acc.items()}
    out["course"] = {k: np.mean(v, axis=0).tolist() for k, v in course.items()}
    out["n_seen"], out["n_unseen"] = int(len(S)), int(len(U))
    return out


# ------------------------------------------------------------------ synthetic gate (label-free; runs first)
T = TMIN + np.arange(NS) / FS
AMP_SEEN, AMP_UNSEEN = 3.5, 1.5        # uV peak at the topography's unit-norm-scaled ROI (AMP world)
AMP_STAB = 2.5                         # uV, both classes (STAB world)
WALK_SD = 0.10                         # rad per sample: unseen pattern random walk (STAB world)
GATE_SHARE_AMP, GATE_SHARE_STAB = 0.8, 0.5


def plant(sub, world):
    """Noise = every kept trial minus the grand mean (labels unused); pseudo-labels at the real seen count."""
    X, y, _, _ = L.subject(sub)
    rng = np.random.default_rng([SEED, int(sub), 1 if world == "AMP" else 2])
    N = X - X.mean(0)
    n, C = N.shape[0], N.shape[1]
    yp = np.zeros(n, int)
    yp[rng.choice(n, int(y.sum()), replace=False)] = 1
    a, b = idx((0.300, 0.500))
    topo = X.mean(0)[:, a:b].mean(1)                            # grand-average 300-500 ms topography (label-free)
    topo = topo - topo.mean()
    topo = topo / np.abs(topo).max()
    wave = np.exp(-(T - 0.40) ** 2 / (2 * 0.08 ** 2))
    if world == "AMP":
        amp = np.where(yp == 1, AMP_SEEN, AMP_UNSEEN)
        N += amp[:, None, None] * topo[None, :, None] * wave[None, None, :]
        return N, yp
    # STAB: unseen pattern rotates within the trial towards a random orthogonal direction; seen pattern fixed.
    u = topo / np.linalg.norm(topo)
    th = np.cumsum(rng.normal(0, WALK_SD, (n, NS)), axis=1)
    th -= th[:, [int(round((0.40 - TMIN) * FS))]]               # angle 0 at the peak
    q = rng.normal(size=(n, C))
    q -= (q @ u)[:, None] * u[None, :]
    q -= q.mean(1, keepdims=True)
    q /= np.linalg.norm(q, axis=1, keepdims=True)
    cosm = np.cos(th).mean(0)                                   # seen amplitude matched to the unseen mean
    for i in range(n):
        if yp[i] == 1:
            pat = AMP_STAB * cosm[None, :] * u[:, None]
        else:
            pat = AMP_STAB * (np.cos(th[i])[None, :] * u[:, None] + np.sin(th[i])[None, :] * q[i][:, None])
        N[i] += np.linalg.norm(topo) * pat * wave[None, :]
    return N, yp


def _gate_one(args):
    sub, world = args
    X, yp = plant(sub, world)
    return sub, stats_from(X, yp, np.random.default_rng([SEED, int(sub), 7]))


def group(r):
    keys = sorted(r)
    dobs = np.array([r[s]["unseen"] - r[s]["seen"] for s in keys])
    t_obs = float(dobs.mean() / (dobs.std(ddof=1) / np.sqrt(len(dobs))))
    rng = np.random.default_rng(SEED + 1)
    boot = [explained(r, list(rng.choice(keys, len(keys)))) for _ in range(NBOOT)]
    return dict(t_seen_more_stable=t_obs, explained_share=explained(r, keys),
                explained_ci95=[float(v) for v in np.nanpercentile(boot, [2.5, 97.5])],
                seen_minus_unseen_dva=float(-dobs.mean()))


def gate():
    sealed()
    subs = L.eligible()
    out = {}
    with Pool(WORKERS) as p:
        for world in ("AMP", "STAB"):
            out[world] = group(dict(p.map(_gate_one, [(s, world) for s in subs])))
    tcrit = float(stats.t.ppf(0.95, len(subs) - 1))
    ok = (out["AMP"]["t_seen_more_stable"] > tcrit and out["STAB"]["t_seen_more_stable"] > tcrit
          and out["AMP"]["explained_ci95"][0] >= GATE_SHARE_AMP and out["STAB"]["explained_ci95"][1] <= GATE_SHARE_STAB)
    out.update(t_crit_one_sided=tcrit, verdict="GATE PASS" if ok else "METHOD BLIND")
    (OUT / "gate.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


def explained(r, keys, inj="inj", seen="seen", unseen="unseen"):
    """Share of the seen-unseen stability difference removed by injection (group ratio of means)."""
    obs = np.mean([r[s][unseen] - r[s][seen] for s in keys])
    res = np.mean([r[s][inj] - r[s][seen] for s in keys])
    return float(1 - res / obs) if obs != 0 else float("nan")


def run():
    sealed()
    if json.loads((OUT / "gate.json").read_text())["verdict"] != "GATE PASS":
        print("gate did not pass; the real labels are not analysed (prereg section 3)")
        return
    subs = L.eligible()
    t0 = time.time()
    with Pool(WORKERS) as p:
        r = dict(p.map(subject_stats, subs))
    keys = sorted(r)
    dobs = np.array([r[s]["unseen"] - r[s]["seen"] for s in keys])      # > 0: seen more stable
    tcrit = stats.t.ppf(0.95, len(keys) - 1)
    t_obs = float(dobs.mean() / (dobs.std(ddof=1) / np.sqrt(len(dobs))))
    replicates = bool(t_obs > tcrit)
    rng = np.random.default_rng(SEED + 1)
    boot = {"inj": [], "injnoise": [], "across": []}
    for _ in range(NBOOT):
        bs = list(rng.choice(keys, len(keys)))
        boot["inj"].append(explained(r, bs))
        boot["injnoise"].append(explained(r, bs, inj="injnoise"))
        boot["across"].append(explained(r, bs, "across_inj", "across_seen", "across_unseen"))
    ci = {k: [float(v) for v in np.nanpercentile(b, [2.5, 97.5])] for k, b in boot.items()}
    S = explained(r, keys)
    if not replicates:
        v = "NO REPLICATION"
    elif ci["inj"][0] >= 0.8:
        v = "STABILITY DIFFERENCE EXPLAINED BY EVOKED AMPLITUDE"
    elif ci["inj"][1] <= 0.5:
        v = "STABILITY DIFFERENCE NOT EXPLAINED BY EVOKED AMPLITUDE"
    else:
        v = "PARTLY EXPLAINED"
    dres = np.array([r[s]["inj"] - r[s]["seen"] for s in keys])
    summ = dict(verdict=v, subjects=len(keys), seen_minus_unseen_dva=float(-dobs.mean()), t_seen_more_stable=t_obs,
                t_crit_one_sided=float(tcrit), replicates=replicates,
                explained_share=S, explained_ci95=ci["inj"],
                injected_minus_seen_dva=float(dres.mean()),
                t_injected_minus_seen=float(dres.mean() / (dres.std(ddof=1) / np.sqrt(len(dres)))),
                explained_share_with_noise_rescale=explained(r, keys, inj="injnoise"), with_noise_ci95=ci["injnoise"],
                across_trial=dict(seen_minus_unseen=float(np.mean([r[s]["across_seen"] - r[s]["across_unseen"]
                                                                   for s in keys])),
                                  explained_share=explained(r, keys, "across_inj", "across_seen", "across_unseen"),
                                  ci95=ci["across"]),
                course_centres_ms=[round(1000 * (w[0] + 0.05)) for w in COURSE],
                course_group={k: np.mean([r[s]["course"][k] for s in keys], axis=0).tolist()
                              for k in ("seen", "unseen", "inj")},
                seconds=round(time.time() - t0))
    (OUT / "subjects.json").write_text(json.dumps(r) + "\n")
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1) + "\n")
    print(json.dumps({k: v for k, v in summ.items() if k not in ("course_group", "course_centres_ms")}, indent=1))


def pilot():
    """Unsealed: timing on one subject with permuted labels; prints timing only."""
    sub = L.eligible()[0]
    X, y, _, _ = L.subject(sub)
    t = time.time()
    subject_stats(sub, np.random.default_rng(1).permutation(y))
    print("one subject", round(time.time() - t, 2), "s")


if __name__ == "__main__":
    {"gate": gate, "run": run, "pilot": pilot}[sys.argv[1]]()
