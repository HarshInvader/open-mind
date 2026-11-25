import numpy as np
rng = np.random.default_rng(0)
C, fs = 63, 500
t = np.arange(-0.1, 0.598, 1 / fs)
T = len(t)
mix = rng.standard_normal((C, C)) * 0.3 + np.eye(C)  # spatially correlated noise

def pink(n_tr):
    X = rng.standard_normal((n_tr, C, T))
    F = np.fft.rfft(X, axis=-1)
    f = np.fft.rfftfreq(T, 1 / fs); f[0] = f[1]
    F /= np.sqrt(f)
    x = np.fft.irfft(F, n=T, axis=-1)
    x = np.einsum('ij,njt->nit', mix, x)
    return x / x.std()

topo = rng.standard_normal(C); topo /= np.linalg.norm(topo)

def evoked(n_tr, amp, jit_sd, peak=0.40, width=0.08):
    lat = peak + rng.standard_normal(n_tr) * jit_sd
    w = np.exp(-0.5 * ((t[None] - lat[:, None]) / width) ** 2)
    return amp * w[:, None, :] * topo[None, :, None] * np.sqrt(C)

def dva_within(x, win=50):
    u = x / np.linalg.norm(x, axis=1, keepdims=True)
    out = np.full(T, np.nan)
    h = win // 2
    for k in range(h, T - h):
        out[k] = 1 - np.linalg.norm(u[:, :, k - h:k + h].mean(-1), axis=1).mean()
    return out

def norm_t(x):
    return np.linalg.norm(x, axis=1).mean(0)

n = 40
win = (t > 0.33) & (t < 0.47)
def run(name, a1, j1, s1, a2, j2, s2, reps=20):
    d = []; nn = []
    for _ in range(reps):
        x1 = evoked(n, a1, j1) + s1 * pink(n)
        x2 = evoked(n, a2, j2) + s2 * pink(n)
        d.append(np.nanmean(dva_within(x1)[win]) - np.nanmean(dva_within(x2)[win]))
        nn.append(norm_t(x1)[win].mean() - norm_t(x2)[win].mean())
    d = np.array(d); nn = np.array(nn)
    print(f"{name:55s} d_dva(A-B)={d.mean():+.4f} (z={d.mean()/d.std()*np.sqrt(len(d)):+.1f})  d_norm={nn.mean():+.3f}")

print('same topography in both conditions; only amplitude / noise / jitter differ')
run('null: identical', .5, .03, 1, .5, .03, 1)
run('amp 0.75 vs 0.5 (signal amplitude only)', .75, .03, 1, .5, .03, 1)
run('noise 0.85 vs 1 (ERD-like, signal fixed)', .5, .03, .85, .5, .03, 1)
run('amp up + noise down (norm roughly matched)', .65, .03, .9, .5, .03, 1)
run('jitter 20ms vs 80ms (amp fixed)', .5, .02, 1, .5, .08, 1)
