"""Fixed-SOA seen vs unseen kill test on Cohen et al. 2024 (SOA 50 ms, report block). Prereg:
docs/prereg/2026-11-24_cohen_fixed_soa_killtest.md

    python -I cohen_killtest.py prep        # label-free: preprocessing, rejection, bad channels -> out/prep.npz, out/prep_summary.json
    python -I cohen_killtest.py align       # label-free: pooled ERP checks (visual response present, timing) -> out/align.json
    python -I cohen_killtest.py eligibility # behaviour counts after rejection -> out/eligibility.csv
    python -I cohen_killtest.py calibrate   # shuffled labels only: false-PASS rate and planted-effect power -> out/calibration.json
    python -I cohen_killtest.py run         # real labels; refuses unless the prereg and this script are sealed -> out/result.json

Channel numbers are the authors' (1-63, EasyCap M10). Ch58 = left mastoid (recorded against the right mastoid),
Ch61 = VEOG under the left eye, Ch62/Ch63 = left/right HEOG, Ch50 = Fp1. Positions from the .vhdr coordinates.
"""
import csv, json, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EP = ROOT / "datasets" / "local" / "cohen2024_epochs"
OUT = HERE / "out"
PREREG = ROOT / "docs" / "prereg" / "2026-11-24_cohen_fixed_soa_killtest.md"
sys.path.insert(0, str(ROOT / "experiments" / "rules"))

FS, TMIN, NS = 500, -0.1, 350
LMAST, VEOG, HEOGL, HEOGR, FP1 = 58, 61, 62, 63, 50
NONSCALP = {58, 61, 62, 63}
SCALP = [c for c in range(1, 64) if c not in NONSCALP]
PILOT = ["1001", "1002", "1003", "1004", "1005", "1007", "1008", "1009", "1014", "1015", "1016", "1017", "1018",
         "1020", "1022"]
# name: (channels, window ms, role, predicted sign of seen - unseen: +1, -1, or 0 = two-sided)
COMP = {
    "P3b": ([1, 4, 5, 6, 13, 14, 15], (300, 500), "gate", +1),
    "N2": ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 17, 18, 19], (250, 290), "target", -1),
    "VAN": ([53, 57], (140, 200), "target", -1),
    "P1": ([41, 42, 43, 44, 45, 53, 54, 55, 56, 57], (100, 140), "null_control", 0),
    "N2_frontal": ([2, 3, 7, 8, 9, 10, 11, 17, 18, 19], (250, 290), "secondary", -1),
}
TARGETS = ["N2", "VAN"]
HEOG_PP, VEOG_PP, SCALP_PP = 50.0, 150.0, 150.0   # uV peak-to-peak over the whole epoch (authors' thresholds)
LOWPASS = 30.0                                      # Hz; without it HEOG line noise alone rejected 36% (subject 1001)
BAD_CH = 3.0                                       # channel bad if its median p2p > 3 x median over channels
MIN_PER_CELL = 20
NPERM = 10000
ALPHA = 0.05
SEED = 20261124


def samp(ms):
    return int(round((ms / 1000 - TMIN) * FS))


def subjects():
    return sorted(p.stem for p in EP.glob("*.npz"))


def sid(s):
    return {"10162": "1016", "2022": "1022"}.get(s, s)


# ------------------------------------------------------------------ preprocessing (label-free)
def preprocess(sub):
    d = np.load(EP / f"{sub}.npz")
    x = d["X"].astype(np.float64) * float(d["scale_uv"])                 # trials x 63 x 350, uV vs right mastoid
    from scipy.signal import butter, filtfilt
    bb, aa = butter(4, LOWPASS / (FS / 2))
    x = filtfilt(bb, aa, x, axis=2, padlen=100)                          # zero-phase 30 Hz low-pass (label-free fix)
    ch =lambda c: x[:, c - 1, :]
    heog = ch(HEOGL) - ch(HEOGR)
    veog = ch(VEOG) - ch(FP1)
    scalp = x[:, [c - 1 for c in SCALP], :] - ch(LMAST)[:, None, :] / 2  # linked mastoids
    scalp -= scalp[:, :, :samp(0)].mean(axis=2, keepdims=True)           # baseline -100..0 ms
    pp = scalp.max(axis=2) - scalp.min(axis=2)                           # trials x scalp channels
    med = np.median(pp, axis=0)
    bad = med > BAD_CH * np.median(med)
    keep = (np.ptp(heog, axis=1) <= HEOG_PP) & (np.ptp(veog, axis=1) <= VEOG_PP) & \
           (pp[:, ~bad].max(axis=1) <= SCALP_PP)
    vals = {}
    for name, (chs, (a, b), _, _) in COMP.items():
        idx = [SCALP.index(c) for c in chs if not bad[SCALP.index(c)]]
        vals[name] = scalp[:, idx, samp(a):samp(b)].mean(axis=(1, 2)) if idx else np.full(len(x), np.nan)
    return dict(vals=vals, keep=keep, bad=[SCALP[i] for i in np.where(bad)[0]], resp=d["resp"], ident=d["ident"],
                onset=d["onset"], erp=scalp[keep].mean(axis=0), n=len(x))


