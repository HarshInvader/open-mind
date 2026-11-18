"""Known-Phi networks, EEG-like observation, and Phi proxies (task #9).

Networks: N binary units, kinetic-Ising update
    P(x_i(t+1)=1 | x(t)) = sigmoid(2*beta*(sum_j W[j,i] s_j + h_i)),  s = 2x-1.
Truth: exact IIT 4.0 system integrated information phi_s (PyPhi 2.0.0rc4,
default formalism IIT_4_0_2026) of the whole system, averaged over states
weighted by the chain's stationary distribution.
"""
import itertools
import os

os.environ.setdefault("PYPHI_AGENT_NOTE_OFF", "1")
os.environ.setdefault("PYPHI_WELCOME_OFF", "1")

import numpy as np
from scipy import signal

N = 5


# ------------------------------------------------------------------ networks
def all_states(n=N):
    """Little-endian state list (node 0 changes fastest), as PyPhi expects."""
    return np.array(list(itertools.product([0, 1], repeat=n)))[:, ::-1]


def tpm_from_W(W, h, beta):
    st = all_states(len(W))
    field = (2 * st - 1) @ W + h
    return 1.0 / (1.0 + np.exp(-2.0 * beta * field))  # state-by-node, (2^n, n)


def make_W(family, rng, n=N):
    W = np.zeros((n, n))
    if family == "FF":  # random DAG: structural phi = 0
        order = rng.permutation(n)
        for a in range(n):
            for b in range(a + 1, n):
                if rng.random() < 0.6:
                    W[order[a], order[b]] = rng.normal(0, 1)
        if not W.any():
            W[order[0], order[1]] = 1.0
    elif family == "DISC":  # two disconnected recurrent modules: phi = 0
        for mod in ([0, 1], [2, 3, 4]):
            for i in mod:
                for j in mod:
                    if i != j:
                        W[i, j] = rng.normal(0, 1)
    elif family in ("DENSE", "SPARSE"):
        p = 0.8 if family == "DENSE" else 0.4
        for i in range(n):
            for j in range(n):
                if i != j and rng.random() < p:
                    W[i, j] = rng.normal(0, 1)
        if family == "SPARSE":  # guarantee one directed cycle through all nodes
            perm = rng.permutation(n)
            for a in range(n):
                i, j = perm[a], perm[(a + 1) % n]
                if W[i, j] == 0:
                    W[i, j] = rng.normal(0, 1)
    elif family == "RING":
        for i in range(n):
            W[i, (i + 1) % n] = rng.choice([-1, 1]) * (1 + 0.2 * rng.random())
        W += (rng.random((n, n)) < 0.2) * rng.normal(0, 0.3, (n, n))
        np.fill_diagonal(W, 0)
    else:
        raise ValueError(family)
    return W


def stationary(tpm):
    """Stationary distribution over joint states of the Markov chain."""
    st = all_states(tpm.shape[1])
    # joint transition P[a, b] = prod_i p_i(a)^b_i (1-p_i(a))^(1-b_i)
    P = np.prod(np.where(st[None, :, :] == 1, tpm[:, None, :], 1 - tpm[:, None, :]), axis=2)
    w, v = np.linalg.eig(P.T)
    k = np.argmin(np.abs(w - 1))
    pi = np.real(v[:, k])
    pi = np.abs(pi) / np.abs(pi).sum()
    return pi


def phi_by_state(tpm, cm, weights, min_w=1e-3):
    """phi_s of the whole system for each state with weight >= min_w."""
    import pyphi

    sub = pyphi.Substrate(tpm=tpm, cm=cm)
    st = all_states(tpm.shape[1])
    out = np.full(len(st), np.nan)
    for k, s in enumerate(st):
        if weights[k] >= min_w:
            a = pyphi.analyze(sub, tuple(int(x) for x in s), compute="sia",
                              parallel=False, progress=False)
            out[k] = float(a.phi)
    return out


