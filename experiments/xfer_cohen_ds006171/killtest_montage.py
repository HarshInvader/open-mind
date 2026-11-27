"""Round 20 #1, kill test step 1 (DESIGN.md §6.1; label-free: stimulus codes only, never 124/125). DRAFT, not sealed.

    python -I killtest_montage.py      # -> out/killtest_montage.json

Within ds006171, leave-one-subject-out present (codes 11-22) vs catch (31-32) decoding on 150-600 ms bin features:
  native  = 128 channels, average reference;
  mapped  = 55 covered Cohen positions, hemisphere-symmetrised (primary feature space of the transfer test).
Retention = (AUC_mapped - 0.5) / (AUC_native - 0.5), ratio of subject means; one-sided 95% lower bound by subject
bootstrap must be >= 0.80, and the native AUC's lower bound must be > 0.5.
Subjects with VEOG rejection > 45% are left out (same rule as round 19 #2).
"""
import json
from pathlib import Path

import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent
FEAT, MONT = HERE / "out" / "feat", HERE / "out" / "montage.npz"
BINS = slice(3, 12)                       # 150-600 ms
REJ_MAX, NBOOT, SEED = 0.45, 10000, 20261128
GAB, CATCH = (11, 12, 21, 22), (31, 32)


def sym_pairs(pos):
    """Homologous pairs by mirroring x; a channel whose mirror is itself (within 5 deg) is midline."""
    mir = pos * np.array([-1, 1, 1])
    ang = np.degrees(np.arccos(np.clip(mir @ pos.T, -1, 1)))
    groups, used = [], set()
    for i in range(len(pos)):
        if i in used:
            continue
        j = int(np.argmin(ang[i]))
        assert ang[i, j] < 5, f"no mirror for channel {i} ({ang[i, j]:.1f} deg)"
        groups.append([i] if j == i else [i, j]); used |= {i, j}
    return groups


def symmetrise(X, groups):
    return np.stack([X[:, g, :].mean(axis=1) for g in groups], axis=1)


def load(groups):
    S = {}
    for f in sorted(FEAT.glob("sub-*.npz")):
        d = np.load(f)
        code = d["code"]
        gab = np.isin(code, GAB)
        if d["rej_veog"][gab].mean() > REJ_MAX:
            continue
        k = d["keep"] & (gab | np.isin(code, CATCH))
        y = gab[k].astype(int)
        S[f.stem] = dict(native=d["native"][k][:, :, BINS].reshape(k.sum(), -1),
                         mapped=symmetrise(d["mapped"][k], groups)[:, :, BINS].reshape(k.sum(), -1), y=y)
    return S


def zs(X):
    return (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-9)


def loso(S, key):
    subs = list(S)
    auc = {}
    for s in subs:
        Xtr = np.vstack([zs(S[t][key]) for t in subs if t != s]); ytr = np.concatenate([S[t]["y"] for t in subs if t != s])
        clf = LDA(solver="lsqr", shrinkage="auto").fit(Xtr, ytr)
        auc[s] = float(roc_auc_score(S[s]["y"], clf.decision_function(zs(S[s][key]))))
    return auc


def main():
    mz = np.load(MONT)
    groups = sym_pairs(mz["cohen_pos"][mz["covered"]])
    S = load(groups)
    print(f"subjects {len(S)}; symmetrised groups {len(groups)} ({sum(len(g) == 1 for g in groups)} midline)", flush=True)
    an, am = loso(S, "native"), loso(S, "mapped")
    subs = list(S)
    a_n, a_m = np.array([an[s] for s in subs]), np.array([am[s] for s in subs])
    rng = np.random.default_rng(SEED)
    I = rng.integers(0, len(subs), (NBOOT, len(subs)))
    ret_b = (a_m[I].mean(axis=1) - 0.5) / (a_n[I].mean(axis=1) - 0.5)
    ret = (a_m.mean() - 0.5) / (a_n.mean() - 0.5)
    out = dict(n=len(subs), groups=len(groups), auc_native=float(a_n.mean()), auc_mapped=float(a_m.mean()),
               native_lo95=float(np.percentile(a_n[I].mean(axis=1), 5)), retention=float(ret),
               retention_lo95=float(np.percentile(ret_b, 5)), per_subject=dict(native=an, mapped=am))
    out["PASS"] = bool(out["retention_lo95"] >= 0.80 and out["native_lo95"] > 0.5)
    print({k: v for k, v in out.items() if k != "per_subject"})
    json.dump(out, open(HERE / "out" / "killtest_montage.json", "w"), indent=1)


if __name__ == "__main__":
    main()
