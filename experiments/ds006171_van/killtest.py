"""Round 19 #2 kill test (label-free; DRAFT, not sealed). Reads out/prep/<sub>.npz only (codes 11-32 and 128).
Per-subject seen/unseen COUNTS come from the events files (behaviour totals); no trial-level label touches EEG.

    python -I killtest.py      # -> out/killtest.json

1. Subject EOG exclusion (prereg 5b): HEOG-step or VEOG rejection > 45%; or the 6 Hz low-passed residual HEOG
   difference wave (left- minus right-target kept Gabor trials, 0-300 ms) has its max beyond the subject's own
   shuffled-side 95th percentile (side-locked eye movement detectable), or its mean beyond 3.2 uV.
   (A fixed 3.2 uV cut on the max was tried first and measured noise: shuffled-side max median ~2.5, q95 ~5.3 uV.)
2. Catch check: L(catch) in the window, 95% bootstrap CI over subjects must include 0.
3. Pooled check: label-free mean L over all kept Gabor trials must have some time point in 80-300 ms whose
   95% bootstrap upper bound is < 0.
4. Planted gate: per trial the Gabor L window mean is sign-flipped at random (keeps noise, removes lateralisation);
   pseudo hits/misses at the subject's real counts (scaled to kept trials); contrast matching as in the prereg;
   plant delta_s ~ N(-0.4, 0.4) uV (and 0) on pseudo hits. Calls as sealed: one-sided sign-flip p < .05 and
   bootstrap CI excluding 0. Required: detection >= 0.80 at -0.4, false calls <= 0.05 at 0.
"""
import csv, json, sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, filtfilt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "datasets" / "local" / "r19_ds006171" / "files"
PREP = HERE / "out" / "prep"
WIN = (0.180, 0.280)
REJ_MAX, HEOG_RESID = 0.45, 3.2
CALIPER, NMATCH_GATE = 0.01, 20
NSIM, NPERM, NBOOT, SEED = 200, 2000, 2000, 20261126
NSHUF = 500
PLANT_MEAN, PLANT_SD = -0.4, 0.4
GABOR = {11, 12, 21, 22}


def counts(sub):
    rows = list(csv.DictReader(open(RAW / sub / "eeg" / f"{sub}_task-nocue_events.tsv"), delimiter="\t"))
    return sum(r["trial_type"] == "124" for r in rows), sum(r["trial_type"] == "125" for r in rows)


def boot_ci(x, rng, axis_len=None):
    i = rng.integers(0, len(x), (NBOOT, len(x)))
    return np.quantile(x[i].mean(axis=1), [0.025, 0.975], axis=0)


def signflip_p(x, rng):
    s = rng.choice([-1, 1], (NPERM, len(x)))
    return float(((s * x).mean(axis=1) <= x.mean()).mean())          # one-sided: delta < 0


def match(con_h, con_m, rng):
    """1:1 nearest log contrast within caliper, random processing order; returns index pairs."""
    lh, lm = np.log(con_h), np.log(con_m)
    free = np.ones(len(lm), bool)
    pairs = []
    for i in rng.permutation(len(lh)):
        if not free.any():
            break
        d = np.where(free, np.abs(lm - lh[i]), np.inf)
        j = int(np.argmin(d))
        if d[j] <= CALIPER:
            free[j] = False
            pairs.append((i, j))
    return pairs