def weighted_mean(vals, w):
    m = ~np.isnan(vals)
    return float(np.sum(vals[m] * w[m]) / np.sum(w[m]))


# ---------------------------------------------------------------- simulation
def simulate(tpm, T, rng, burn=500):
    n = tpm.shape[1]
    pow2 = 2 ** np.arange(n)
    x = rng.integers(0, 2, n)
    out = np.empty((T, n), dtype=np.int8)
    u = rng.random((T + burn, n))
    for t in range(T + burn):
        p = tpm[int(x @ pow2)]
        x = (u[t] < p).astype(np.int64)
        if t >= burn:
            out[t - burn] = x
    return out


def pink_noise(T, rng):
    f = np.fft.rfftfreq(T)
    spec = rng.normal(size=len(f)) + 1j * rng.normal(size=len(f))
    spec[1:] /= np.sqrt(f[1:])
    spec[0] = 0
    x = np.fft.irfft(spec, n=T)
    return x / x.std()


def observe_eeg(x, rng, leak=0.6, snr=1.0, sigma_mix=1.0, down=2):
    """Binary unit states -> EEG-like sensors.

    leaky integration (synaptic low-pass) -> volume-conduction mixing
    (Gaussian falloff, sources and sensors on a line) -> pink + white noise
    at the given signal-to-noise power ratio -> decimate by `down`.
    """
    T, n = x.shape
    s = 2.0 * x - 1.0
    y = signal.lfilter([1.0], [1.0, -leak], s, axis=0)
    pos = np.arange(n)
    M = np.exp(-((pos[:, None] - pos[None, :]) ** 2) / (2 * sigma_mix ** 2))
    z = y @ M
    z = (z - z.mean(0)) / (z.std(0) + 1e-12)
    noise = np.column_stack([pink_noise(T, rng) for _ in range(n)])
    noise = 0.95 * noise + 0.3122 * rng.normal(size=(T, n))  # ~10% white power
    noise /= noise.std(0)
    z = z + noise / np.sqrt(snr)
    return z[::down].copy()


# ------------------------------------------------------------------- proxies
def _logdet(C):
    sign, ld = np.linalg.slogdet(np.atleast_2d(C))
    return ld


def gauss_mi_lag(X, idx, tau=1):
    """I(X_idx(t-tau); X_idx(t)) under a Gaussian model."""
    A = X[:-tau, idx]
    B = X[tau:, idx]
    k = len(idx)
    C = np.cov(np.hstack([A, B]).T)
    return 0.5 * (_logdet(C[:k, :k]) + _logdet(C[k:, k:]) - _logdet(C))


