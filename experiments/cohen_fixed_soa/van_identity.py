"""Robustness of the sealed VAN result (Fable round 15, study 2): (a) within the same face image (identity dummies),
(b) under an average reference, with the fronto-central positive counterpart (VPP). Prereg:
docs/prereg/2026-11-24_cohen_van_identity_avgref.md

    python -I van_identity.py prep       # label-free: average-reference VAN and VPP per kept trial -> out/avgref.npz (small)
    python -I van_identity.py calibrate  # fake labels only -> out/identity_calibration.json
    python -I van_identity.py run        # real labels; refuses unless sealed -> out/identity_result.json
"""
import json, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cohen_killtest as ck  # noqa: E402

OUT = HERE / "out"
PREREG = HERE.parents[1] / "docs" / "prereg" / "2026-11-24_cohen_van_identity_avgref.md"
VPP = [1, 2, 3, 7, 8]          # Cz, FCz and neighbours (layout coordinates), 140-200 ms, predicted seen - unseen > 0
WIN = (140, 200)
B = 10000
SEED = 20261127
RUNS = 300
PLANT_UV = 1.2
RETAIN = 0.5


def prep():
    from scipy.signal import butter, filtfilt
    bb, aa = butter(4, ck.LOWPASS / (ck.FS / 2))
    D = ck.load()
    store = {}
    for s in D:
        p = ck.preprocess(s)
        k = p["keep"]
        d = np.load(ck.EP / f"{s}.npz")
        x = filtfilt(bb, aa, d["X"][k][:, [c - 1 for c in ck.SCALP], :].astype(np.float64) * float(d["scale_uv"]),
                     axis=2, padlen=100)
        good = [i for i, c in enumerate(ck.SCALP) if c not in set(p["bad"])]
        x = x - x[:, good, :].mean(axis=1, keepdims=True)            # average reference over good scalp channels
        x -= x[:, :, :ck.samp(0)].mean(axis=2, keepdims=True)
        a, b = ck.samp(WIN[0]), ck.samp(WIN[1])
        for name, chs in (("VAN_avg", ck.COMP["VAN"][0]), ("VPP_avg", VPP)):
            idx = [ck.SCALP.index(c) for c in chs if c not in set(p["bad"])]
            store[f"{s}|{name}"] = x[:, idx, a:b].mean(axis=(1, 2))
        assert len(store[f"{s}|VAN_avg"]) == len(D[s]["VAN"])
    np.savez_compressed(OUT / "avgref.npz", **store)
    print("average-reference values for", len(D), "subjects")


def load():
    D = ck.load()
    z = np.load(OUT / "avgref.npz")
    for k in z.files:
        s, c = k.split("|")
        D[s][c] = z[k]
    return D


def betas(v, seen, ident):
    raw = v[seen].mean() - v[~seen].mean()
    ids = np.unique(ident)
    X = np.column_stack([seen.astype(float)] + [(ident == i).astype(float) for i in ids])
    b = np.linalg.lstsq(X, v, rcond=None)[0]
    return raw, b[0]


def tq(n):
    from scipy.stats import t
    return float(t.ppf(0.975, n - 1))


def group(raws, adjs, rng, sign=-1):
    raws, adjs = np.array(raws), np.array(adjs)
    n = len(raws)
    idx = rng.integers(0, n, size=(B, n))
    ratio = adjs[idx].mean(axis=1) / raws[idx].mean(axis=1)
    se = adjs.std(ddof=1) / np.sqrt(n)
    g = dict(n=n, unadjusted_uv=float(raws.mean()), adjusted_uv=float(adjs.mean()),
             adjusted_ci95=[float(adjs.mean() - tq(n) * se), float(adjs.mean() + tq(n) * se)],
             retained=float(adjs.mean() / raws.mean()),
             retained_ci95=[float(np.percentile(ratio, 2.5)), float(np.percentile(ratio, 97.5))])
    lo, hi = g["adjusted_ci95"]
    excl = hi < 0 if sign < 0 else lo > 0                     # one-sided, predicted direction fixed in advance
    if excl and g["retained_ci95"][0] > RETAIN:
        g["verdict"] = "ROBUST"
    elif g["retained_ci95"][1] < RETAIN:
        g["verdict"] = "EXPLAINED"
    elif excl:
        g["verdict"] = "REDUCED"
    else:
        g["verdict"] = "INCONCLUSIVE"
    return g


