"""Planted-answer checks on synthetic EEG (no real EEG, no real labels).

1. Detector check: synthetic posterior ROI signals with KNOWN OFF-periods (slow negative wave +
   25-45 Hz suppression) and decoy slow waves (no suppression). Recall, precision, decoy rejection,
   timing error of the OFF-period end.
2. Power / error rates of the full pipeline (detector -> features -> four tests -> verdict) on
   synthetic datasets with the real Tononi structure (39 subjects, per-subject class counts from the
   DREAM metadata), in three worlds:
     null   : labels depend on sleep depth only (an arousal confound), not on recency;
     T1     : experience (E or WR) depends on posterior recency with conditional log-odds b per SD,
              recall failure (WR) is random among experiences;
     recall : experience is independent of recency; RECALL (E vs WR) depends on recency with b per SD.
   plus label-shuffled T1 datasets.
Run: board/run.sh .venv/bin/python -I experiments/t1_dream/planted.py [reps]
Output: planted_results.json, planted_reps.jsonl (resumable).
"""
import json
import os
import sys
from multiprocessing import Pool

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t1lib as T  # noqa: E402

N = int(T.SEG * T.FS)
NCH = 9
COUNTS = os.path.join(HERE, "subject_counts.csv")


def pink(rng, nch, n, beta=2.0):
    f = np.fft.rfftfreq(n, 1 / T.FS)
    f[0] = f[1]
    spec = (rng.standard_normal((nch, len(f))) + 1j * rng.standard_normal((nch, len(f)))) / f ** (beta / 2)
    x = np.fft.irfft(spec, n=n, axis=-1)
    return x / x.std(1, keepdims=True)


def place_events(rng, rate, trend, n_max=40):
    """Inhomogeneous Poisson event times over the segment, durations 0.3-0.9 s, no overlap."""
    ev = []
    t = 0.0
    lam_max = rate * np.exp(abs(trend))
    while t < T.SEG and len(ev) < n_max:
        t += rng.exponential(1 / lam_max)
        if t >= T.SEG:
            break
        lam = rate * np.exp(trend * (t - T.SEG / 2) / (T.SEG / 2))
        if rng.uniform() > lam / lam_max:
            continue
        d = rng.uniform(0.3, 0.9)
        if t + d > T.SEG:
            break
        ev.append((t, t + d))
        t += d
    return ev


def synth_roi(rng, off_events, decoys):
    common = pink(rng, 1, N) * 12
    x = common + pink(rng, NCH, N) * 8
    hfn = rng.standard_normal((NCH, N))
    from scipy.signal import sosfiltfilt
    hf = sosfiltfilt(T._SOS_HF, hfn, axis=-1)
    hf = hf / hf.std(1, keepdims=True) * 2.0
    gate = np.ones(N)
    for (a, b), is_off in [(e, True) for e in off_events] + [(e, False) for e in decoys]:
        ia, ib = int(a * T.FS), int(b * T.FS)
        amp = rng.uniform(50, 110)
        shape = -np.sin(np.linspace(0, np.pi, ib - ia))
        x[:, ia:ib] += amp * shape[None, :] * rng.uniform(0.8, 1.2, (NCH, 1))
        if is_off:
            gate[ia:ib] = 0.35
    return x + hf * gate[None, :]


def synth_awakening(rng, depth, trend):
    rate = 0.30 * np.exp(0.4 * depth)
    ev = place_events(rng, rate, trend)
    dec = [e for e in place_events(rng, 0.08, 0.0)
           if all(e[1] < a - 0.2 or e[0] > b + 0.2 for a, b in ev)]
    return synth_roi(rng, ev, dec), ev, dec


