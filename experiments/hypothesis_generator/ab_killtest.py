"""ds001810 T2 identification screen: discovery half -> survivors -> held-out half, label-shuffled null.

Prereg: docs/prereg/2026-11-24_ab_t2_identification_killtest.md. Outcome is T2 identification, NOT seen vs unseen.

    python -I ab_killtest.py channels    # fetch each block's _channels.tsv (tiny, 1 request/s)
    python -I ab_killtest.py prep        # preprocess, eligibility (label counts only), split.json
    python -I ab_killtest.py calibrate   # shuffled-label and planted-answer checks (no real labels)
    python -I ab_killtest.py discover    # needs sealed prereg; writes survivors.json (+ hash)
    python -I ab_killtest.py heldout     # needs survivors.json; writes result.json
"""
import csv, hashlib, io, json, sys, time, urllib.request
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[2]
EP = ROOT / "datasets" / "local" / "ds001810_epochs"
CH = EP / "channels"
HERE = Path(__file__).resolve().parent
OUT = HERE / "ab_out"
PREREG = "docs/prereg/2026-11-24_ab_t2_identification_killtest.md"
S3 = "https://s3.amazonaws.com/openneuro.org/ds001810"
NONEEG = {f"EXG{i}" for i in range(1, 9)} | {"Status"}

CANDS = {  # id: (window ms, channels or None=all (GFP), direction: +1 / -1 / 0 two-sided, kind)
    "C1_P3b": ((350, 600), ["CPz", "Pz", "CP1", "CP2", "P1", "P2"], +1, "mean"),
    "C2_N2_VAN": ((200, 300), ["PO7", "PO8", "P7", "P8", "O1", "O2"], -1, "mean"),
    "C3_P1": ((80, 130), ["O1", "Oz", "O2", "PO7", "PO8"], 0, "mean"),
    "C4_N1": ((150, 200), ["PO7", "PO8", "P7", "P8"], 0, "mean"),
    "C5_frontal_late": ((300, 500), ["Fz", "FCz", "Cz", "AFz", "F2", "FC2"], +1, "mean"),
    "C6_GFP": ((300, 600), None, +1, "gfp"),
    "C7_late_posterior": ((600, 800), ["Pz", "POz", "PO3", "PO4", "Oz"], +1, "mean"),
    "C8_preT2": ((-200, 0), ["Pz", "POz", "PO3", "PO4", "Oz"], 0, "prebase"),
}
CONTROLS = {"C3_P1", "C4_N1"}
DIRS = {**{k: v[2] for k, v in CANDS.items()}, "C9_decoder": +1}


# ------------------------------------------------------------------ io
def blocks():
    return sorted(p for p in EP.glob("sub-*_*.npz"))


