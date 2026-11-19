"""Planted checks P1 (a)-(c) for task #42 (prereg §7). Synthetic EEG only; no DREAM data is read.

  .venv/bin/python -I experiments/experience_benchmark/planted.py features   (heavy: synthetic EEG -> measures)
  .venv/bin/python -I experiments/experience_benchmark/planted.py evaluate   (light: families A, B, gate)

Everything below is fixed before any synthetic feature was computed.

Structure. The real Tier 1 N2 design: 53 subjects in 5 labs with their real (experience, no-experience)
counts (de-duplicated DREAM metadata, the counts in the docstring of bounds_sim.py; listed in TIER1 below).
Deviation from §7, declared: 16 channels at 200 Hz instead of each lab's real channel count and rate, to
keep compute feasible (the real counts would take about 30 CPU-hours per world). Channels 12-15 are the
"posterior ROI"; all 16 form the 10-20 subset.

Synthetic awakening (20 s at 200 Hz):
- Per subject: 1/f exponent beta_s ~ U(1.6, 2.4); mixing matrix A_s (16 x 6) ~ N(0, 1);
  spindle amplitude ~ U(0.2, 0.6); nonlinear-source weights w_s ~ U(0.5, 1) per channel.
- Per awakening: beta = beta_s + N(0, 0.1); 6 latent 1/f^beta sources mixed by A_s, plus independent
  1/f^beta channel noise (weight 0.7); one 13 Hz spindle (Gaussian envelope, SD 0.5 s, random time);
  each channel standardised, then scaled to SD 30 uV.
Worlds (the experience class y = 1 differs as follows; nothing else depends on y):
- null: no difference.
- nonlinear (P1a): every awakening gets a common source c mixed into each channel with weight w_s and
  variance share lam (channel = sqrt(1 - lam) * background + sqrt(lam) * w_s/|w_s| * c, then rescaled).
  c is the x-component of a Rossler system (a 0.2, b 0.2, c 5.7; main frequency drawn U(4, 8) Hz).
  For y = 1, c is the Rossler signal; for y = 0, c is a single-channel IAAFT surrogate of a Rossler signal.
  The power spectrum and amplitude distribution are therefore matched between classes; only the
  nonlinear (phase) structure differs. lam in {0.1, 0.25, 0.5}; the pass mark is judged at lam = 0.5.
- spectral (P1b): for y = 1, beta is lowered by 0.15 (a flatter 1/f slope). Nothing else differs.
Covariates (clock time, awakening index) are drawn independently of y.

Features: measures.native on channels 12-15 at 200 Hz (50 Hz notch), measures.m100 (primary only) on the
resampled (200 -> 100 Hz) and preprocessed 16 channels, and for the nonlinear and spectral worlds
measures.surrogate_block (5 FT + 5 IAAFT, primary non-spectral measures). Pools: null world 2 x the real
counts (two independent copies of the design); nonlinear and spectral worlds 2 x the real counts per subject.

Datasets and tests (stats.py, the code the analysis script will use):
- P1(c) null: 200 datasets = 2 null copies x 100 random label draws (labels re-drawn within subject with
  the real counts; features fixed). Family A (Holm over 8, 2,000 permutations) and Family B (Holm over 4,
  1,000 permutations). PASS if the family-wise rejection rate is <= 0.08 in each family.
- P1(a), P1(b): 40 datasets each, made by drawing, per subject, the real counts without replacement from
  the 2 x pool. Family A (2,000 permutations), Family B (1,000 permutations), gate per measure.
  P1(a) PASS (at lam = 0.5): at least one of LZ, PE, HFD is Holm-significant in Family A in >= 80% of
    datasets AND in Family B in >= 80%, and the gate PASSes in >= 80% of the datasets where Family A detects it.
  P1(b) PASS: every Family B measure rejects in <= 0.05 + 1.96 * sqrt(0.05 * 0.95 / 40) = 0.118 of
    datasets, and for every non-spectral measure that Family A detects in >= 50% of datasets, the gate
    FAILs in >= 80% of the datasets where it is detected.
Fewer permutations than the analysis (5,000) are used for compute; p-values of 1/2001 and 1/1001 still
resolve Holm thresholds down to 0.05/8.
"""
import json
import os
import sys
import zlib
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy.integrate import solve_ivp
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measures as M  # noqa: E402
import stats as S  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "nonequilibrium"))
from ne_measures import iaaft  # noqa: E402

