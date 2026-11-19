"""Measures for task #42. Definitions: docs/prereg/2026-11-19_experience_benchmark.md §4 (+ amendment 1).

Two branches:
  native(x_roi, fs, line_hz)  -> posterior delta / high-frequency (native sampling rate, Welch 4 s)
  m100(x, x1020, rng)         -> everything else, on 100 Hz data already passed through
                                 lz_slope.features.preprocess (detrend + 40 Hz low-pass)
x: (n_channels, n_samples) all good EEG channels; x1020: the 10-20 subset (pairwise measures).
Surrogates: FT = lz_slope.features.phase_surrogate (multichannel, shared phases); IAAFT = ne_measures.iaaft.
"""
import os
import sys

import antropy as ant
import numpy as np
from scipy.signal import iirnotch, filtfilt, welch

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "experiments", "lz_slope"))
sys.path.insert(0, os.path.join(REPO, "experiments", "nonequilibrium"))
from features import band_powers, lz, perm_entropy, phase_surrogate, preprocess, psd, spectral_exponent  # noqa: E402
from ne_measures import iaaft, tra  # noqa: E402

FS = 100.0
PRIMARY = ["post_delta", "post_hf", "exponent", "lz", "pe", "hfd", "wsmi", "tc"]
SECONDARY = ["sampen", "mse", "k01", "dfa", "tra", "cser"]
NONSPECTRAL_100 = ["lz", "pe", "hfd", "wsmi", "tc"] + SECONDARY


