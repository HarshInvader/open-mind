"""T1 DREAM test: OFF-period detector, features, models and tests.

Shared by planted.py (synthetic EEG, power), features.py (real EEG, label-blind)
and analysis.py (labels joined). Everything here is fixed by PREREG.md.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import butter, sosfiltfilt, welch

FS = 128.0          # analysis sampling rate (Hz)
SEG = 12.0          # seconds of signal handed to the detector: file time [-12, 0] s
WIN = (1.0, 11.0)   # analysis window, seconds from segment start: file time [-11, -1] s
WLEN = WIN[1] - WIN[0]
HF_BAND = (25.0, 45.0)
HF_RATIO = 0.8      # OFF-period: HF power in the wave's central half <= 0.8 x window median
AMP_SW = 75.0       # slow-wave COUNT covariate: |trough| >= 75th percentile of a subject's half-wave troughs
AMP_OFF = 50.0      # OFF-period candidates: |trough| >= median; the 25-45 Hz suppression then decides
DUR = (0.25, 1.0)   # half-wave duration limits (s)

_SOS_SW = butter(4, [0.5, 4.0], btype="band", fs=FS, output="sos")
_SOS_HF = butter(4, HF_BAND, btype="band", fs=FS, output="sos")


# ------------------------------------------------------------ detection
def half_waves(x_roi: np.ndarray):
    """Negative half-waves of the 0.5-4 Hz ROI-mean signal inside the window.

    x_roi: (n_ch, n_samp) ROI channels at FS covering SEG seconds.
    Returns list of (t_down, t_up, t_trough, trough_uV) in seconds from segment start,
    plus the HF envelope (for the OFF criterion).
    """
    sw = sosfiltfilt(_SOS_SW, x_roi.mean(0))
    hf = sosfiltfilt(_SOS_HF, x_roi, axis=-1) ** 2
    hf = hf.mean(0)
    k = int(0.1 * FS)
    hf = np.convolve(hf, np.ones(k) / k, mode="same")
    a, b = int(WIN[0] * FS), int(WIN[1] * FS)
    base = np.median(hf[a:b])
    s = np.sign(sw)
    down = np.nonzero((s[:-1] >= 0) & (s[1:] < 0))[0] + 1
    up = np.nonzero((s[:-1] < 0) & (s[1:] >= 0))[0] + 1
    out = []
    for d in down:
        u = up[up > d]
        if len(u) == 0:
            break
        u = u[0]
        dur = (u - d) / FS
        if not (DUR[0] <= dur <= DUR[1]):
            continue
        tr = d + int(np.argmin(sw[d:u]))
        if not (a <= tr < b):
            continue
        q1, q3 = d + (u - d) // 4, d + 3 * (u - d) // 4 + 1
        ratio = float(hf[q1:q3].mean() / base) if base > 0 else np.inf
        out.append((d / FS, u / FS, tr / FS, float(sw[tr]), ratio))
    return out


def subject_threshold(all_waves: list[list[tuple]]):
    """Label-blind amplitude thresholds (count, OFF) from |trough| over all of a subject's awakenings."""
    mags = [-w[3] for ws in all_waves for w in ws]
    if not mags:
        return (np.inf, np.inf)
    return (float(np.percentile(mags, AMP_SW)), float(np.percentile(mags, AMP_OFF)))


def classify(waves, thr):
    """Split half-waves into slow waves (amplitude only) and OFF-periods (amplitude + HF suppression)."""
    sw = [w for w in waves if -w[3] >= thr[0]]
    off = [w for w in waves if -w[3] >= thr[1] and w[4] <= HF_RATIO]
    return sw, off


def recency(events) -> float:
    """Seconds from the end (up-crossing) of the last event to the window end; WLEN if none."""
    if not events:
        return WLEN
    end = max(min(e[1], WIN[1]) for e in events)
    return float(max(WIN[1] - end, 0.0))


def logL(L):
    return np.log(np.asarray(L, float) + 0.25)


