"""ds001810 T2 identification screen: discovery half -> survivors -> held-out half, label-shuffled null.

Prereg: docs/prereg/2026-11-24_ab_t2_identification_killtest.md. Outcome is T2 identification, NOT seen vs unseen.

    python -I ab_killtest.py channels    # fetch each block's _channels.tsv (tiny, 1 request/s)
    python -I ab_killtest.py survey      # label-free: rejection rates, retained channels, frozen decoder channels
    python -I ab_killtest.py prep        # preprocess, eligibility (label counts only), split, per-half files, hashes
    python -I ab_killtest.py calibrate   # shuffled-label and planted-answer checks (no real label-EEG statistic)
    python -I ab_killtest.py discover    # needs everything sealed; discovery half only; writes + seals survivors.json
    python -I ab_killtest.py heldout     # needs sealed survivors.json; runs once; writes result.json

All label-EEG statistics are within block (one block = one pre-tDCS visit): AUC per block, labels shuffled
within block, subject value = trial-weighted mean of its block AUCs, group value = mean over subjects.
"""
import csv, hashlib, io, json, os, sys, time, urllib.request
from pathlib import Path

import numpy as np
from scipy.signal import butter, filtfilt
from scipy.stats import rankdata
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[2]
EP = ROOT / "datasets" / "local" / "ds001810_epochs"
CH = EP / "channels"
HERE = Path(__file__).resolve().parent
OUT = HERE / "ab_out"
PREREG = "docs/prereg/2026-11-24_ab_t2_identification_killtest.md"
SEALED_INPUTS = [PREREG, "experiments/hypothesis_generator/ab_killtest.py",
                 "experiments/hypothesis_generator/ab_out/split.json",
                 "experiments/hypothesis_generator/ab_out/eligibility.csv",
                 "experiments/hypothesis_generator/ab_out/prep_hashes.json"]
S3 = "https://s3.amazonaws.com/openneuro.org/ds001810"
NONSCALP = {f"EXG{i}" for i in range(1, 9)} | {"Status"}

LOWPASS_HZ = 30.0
PTP_UV = 150.0            # scalp, on the low-passed, re-referenced epoch
VEOG_UV = 80.0            # EXG1-EXG2 peak-to-peak in -200..300 ms
BLOCK_FLOOR = 0.5         # drop a block that keeps < 50% of its trials
MIN_PER_CLASS = 15        # per block
PLANT_UV = 1.5

CANDS = {  # id: (window ms, channels or None = all (GFP), direction +1/-1/0, kind)
    "C1_P3b": ((350, 600), ["CPz", "Pz", "CP1", "CP2", "P1", "P2"], +1, "mean"),
    "C2_posterior_N2": ((200, 300), ["PO7", "PO8", "P7", "P8", "O1", "O2"], -1, "mean"),
    "C3_P1": ((80, 130), ["O1", "Oz", "O2", "PO7", "PO8"], 0, "mean"),
    "C4_N1": ((150, 200), ["PO7", "PO8", "P7", "P8"], 0, "mean"),
    "C5_frontal_late": ((300, 500), ["Fz", "FCz", "Cz", "AFz", "F2", "FC2"], +1, "mean"),
    "C6_GFP": ((300, 600), None, +1, "gfp"),
    "C7_late_posterior": ((600, 800), ["Pz", "POz", "PO3", "PO4", "Oz"], +1, "mean"),
    "C8_preT2": ((-200, 0), ["Pz", "POz", "PO3", "PO4", "Oz"], 0, "mean"),
}
POS_CONTROLS = ["C1_P3b", "C2_posterior_N2"]
NULL_CONTROLS = ["C3_P1", "C4_N1"]
DESCRIPTIVE = ["C8_preT2"]
TARGETS = ["C5_frontal_late", "C6_GFP", "C7_late_posterior"]
OMNIBUS = ["C9_decoder"]  # always reported; cannot earn PASS (residualising on C1/C2 does not remove a P3b from it)
DIRS = {**{k: v[2] for k, v in CANDS.items()}, "C9_decoder": +1}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ------------------------------------------------------------------ io
def blocks():
    return sorted(EP.glob("sub-*_*.npz"))


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