FS, NSEC, NCH = 200.0, 20, 16
N = int(FS * NSEC)
POST = [12, 13, 14, 15]
TIER1 = [("Aamodt", 3, 4), ("Aamodt", 3, 3), ("Aamodt", 5, 1), ("Aamodt", 5, 2), ("Aamodt", 1, 1), ("Aamodt", 2, 3),
         ("Aamodt", 2, 2), ("Aamodt", 3, 3), ("Aamodt", 1, 1), ("DATA1", 4, 2), ("DATA1", 1, 1), ("DATA1", 2, 9),
         ("DATA1", 1, 4), ("DATA1", 7, 2), ("LODE", 1, 3), ("LODE", 2, 1), ("LODE", 1, 4), ("LODE", 1, 1),
         ("LODE", 7, 1), ("LODE", 3, 1), ("LODE", 5, 1), ("LODE", 3, 2), ("LODE", 4, 3), ("LODE", 1, 2),
         ("LODE", 3, 2), ("LODE", 1, 1), ("LODE", 2, 1), ("LODE", 2, 4), ("LODE", 5, 1), ("Rome", 12, 8),
         ("Rome", 15, 6), ("Rome", 19, 1), ("Rome", 6, 2), ("Rome", 9, 3), ("Rome", 13, 5), ("Rome", 7, 4),
         ("Rome", 8, 3), ("Rome", 6, 5), ("Rome", 6, 5), ("Rome", 4, 10), ("Rome", 8, 3), ("Rome", 10, 5),
         ("Rome", 7, 7), ("Rome", 21, 4), ("Rome", 12, 6), ("Rome", 1, 6), ("Rome", 7, 2), ("Set19", 1, 1),
         ("Set19", 1, 2), ("Set19", 1, 1), ("Set19", 2, 1), ("Set19", 3, 1), ("Set19", 1, 1)]
WORLDS = {"null": dict(kind="null", lam=0.0, surr=False), "nl10": dict(kind="nl", lam=0.10, surr=True),
          "nl25": dict(kind="nl", lam=0.25, surr=True), "nl50": dict(kind="nl", lam=0.50, surr=True),
          "spec": dict(kind="spec", lam=0.0, surr=True)}
NONSPEC = ["lz", "pe", "hfd", "wsmi", "tc"]
FAM_B = ["lz", "pe", "hfd", "wsmi"]
BASE = ["exponent", "bp_delta", "bp_theta", "bp_alpha", "bp_sigma", "bp_beta", "bp_lowgamma"]
DIRECTION = {"post_delta": -1, "post_hf": 1, "exponent": 1, "lz": 1, "pe": 1, "hfd": 1, "wsmi": 1, "tc": -1}


def pink(beta, shape, rng):
    f = np.fft.rfftfreq(N, 1 / FS)
    amp = np.where(f < 0.5, 0.5, f) ** (-beta / 2); amp[0] = 0
    X = (rng.normal(size=shape + (len(f),)) + 1j * rng.normal(size=shape + (len(f),))) * amp
    return np.fft.irfft(X, n=N, axis=-1)


def rossler(rng):
    f0 = rng.uniform(4, 8)                       # Rossler main angular frequency is about 1 per time unit
    t_end = NSEC * 2 * np.pi * f0 * 1.07 + 50
    sol = solve_ivp(lambda t, u: [-u[1] - u[2], u[0] + 0.2 * u[1], 0.2 + u[2] * (u[0] - 5.7)],
                    (0, t_end), rng.normal(0, 1, 3) + [1, 1, 0], t_eval=np.linspace(50, t_end, N),
                    rtol=1e-6, atol=1e-8)
    x = sol.y[0]
    return (x - x.mean()) / x.std()


def subject_params(world, si):
    r = np.random.default_rng(zlib.crc32(f"subj|{si}".encode()))     # same subjects in every world
    return {"beta": r.uniform(1.6, 2.4), "A": r.normal(size=(NCH, 6)), "spin": r.uniform(0.2, 0.6),
            "w": r.uniform(0.5, 1.0, NCH)}


