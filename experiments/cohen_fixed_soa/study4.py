"""Item 4: does the seen/unseen VAN difference need a report? Double difference with mask-only trials (Cohen et al. 2024).
Prereg: docs/prereg/2026-11-25_cohen_noreport_dd.md

    python -I study4.py prep    # ONCE, after the fetch process has exited; label-free preprocessing of all four cells -> out/s4_prep.npz, out/s4_prep_summary.csv
    python -I study4.py align   # sealed; label-free alignment check on no-report face trials -> out/s4_align.json
    python -I study4.py gate    # sealed; planted-proportion calibration from REPORT-block trials only -> out/s4_gate.json
    python -I study4.py gate99  # sealed fallback F2, only if gate FAILED: 99% intervals, new seed -> out/s4_gate99.json
    python -I study4.py run     # sealed; the real double difference -> out/s4_result.json

Cells per subject: RF report face SOA 50 (with seen/unseen answer), RM report mask-only, NF no-report face SOA 50,
NM no-report mask-only. All epochs -100..+300 ms around the (virtual) face onset; the mask is at +50 ms in all four.
Report-face epochs (-100..+600 ms on disk) are cut to the same 200 samples BEFORE filtering, so all cells get the same
processing. Channel numbers and rejection rules are those of the sealed fixed-SOA study (cohen_killtest.py).
The gate never reads NF or NM values; it builds pseudo no-report blocks from held-out halves of the report block.
"""
import csv, hashlib, json, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EP_R = ROOT / "datasets" / "local" / "cohen2024_epochs"
EP_N = ROOT / "datasets" / "local" / "cohen2024_nr_epochs"
OUT = HERE / "out"
PREREG = ROOT / "docs" / "prereg" / "2026-11-25_cohen_noreport_dd.md"

FS, TMIN, NS = 500, -0.1, 200
LMAST, VEOG, HEOGL, HEOGR, FP1 = 58, 61, 62, 63, 50
NONSCALP = {58, 61, 62, 63}
SCALP = [c for c in range(1, 64) if c not in NONSCALP]
ROI = {"VAN": ([53, 57], (140, 200)), "P1": ([41, 42, 43, 44, 45, 53, 54, 55, 56, 57], (100, 140))}
HEOG_PP, VEOG_PP, SCALP_PP = 50.0, 150.0, 150.0
LOWPASS, BAD_CH, MIN_COVER = 30.0, 3.0, 0.5
MIN_SEEN = 20            # clean seen and clean unseen RF trials (sealed study's per-cell minimum)
MIN_CELL = 40            # clean trials in NF, and in each mask-only cell (of 60)
MIN_SUBJ = 30
NBOOT_REAL, NBOOT_GATE, NRUN = 10000, 2000, 200
BETA_SD, TAU_INT = 1.0, (0.3, 0.6)
GATE_MAX_WRONG, GATE_MAX_HALF, GATE_MAX_SHUF = 0.05, 0.10, 0.05
SEED = 20261125
DELTAS = (-0.4, -0.2, 0.2, 0.4)   # uV, fixed face-only block shift in the AWARE world (reported, not gated)
CELLS = ("RF", "RM", "NF", "NM")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sealed():
    sys.path.insert(0, str(ROOT / "experiments" / "rules"))
    from evidence import require_sealed
    require_sealed(str(PREREG)); require_sealed(str(Path(__file__)))


def samp(ms):
    return int(round((ms / 1000 - TMIN) * FS))


def subjects():
    return sorted(p.stem for p in EP_N.glob("*.npz") if (EP_R / p.name).exists())


# ------------------------------------------------------------------ preprocessing (label-free)
def load_raw(sub):
    r = np.load(EP_R / f"{sub}.npz")
    n = np.load(EP_N / f"{sub}.npz")
    assert set(np.unique(r["resp"]).tolist()) <= {1, 2}, sub
    assert float(r["tmin"]) == TMIN and float(n["tmin"]) == TMIN and int(n["mask_shift"]) == 25
    xr = r["X"][:, :, :NS]
    cond = np.array([("NF" if c == "face50" else "NM") if b == "noreport" else "RM"
                     for c, b in zip(n["cond"], n["block"])])
    assert not np.any((n["cond"] == "face50") & (n["block"] == "report"))
    X = np.concatenate([xr, n["X"]]).astype(np.float64) * 0.1
    cells = np.concatenate([np.full(len(xr), "RF"), cond])
    resp = np.concatenate([r["resp"], np.zeros(len(cond), int)])
    return X, cells, resp


