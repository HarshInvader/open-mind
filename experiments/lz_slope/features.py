"""Measures and surrogates shared by task #8 (surrogate gate) and #4 (LZ vs slope).

All functions take one epoch `x` of shape (n_channels, n_samples) at FS Hz
(already low-passed, see `preprocess`) and return one number averaged over
channels, unless stated otherwise.
"""
import antropy as ant
import numpy as np
from scipy.signal import butter, detrend, sosfiltfilt, welch

FS = 100.0
BANDS = {"delta": (1, 4), "theta": (4, 8), "alpha": (8, 12), "sigma": (12, 15),
         "beta": (15, 30), "lowgamma": (30, 40)}
_SOS = butter(4, 40.0, btype="low", fs=FS, output="sos")


def preprocess(x):
    """Linear detrend and 4th-order zero-phase Butterworth low-pass at 40 Hz."""
    return sosfiltfilt(_SOS, detrend(np.asarray(x, float), axis=-1), axis=-1)


# ---------------------------------------------------------------- surrogates
def phase_surrogate(x, rng):
    """Multichannel Fourier phase-randomised surrogate.

    Same random phases are added to every channel, so each channel's power
    spectrum AND the cross-spectrum are preserved; only nonlinear / phase
    structure is destroyed.
    """
    x = np.atleast_2d(x)
    n = x.shape[-1]
    X = np.fft.rfft(x, axis=-1)
    ph = rng.uniform(0, 2 * np.pi, X.shape[-1])
    ph[0] = 0.0
    if n % 2 == 0:
        ph[-1] = 0.0
    return np.fft.irfft(X * np.exp(1j * ph)[None, :], n=n, axis=-1)


# ---------------------------------------------------------------- measures
def lz(x):
    """Lempel-Ziv complexity (LZ76), signal binarised at its median, normalised by n/log2(n)."""
    x = np.atleast_2d(x)
    return float(np.mean([ant.lziv_complexity(c > np.median(c), normalize=True) for c in x]))


def pnlz(x, rng, k=10):
    """Phase-normalised LZ: LZ(x) / mean LZ over k phase-randomised surrogates of x."""
    base = lz(x)
    s = np.mean([lz(phase_surrogate(x, rng)) for _ in range(k)])
    return float(base / s)


def psd(x):
    f, p = welch(np.atleast_2d(x), fs=FS, nperseg=int(2 * FS), noverlap=int(FS), window="hann", axis=-1)
    return f, p


def spectral_exponent(x):
    """Slope of log10 PSD vs log10 f over 1-40 Hz (OLS), averaged over channels.
    More negative = steeper (more 'unconscious' per Colombo et al.)."""
    f, p = psd(x)
    m = (f >= 1) & (f <= 40)
    lf = np.log10(f[m])
    return float(np.mean([np.polyfit(lf, np.log10(pc[m]), 1)[0] for pc in p]))


def band_powers(x):
    """log10 relative power per band (relative to 1-40 Hz), channel-averaged."""
    f, p = psd(x)
    tot = p[:, (f >= 1) & (f <= 40)].sum(1)
    out = {}
    for b, (lo, hi) in BANDS.items():
        m = (f >= lo) & (f < hi) if hi < 40 else (f >= lo) & (f <= hi)
        out["bp_" + b] = float(np.mean(np.log10(p[:, m].sum(1) / tot)))
    return out


def perm_entropy(x):
    x = np.atleast_2d(x)
    return float(np.mean([ant.perm_entropy(c, order=3, delay=1, normalize=True) for c in x]))


def time_asymmetry(x):
    """Time-reversal asymmetry  mean((x[t+1]-x[t])^3) / var-scaled; channel-averaged absolute value.
    Used only in the synthetic planted check of the gate (a non-spectral measure)."""
    x = np.atleast_2d(x)
    d = np.diff(x, axis=-1)
    return float(np.mean(np.abs(np.mean(d ** 3, -1) / (np.mean(d ** 2, -1) ** 1.5 + 1e-12))))


def all_measures(x, rng):
    out = {"lz": lz(x), "pnlz": pnlz(x, rng), "slope": spectral_exponent(x),
           "perm_entropy": perm_entropy(x)}
    out.update(band_powers(x))
    return out