def timing_surrogate_L(events, rng, n: int) -> np.ndarray:
    """Recency after re-placing the same events (same durations and shapes) at random,
    non-overlapping positions in the window. Count and wave shape are kept; only timing changes."""
    if not events:
        return np.full(n, WLEN)
    durs = np.array([min(e[1], WIN[1]) - max(e[0], WIN[0]) for e in events])
    durs = np.clip(durs, 0.05, None)
    free = WLEN - durs.sum()
    if free <= 0:
        return np.zeros(n)
    # Uniform random non-overlapping placement (random order, k+1 gaps uniform on the simplex):
    # the free time is cut at k uniform points; the gap after the last event is free - max(U).
    k = len(durs)
    U = rng.uniform(0, free, size=(n, k))
    return np.clip(free - U.max(1), 0, WLEN)


def spectral(x_roi: np.ndarray):
    """Model-A spectral baselines from the ROI-mean signal."""
    m = x_roi.mean(0)
    a5, b = int((WIN[1] - 5.0) * FS), int(WIN[1] * FS)
    a10 = int(WIN[0] * FS)

    def bp(seg, lo, hi):
        f, p = welch(seg, fs=FS, nperseg=int(2 * FS), noverlap=int(FS))
        return float(np.log10(p[(f >= lo) & (f <= hi)].mean() + 1e-12))
    f, p = welch(m[a10:b], fs=FS, nperseg=int(2 * FS), noverlap=int(FS))
    k = (f >= 1) & (f <= 30)
    slope = float(np.polyfit(np.log10(f[k]), np.log10(p[k] + 1e-12), 1)[0])
    return dict(delta5=bp(m[a5:b], 1, 4), delta10=bp(m[a10:b], 1, 4),
                sigma=bp(m[a10:b], 12, 15), beta5=bp(m[a5:b], 16, 30), exp10=slope)


# ------------------------------------------------------------ models
def logit_fit(X: np.ndarray, y: np.ndarray, iters: int = 25, ridge: float = 1e-4) -> np.ndarray:
    """Newton-IRLS logistic regression with intercept (column 0 added here). Tiny ridge for stability."""
    Xi = np.c_[np.ones(len(X)), X]
    w = np.zeros(Xi.shape[1])
    R = ridge * np.eye(Xi.shape[1]); R[0, 0] = 0
    for _ in range(iters):
        z = np.clip(Xi @ w, -30, 30)
        p = 1 / (1 + np.exp(-z))
        g = Xi.T @ (y - p) - R @ w
        H = (Xi * (p * (1 - p))[:, None]).T @ Xi + R
        step = np.linalg.solve(H, g)
        w += step
        if np.abs(step).max() < 1e-7:
            break
    return w[1:]


def centre_z(F: np.ndarray, subj: np.ndarray) -> np.ndarray:
    """Centre each column within subject (label-blind), then z-score over rows."""
    F = F.astype(float).copy()
    for s in np.unique(subj):
        m = subj == s
        F[m] -= F[m].mean(0)
    sd = F.std(0)
    sd[sd == 0] = 1
    return (F - F.mean(0)) / sd


def perm_within(y, subj, rng):
    y2 = y.copy()
    for s in np.unique(subj):
        m = np.nonzero(subj == s)[0]
        y2[m] = y[rng.permutation(m)]
    return y2


def coef_test(XA, x_test, y, subj, rng, n_perm, n_boot, contrast=None):
    """One-sided (positive) test of a coefficient (or a contrast of the last columns).

    XA: Model-A covariates (already centred/z-scored); x_test: (n, k) test columns.
    contrast: weights over the k test columns (default: the single column).
    Returns dict(est, p, ci90, ci95).
    """
    X = np.c_[XA, x_test]
    k = x_test.shape[1]
    c = np.ones(1) if contrast is None else np.asarray(contrast, float)

    def stat(Xm, ym):
        return float(logit_fit(Xm, ym)[-k:] @ c)
    est = stat(X, y)
    ge = 0
    for _ in range(n_perm):
        if stat(X, perm_within(y, subj, rng)) >= est:
            ge += 1
    p = (ge + 1) / (n_perm + 1)
    subs = np.unique(subj)
    idx = {s: np.nonzero(subj == s)[0] for s in subs}
    bs = []
    for _ in range(n_boot):
        rows = np.concatenate([idx[s] for s in rng.choice(subs, len(subs))])
        yb = y[rows]
        if yb.min() == yb.max():
            continue
        bs.append(stat(X[rows], yb))
    bs = np.array(bs)
    return dict(est=est, p=p, ci90=[float(np.percentile(bs, 5)), float(np.percentile(bs, 95))],
                ci95=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))])