def fetch_channels():
    CH.mkdir(parents=True, exist_ok=True)
    for p in blocks():
        sub, ses = p.stem.split("_")
        dst = CH / f"{p.stem}.tsv"
        if dst.exists():
            continue
        url = f"{S3}/{sub}/ses-{ses}/eeg/{sub}_ses-{ses}_task-attentionalblink_channels.tsv"
        req = urllib.request.Request(url, headers={"User-Agent": "open-research-site/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            dst.write_bytes(r.read())
        time.sleep(1.0)
    print("channels:", len(list(CH.glob("*.tsv"))))


def bad_channels(stem):
    f = CH / f"{stem}.tsv"
    if not f.exists():
        raise SystemExit(f"missing {f}; run `channels` first")
    rows = csv.DictReader(io.StringIO(f.read_text()), delimiter="\t")
    return {r["name"] for r in rows if r.get("status", "").strip().lower() == "bad"}


# ------------------------------------------------------------------ preprocessing (no labels used)
def preprocess(path):
    d = np.load(path, allow_pickle=False)
    X, ch, fs, tmin = d["X"].astype(np.float64), [str(c) for c in d["ch"]], float(d["fs"]), float(d["tmin"])
    keep = [i for i, c in enumerate(ch) if c not in NONEEG and c not in bad_channels(path.stem)]
    X, ch = X[:, keep], [ch[i] for i in keep]
    X = X - X.mean(1, keepdims=True)                         # provisional average reference
    ptp = np.median(np.ptp(X, axis=2), axis=0)                # per channel, median over trials
    ok = ptp <= 5 * np.median(ptp)
    raw = d["X"].astype(np.float64)[:, keep][:, ok]
    ch = [c for c, k in zip(ch, ok) if k]
    X = raw - raw.mean(1, keepdims=True)                      # final average reference
    t = (np.arange(X.shape[2]) / fs + tmin) * 1000.0
    pre = X[:, :, t < 0].mean(2, keepdims=True)
    prebase = pre[:, :, 0] - X.mean(2)                        # C8: pre-T2 mean minus whole-epoch mean
    Xb = X - pre                                              # baseline -200..0
    good = np.ptp(Xb, axis=2).max(1) <= 150.0
    return dict(X=Xb[good], prebase=prebase[good], y=d["y"][good].astype(int), ch=ch, t=t,
                n_raw=len(d["y"]), n_rej=int((~good).sum()))


def features(b):
    X, t, ch = b["X"], b["t"], b["ch"]
    f = {}
    for k, ((lo, hi), roi, _, kind) in CANDS.items():
        w = (t >= lo) & (t < hi)
        if kind == "gfp":
            f[k] = X[:, :, w].std(1).mean(1)
            continue
        idx = [ch.index(c) for c in roi if c in ch]
        if not idx:
            f[k] = None
        elif kind == "prebase":
            f[k] = b["prebase"][:, idx].mean(1)
        else:
            f[k] = X[:, idx][:, :, w].mean((1, 2))
    return f


def dec_features(b, common):
    X, t = b["X"], b["t"]
    idx = [b["ch"].index(c) for c in common]
    bins = [((t >= lo) & (t < lo + 50)) for lo in range(0, 800, 50)]
    F = np.stack([X[:, idx][:, :, w].mean(2) for w in bins], 2).reshape(len(X), -1)
    return (F - F.mean(0)) / (F.std(0) + 1e-9)


# ------------------------------------------------------------------ stats
def auc_ranks(r, y):
    n1 = y.sum(1) if y.ndim == 2 else y.sum()
    n0 = y.shape[-1] - n1
    s = (r * y).sum(-1)
    return (s - n1 * (n1 + 1) / 2) / (n1 * n0)


def rank(x):
    from scipy.stats import rankdata
    return rankdata(x)


def group_test(scores, labels, direction, n_perm, seed):
    """scores/labels: dict subj -> arrays. Mean within-subject AUC; null by within-subject label shuffles."""
    rng = np.random.default_rng(seed)
    subs = [s for s in scores if scores[s] is not None]
    obs, null = [], np.zeros(n_perm)
    for s in subs:
        r, y = rank(scores[s]), labels[s]
        a = auc_ranks(r, y)
        obs.append(a)
        P = np.argsort(rng.random((n_perm, len(y))), axis=1)
        null += auc_ranks(r[None, :], y[P])
    obs, null = np.array(obs), null / len(subs)
    m = obs.mean()
    if direction == 0:
        p = (1 + np.sum(np.abs(null - 0.5) >= abs(m - 0.5))) / (n_perm + 1)
    else:
        sm, sn = direction * (m - 0.5), direction * (null - 0.5)
        p = (1 + np.sum(sn >= sm)) / (n_perm + 1)
    return dict(auc=float(m), p=float(p), n_sub=len(subs), per_sub=obs.tolist())


def boot_ci(v, B=5000, seed=3):
    rng = np.random.default_rng(seed)
    v = np.asarray(v)
    m = v[rng.integers(0, len(v), (B, len(v)))].mean(1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def holm(ps):
    order = np.argsort(ps)
    out, run = np.empty(len(ps)), 0.0
    for i, j in enumerate(order):
        run = max(run, min(1.0, (len(ps) - i) * ps[j]))
        out[j] = run
    return out


def fit_decoder(F, y):
    m = LogisticRegression(C=0.01, class_weight="balanced", max_iter=2000)
    return m.fit(F, y)


# ------------------------------------------------------------------ pipeline on (possibly fake) labels
def pipeline(subj, labels, split, common, n_perm, seed=2411, with_dec=True):
    disc, held = split["discovery"], split["heldout"]
    out = dict(discovery={}, heldout={})
    for k in CANDS:
        sc = {s: subj[s]["f"][k] for s in disc}
        out["discovery"][k] = group_test(sc, {s: labels[s] for s in disc}, DIRS[k], n_perm, seed)
    if with_dec and common:
        dv = {}
        for s in disc:
            tr = [u for u in disc if u != s]
            m = fit_decoder(np.vstack([subj[u]["F"] for u in tr]), np.concatenate([labels[u] for u in tr]))
            dv[s] = m.decision_function(subj[s]["F"])
        out["discovery"]["C9_decoder"] = group_test(dv, {s: labels[s] for s in disc}, +1, n_perm, seed)
    surv = [k for k, r in out["discovery"].items() if r["p"] < 0.05]
    if with_dec and common and "C9_decoder" in surv:
        model = fit_decoder(np.vstack([subj[u]["F"] for u in disc]), np.concatenate([labels[u] for u in disc]))
    for k in (surv if held else []):
        if k == "C9_decoder":
            sc = {s: model.decision_function(subj[s]["F"]) for s in held}
        else:
            sc = {s: subj[s]["f"][k] for s in held}
        out["heldout"][k] = group_test(sc, {s: labels[s] for s in held}, DIRS[k], n_perm, seed + 1)
    if surv and held:
        adj = holm(np.array([out["heldout"][k]["p"] for k in surv]))
        for k, a in zip(surv, adj):
            out["heldout"][k]["p_holm"] = float(a)
    out["survivors"] = surv
    return out


def load_prepped():
    P = np.load(OUT / "prepped.npz", allow_pickle=True)["d"].item()
    return P["subj"], P["labels"], json.loads((OUT / "split.json").read_text()), P["common"]


def prep():
    OUT.mkdir(exist_ok=True)
    per = {}
    for p in blocks():
        sub = p.stem.split("_")[0]
        per.setdefault(sub, []).append(preprocess(p))
    common = None
    rows, subj, labels = [], {}, {}
    for sub, bl in sorted(per.items()):
        y = np.concatenate([b["y"] for b in bl])
        nc, ni = int(y.sum()), int((1 - y).sum())
        elig = nc >= 20 and ni >= 20
        rows.append(dict(sub=sub, blocks=len(bl), trials=sum(b["n_raw"] for b in bl),
                         rejected=sum(b["n_rej"] for b in bl), correct=nc, incorrect=ni, eligible=elig,
                         channels=min(len(b["ch"]) for b in bl)))
        if not elig:
            continue
        for b in bl:
            common = set(b["ch"]) if common is None else common & set(b["ch"])
        subj[sub], labels[sub] = bl, y
    common = [c for c in per[next(iter(per))][0]["ch"] if c in common] if common else []
    if len(common) < 40:
        common = []
    for sub, bl in subj.items():
        fs = [features(b) for b in bl]
        f = {k: (None if any(x[k] is None for x in fs) else np.concatenate([x[k] for x in fs])) for k in CANDS}
        F = np.vstack([dec_features(b, common) for b in bl]) if common else None
        subj[sub] = dict(f=f, F=F)
    ids = sorted(subj)
    rng = np.random.default_rng(1810)
    perm = [ids[i] for i in rng.permutation(len(ids))]
    h = -(-len(ids) // 2)
    split = dict(discovery=sorted(perm[:h]), heldout=sorted(perm[h:]), seed=1810)
    (OUT / "split.json").write_text(json.dumps(split, indent=1) + "\n")
    with open(OUT / "eligibility.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    np.savez(OUT / "prepped.npz", d=np.array(dict(subj=subj, labels=labels, common=common), dtype=object))
    print(f"eligible {len(ids)} of {len(rows)}; discovery {h}, held-out {len(ids) - h}; common channels {len(common)}")
    print(f"rejected {sum(r['rejected'] for r in rows)} of {sum(r['trials'] for r in rows)} trials")


def shuffled(labels, rng):
    return {s: rng.permutation(y) for s, y in labels.items()}


def calibrate(n_null=200, n_plant=50):
    subj, labels, split, common = load_prepped()
    rng = np.random.default_rng(7)
    fp = 0
    for i in range(n_null):
        r = pipeline(subj, shuffled(labels, rng), split, common, 500, seed=10 + i, with_dec=bool(common))
        hit = [k for k, v in r["heldout"].items() if k not in CONTROLS and v.get("p_holm", 1) < 0.05]
        fp += bool(hit)
        if i % 20 == 0:
            print("null run", i, "fp so far", fp, flush=True)
    rec = 0
    for i in range(n_plant):
        lab = shuffled(labels, rng)
        planted = {}
        for s, d in subj.items():
            f = dict(d["f"])
            add = (lab[s] == 1) & (rng.random(len(lab[s])) < 0.5)
            # +1 uV on the C1 window mean, -1 uV on the C2 window mean, for the planted trials
            f["C1_P3b"] = f["C1_P3b"] + 1.0 * add
            f["C2_N2_VAN"] = f["C2_N2_VAN"] - 1.0 * add
            planted[s] = dict(f=f, F=d["F"])
        r = pipeline(planted, lab, split, common, 500, seed=500 + i, with_dec=False)
        ok = all(r["heldout"].get(k, {}).get("p_holm", 1) < 0.05 for k in ("C1_P3b", "C2_N2_VAN"))
        rec += ok
    res = dict(null_runs=n_null, any_noncontrol_fp=fp / n_null, plant_runs=n_plant, plant_recovered=rec / n_plant,
               pass_null=fp / n_null <= 0.10, pass_plant=rec / n_plant >= 0.80)
    (OUT / "calibration.json").write_text(json.dumps(res, indent=1) + "\n")
    print(res)


def require_seal():
    sys.path.insert(0, str(ROOT / "experiments" / "rules"))
    from evidence import require_sealed
    import os
    os.chdir(ROOT)
    return require_sealed(PREREG)


def discover():
    t = require_seal()
    subj, labels, split, common = load_prepped()
    held = set(split["heldout"])
    r = pipeline({s: v for s, v in subj.items() if s not in held}, {s: v for s, v in labels.items() if s not in held},
                 dict(discovery=split["discovery"], heldout=[]), common, 5000)
    body = json.dumps(dict(sealed=t, discovery=r["discovery"], survivors=r["survivors"]), indent=1) + "\n"
    (OUT / "survivors.json").write_text(body)
    print("survivors:", r["survivors"], "sha256", hashlib.sha256(body.encode()).hexdigest())


def heldout():
    require_seal()
    sv = json.loads((OUT / "survivors.json").read_text())
    subj, labels, split, common = load_prepped()
    r = pipeline(subj, labels, split, common, 5000)
    assert r["survivors"] == sv["survivors"], "discovery not reproducible"
    for k, v in r["heldout"].items():
        v["ci95"] = boot_ci(v["per_sub"])
    noncontrol = [k for k, v in r["heldout"].items() if k not in CONTROLS and v["p_holm"] < 0.05]
    gate = r["heldout"].get("C1_P3b", {}).get("p_holm", 1) < 0.05
    p1flag = r["heldout"].get("C3_P1", {}).get("p_holm", 1) < 0.05
    verdict = "INVALID" if not gate else ("PASS" if noncontrol else "FAIL")
    res = dict(verdict=verdict, p1_flag=p1flag, passing=noncontrol, **r)
    (OUT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(verdict, noncontrol, "P1 flag" if p1flag else "")
    for k, v in r["heldout"].items():
        print(f"  {k}: AUC {v['auc']:.3f} {v['ci95']} p {v['p']:.4f} holm {v['p_holm']:.4f} n {v['n_sub']}")


if __name__ == "__main__":
    {"channels": fetch_channels, "prep": prep, "calibrate": calibrate, "discover": discover,
     "heldout": heldout}[sys.argv[1]]()