def awakening(world, si, y, k, copy):
    W = WORLDS[world]
    rng = np.random.default_rng(zlib.crc32(f"{world}|{copy}|{si}|{y}|{k}".encode()))
    P = subject_params(world, si)
    beta = P["beta"] + rng.normal(0, 0.1) - (0.15 if (W["kind"] == "spec" and y == 1) else 0.0)
    x = P["A"] @ pink(beta, (6,), rng) + 0.7 * pink(beta, (NCH,), rng)
    t = np.arange(N) / FS; t0 = rng.uniform(2, NSEC - 2)
    sp = np.sin(2 * np.pi * 13 * t) * np.exp(-0.5 * ((t - t0) / 0.5) ** 2)
    x = (x - x.mean(1, keepdims=True)) / x.std(1, keepdims=True) + P["spin"] * np.outer(P["w"], sp)
    x = (x - x.mean(1, keepdims=True)) / x.std(1, keepdims=True)
    if W["kind"] == "nl":
        c = rossler(rng)
        if y == 0:
            c = iaaft(c[None, :], rng)[0]
        x = np.sqrt(1 - W["lam"]) * x + np.sqrt(W["lam"]) * np.outer(P["w"] / np.abs(P["w"]).max(), c)
        x = (x - x.mean(1, keepdims=True)) / x.std(1, keepdims=True)
    return 30.0 * x, rng


def features(job):
    world, si, y, k, copy = job
    x, rng = awakening(world, si, y, k, copy)
    r = {"world": world, "copy": copy, "si": si, "lab": TIER1[si][0], "y": y, "k": k}
    r.update(M.native(x[POST], FS, 50.0))
    xp = M.preprocess(resample_poly(x, 1, 2, axis=-1))
    r.update(M.m100(xp, xp, rng, secondary=False))
    if WORLDS[world]["surr"]:
        sb = M.surrogate_block(xp, xp, np.arange(NCH), rng, n=5, secondary=False)
        r.update({k2: v for k2, v in sb.items() if k2.split("__")[0] in NONSPEC})
    return r


def all_jobs():
    for world in WORLDS:
        for si, (lab, e, n) in enumerate(TIER1):
            for copy in (0, 1):
                for y, cnt in ((1, e), (0, n)):
                    for k in range(cnt):
                        yield (world, si, y, k, copy)


def run_features():
    out = os.path.join(HERE, "planted_features.jsonl")
    done = set()
    if os.path.exists(out):
        done = {(r["world"], r["si"], r["y"], r["k"], r["copy"]) for r in map(json.loads, open(out))}
    todo = [j for j in all_jobs() if j not in done]
    print("todo", len(todo), flush=True)
    with ProcessPoolExecutor(max_workers=2) as ex, open(out, "a") as f:
        for i, r in enumerate(ex.map(features, todo, chunksize=4)):
            f.write(json.dumps(r) + "\n")
            if i % 100 == 0:
                f.flush(); print(i, "/", len(todo), flush=True)


# ------------------------------------------------------------------ evaluation
def arrays(rows):
    y = np.array([r["y"] for r in rows]); s = np.array([f"{r['si']}" for r in rows]); lab = np.array([r["lab"] for r in rows])
    return y, s, lab


def run_tests(rows, rng, seed, gate=False):
    y, s, lab = arrays(rows)
    F = np.array([[r.get(m, np.nan) for m in M.PRIMARY] for r in rows], float)
    A = S.family_a(F, M.PRIMARY, [DIRECTION[m] for m in M.PRIMARY], y, s, lab, n_perm=2000, n_boot=0, seed=seed)
    cov = rng.normal(size=(len(rows), 2))                       # clock time, awakening index: unrelated to y
    X0 = S.centre_z(np.c_[np.array([[r[b] for b in BASE] for r in rows]), cov], s)
    Mb = S.centre_z(np.array([[r[m] for m in FAM_B] for r in rows]), s)
    B = S.family_b(X0, Mb, FAM_B, y, s, lab, set(lab), n_perm=1000, n_boot=0, seed=seed + 1)
    out = {"A": {m: A[m]["holm_sig"] for m in M.PRIMARY}, "A_auc": {m: A[m]["auc"] for m in M.PRIMARY},
           "B": {m: B[m]["holm_sig"] for m in FAM_B}, "B_delta": {m: B[m]["delta"] for m in FAM_B}}
    if gate:
        out["gate"] = {}
        for m in NONSPEC:
            g = S.gate(F[:, M.PRIMARY.index(m)], np.array([r[m + "__ft"] for r in rows]),
                       np.array([r[m + "__iaaft"] for r in rows]), DIRECTION[m], y, s)
            out["gate"][m] = g["pass"]
    return out