# ------------------------------------------------------------------ preprocessing (labels only carried along)
def preprocess(path):
    d = np.load(path, allow_pickle=False)
    raw, ch, fs, tmin = d["X"].astype(np.float64), [str(c) for c in d["ch"]], float(d["fs"]), float(d["tmin"])
    raw = raw - raw.mean(2, keepdims=True)                           # remove DC per channel and trial
    bb, aa = butter(4, LOWPASS_HZ / (fs / 2))
    raw = filtfilt(bb, aa, raw, axis=2)                              # 30 Hz zero-phase low-pass
    t = (np.arange(raw.shape[2]) / fs + tmin) * 1000.0
    veog = raw[:, ch.index("EXG1")] - raw[:, ch.index("EXG2")]
    vptp = np.ptp(veog[:, (t >= -200) & (t < 300)], axis=1)
    eog_ok = bool(np.median(vptp) <= VEOG_UV)
    bad = bad_channels(path.stem)
    keep = [i for i, c in enumerate(ch) if c not in NONSCALP and c not in bad]
    X, ch = raw[:, keep], [ch[i] for i in keep]
    X = X - X.mean(1, keepdims=True)                                 # provisional average reference
    med = np.median(np.ptp(X, axis=2), axis=0)
    ok = med <= 5 * np.median(med)
    X, ch = raw[:, keep][:, ok], [c for c, k in zip(ch, ok) if k]
    X = X - X.mean(1, keepdims=True)                                 # final average reference
    X = X - X.mean(2, keepdims=True)                                 # measure basis: whole-epoch mean, no baseline
    good = np.ptp(X, axis=2).max(1) <= PTP_UV
    if eog_ok:
        good &= vptp <= VEOG_UV
    return dict(X=X[good], y=d["y"][good].astype(int), ch=ch, t=t, stem=path.stem, n_raw=len(d["y"]),
                n_keep=int(good.sum()), eog_ok=eog_ok, dropped_block=bool(good.mean() < BLOCK_FLOOR))


def features(b):
    X, t, ch = b["X"], b["t"], b["ch"]
    f = {}
    for k, ((lo, hi), roi, _, kind) in CANDS.items():
        w = (t >= lo) & (t < hi)
        if kind == "gfp":
            f[k] = X[:, :, w].std(1).mean(1)
            continue
        idx = [ch.index(c) for c in roi if c in ch]
        f[k] = X[:, idx][:, :, w].mean((1, 2)) if idx else None
    return f


def dec_features(b, common):
    X, t = b["X"], b["t"]
    idx = [b["ch"].index(c) for c in common]
    bins = [((t >= lo) & (t < lo + 50)) for lo in range(0, 800, 50)]
    F = np.stack([X[:, idx][:, :, w].mean(2) for w in bins], 2).reshape(len(X), -1)
    return (F - F.mean(0)) / (F.std(0) + 1e-9)                      # z-scored within block


# ------------------------------------------------------------------ stats (within block)
def auc_ranks(r, y):
    n1 = y.sum(-1)
    n0 = y.shape[-1] - n1
    return ((r * y).sum(-1) - n1 * (n1 + 1) / 2) / (n1 * n0)


def group_test(scores, labels, direction, n_perm, seed):
    """scores/labels: subj -> list of per-block arrays (None = missing). Returns mean over subjects of
    trial-weighted block AUCs, p from within-block label shuffles."""
    rng = np.random.default_rng(seed)
    obs, null, subs = [], np.zeros(n_perm), []
    for s in sorted(scores):
        bl = [(sc, y) for sc, y in zip(scores[s], labels[s]) if sc is not None]
        if not bl:
            continue
        w = np.array([len(y) for _, y in bl], float)
        w /= w.sum()
        a, nl = 0.0, np.zeros(n_perm)
        for (sc, y), wi in zip(bl, w):
            r = rankdata(sc)
            a += wi * auc_ranks(r, y)
            P = np.argsort(rng.random((n_perm, len(y))), axis=1)
            nl += wi * auc_ranks(r[None, :], y[P])
        obs.append(a)
        null += nl
        subs.append(s)
    obs, null = np.array(obs), null / len(subs)
    m = obs.mean()
    if direction == 0:
        p = (1 + np.sum(np.abs(null - 0.5) >= abs(m - 0.5))) / (n_perm + 1)
    else:
        p = (1 + np.sum(direction * (null - 0.5) >= direction * (m - 0.5))) / (n_perm + 1)
    return dict(auc=float(m), p=float(p), n_sub=len(subs), per_sub=obs.tolist(), subs=subs)