def main():
    rng = np.random.default_rng(SEED)
    subs, excl, S = sorted(p.stem for p in PREP.glob("sub-*.npz")), {}, {}
    for s in subs:
        d = np.load(PREP / f"{s}.npz")
        t = d["times"]
        w = (t >= WIN[0]) & (t <= WIN[1])
        keep, code, side = d["keep"], d["code"], d["side"]
        gab = np.isin(code, list(GABOR))
        why = []
        if d["rej_heog"][gab].mean() > REJ_MAX:
            why.append(f"heog-rej {d['rej_heog'][gab].mean():.2f}")
        if d["rej_veog"][gab].mean() > REJ_MAX:
            why.append(f"veog-rej {d['rej_veog'][gab].mean():.2f}")
        tw = (t >= 0) & (t <= 0.3)
        gg = keep & gab
        h = filtfilt(*butter(4, 6 / 128), d["heog"][gg].astype(float), axis=1)[:, tw]   # 6 Hz low-pass
        sd_ = side[gg]
        stat = lambda z: np.abs(h[z == "L"].mean(axis=0) - h[z == "R"].mean(axis=0))
        real = stat(sd_)
        shuf = np.array([stat(rng.permutation(sd_)).max() for _ in range(NSHUF)])
        # side-locked eye movement detectable beyond the subject's own noise, or mean residual beyond the sourced 3.2 uV
        if real.max() > np.quantile(shuf, 0.95):
            why.append(f"heog-sidelocked max {real.max():.2f} > shuffled q95 {np.quantile(shuf, 0.95):.2f}")
        if real.mean() > HEOG_RESID:
            why.append(f"heog-resid mean {real.mean():.2f}")
        if why:
            excl[s] = why
            continue
        nh, nm = counts(s)
        g = keep & gab & np.isfinite(d["contrast"])
        S[s] = dict(Lw=d["L"][:, w].mean(axis=1), Lt=d["L"], keep=keep, gab=gab, side=side,
                    catch=keep & ~gab, g=g, con=d["contrast"], nh=nh, nm=nm, t=t)
    out = dict(n_prepped=len(subs), excluded=excl, n_used=len(S))
    print(f"prepped {len(subs)}, excluded {len(excl)} {excl}, used {len(S)}")
    if len(S) < 3:
        print("too few subjects for group checks"); json.dump(out, open(HERE / "out" / "killtest.json", "w"), indent=1)
        return
    # 2. catch check
    # equal weight to the two (nominal) sides, as in the prereg
    lc = np.array([(v["Lw"][v["catch"] & (v["side"] == "L")].mean() + v["Lw"][v["catch"] & (v["side"] == "R")].mean()) / 2
                   for v in S.values()])
    lo, hi = boot_ci(lc, rng)
    out["catch"] = dict(mean=float(lc.mean()), ci95=[float(lo), float(hi)], PASS=bool(lo <= 0 <= hi))
    # 3. pooled check
    t = next(iter(S.values()))["t"]
    P = np.array([(v["Lt"][v["g"] & (v["side"] == "L")].mean(axis=0) + v["Lt"][v["g"] & (v["side"] == "R")].mean(axis=0)) / 2
                  for v in S.values()])
    lo_t, hi_t = boot_ci(P, rng)
    tw = (t >= 0.080) & (t <= 0.300)
    neg = np.where(tw & (hi_t < 0))[0]
    out["pooled"] = dict(PASS=bool(len(neg)), first_ms=float(t[neg[0]] * 1000) if len(neg) else None,
                         min_mean_uV=float(P.mean(axis=0)[tw].min()))
    print("catch", out["catch"], "\npooled", out["pooled"], flush=True)
    # 4. planted gate
    res = {}
    for plant in (0.0, PLANT_MEAN):
        calls = 0
        for _ in range(NSIM):
            deltas = []
            for v in S.values():
                idx = np.where(v["g"])[0]
                x = v["Lw"][idx] * rng.choice([-1, 1], len(idx))
                n = len(idx)
                nh = int(round(n * v["nh"] / (v["nh"] + v["nm"])))
                lab = np.zeros(n, bool); lab[rng.choice(n, nh, replace=False)] = True
                x = x + lab * (rng.normal(plant, PLANT_SD) if plant else 0.0)
                sd = v["side"][idx]
                dm = []
                for _m in range(NMATCH_GATE):
                    hm = []
                    for hemi in ("L", "R"):              # equal weight to the two hemifields
                        h = np.where(lab & (sd == hemi))[0]; m = np.where(~lab & (sd == hemi))[0]
                        pr = match(v["con"][idx][h], v["con"][idx][m], rng)
                        hm.append(np.mean([x[h[i]] - x[m[j]] for i, j in pr]) if pr else np.nan)
                    dm.append(np.mean(hm))
                deltas.append(np.nanmean(dm))
            dlt = np.array(deltas)
            p = signflip_p(dlt, rng)
            lo, hi = boot_ci(dlt, rng)
            calls += (p < 0.05) and (hi < 0)
        res[str(plant)] = calls / NSIM
        print(f"plant {plant}: call rate {calls / NSIM:.3f}", flush=True)
    out["planted"] = res
    out["PASS"] = bool(out["catch"]["PASS"] and out["pooled"]["PASS"] and res[str(PLANT_MEAN)] >= 0.80
                       and res["0.0"] <= 0.05)
    print("KILLTEST", "PASS" if out["PASS"] else "FAIL")
    json.dump(out, open(HERE / "out" / "killtest.json", "w"), indent=1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "smoke":
        NSIM, NMATCH_GATE = 10, 3
    main()