def draw_dataset(pool, rng):
    """Per subject, the real counts drawn without replacement from the 2 x pool."""
    by = {}
    for r in pool:
        by.setdefault((r["si"], r["y"]), []).append(r)
    rows = []
    for si, (lab, e, n) in enumerate(TIER1):
        for y, cnt in ((1, e), (0, n)):
            c = by[(si, y)]
            rows += [c[i] for i in rng.choice(len(c), cnt, replace=False)]
    return rows


def relabel(rows, rng):
    """Null datasets: labels re-drawn within subject with the real counts; features unchanged."""
    out = []
    by = {}
    for r in rows:
        by.setdefault(r["si"], []).append(r)
    for si, rs in by.items():
        ys = np.array([r["y"] for r in rs]); ys = ys[rng.permutation(len(ys))]
        out += [dict(r, y=int(v)) for r, v in zip(rs, ys)]
    return out


def evaluate():
    rows = [json.loads(l) for l in open(os.path.join(HERE, "planted_features.jsonl"))]
    rng = np.random.default_rng(20261119)
    res = {}
    # P1(c)
    null = [r for r in rows if r["world"] == "null"]
    fa = fb = 0; n_ds = 0
    for copy in (0, 1):
        base = [r for r in null if r["copy"] == copy]
        for i in range(100):
            o = run_tests(relabel(base, rng), rng, seed=1000 * copy + i)
            fa += any(o["A"].values()); fb += any(o["B"].values()); n_ds += 1
    res["P1c"] = {"n_datasets": n_ds, "fwer_A": fa / n_ds, "fwer_B": fb / n_ds, "pass": fa / n_ds <= 0.08 and fb / n_ds <= 0.08}
    print("P1c", res["P1c"], flush=True)
    for world in ("nl10", "nl25", "nl50", "spec"):
        pool = [r for r in rows if r["world"] == world]
        O = [run_tests(draw_dataset(pool, rng), rng, seed=5000 + i, gate=True) for i in range(40)]
        rate = lambda key, m: float(np.mean([o[key][m] for o in O]))
        gate_given_A = {m: (float(np.mean([o["gate"][m] for o in O if o["A"][m]])) if any(o["A"][m] for o in O) else None)
                        for m in NONSPEC}
        res[world] = {"A_rate": {m: rate("A", m) for m in M.PRIMARY}, "B_rate": {m: rate("B", m) for m in FAM_B},
                      "gate_pass_given_A": gate_given_A,
                      "mean_auc": {m: float(np.mean([o["A_auc"][m] for o in O])) for m in M.PRIMARY},
                      "mean_delta": {m: float(np.mean([o["B_delta"][m] for o in O])) for m in FAM_B}}
        print(world, res[world], flush=True)
    a = res["nl50"]
    res["P1a_pass"] = any(a["A_rate"][m] >= 0.8 and a["B_rate"][m] >= 0.8 and (a["gate_pass_given_A"][m] or 0) >= 0.8
                          for m in ("lz", "pe", "hfd"))
    b = res["spec"]
    res["P1b_pass"] = all(b["B_rate"][m] <= 0.118 for m in FAM_B) and all(
        (1 - (b["gate_pass_given_A"][m] or 0)) >= 0.8 for m in NONSPEC if b["A_rate"][m] >= 0.5)
    print("P1a_pass", res["P1a_pass"], "P1b_pass", res["P1b_pass"])
    json.dump(res, open(os.path.join(HERE, "planted.json"), "w"), indent=1)


if __name__ == "__main__":
    {"features": run_features, "evaluate": evaluate}[sys.argv[1]]()