def boot_ci(v, B=5000, seed=3):
    rng = np.random.default_rng(seed)
    v = np.asarray(v)
    m = v[rng.integers(0, len(v), (B, len(v)))].mean(1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def holm(ps):
    order, out, run = np.argsort(ps), np.empty(len(ps)), 0.0
    for i, j in enumerate(order):
        run = max(run, min(1.0, (len(ps) - i) * ps[j]))
        out[j] = run
    return out


def fit_decoder(F, y):
    return LogisticRegression(C=0.01, class_weight="balanced", max_iter=2000).fit(F, y)


def residualise(score_blocks, subj_s):
    """Within each block, residual of the score after regressing on [1, C1, C2] (label-free)."""
    out = []
    for sc, f in zip(score_blocks, subj_s["f"]):
        if sc is None or f["C1_P3b"] is None or f["C2_posterior_N2"] is None:
            out.append(None)
            continue
        A = np.column_stack([np.ones(len(sc)), f["C1_P3b"], f["C2_posterior_N2"]])
        out.append(sc - A @ np.linalg.lstsq(A, sc, rcond=None)[0])
    return out


# ------------------------------------------------------------------ the two stages
def scores_for(k, subj, subs, model=None, loso=None):
    if k == "C9_decoder":
        if loso is not None:
            return {s: loso[s] for s in subs}
        return {s: [model.decision_function(F) for F in subj[s]["F"]] for s in subs}
    return {s: [f[k] for f in subj[s]["f"]] for s in subs}


def stage_discovery(subj, labels, subs, common, n_perm, seed=2411):  # common kept for the call signature
    res = {}
    for k in CANDS:
        res[k] = group_test(scores_for(k, subj, subs), {s: labels[s] for s in subs}, DIRS[k], n_perm, seed)
    # C9 has no discovery statistic: leave-one-subject-out scores are correlated across subjects, so the
    # within-subject shuffle null is too narrow (calibration: 11.5% at p<.05). It is tested on held-out only.
    surv = [k for k in TARGETS if k in res and res[k]["p"] < 0.05]
    return res, surv


def stage_heldout(subj, labels, disc_subj, disc_labels, subs, common, surv, n_perm, seed=2412):
    model = None
    if common:
        model = fit_decoder(np.vstack([F for u in disc_subj for F in disc_subj[u]["F"]]),
                            np.concatenate([y for u in disc_subj for y in disc_labels[u]]))
    lab = {s: labels[s] for s in subs}
    res = {}
    for k in POS_CONTROLS + NULL_CONTROLS + DESCRIPTIVE:
        res[k] = group_test(scores_for(k, subj, subs), lab, DIRS[k], n_perm, seed)
    if model is not None:
        res["C9_decoder"] = group_test(scores_for("C9_decoder", subj, subs, model=model), lab, +1, n_perm, seed)
    for k in surv:
        sc = scores_for(k, subj, subs)
        r = group_test(sc, lab, DIRS[k], n_perm, seed)
        rs = {s: residualise(sc[s], subj[s]) for s in subs}
        r["resid"] = {kk: v for kk, v in group_test(rs, lab, DIRS[k], n_perm, seed).items() if kk in ("auc", "p")}
        res[k] = r
    if surv:
        for k, a in zip(surv, holm(np.array([res[k]["p"] for k in surv]))):
            res[k]["p_holm"] = float(a)
    for k, r in res.items():
        r["ci95"] = boot_ci(r["per_sub"])
    passing = [k for k in surv if res[k]["p_holm"] < 0.05 and res[k]["resid"]["p"] < 0.05
               and (res[k]["ci95"][0] > 0.5 if DIRS[k] > 0 else res[k]["ci95"][1] < 0.5)]
    gate = res["C1_P3b"]["p"] < 0.05
    flags = [k for k in NULL_CONTROLS if res[k]["p"] < 0.05]
    verdict = "INVALID" if not gate else ("PASS" if passing else "FAIL")
    return dict(verdict=verdict, gate_C1=gate, passing=passing, null_control_flags=flags, results=res)


# ------------------------------------------------------------------ data assembly
def assemble(per_block, common):
    subj, labels = {}, {}
    for sub, bl in per_block.items():
        subj[sub] = dict(f=[features(b) for b in bl],
                         F=[dec_features(b, common) for b in bl] if common else None,
                         stems=[b["stem"] for b in bl])
        labels[sub] = [b["y"] for b in bl]
    return subj, labels


def eligible_blocks(write=False):
    per, rows = {}, []
    for p in blocks():
        b = preprocess(p)
        nc, ni = int(b["y"].sum()), int((1 - b["y"]).sum())
        ok = (not b["dropped_block"]) and nc >= MIN_PER_CLASS and ni >= MIN_PER_CLASS
        rows.append(dict(block=b["stem"], trials=b["n_raw"], kept=b["n_keep"], eog_rule=b["eog_ok"],
                         channels=len(b["ch"]), correct=nc, incorrect=ni, eligible=ok))
        if ok:
            per.setdefault(b["stem"].split("_")[0], []).append(b)
    return per, rows


def frozen_common(per):
    sets = [set(b["ch"]) for bl in per.values() for b in bl]
    first = next(iter(per.values()))[0]["ch"]
    return [c for c in first if all(c in s for s in sets)]


def survey():
    per, rows = eligible_blocks()
    kept = sum(r["kept"] for r in rows)
    tot = sum(r["trials"] for r in rows)
    print(f"blocks {len(rows)}; trials kept {kept}/{tot} ({1 - kept / tot:.1%} rejected)")
    print("dropped by floor:", [r["block"] for r in rows if r["kept"] < BLOCK_FLOOR * r["trials"]])
    print("EOG rule skipped:", [r["block"] for r in rows if not r["eog_rule"]])
    com = frozen_common(per)
    print(f"common channels over eligible blocks: {len(com)}: {' '.join(com)}")


def prep():
    OUT.mkdir(exist_ok=True)
    per, rows = eligible_blocks()
    common = frozen_common(per)
    if len(common) < 40:
        common = []
    ids = sorted(per)
    rng = np.random.default_rng(1810)
    perm = [ids[i] for i in rng.permutation(len(ids))]
    h = -(-len(ids) // 2)
    split = dict(discovery=sorted(perm[:h]), heldout=sorted(perm[h:]), seed=1810, common_channels=common)
    (OUT / "split.json").write_text(json.dumps(split, indent=1) + "\n")
    with open(OUT / "eligibility.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    hashes = {}
    for half in ("discovery", "heldout"):
        subj, labels = assemble({s: per[s] for s in split[half]}, common)
        f = OUT / f"prepped_{half}.npz"
        np.savez(f, d=np.array(dict(subj=subj, labels=labels), dtype=object))
        hashes[f.name] = sha(f)
    (OUT / "prep_hashes.json").write_text(json.dumps(hashes, indent=1) + "\n")
    print(f"eligible subjects {len(ids)}; discovery {h}, held-out {len(ids) - h}; common channels {len(common)}")


def load_half(half):
    f = OUT / f"prepped_{half}.npz"
    want = json.loads((OUT / "prep_hashes.json").read_text())[f.name]
    if sha(f) != want:
        raise SystemExit(f"{f.name} changed since prep")
    d = np.load(f, allow_pickle=True)["d"].item()
    return d["subj"], d["labels"]


# ------------------------------------------------------------------ calibration (shuffled labels only)
def shuffled(labels, rng):
    return {s: [rng.permutation(y) for y in ys] for s, ys in labels.items()}


def calibrate(n_null=200, n_plant=50):
    split = json.loads((OUT / "split.json").read_text())
    common = split["common_channels"]
    ds, dl = load_half("discovery")
    hs, hl = load_half("heldout")
    subj, labels = {**ds, **hs}, {**dl, **hl}
    D, H = split["discovery"], split["heldout"]
    rng = np.random.default_rng(7)
    fp, stage1 = 0, {k: 0 for k in CANDS}
    held1 = {k: 0 for k in POS_CONTROLS + NULL_CONTROLS + DESCRIPTIVE + OMNIBUS}
    t0 = time.time()
    for i in range(n_null):
        lab = shuffled(labels, rng)
        dres, surv = stage_discovery({s: subj[s] for s in D}, lab, D, common, 500, seed=10 + i)
        for k, r in dres.items():
            stage1[k] += r["p"] < 0.05
        hres = stage_heldout(subj, lab, {s: subj[s] for s in D}, {s: lab[s] for s in D}, H, common, surv, 500,
                             seed=5000 + i)
        fp += bool(hres["passing"])
        for k in held1:
            held1[k] += hres["results"][k]["p"] < 0.05
        if i % 10 == 0:
            print(f"null run {i}: fp {fp}, {time.time() - t0:.0f}s", flush=True)
    # planted answer: add the effect to the preprocessed epochs, then recompute every feature
    per, _ = eligible_blocks()
    rec = 0
    for i in range(n_plant):
        lab, psubj = {}, {}
        for s in D + H:
            ys, fs_ = [], []
            for b in per[s]:
                y = rng.permutation(b["y"])
                add = (y == 1) & (rng.random(len(y)) < 0.5)
                X = b["X"].copy()
                for k, sign in (("C1_P3b", +1), ("C2_posterior_N2", -1)):
                    (lo, hi), roi, _, _ = CANDS[k]
                    w = (b["t"] >= lo) & (b["t"] < hi)
                    idx = [b["ch"].index(c) for c in roi if c in b["ch"]]
                    X[np.ix_(add, idx, np.flatnonzero(w))] += sign * PLANT_UV
                X = X - X.mean(2, keepdims=True)                     # same whole-epoch measure basis as real data
                fs_.append(features(dict(b, X=X)))
                ys.append(y)
            lab[s], psubj[s] = ys, dict(f=fs_, F=None)
        r = stage_heldout(psubj, lab, {}, {}, H, [], [], 500, seed=9000 + i)["results"]
        rec += r["C1_P3b"]["p"] < 0.05 and r["C2_posterior_N2"]["p"] < 0.05
    res = dict(null_runs=n_null, any_target_pass_rate=fp / n_null,
               stage1_p05_rate={k: v / n_null for k, v in stage1.items()},
               heldout_p05_rate={k: v / n_null for k, v in held1.items()},
               plant_runs=n_plant, plant_uV=PLANT_UV, plant_recovered=rec / n_plant,
               pass_null=fp / n_null <= 0.05, pass_stage1=all(v / n_null <= 0.08 for v in list(stage1.values()) + list(held1.values())),
               pass_plant=rec / n_plant >= 0.80)
    (OUT / "calibration.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


# ------------------------------------------------------------------ sealed runs
def evidence():
    sys.path.insert(0, str(ROOT / "experiments" / "rules"))
    os.chdir(ROOT)
    import evidence as ev
    return ev


def discover():
    ev = evidence()
    for p in SEALED_INPUTS:
        ev.require_sealed(p)
    f = OUT / "survivors.json"
    if f.exists():
        raise SystemExit("survivors.json exists; discovery runs once")
    split = json.loads((OUT / "split.json").read_text())
    subj, labels = load_half("discovery")
    res, surv = stage_discovery(subj, labels, split["discovery"], split["common_channels"], 5000)
    f.write_text(json.dumps(dict(discovery=res, survivors=surv), indent=1) + "\n")
    ev.seal([str(f.relative_to(ROOT))])
    print("survivors:", surv)
    for k, r in res.items():
        print(f"  {k}: AUC {r['auc']:.3f} p {r['p']:.4f} n {r['n_sub']}")


def heldout():
    ev = evidence()
    for p in SEALED_INPUTS + ["experiments/hypothesis_generator/ab_out/survivors.json"]:
        ev.require_sealed(p)
    out = OUT / "result.json"
    if out.exists():
        raise SystemExit("result.json exists; the held-out test runs once")
    split = json.loads((OUT / "split.json").read_text())
    sv = json.loads((OUT / "survivors.json").read_text())
    dsub, dlab = load_half("discovery")
    res, surv = stage_discovery(dsub, dlab, split["discovery"], split["common_channels"], 5000)
    if json.loads(json.dumps(dict(discovery=res, survivors=surv))) != sv:
        raise SystemExit("discovery does not reproduce the sealed survivors.json")
    hsub, hlab = load_half("heldout")
    r = stage_heldout(hsub, hlab, dsub, dlab, split["heldout"], split["common_channels"], surv, 5000)
    out.write_text(json.dumps(r, indent=1) + "\n")
    print(r["verdict"], "passing:", r["passing"], "null-control flags:", r["null_control_flags"])
    for k, v in r["results"].items():
        extra = f" holm {v['p_holm']:.4f} resid p {v['resid']['p']:.4f}" if "p_holm" in v else ""
        print(f"  {k}: AUC {v['auc']:.3f} {np.round(v['ci95'], 3).tolist()} p {v['p']:.4f}{extra} n {v['n_sub']}")


if __name__ == "__main__":
    {"channels": fetch_channels, "survey": survey, "prep": prep, "calibrate": calibrate,
     "discover": discover, "heldout": heldout}[sys.argv[1]]()
