"""Round 19 #1 kill test (pre-seal; never reads mask-only values).

Question: can the report block, at real per-subject counts, pin R = (miss - CR) / (hit - CR) at the VAN tightly enough
(95% CI half-width <= 0.12) and call the cut at 0.20 correctly (>= 80% of runs) when R is planted at 0 and at 0.4?

Real data used: report-block SOA-50 face trials (RF) on disk (datasets/local/cohen2024_epochs), with item 4's sealed
preprocessing rules re-applied to RF only (bad channels judged on RF alone, a small difference from item 4's prep).
Synthetic CR (mask-only) per subject: n_RM = round(60 * the subject's RF keep rate) trials, drawn by resampling the
subject's RF-unseen VAN residuals around a planted CR mean c = (miss - R * hit) / (1 - R).
Output: out/killtest.json. Prints the subject counts and the call rates only.
"""
import json, sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, filtfilt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "cohen_fixed_soa"))
import study4 as S   # sealed constants only; nothing in study4 is executed beyond import

EP_R = ROOT / "datasets" / "local" / "cohen2024_epochs"
NRUN, NBOOT, CUT, MAX_HALF, SEED = 200, 2000, 0.20, 0.12, 20261126
STAT = sys.argv[1] if len(sys.argv) > 1 else "ratio"   # "ratio" (version 1, FAILED) or "linear" (version 2)
N_RM = int(sys.argv[2]) if len(sys.argv) > 2 else 60       # mask-only trials per subject before rejection
if len(sys.argv) > 3: CUT = float(sys.argv[3])


def rf_van(sub):
    r = np.load(EP_R / f"{sub}.npz")
    x = r["X"][:, :, :S.NS].astype(np.float64) * 0.1
    bb, aa = butter(4, S.LOWPASS / (S.FS / 2))
    x = filtfilt(bb, aa, x, axis=2, padlen=100)
    ch = lambda c: x[:, c - 1, :]
    heog, veog = ch(S.HEOGL) - ch(S.HEOGR), ch(S.VEOG) - ch(S.FP1)
    scalp = x[:, [c - 1 for c in S.SCALP], :] - ch(S.LMAST)[:, None, :] / 2
    scalp -= scalp[:, :, :S.samp(0)].mean(axis=2, keepdims=True)
    pp = scalp.max(axis=2) - scalp.min(axis=2)
    med = np.median(pp, axis=0)
    bad = med > S.BAD_CH * np.median(med)
    keep = (np.ptp(heog, axis=1) <= S.HEOG_PP) & (np.ptp(veog, axis=1) <= S.VEOG_PP) & \
           (pp[:, ~bad].max(axis=1) <= S.SCALP_PP)
    chs, (a, b) = S.ROI["VAN"]
    idx = [S.SCALP.index(c) for c in chs if not bad[S.SCALP.index(c)]]
    if len(idx) < len(chs):
        return None
    v = scalp[:, idx, S.samp(a):S.samp(b)].mean(axis=(1, 2))
    return v[keep], r["resp"][keep], keep.mean()


def main():
    data = {}
    for p in sorted(EP_R.glob("*.npz")):
        out = rf_van(p.stem)
        if out is None:
            continue
        v, y, kr = out
        if (y == 1).sum() >= S.MIN_SEEN and (y == 2).sum() >= S.MIN_SEEN:
            data[p.stem] = (v[y == 1], v[y == 2], int(round(N_RM * kr)))
    subs = sorted(data)
    print(f"eligible subjects {len(subs)}; median RM n {np.median([data[s][2] for s in subs]):.0f}")
    rng = np.random.default_rng(SEED)
    res = {}
    for R in (0.0, 0.4):
        calls, halves = {"ALL-OR-NONE-COMPATIBLE": 0, "NOT-ALL-OR-NONE": 0, "INCONCLUSIVE": 0}, []
        for _ in range(NRUN):
            h, m, c = [], [], []
            for s in subs:
                seen, uns, nrm = data[s]
                # resample real trials for hit and miss too, so trial noise is in every cell
                hs, ms = rng.choice(seen, len(seen)), rng.choice(uns, len(uns))
                cr_mean = (uns.mean() - R * seen.mean()) / (1 - R)
                cr = cr_mean + rng.choice(uns - uns.mean(), nrm)
                h.append(hs.mean()); m.append(ms.mean()); c.append(cr.mean())
            h, m, c = map(np.array, (h, m, c))
            I = rng.integers(0, len(subs), (NBOOT, len(subs)))
            if STAT == "ratio":
                bs = (m[I] - c[I]).mean(1) / (h[I] - c[I]).mean(1)
                lo, hi = np.quantile(bs, [0.025, 0.975]); thr = CUT
                halves.append((hi - lo) / 2)
            else:   # linear, in the awareness direction (VAN is a negativity: seen more negative, sealed VAN PASS)
                # T = (CR - miss) - CUT/(1-CUT) * (miss - hit); R < CUT  <=>  T < 0
                kk = CUT / (1 - CUT)
                bs = (c[I] - m[I]).mean(1) - kk * (m[I] - h[I]).mean(1)
                lo, hi = np.quantile(bs, [0.025, 0.975]); thr = 0.0
                rb = (m[I] - c[I]).mean(1) / (h[I] - c[I]).mean(1)      # half-width reported on the R scale
                halves.append(float(np.diff(np.quantile(rb, [0.025, 0.975]))[0] / 2))
            calls["ALL-OR-NONE-COMPATIBLE" if hi < thr else "NOT-ALL-OR-NONE" if lo > thr else "INCONCLUSIVE"] += 1
        res[f"R={R}"] = dict(calls={k: v / NRUN for k, v in calls.items()},
                             half_width_median=float(np.median(halves)), half_width_q90=float(np.quantile(halves, 0.9)))
        print(f"R={R}", res[f"R={R}"], flush=True)
    right0 = res["R=0.0"]["calls"]["ALL-OR-NONE-COMPATIBLE"]
    right4 = res["R=0.4"]["calls"]["NOT-ALL-OR-NONE"]
    ok = right0 >= 0.8 and right4 >= 0.8 and max(r["half_width_median"] for r in res.values()) <= MAX_HALF
    res.update(n_subjects=len(subs), PASS=bool(ok))
    print("KILLTEST", "PASS" if ok else "FAIL")
    (HERE / "out").mkdir(exist_ok=True)
    res.update(stat=STAT, n_rm=N_RM, cut=CUT)
    json.dump(res, open(HERE / "out" / f"killtest_{STAT}_rm{N_RM}_cut{CUT}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