def prep():
    OUT.mkdir(exist_ok=True)
    rows, store = [], {}
    for s in subjects():
        p = preprocess(s)
        k = p["keep"]
        rows.append(dict(sub=sid(s), n=p["n"], kept=int(k.sum()), rejected_pct=round(100 * (1 - k.mean()), 1),
                         bad_channels=" ".join(map(str, p["bad"]))))
        for name, v in p["vals"].items():
            store[f"{sid(s)}|{name}"] = v[k]
        store[f"{sid(s)}|resp"] = p["resp"][k]
        store[f"{sid(s)}|ident"] = p["ident"][k]
        store[f"{sid(s)}|onset"] = p["onset"][k]
        store[f"{sid(s)}|erp"] = p["erp"]
    np.savez_compressed(OUT / "prep.npz", **store)
    with open(OUT / "prep_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    rej = [r["rejected_pct"] for r in rows]
    print(f"{len(rows)} subjects; rejected median {np.median(rej):.1f}% (max {max(rej):.1f}%); "
          f"subjects with bad channels {sum(1 for r in rows if r['bad_channels'])}")


def load():
    z = np.load(OUT / "prep.npz")
    subs = sorted({k.split("|")[0] for k in z.files})
    return {s: {k.split("|")[1]: z[k] for k in z.files if k.startswith(s + "|")} for s in subs}


# ------------------------------------------------------------------ label-free alignment check
def align():
    D = load()
    erp = np.stack([D[s]["erp"] for s in D])                              # subjects x scalp x time
    t = (np.arange(NS) / FS + TMIN) * 1000
    occ = [SCALP.index(c) for c in COMP["P1"][0]]
    o = erp[:, occ, :].mean(axis=1)
    g = o.mean(axis=0)
    w1 = (t >= 80) & (t <= 140)
    w2 = (t >= 130) & (t <= 220)
    p1_t = float(t[w1][np.argmax(g[w1])])
    n1_t = float(t[w2][np.argmin(g[w2])])
    n1 = o[:, samp(140):samp(200)].mean(axis=1)
    from scipy import stats
    tt = stats.ttest_1samp(n1, 0.0)                                       # baseline-corrected, so 0 = baseline
    late = erp[:, [SCALP.index(c) for c in COMP["P3b"][0]], :].mean(axis=1).mean(axis=0)
    ok = bool(140 <= n1_t <= 200 and tt.statistic < 0 and tt.pvalue < 0.01)
    res = dict(n_subjects=len(D), PASS=ok, criterion="grand occipital N1 trough in 140-200 ms and 140-200 ms mean < 0, p < .01",
               occipital_p1_peak_ms=p1_t, occipital_n1_trough_ms=n1_t,
               occipital_140_200_uv=float(n1.mean()), t=float(tt.statistic), p=float(tt.pvalue),
               grand_occipital_uv_every_20ms={int(t[i]): round(float(g[i]), 2) for i in range(0, NS, 10)},
               grand_p3b_roi_uv_every_20ms={int(t[i]): round(float(late[i]), 2) for i in range(0, NS, 10)})
    (OUT / "align.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: v for k, v in res.items() if not k.startswith("grand")}, indent=1))


# ------------------------------------------------------------------ eligibility (behaviour counts only)
def eligibility():
    D = load()
    rows = []
    for s, d in D.items():
        n1, n0 = int((d["resp"] == 1).sum()), int((d["resp"] == 2).sum())
        rows.append(dict(sub=s, set="pilot" if s in PILOT else "confirm", seen=n1, unseen=n0,
                         eligible=int(n1 >= MIN_PER_CELL and n0 >= MIN_PER_CELL)))
    with open(OUT / "eligibility.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for st in ("pilot", "confirm"):
        print(st, sum(r["eligible"] for r in rows if r["set"] == st), "eligible of",
              sum(1 for r in rows if r["set"] == st))


def eligible(group):
    rows = list(csv.DictReader(open(OUT / "eligibility.csv")))
    return [r["sub"] for r in rows if r["set"] == group and r["eligible"] == "1"]


# ------------------------------------------------------------------ statistics
def strata(onset):
    """Time-on-task quintile of each trial within the subject (permutations stay inside a quintile)."""
    r = np.argsort(np.argsort(onset))
    return (r * 5) // len(onset)


def perm_labels(y, st, P, rng):
    L = np.empty((P, len(y)), dtype=bool)
    for q in np.unique(st):
        idx = np.where(st == q)[0]
        L[:, idx] = y[idx][np.argsort(rng.random((P, len(idx))), axis=1)]
    return L


def ranks(v):
    o = np.argsort(v, kind="mergesort")
    r = np.empty(len(v))
    r[o] = np.arange(1, len(v) + 1)
    sv = v[o]                                                             # average ties
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and sv[j + 1] == sv[i]:
            j += 1
        if j > i:
            r[o[i:j + 1]] = (i + j + 2) / 2
        i = j + 1
    return r


def auc_many(v, L):
    """AUC of v for label rows L (True = seen); P(v_seen > v_unseen)."""
    r = ranks(v)
    n1 = L.sum(axis=1)
    n0 = L.shape[1] - n1
    return (L @ r - n1 * (n1 + 1) / 2) / (n1 * n0)


def analyse(D, subs, labels, P, rng, comps=None, resid=True):
    """labels: sub -> bool array (True = seen). Returns per component the group statistics."""
    comps = comps or list(COMP)
    out = {}
    per = {c: [] for c in comps}
    null = {c: np.zeros(P) for c in comps}
    diff = {c: [] for c in comps}
    extra = {}
    for s in subs:
        y = labels[s]
        st = strata(D[s]["onset"])
        L = np.vstack([y[None, :], perm_labels(y, st, P, rng)])
        vs = {c: D[s][c] for c in comps}
        if resid and "N2" in comps and "P3b" in D[s]:
            b = np.polyfit(D[s]["P3b"], D[s]["N2"], 1)
            vs["N2_resid_P3b"] = D[s]["N2"] - np.polyval(b, D[s]["P3b"])
        for c, v in vs.items():
            sign = COMP[c][3] if c in COMP else -1
            a = auc_many(v if sign >= 0 else -v, L)
            if c not in per:
                per[c], null[c], diff[c] = [], np.zeros(P), []
            per[c].append(a[0])
            null[c] += a[1:]
            diff[c].append(float(v[y].mean() - v[~y].mean()))
    n = len(subs)
    for c in per:
        a = np.array(per[c])
        nl = null[c] / n
        sign = COMP[c][3] if c in COMP else -1
        obs = a.mean()
        if sign == 0:
            p_perm = (1 + np.sum(np.abs(nl - 0.5) >= abs(obs - 0.5))) / (1 + P)
        else:
            p_perm = (1 + np.sum(nl >= obs)) / (1 + P)
        flips = rng.choice([-1.0, 1.0], size=(P, n))
        dev = a - 0.5
        fm = (flips * dev).mean(axis=1)
        p_sf = ((1 + np.sum(np.abs(fm) >= abs(dev.mean()))) if sign == 0 else (1 + np.sum(fm >= dev.mean()))) / (1 + P)
        dd = np.array(diff[c])
        boot = dd[rng.integers(0, n, size=(P, n))].mean(axis=1)
        bauc = a[rng.integers(0, n, size=(P, n))].mean(axis=1)
        out[c] = dict(mean_auc_predicted_direction=float(obs), p_perm=float(p_perm), p_signflip=float(p_sf),
                      p=float(max(p_perm, p_sf)), auc_ci95=[float(np.percentile(bauc, 2.5)), float(np.percentile(bauc, 97.5))],
                      seen_minus_unseen_uv=float(dd.mean()),
                      seen_minus_unseen_uv_ci95=[float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
                      n_subjects=n, subjects_in_predicted_direction=int(np.sum(a > 0.5)) if sign != 0 else None)
    return out


def decide(r):
    """Decision rules, section 5 of the prereg."""
    g = r["P3b"]
    if not (g["p"] < ALPHA and g["mean_auc_predicted_direction"] > 0.5):
        return dict(verdict="INVALID", reason="P3b positive-control gate failed")
    ps = sorted((r[t]["p"], t) for t in TARGETS)
    holm, passed, stop = {}, {}, False
    for i, (p, t) in enumerate(ps):
        adj = min(1.0, p * (len(ps) - i))
        holm[t] = adj
        passed[t] = (not stop) and adj < ALPHA
        stop = stop or not passed[t]
    status = {}
    for t in TARGETS:
        lo_pred = -r[t]["seen_minus_unseen_uv_ci95"][0]                   # largest predicted-direction effect in CI
        if passed[t]:
            status[t] = "PASS"
        elif lo_pred < 0.5:
            status[t] = "KILLED"                                          # CI excludes a predicted effect >= 0.5 uV
        else:
            status[t] = "INCONCLUSIVE"
    p1 = r["P1"]
    return dict(verdict="VALID", targets=status, holm=holm,
                p1_flag=bool(p1["p"] < ALPHA), p1_note="P1 differs: early-state confound possible" if p1["p"] < ALPHA else "")


def calibrate():
    D = load()
    subs = eligible("confirm")
    rng = np.random.default_rng(SEED)
    P = 2000
    fp, plant = 0, {"N2": 0, "VAN": 0}
    runs, pruns = 200, 50
    for k in range(runs):
        lab = {s: rng.permutation(D[s]["resp"] == 1) for s in subs}
        r = analyse(D, subs, lab, P, rng, resid=False)
        r["P3b"] = dict(r["P3b"], p=0.0, mean_auc_predicted_direction=1.0)   # force gate open to test targets
        d = decide(r)
        fp += any(v == "PASS" for v in d["targets"].values())
    for t in plant:
        chs, (a, b), _, _ = COMP[t]
        for k in range(pruns):
            lab = {s: rng.permutation(D[s]["resp"] == 1) for s in subs}
            E = {s: dict(D[s]) for s in subs}
            for s in subs:
                E[s][t] = D[s][t] - 1.0 * lab[s]                            # seen 1 uV more negative (window mean)
            r = analyse(E, subs, lab, P, rng, resid=False)
            r["P3b"] = dict(r["P3b"], p=0.0, mean_auc_predicted_direction=1.0)
            plant[t] += decide(r)["targets"][t] == "PASS"
    res = dict(subjects=len(subs), shuffled_runs=runs, false_any_target_pass=fp, false_rate=fp / runs,
               planted_1uv_runs=pruns, planted_power={t: v / pruns for t, v in plant.items()}, perms_per_run=P)
    (OUT / "calibration.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


def run():
    from evidence import require_sealed
    for f in (PREREG, Path(__file__), OUT / "eligibility.csv", OUT / "prep_hashes.json"):
        require_sealed(str(f))
    import hashlib
    h = json.loads((OUT / "prep_hashes.json").read_text())
    assert hashlib.sha256((OUT / "prep.npz").read_bytes()).hexdigest() == h["prep.npz"], "prep.npz changed"
    D = load()
    rng = np.random.default_rng(SEED)
    res = {}
    for group in ("confirm", "pilot"):
        subs = eligible(group)
        lab = {s: D[s]["resp"] == 1 for s in subs}
        r = analyse(D, subs, lab, NPERM, rng)
        res[group] = dict(stats=r, decision=decide(r))
    res["verdict_from"] = "confirm (pilot is a secondary replication; its 15 subjects set the authors' windows)"
    (OUT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


def hashes():
    import hashlib
    (OUT / "prep_hashes.json").write_text(json.dumps(
        {"prep.npz": hashlib.sha256((OUT / "prep.npz").read_bytes()).hexdigest()}, indent=1) + "\n")


if __name__ == "__main__":
    {"prep": prep, "align": align, "eligibility": eligibility, "calibrate": calibrate, "run": run,
     "hashes": hashes}[sys.argv[1]]()