def phi_wms(X, tau=1):
    """Barrett & Seth (2011) whole-minus-sum Phi_E at the size-normalised MIB."""
    n = X.shape[1]
    whole = gauss_mi_lag(X, list(range(n)), tau)
    best, best_norm = None, np.inf
    for r in range(1, n // 2 + 1):
        for A in itertools.combinations(range(n), r):
            B = [i for i in range(n) if i not in A]
            ph = whole - gauss_mi_lag(X, list(A), tau) - gauss_mi_lag(X, B, tau)
            norm = ph / min(len(A), len(B))
            if norm < best_norm:
                best_norm, best = norm, ph
    return float(best)


def _var_resid_var(Y, Xlag):
    beta, *_ = np.linalg.lstsq(Xlag, Y, rcond=None)
    return np.var(Y - Xlag @ beta)


def causal_density(X, p=2):
    """Mean conditional Granger causality over ordered pairs (Seth 2005)."""
    T, n = X.shape
    X = X - X.mean(0)
    lags = np.hstack([X[p - k - 1:T - k - 1] for k in range(p)])  # (T-p, n*p)
    Y = X[p:]
    cols = lambda keep: [k * n + j for k in range(p) for j in keep]
    vals = []
    for i in range(n):
        full = _var_resid_var(Y[:, i], lags)
        for j in range(n):
            if j == i:
                continue
            keep = [m for m in range(n) if m != j]
            red = _var_resid_var(Y[:, i], lags[:, cols(keep)])
            vals.append(np.log(red / full))
    return float(np.mean(vals))


def integration(X):
    C = np.cov(X.T)
    return float(0.5 * (np.sum(np.log(np.diag(C))) - _logdet(C)))


def tse_complexity(X):
    """Tononi-Sporns-Edelman neural complexity, Gaussian."""
    n = X.shape[1]
    C = np.cov(X.T)
    I_all = integration(X)
    total = 0.0
    for k in range(1, n):
        Is = [0.5 * (np.sum(np.log(np.diag(C)[list(S)])) - _logdet(C[np.ix_(S, S)]))
              for S in itertools.combinations(range(n), k)]
        total += (k / n) * I_all - np.mean(Is)
    return float(total)


def lz76(seq):
    """Lempel-Ziv (1976) phrase count of a 0/1 sequence (Kaspar-Schuster)."""
    s = seq
    n = len(s)
    i, k, l, c, kmax = 0, 1, 1, 1, 1
    while True:
        if s[i + k - 1] == s[l + k - 1]:
            k += 1
            if l + k > n:
                c += 1
                break
        else:
            kmax = max(k, kmax)
            i += 1
            if i == l:
                c += 1
                l += kmax
                if l + 1 > n:
                    break
                i, k, kmax = 0, 1, 1
            else:
                k = 1
    return c


def lzc_multi(B, rng, n_shuf=3):
    """Schartner-style multichannel LZc: binary (T, n), column-major
    concatenation (time-major), normalised by time-shuffled copies."""
    seq = B.reshape(-1).astype(np.int8).tolist()
    c = lz76(seq)
    cs = []
    for _ in range(n_shuf):
        Bs = B[rng.permutation(len(B))]
        cs.append(lz76(Bs.reshape(-1).astype(np.int8).tolist()))
    return float(c / np.mean(cs))


def binarize(X):
    return (X > np.median(X, axis=0)).astype(np.int8)


def plugin_tpm(B, alpha=1.0):
    """Empirical state-by-node TPM from a binary series, Laplace-smoothed."""
    T, n = B.shape
    pow2 = 2 ** np.arange(n)
    idx = B[:-1] @ pow2
    nxt = B[1:]
    tpm = np.full((2 ** n, n), 0.5)
    counts = np.bincount(idx, minlength=2 ** n)
    for s in range(2 ** n):
        m = idx == s
        if m.any():
            tpm[s] = (nxt[m].sum(0) + alpha) / (m.sum() + 2 * alpha)
    freq = counts / counts.sum()
    return tpm, freq


def phi_plugin(B, min_w=1e-3):
    tpm, freq = plugin_tpm(B)
    n = B.shape[1]
    cm = np.ones((n, n), dtype=int)
    vals = phi_by_state(tpm, cm, freq, min_w=min_w)
    return weighted_mean(vals, freq)


def baseline_local_pred(X):
    """Sum of single-channel lag-1 Gaussian MI: predictability, no integration."""
    return float(sum(gauss_mi_lag(X, [i]) for i in range(X.shape[1])))


def baseline_mean_corr(X):
    C = np.corrcoef(X.T)
    return float(np.mean(np.abs(C[np.triu_indices_from(C, 1)])))


def all_proxies(X, B, rng, with_plugin=True):
    out = {
        "phi_wms": phi_wms(X),
        "causal_density": causal_density(X),
        "integration": integration(X),
        "tse_complexity": tse_complexity(X),
        "lzc": lzc_multi(B, rng),
        "base_local_pred": baseline_local_pred(X),
        "base_mean_corr": baseline_mean_corr(X),
    }
    if with_plugin:
        out["phi_plugin"] = phi_plugin(B)
    return out