def preprocess(sub):
    from scipy.signal import butter, filtfilt
    x, cells, resp = load_raw(sub)
    bb, aa = butter(4, LOWPASS / (FS / 2))
    x = filtfilt(bb, aa, x, axis=2, padlen=100)
    ch = lambda c: x[:, c - 1, :]
    heog = ch(HEOGL) - ch(HEOGR)
    veog = ch(VEOG) - ch(FP1)
    scalp = x[:, [c - 1 for c in SCALP], :] - ch(LMAST)[:, None, :] / 2
    scalp -= scalp[:, :, :samp(0)].mean(axis=2, keepdims=True)
    pp = scalp.max(axis=2) - scalp.min(axis=2)
    med = np.median(pp, axis=0)                                           # pooled over all four cells
    bad = med > BAD_CH * np.median(med)
    keep = (np.ptp(heog, axis=1) <= HEOG_PP) & (np.ptp(veog, axis=1) <= VEOG_PP) & \
           (pp[:, ~bad].max(axis=1) <= SCALP_PP)
    vals, cover = {}, {}
    for name, (chs, (a, b)) in ROI.items():
        idx = [SCALP.index(c) for c in chs if not bad[SCALP.index(c)]]
        cover[name] = len(idx) / len(chs)
        vals[name] = scalp[:, idx, samp(a):samp(b)].mean(axis=(1, 2)) if idx else np.full(len(x), np.nan)
    mast = float(np.median(np.ptp(ch(LMAST), axis=1)) / np.median(med))
    nf_erp = scalp[keep & (cells == "NF")].mean(axis=0)
    return dict(vals=vals, cover=cover, keep=keep, cells=cells, resp=resp, bad=[SCALP[i] for i in np.where(bad)[0]],
                mastoid_ratio=mast, nf_erp=nf_erp)


def prep():
    OUT.mkdir(exist_ok=True)
    assert not (OUT / "s4_prep.npz").exists(), "prep runs once"
    rows, store = [], {}
    for s in subjects():
        p = preprocess(s)
        k, c, r = p["keep"], p["cells"], p["resp"]
        row = dict(sub=s, bad_channels=" ".join(map(str, p["bad"])), van_cover=p["cover"]["VAN"],
                   p1_cover=p["cover"]["P1"], mastoid_flag=int(p["mastoid_ratio"] > BAD_CH or p["mastoid_ratio"] < 0.2))
        for cell in CELLS:
            m = k & (c == cell)
            row[f"n_{cell}"] = int(m.sum())
            row[f"rej_{cell}"] = round(1 - m.sum() / max(1, (c == cell).sum()), 3)
            for name in ROI:
                store[f"{s}|{cell}|{name}"] = p["vals"][name][m]
            if cell == "RF":
                store[f"{s}|RF|resp"] = r[m]
                row["rf_seen"], row["rf_unseen"] = int((r[m] == 1).sum()), int((r[m] == 2).sum())
        store[f"{s}|nf_erp"] = p["nf_erp"]
        okc = row["van_cover"] == 1.0 and row["p1_cover"] >= MIN_COVER and row["mastoid_flag"] == 0
        row["eligible"] = int(okc and row["rf_seen"] >= MIN_SEEN and row["rf_unseen"] >= MIN_SEEN and
                              all(row[f"n_{cc}"] >= MIN_CELL for cc in ("NF", "RM", "NM")))
        rows.append(row)
    np.savez_compressed(OUT / "s4_prep.npz", **store)
    with open(OUT / "s4_prep_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} subjects, eligible {sum(r['eligible'] for r in rows)}; "
          f"median rejection RF {np.median([r['rej_RF'] for r in rows]):.3f} RM {np.median([r['rej_RM'] for r in rows]):.3f} "
          f"NF {np.median([r['rej_NF'] for r in rows]):.3f} NM {np.median([r['rej_NM'] for r in rows]):.3f}")


def load():
    z = np.load(OUT / "s4_prep.npz")
    D = {}
    for k in z.files:
        parts = k.split("|")
        D.setdefault(parts[0], {})["|".join(parts[1:])] = z[k]
    elig = {r["sub"] for r in csv.DictReader(open(OUT / "s4_prep_summary.csv")) if r["eligible"] == "1"}
    return D, sorted(elig)