def analyse(D, subs, labels, rng, comp="VAN", van=None):
    sign = 1 if comp == "VPP_avg" else -1
    raws, adjs = [], []
    for s in subs:
        v = D[s][comp] if van is None else van[s]
        r, a = betas(v, labels[s], D[s]["ident"])
        raws.append(r)
        adjs.append(a)
    return group(raws, adjs, rng, sign)


def calibrate():
    D = load()
    subs = ck.eligible("confirm")
    rng = np.random.default_rng(SEED)
    T = {w: {} for w in ("null", "confound", "within")}
    raw_conf = []
    for k in range(RUNS):
        lab = {s: rng.permutation(D[s]["resp"] == 1) for s in subs}
        v = analyse(D, subs, lab, rng)["verdict"]
        T["null"][v] = T["null"].get(v, 0) + 1
        # within-image effect: shuffled labels plus a direct -1.2 uV seen effect
        van = {s: D[s]["VAN"] - PLANT_UV * lab[s] for s in subs}
        v = analyse(D, subs, lab, rng, van=van)["verdict"]
        T["within"][v] = T["within"].get(v, 0) + 1
        # between-image confound: per-image visibility offsets drive the labels, the same offsets shift the VAN, and
        # there is no within-image effect. Scaled so that seen - unseen is about -1.2 uV.
        lab2, van2 = {}, {}
        for s in subs:
            off = rng.normal(0, 1.5, 41)
            o = off[D[s]["ident"]]
            eta = o + rng.logistic(size=len(o))
            rate = (D[s]["resp"] == 1).mean()
            lab2[s] = eta > np.quantile(eta, 1 - rate)
            d = o[lab2[s]].mean() - o[~lab2[s]].mean()
            van2[s] = D[s]["VAN"] - PLANT_UV * o / max(d, 1e-6)
        g = analyse(D, subs, lab2, rng, van=van2)
        raw_conf.append(g["unadjusted_uv"])
        T["confound"][g["verdict"]] = T["confound"].get(g["verdict"], 0) + 1
    res = dict(subjects=len(subs), runs=RUNS, plant_uv=PLANT_UV,
               rates={w: {v: n / RUNS for v, n in t.items()} for w, t in T.items()},
               confound_mean_unadjusted_uv=float(np.mean(raw_conf)))
    r = res["rates"]
    res["false_robust_null"] = r["null"].get("ROBUST", 0) + r["null"].get("REDUCED", 0)
    res["false_robust_confound"] = r["confound"].get("ROBUST", 0)
    res["explained_confound"] = r["confound"].get("EXPLAINED", 0)
    res["power_within"] = r["within"].get("ROBUST", 0)
    res["PASS"] = bool(res["false_robust_null"] <= 0.05 and res["explained_confound"] >= 0.75 and res["false_robust_confound"] <= 0.05 and
                       res["power_within"] >= 0.9)
    (OUT / "identity_calibration.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


def run():
    from evidence import require_sealed
    for f in (PREREG, Path(__file__), OUT / "identity_calibration.json", OUT / "avgref.npz"):
        require_sealed(str(f))
    assert json.loads((OUT / "identity_calibration.json").read_text())["PASS"], "calibration failed: no run"
    D = load()
    rng = np.random.default_rng(SEED)
    res = {}
    for grp in ("confirm", "pilot"):
        subs = ck.eligible(grp)
        lab = {s: D[s]["resp"] == 1 for s in subs}
        r = dict(within_image=analyse(D, subs, lab, rng),
                 avgref_VAN=analyse(D, subs, lab, rng, comp="VAN_avg"),
                 avgref_VPP=analyse(D, subs, lab, rng, comp="VPP_avg"))
        # average reference: present if the identity-adjusted CI excludes 0 in the predicted direction
        r["avgref_VAN"]["present"] = r["avgref_VAN"]["adjusted_ci95"][1] < 0
        r["avgref_VPP"]["present"] = r["avgref_VPP"]["adjusted_ci95"][0] > 0
        res[grp] = r
    (OUT / "identity_result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    {"prep": prep, "calibrate": calibrate, "run": run}[sys.argv[1]]()