# ------------------------------------------------------------------ native branch
def native(x_roi, fs, line_hz, hf_hi=45.0):
    x = np.atleast_2d(np.asarray(x_roi, float))
    if line_hz and fs > 2 * line_hz + 5:
        b, a = iirnotch(line_hz, 30.0, fs)
        x = filtfilt(b, a, x, axis=-1)
    n = int(4 * fs)
    f, p = welch(x, fs=fs, nperseg=n, noverlap=n // 2, window="hann", axis=-1)
    def rel(lo, hi, tlo, thi):
        num = p[:, (f >= lo) & (f <= hi)].sum(1); den = p[:, (f >= tlo) & (f <= thi)].sum(1)
        return float(np.mean(np.log10(num / den)))
    hf_hi = min(hf_hi, fs / 2 - 5)
    return {"post_delta": rel(1, 4, 1, 40), "post_hf": rel(20, hf_hi, 1, hf_hi)}


# ------------------------------------------------------------------ 100 Hz measures
def hfd(x):
    return float(np.mean([ant.higuchi_fd(np.ascontiguousarray(c, dtype=np.float64), kmax=10) for c in np.atleast_2d(x)]))


def _symbols(c, k=3, tau=3):
    n = len(c) - (k - 1) * tau
    emb = np.stack([c[i * tau:i * tau + n] for i in range(k)], 1)
    r = np.argsort(np.argsort(emb, 1), 1)
    return r[:, 0] * 9 + r[:, 1] * 3 + r[:, 2]          # unique code per rank pattern


def _opposite_code(code):
    r = np.array([code // 9, (code // 3) % 3, code % 3])
    r = 2 - r
    return r[0] * 9 + r[1] * 3 + r[2]


_CODES = sorted({a * 9 + b * 3 + c for a in range(3) for b in range(3) for c in range(3) if len({a, b, c}) == 3})
_CI = {c: i for i, c in enumerate(_CODES)}
_W = np.ones((6, 6))
for c in _CODES:
    _W[_CI[c], _CI[c]] = 0
    _W[_CI[c], _CI[_opposite_code(c)]] = 0


def wsmi(x):
    """King et al. 2013 weighted symbolic mutual information, k 3, tau 3 samples, mean over channel pairs."""
    x = np.atleast_2d(x)
    S = [np.vectorize(_CI.get)(_symbols(c)) for c in x]
    vals = []
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            J = np.zeros((6, 6)); np.add.at(J, (S[i], S[j]), 1); J /= J.sum()
            pi, pj = J.sum(1), J.sum(0)
            with np.errstate(divide="ignore", invalid="ignore"):
                t = J * np.log(J / np.outer(pi, pj))
            vals.append(np.nansum(_W * t) / np.log(6))
    return float(np.mean(vals)) if vals else np.nan


def tc(x):
    x = np.atleast_2d(x)
    if x.shape[0] < 3:
        return np.nan
    R = np.corrcoef(x)
    sign, ld = np.linalg.slogdet(0.9 * R + 0.1 * np.eye(len(R)))
    return float(-0.5 * ld / len(R))


def sampen(x):
    return float(np.nanmean([ant.sample_entropy(np.ascontiguousarray(c, dtype=np.float64), order=2) for c in np.atleast_2d(x)]))


def mse(x, scales=(1, 2, 3, 4, 5)):
    """Multiscale entropy (Costa): sample entropy (m 2) of coarse-grained signals, r = 0.2 SD of the original."""
    from antropy.entropy import _numba_sampen
    out = []
    for c in np.atleast_2d(x):
        r = 0.2 * np.std(c)
        for s in scales:
            cg = np.ascontiguousarray(c[:len(c) // s * s].reshape(-1, s).mean(1), dtype=np.float64)
            v = _numba_sampen(cg, order=2, r=r)
            out.append(v if np.isfinite(v) else np.nan)
    return float(np.nanmean(out))


def k01(x, n_c=20, rng=None):
    """Gottwald-Melbourne 0-1 test for chaos (correlation method), median K over n_c values of c."""
    rng = rng or np.random.default_rng(0)
    out = []
    for c0 in np.atleast_2d(x):
        c0 = c0 - c0.mean(); N = len(c0); ncut = N // 10; j = np.arange(1, N + 1)
        Ks = []
        for c in rng.uniform(np.pi / 5, 4 * np.pi / 5, n_c):
            p = np.cumsum(c0 * np.cos(j * c)); q = np.cumsum(c0 * np.sin(j * c))
            nn = np.arange(1, ncut + 1)
            M = np.array([np.mean((p[k:] - p[:-k]) ** 2 + (q[k:] - q[:-k]) ** 2) for k in nn])
            M = M - (c0.mean() ** 2) * (1 - np.cos(nn * c)) / (1 - np.cos(c))
            Ks.append(np.corrcoef(nn, M)[0, 1])
        out.append(np.median(Ks))
    return float(np.mean(out))


def dfa(x):
    sizes = np.unique(np.logspace(np.log10(4), np.log10(200), 12).astype(int))
    out = []
    for c in np.atleast_2d(x):
        y = np.cumsum(c - c.mean()); F = []
        for s in sizes:
            nseg = len(y) // s
            seg = y[:nseg * s].reshape(nseg, s); t = np.arange(s)
            coef = np.polyfit(t, seg.T, 1)
            fit = np.outer(coef[0], t) + coef[1][:, None]
            F.append(np.sqrt(np.mean((seg - fit) ** 2)))
        out.append(np.polyfit(np.log(sizes), np.log(F), 1)[0])
    return float(np.mean(out))


def cser(x):
    """Gaussian entropy rate from the spectrum (Mediano et al.): 0.5 log(2 pi e) + 0.5 mean_f log(S(f) fs / 2)."""
    f, p = welch(np.atleast_2d(x), fs=FS, nperseg=200, noverlap=100, axis=-1)
    m = (f > 0) & (f < FS / 2)
    return float(np.mean(0.5 * np.log(2 * np.pi * np.e) + 0.5 * np.mean(np.log(p[:, m] * FS / 2), 1)))


def m100(x, x1020, rng, secondary=True):
    out = {"exponent": spectral_exponent(x), "lz": lz(x), "pe": perm_entropy(x), "hfd": hfd(x),
           "wsmi": wsmi(x1020), "tc": tc(x1020)}
    out.update(band_powers(x))
    if secondary:
        out.update({"sampen": sampen(x), "mse": mse(x), "k01": k01(x, rng=rng), "dfa": dfa(x),
                    "tra": tra(x), "cser": cser(x)})
    return out


def surrogate_block(x, x1020, idx1020, rng, n=5, secondary=True):
    """Mean of each non-spectral measure over n FT and n IAAFT surrogates of the whole montage.
    The 10-20 subset of each surrogate is taken from the same surrogate (idx1020 = row indices in x)."""
    res = {}
    for kind in ("ft", "iaaft"):
        vals = []
        for _ in range(n):
            s = phase_surrogate(x, rng) if kind == "ft" else iaaft(x, rng)
            v = m100(s, s[idx1020] if idx1020 is not None else x1020, rng, secondary)
            vals.append({k: v[k] for k in NONSPECTRAL_100 if k in v})
        for k in vals[0]:
            res[f"{k}__{kind}"] = float(np.nanmean([v[k] for v in vals]))
    return res