# ------------------------------------------------------------------ 1. detector check
def detector_check(seed=1, n_subj=10, per=20):
    rng = np.random.default_rng(seed)
    tp = fn = fp = 0
    dec_seen = dec_rej = 0
    end_err = []
    Ltrue, Ldet = [], []
    for s in range(n_subj):
        recs = [synth_awakening(rng, rng.normal(), rng.normal(0, 0.3)) for _ in range(per)]
        waves = [T.half_waves(x) for x, _, _ in recs]
        thr = T.subject_threshold(waves)
        for (x, ev, dec), ws in zip(recs, waves):
            _, off = T.classify(ws, thr)
            sw_all = [w for w in ws if -w[3] >= thr[1]]
            ev_in = [e for e in ev if T.WIN[0] <= (e[0] + e[1]) / 2 < T.WIN[1]]
            used = set()
            for e in ev_in:
                mid = (e[0] + e[1]) / 2
                hit = [i for i, w in enumerate(off) if abs(w[2] - mid) <= 0.1 and i not in used]
                if hit:
                    tp += 1
                    used.add(hit[0])
                    end_err.append(abs(off[hit[0]][1] - e[1]))
                else:
                    fn += 1
            fp += len(off) - len(used)
            for d in dec:
                mid = (d[0] + d[1]) / 2
                if not (T.WIN[0] <= mid < T.WIN[1]):
                    continue
                big = [w for w in sw_all if abs(w[2] - mid) <= 0.1]
                if big:
                    dec_seen += 1
                    if not any(abs(w[2] - mid) <= 0.1 for w in off):
                        dec_rej += 1
            Ltrue.append(T.recency([e for e in ev if e[0] < T.WIN[1] and e[1] > T.WIN[0]]))
            Ldet.append(T.recency(off))
    rec, prec = tp / max(tp + fn, 1), tp / max(tp + fp, 1)
    out = dict(recall=rec, precision=prec, decoys_over_threshold=dec_seen,
               decoy_rejection=dec_rej / max(dec_seen, 1), median_end_error_s=float(np.median(end_err)),
               corr_logL_true_vs_detected=float(np.corrcoef(T.logL(Ltrue), T.logL(Ldet))[0, 1]))
    out["pass"] = bool(rec >= 0.8 and prec >= 0.8 and out["decoy_rejection"] >= 0.8
                       and out["median_end_error_s"] <= 0.1)
    return out


# ------------------------------------------------------------------ 2. pipeline power
def synth_dataset(rng, world, b, shuffle=False):
    cnt = pd.read_csv(COUNTS)
    rows = []
    for _, r in cnt.iterrows():
        nE, nNE, nWR = int(r.E), int(r.NE), int(r.WR)
        n = nE + nNE + nWR
        off_s = rng.normal(0, 0.5)
        recs = []
        for i in range(n):
            depth = off_s + rng.normal()
            xp, evp, _ = synth_awakening(rng, depth, rng.normal(0, 0.3))
            xf, evf, _ = synth_awakening(rng, 0.7 * depth + 0.7 * rng.normal(), rng.normal(0, 0.3))
            Lt = T.recency([e for e in evp if e[0] < T.WIN[1] and e[1] > T.WIN[0]])
            recs.append(dict(xp=xp, xf=xf, depth=depth, Lt=Lt, awak_idx=i + 1,
                             clock_h=rng.uniform(4, 13)))
        zL = T.logL([q["Lt"] for q in recs]); zL = (zL - zL.mean()) / (zL.std() + 1e-9)
        dz = np.array([q["depth"] for q in recs]); dz = (dz - dz.mean()) / (dz.std() + 1e-9)
        g = rng.gumbel(size=(2, n))
        conf = -0.3 * dz  # lighter sleep -> more reports in every world (arousal/recall confound)
        if world == "T1":
            exp_score, rec_score = b * zL + conf + g[0], g[1]
        elif world == "recall":
            exp_score, rec_score = conf + g[0], b * zL + g[1]
        else:
            exp_score, rec_score = conf + g[0], g[1]
        lab = np.array(["NE"] * n, dtype=object)
        expd = np.argsort(-exp_score)[:nE + nWR]
        order = expd[np.argsort(-rec_score[expd])]
        lab[order[:nE]] = "E"
        lab[order[nE:]] = "WR"
        if shuffle:
            lab = rng.permutation(lab)
        for q, l in zip(recs, lab):
            q.update(subject=r.subject, label=l)
            rows.append(q)
    return rows


