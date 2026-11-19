"""Irreversibility (non-equilibrium) measures for the NE test. Prereg: docs/prereg/2026-11-18_nonequilibrium_vs_spectrum.md

Every function takes one epoch x of shape (n_channels, n_samples) at 100 Hz, already preprocessed
(detrend + 40 Hz low-pass, experiments/lz_slope/features.preprocess), and returns one number.

- tra:   higher-order time-reversal asymmetry. Normalised third moment of increments,
         |E[(x[t+tau]-x[t])^3]| / E[(x[t+tau]-x[t])^2]^1.5, at tau = 1, 2, 4, 8 samples (10-80 ms),
         averaged over lags and channels. Its expectation is 0 for every Gaussian (linear) stationary
         process, so phase-randomised surrogates have none: it cannot be carried by the spectrum.
- ptir:  permutation time irreversibility (order 3, delay 1): half the L1 distance between the
         ordinal-pattern distribution of x and of x reversed in time, channel-averaged. Secondary.
- ne2:   second-order irreversibility in the form used by Deco, Kringelbach and colleagues:
         mean over channel pairs i<j of (C_ij(tau) - C_ji(tau))^2, C_ij(tau) = corr(x_i[t+tau], x_j[t]),
         averaged over tau = 1, 2, 4, 8 samples. It depends only on the cross-spectrum, so
         multichannel phase-randomised surrogates (same phases on every channel) keep it.
"""
import numpy as np

LAGS = (1, 2, 4, 8)


def tra(x):
    x = np.atleast_2d(np.asarray(x, float))
    out = []
    for t in LAGS:
        d = x[:, t:] - x[:, :-t]
        m3 = np.mean(d ** 3, -1)
        m2 = np.mean(d ** 2, -1)
        out.append(np.abs(m3) / (m2 ** 1.5 + 1e-30))
    return float(np.mean(out))


_PAT = {p: i for i, p in enumerate([(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)])}


def _ordinal_dist(c):
    w = np.stack([c[:-2], c[1:-1], c[2:]], 1)
    r = np.argsort(np.argsort(w, axis=1, kind="stable"), axis=1, kind="stable")
    codes = r[:, 0] * 9 + r[:, 1] * 3 + r[:, 2]
    keys = {a * 9 + b * 3 + cc: i for (a, b, cc), i in _PAT.items()}
    h = np.zeros(6)
    for k, i in keys.items():
        h[i] = np.sum(codes == k)
    return h / max(h.sum(), 1)


def ptir(x):
    x = np.atleast_2d(np.asarray(x, float))
    return float(np.mean([0.5 * np.abs(_ordinal_dist(c) - _ordinal_dist(c[::-1])).sum() for c in x]))


def ne2(x):
    x = np.atleast_2d(np.asarray(x, float))
    if x.shape[0] < 2:
        return float("nan")
    z = (x - x.mean(1, keepdims=True)) / (x.std(1, keepdims=True) + 1e-30)
    n = z.shape[1]
    iu = np.triu_indices(z.shape[0], 1)
    vals = []
    for t in LAGS:
        C = z[:, t:] @ z[:, :n - t].T / (n - t)        # C[i, j] = corr(x_i[t+tau], x_j[t])
        vals.append(np.mean((C - C.T)[iu] ** 2))
    return float(np.mean(vals))


def iaaft(x, rng, n_iter=50):
    """Per-channel IAAFT surrogate: keeps each channel's amplitude distribution and (closely) its spectrum."""
    x = np.atleast_2d(np.asarray(x, float))
    out = np.empty_like(x)
    for k, c in enumerate(x):
        amp = np.abs(np.fft.rfft(c))
        srt = np.sort(c)
        s = rng.permutation(c)
        for _ in range(n_iter):
            S = np.fft.rfft(s)
            s = np.fft.irfft(amp * np.exp(1j * np.angle(S)), n=len(c))
            s = srt[np.argsort(np.argsort(s))]
        out[k] = s
    return out


N_SURR = 5


def ne_measures(x, rng, phase_surrogate):
    """Raw measures plus the primary 'excess' versions: value minus the mean over N_SURR multichannel
    phase-randomised surrogates of the same epoch. |m3|-type statistics have a finite-sample bias that
    depends on the spectrum (smoother signal, fewer effective samples, larger bias), so the raw values
    can carry spectral information; the excess removes that bias epoch by epoch."""
    surr = [phase_surrogate(x, rng) for _ in range(N_SURR)]
    t0, p0 = tra(x), ptir(x)
    return {"tra": t0, "ptir": p0, "ne2": ne2(x),
            "tra_x": t0 - float(np.mean([tra(s) for s in surr])),
            "ptir_x": p0 - float(np.mean([ptir(s) for s in surr]))}