def holm(pvals: dict, alpha: float = 0.05) -> dict:
    keys = sorted(pvals, key=lambda k: pvals[k])
    m, out, stop = len(keys), {}, False
    for i, k in enumerate(keys):
        thr = alpha / (m - i)
        rej = (not stop) and pvals[k] <= thr
        if not rej:
            stop = True
        out[k] = dict(p=pvals[k], threshold=thr, reject=rej)
    return out


MODEL_A = ["delta5", "delta10", "count10", "sigma", "beta5", "exp10", "clock_h", "awak_idx"]


def run_tests(df, rng, delta, n_perm=2000, n_boot=2000, n_surr=1000):
    """The four pre-registered tests and the verdict. df: pandas DataFrame, one row per awakening with
    columns subject, label in {E, NE, WR}, MODEL_A, logL_post, logL_front, surr_logL_post (array per row)."""
    res = {}
    en = df[df.label.isin(["E", "NE"])].reset_index(drop=True)
    wn = df[df.label.isin(["WR", "NE"])].reset_index(drop=True)
    cols = MODEL_A + ["logL_post", "logL_front"]

    def design(d):
        Z = centre_z(d[cols].to_numpy(), d.subject.to_numpy())
        return Z[:, :len(MODEL_A)], Z[:, len(MODEL_A):]
    XA, XT = design(en)
    y = (en.label == "E").to_numpy().astype(float)
    s = en.subject.to_numpy()
    res["TA_recency"] = coef_test(XA, XT[:, :1], y, s, rng, n_perm, n_boot)
    res["TC_post_minus_front"] = coef_test(XA, XT, y, s, rng, n_perm, n_boot, contrast=[1, -1])
    # TB: count-matched timing test. Replace every awakening's posterior recency by a
    # timing-only surrogate (same waves, random positions), refit, compare.
    S = np.vstack(en.surr_logL_post.to_numpy())  # (n, n_surr_avail)
    raw = en[cols].to_numpy().astype(float)
    bs = []
    for j in range(min(n_surr, S.shape[1])):
        r2 = raw.copy()
        r2[:, len(MODEL_A)] = S[:, j]
        Z = centre_z(r2, s)
        bs.append(logit_fit(np.c_[Z[:, :len(MODEL_A)], Z[:, len(MODEL_A):len(MODEL_A) + 1]], y)[-1])
    bs = np.array(bs)
    est = res["TA_recency"]["est"]
    res["TB_timing"] = dict(est=float(est - np.median(bs)), beta_real=est, beta_surr_median=float(np.median(bs)),
                            p=float((1 + (bs >= est).sum()) / (1 + len(bs))))
    XA2, XT2 = design(wn)
    y2 = (wn.label == "WR").to_numpy().astype(float)
    res["TD_without_recall"] = coef_test(XA2, XT2[:, :1], y2, wn.subject.to_numpy(), rng, n_perm, n_boot)
    H = holm({k: res[k]["p"] for k in ["TA_recency", "TB_timing", "TC_post_minus_front", "TD_without_recall"]})
    res["holm"] = H
    res["verdict"] = verdict(res, H, delta)
    res["n"] = dict(E=int((df.label == "E").sum()), NE=int((df.label == "NE").sum()),
                    WR=int((df.label == "WR").sum()), subjects=int(df.subject.nunique()))
    return res


def verdict(res, H, delta):
    A, D = res["TA_recency"], res["TD_without_recall"]
    rej = {k: H[k]["reject"] for k in H}
    if rej["TA_recency"] and rej["TB_timing"] and rej["TD_without_recall"]:
        return "STRONG PASS" if rej["TC_post_minus_front"] else "PASS"
    if (-delta < A["ci90"][0] and A["ci90"][1] < delta) or A["ci95"][1] < 0:
        return "REFUTED (no recency effect of the stated size)"
    if rej["TA_recency"] and D["ci90"][1] < delta:
        return "REFUTED (recency tracks recall, not experience)"
    return "INCONCLUSIVE"