def table_from_rows(rows, rng, n_surr):
    """Same feature code path as the real data (features.py uses these functions)."""
    df = pd.DataFrame(rows)
    wp = [T.half_waves(x) for x in df.xp]
    wf = [T.half_waves(x) for x in df.xf]
    feats = []
    for s in df.subject.unique():
        idx = np.nonzero((df.subject == s).to_numpy())[0]
        thp = T.subject_threshold([wp[i] for i in idx])
        thf = T.subject_threshold([wf[i] for i in idx])
        for i in idx:
            swp, offp = T.classify(wp[i], thp)
            _, offf = T.classify(wf[i], thf)
            sp = T.spectral(df.xp[i])
            feats.append(dict(i=i, **sp, count10=len(swp), n_off_post=len(offp),
                              logL_post=float(T.logL(T.recency(offp))),
                              logL_front=float(T.logL(T.recency(offf))),
                              surr_logL_post=T.logL(T.timing_surrogate_L(offp, rng, n_surr))))
    F = pd.DataFrame(feats).set_index("i").sort_index()
    return pd.concat([df[["subject", "label", "clock_h", "awak_idx"]], F], axis=1)


def one_rep(args):
    world, b, shuffle, rep = args
    rng = np.random.default_rng(10_000 + rep + int(b * 1000) * 7 + {"null": 0, "T1": 1, "recall": 2}[world] * 997
                                + (500_000 if shuffle else 0))
    rows = synth_dataset(rng, world, b, shuffle)
    df = table_from_rows(rows, rng, 300)
    r = T.run_tests(df, rng, DELTA, n_perm=400, n_boot=400, n_surr=300)
    return dict(world=world, b=b, shuffle=shuffle, rep=rep, verdict=r["verdict"],
                **{k: r[k]["est"] for k in ["TA_recency", "TB_timing", "TC_post_minus_front", "TD_without_recall"]},
                **{k + "_rej": r["holm"][k]["reject"] for k in r["holm"]},
                TA_ci90=r["TA_recency"]["ci90"], TD_ci90=r["TD_without_recall"]["ci90"])


DELTA = float(os.environ.get("T1_DELTA", np.log(2.0)))


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    out_jsonl = os.path.join(HERE, "planted_reps.jsonl")
    det = detector_check()
    print("detector", det, flush=True)
    done = set()
    if os.path.exists(out_jsonl):
        for ln in open(out_jsonl):
            r = json.loads(ln)
            done.add((r["world"], r["b"], r["shuffle"], r["rep"]))
    bs = [float(np.log(1.5)), float(np.log(2.0)), float(np.log(2.5))]
    jobs = [("null", 0.0, False, k) for k in range(reps)]
    jobs += [("T1", b, False, k) for b in bs for k in range(reps)]
    jobs += [("recall", b, False, k) for b in bs for k in range(reps)]
    jobs += [("T1", float(np.log(2.0)), True, k) for k in range(reps // 2)]
    jobs = [j for j in jobs if j not in done]
    with Pool(2) as pool, open(out_jsonl, "a") as fh:
        for r in pool.imap_unordered(one_rep, jobs):
            fh.write(json.dumps(r) + "\n")
            fh.flush()
    R = pd.DataFrame([json.loads(l) for l in open(out_jsonl)])
    summ = {}
    for (w, b, sh), g in R.groupby(["world", "b", "shuffle"]):
        v = g.verdict.value_counts(normalize=True).round(3).to_dict()
        summ[f"{w}_OR{np.exp(b):.2f}{'_shuffled' if sh else ''}"] = dict(
            reps=len(g), verdicts=v,
            mean_TA=round(g.TA_recency.mean(), 3), mean_TD=round(g.TD_without_recall.mean(), 3),
            reject_rates={k: round(g[k + "_rej"].mean(), 3) for k in
                          ["TA_recency", "TB_timing", "TC_post_minus_front", "TD_without_recall"]})
    json.dump(dict(delta=DELTA, detector=det, scenarios=summ), open(os.path.join(HERE, "planted_results.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