# ------------------------------------------------------------------ label-free alignment (sealed criterion)
def align():
    sealed()
    D, _ = load()
    good = [s for s in D if np.all(np.isfinite(D[s]["nf_erp"]))]
    erp = np.stack([D[s]["nf_erp"] for s in good])
    t = (np.arange(NS) / FS + TMIN) * 1000
    o = erp[:, [SCALP.index(c) for c in ROI["P1"][0]], :].mean(axis=1)
    g = o.mean(axis=0)
    w1 = (t >= 80) & (t <= 160)
    p1_t = float(t[w1][np.argmax(g[w1])])
    early = o[:, samp(100):samp(160)].mean(axis=1)
    onset = float(t[np.argmax((t > 0) & (g > 1.0))])
    from scipy import stats
    tt = stats.ttest_1samp(early, 0.0)
    ok = bool(60 <= onset <= 120 and 100 <= p1_t <= 160 and tt.statistic > 0 and tt.pvalue < 0.01)
    res = dict(n_subjects=len(good), skipped_no_clean_nf=len(D) - len(good), PASS=ok, occipital_onset_ms=onset, occipital_p1_peak_ms=p1_t,
               occipital_100_160_uv=float(early.mean()), t=float(tt.statistic), p=float(tt.pvalue),
               criterion="sealed fixed-SOA criterion, applied to no-report face SOA-50 trials, all subjects")
    (OUT / "s4_align.json").write_text(json.dumps(res, indent=1) + "\n")
    print("ALIGN", "PASS" if ok else "FAIL", f"onset {onset} ms, P1 peak {p1_t} ms, p {tt.pvalue:.2g}, n {len(good)}")


# ------------------------------------------------------------------ statistic
def subject_terms(rf, resp, rm, nf, nm):
    """Per-subject DD and pi*Delta from cell means (VAN or P1 values)."""
    seen, uns = rf[resp == 1], rf[resp == 2]
    pi = len(seen) / (len(seen) + len(uns))
    delta = seen.mean() - uns.mean()
    dd = (nf.mean() - nm.mean()) - (rf.mean() - rm.mean())
    return dd, pi * delta


def boot_ratio(dd, pd, nboot, rng, level=95):
    """DD_norm = mean(DD) / -mean(pi*Delta); percentile 95% CIs over subjects (numerator and denominator together)."""
    n = len(dd)
    I = rng.integers(0, n, size=(nboot, n))
    num, den = dd[I].mean(axis=1), -pd[I].mean(axis=1)
    est = dd.mean() / -pd.mean()
    with np.errstate(divide="ignore", invalid="ignore"):
        r = num / den
    a = (100 - level) / 2
    lo, hi = np.percentile(r, [a, 100 - a])
    dlo = float(np.percentile(den, a))
    return float(est), float(lo), float(hi), dlo


def call(est, lo, hi, dlo):
    if not (dlo > 0) or not np.isfinite(lo) or not np.isfinite(hi):
        return "INVALID"                                 # report-block seen-unseen VAN difference not clearly present
    if lo > 0.5:
        return "REPORT-like"
    if hi < 0.5:
        return "AWARE-like"
    return "INCONCLUSIVE"


# ------------------------------------------------------------------ gate: planted proportions, report block only
def gate(level=95):
    sealed()
    D, subs = load()
    if len(subs) < MIN_SUBJ:
        raise SystemExit(f"only {len(subs)} eligible: INVALID (gate not run)")
    rng = np.random.default_rng(SEED if level == 95 else SEED + 2)
    if level != 95:
        assert not json.loads((OUT / "s4_gate.json").read_text())["PASS"], "fallback F2 only after a FAILED gate"
    worlds = [("AWARE", 1.0, 0.0), ("HALF", 0.5, 0.0), ("REPORT", 0.0, 0.0), ("SHUFFLED", 1.0, 0.0)]
    worlds += [(f"AWARE_delta{d:+.1f}", 1.0, d) for d in DELTAS]
    res = {}
    for tau in TAU_INT:
        for wname, frac, delta in worlds:
            calls = []
            for _ in range(NRUN):
                dd, pd = [], []
                for s in subs:
                    v, y, m = D[s]["RF|VAN"], D[s]["RF|resp"], D[s]["RM|VAN"]
                    a_idx, b_idx = [], []
                    for lab in (1, 2):                    # split RF in halves, stratified by answer
                        ii = rng.permutation(np.where(y == lab)[0])
                        a_idx += list(ii[:len(ii) // 2]); b_idx += list(ii[len(ii) // 2:])
                    a_idx, b_idx = np.array(a_idx), np.array(b_idx)
                    mm = rng.permutation(len(m))
                    rmA, rmB = m[mm[:len(m) // 2]], m[mm[len(m) // 2:]]
                    yA = y[a_idx] if wname != "SHUFFLED" else rng.permutation(y[a_idx])
                    vb, yb = v[b_idx], y[b_idx]
                    q = frac * (yb == 1).mean()                # planted seen share in the pseudo no-report block
                    nb = len(b_idx)
                    k = rng.binomial(nb, q)
                    pseudo = np.concatenate([rng.choice(vb[yb == 1], k), rng.choice(vb[yb == 2], nb - k)])
                    beta = rng.normal(0, BETA_SD)
                    nf = pseudo + beta + delta + rng.normal(0, tau)
                    nm = rmB + beta
                    d1, p1 = subject_terms(v[a_idx], yA, rmA, nf, nm)
                    dd.append(d1); pd.append(p1)
                calls.append(call(*boot_ratio(np.array(dd), np.array(pd), NBOOT_GATE, rng, level)))
            c = {k: calls.count(k) / NRUN for k in ("AWARE-like", "REPORT-like", "INCONCLUSIVE", "INVALID")}
            res[f"{wname}|tau{tau}"] = c
            print(wname, tau, c, flush=True)
    ok = all(res[f"AWARE|tau{t}"]["REPORT-like"] <= GATE_MAX_WRONG and res[f"REPORT|tau{t}"]["AWARE-like"] <= GATE_MAX_WRONG
             and res[f"HALF|tau{t}"]["AWARE-like"] <= GATE_MAX_HALF and res[f"HALF|tau{t}"]["REPORT-like"] <= GATE_MAX_HALF
             and res[f"SHUFFLED|tau{t}"]["AWARE-like"] + res[f"SHUFFLED|tau{t}"]["REPORT-like"] <= GATE_MAX_SHUF
             for t in TAU_INT)
    power = {t: (res[f"AWARE|tau{t}"]["AWARE-like"], res[f"REPORT|tau{t}"]["REPORT-like"]) for t in TAU_INT}
    out = dict(PASS=bool(ok), level=level, prep_sha256=sha(OUT / "s4_prep.npz"), n_subjects=len(subs), runs=NRUN, nboot=NBOOT_GATE, rates=res,
               power_aware_report=power, low_power=bool(min(min(p) for p in power.values()) < 0.5))
    (OUT / ("s4_gate.json" if level == 95 else "s4_gate99.json")).write_text(json.dumps(out, indent=1) + "\n")
    print("GATE", "PASS" if ok else "FAIL", "low power" if out["low_power"] else "")


# ------------------------------------------------------------------ real run
def run():
    sealed()
    assert not (OUT / "s4_result.json").exists(), "the first s4_result.json is final"
    al = json.loads((OUT / "s4_align.json").read_text())
    D, subs = load()
    g, level = dict(PASS=False), 95
    if (OUT / "s4_gate.json").exists():
        g = json.loads((OUT / "s4_gate.json").read_text())
        if not g["PASS"]:
            assert (OUT / "s4_gate99.json").exists(), "gate failed: run gate99 (F2) before run"
            g, level = json.loads((OUT / "s4_gate99.json").read_text()), 99
        assert g["prep_sha256"] == sha(OUT / "s4_prep.npz"), "s4_prep.npz changed after the gate"
    elif len(subs) >= MIN_SUBJ:
        raise SystemExit("gate not run")
    rng = np.random.default_rng(SEED + 1)
    out = dict(n_subjects=len(subs), gate_pass=g["PASS"], ci_level=level, align_pass=al["PASS"])
    if not g["PASS"] or not al["PASS"] or len(subs) < MIN_SUBJ:
        out["verdict"] = "INVALID"
        out["reason"] = [m for m, bad in (("gate failed", not g["PASS"]), ("alignment failed", not al["PASS"]),
                                          (f"fewer than {MIN_SUBJ} eligible", len(subs) < MIN_SUBJ)) if bad]
    else:
        terms = {}
        for name in ("VAN", "P1"):
            terms[name] = np.array([subject_terms(D[s][f"RF|{name}"], D[s]["RF|resp"], D[s][f"RM|{name}"],
                                                  D[s][f"NF|{name}"], D[s][f"NM|{name}"]) for s in subs])
        est, lo, hi, dlo = boot_ratio(terms["VAN"][:, 0], terms["VAN"][:, 1], NBOOT_REAL, rng, level)
        out["verdict"] = call(est, lo, hi, dlo)
        out["VAN"] = dict(dd_norm=est, ci=[lo, hi], denominator_lo95=dlo,
                          mean_dd_uv=float(terms["VAN"][:, 0].mean()), mean_pi_delta_uv=float(terms["VAN"][:, 1].mean()))
        p1, plo, phi, _ = boot_ratio(terms["P1"][:, 0], terms["VAN"][:, 1], NBOOT_REAL, rng)   # P1 DD over VAN denominator
        out["P1_control"] = dict(dd_norm=p1, ci95=[plo, phi], flag=bool(plo > 0 or phi < 0),
                                 note="always 95%; a flag qualifies the verdict, it does not change it")
        out["descriptive"] = dict(
            nf_minus_nm_uv=float(np.mean([D[s]["NF|VAN"].mean() - D[s]["NM|VAN"].mean() for s in subs])),
            rf_minus_rm_uv=float(np.mean([D[s]["RF|VAN"].mean() - D[s]["RM|VAN"].mean() for s in subs])),
            block_offset_mask_uv=float(np.mean([D[s]["NM|VAN"].mean() - D[s]["RM|VAN"].mean() for s in subs])))
    (OUT / "s4_result.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"prep": prep, "align": align, "gate": gate, "gate99": lambda: gate(99), "run": run}[sys.argv[1]]()
