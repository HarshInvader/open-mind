"""Statistics for task #42 (prereg §5-6, amendment 1). Used unchanged by planted.py and by the analysis script.

Everything works on a table of awakenings: v (feature), y (1 = experience), s (subject key, unique across
labs), lab. The AUC is always the within-subject pair AUC: Mann-Whitney over experience/no-experience pairs
from the same subject, pooled over subjects (weighted by pairs).
"""
import numpy as np
from scipy.stats import rankdata


# ------------------------------------------------------------------ pair AUC machinery
def keep_both(y, s):
    """Mask of rows whose subject has both classes."""
    m = np.zeros(len(y), bool)
    for sb in np.unique(s):
        i = s == sb
        if y[i].min() == 0 and y[i].max() == 1:
            m |= i
    return m


class PairAUC:
    """Within-subject pair AUC for a fixed set of rows and subjects; fast for permutations and bootstraps."""

    def __init__(self, y, s, lab=None):
        self.y = np.asarray(y, int); self.s = np.asarray(s)
        self.subs = np.unique(self.s)
        self.idx = [np.flatnonzero(self.s == sb) for sb in self.subs]
        self.n1 = np.array([self.y[i].sum() for i in self.idx]); self.n0 = np.array([len(i) for i in self.idx]) - self.n1
        self.den_s = self.n1 * self.n0
        self.lab = None if lab is None else np.array([np.asarray(lab)[i[0]] for i in self.idx])

    def ranks(self, v):
        r = np.empty(len(v))
        for i in self.idx:
            r[i] = rankdata(v[i])
        return r

    def num_s(self, v, y=None):
        y = self.y if y is None else y
        r = self.ranks(v)
        return np.array([r[i][y[i] == 1].sum() for i in self.idx]) - self.n1 * (self.n1 + 1) / 2

    def auc(self, v):
        return float(self.num_s(v).sum() / self.den_s.sum())

    def perm_labels(self, n_perm, rng):
        """(n_perm, n) labels permuted within subject. Same draws can be reused across measures."""
        Y = np.empty((n_perm, len(self.y)), np.int8)
        for i in self.idx:
            base = self.y[i]
            for p in range(n_perm):
                Y[p, i] = base[rng.permutation(len(i))]
        return Y

    def perm_aucs(self, v, Y):
        r = self.ranks(v)
        C = (self.n1 * (self.n1 + 1) / 2).sum()
        return (Y @ r - C) / self.den_s.sum()

    def boot_draws(self, n_boot, rng):
        """Subject indices drawn with replacement WITHIN lab (each lab keeps its subject count)."""
        if self.lab is None:
            groups = [np.arange(len(self.subs))]
        else:
            groups = [np.flatnonzero(self.lab == l) for l in np.unique(self.lab)]
        return [np.concatenate([g[rng.integers(0, len(g), len(g))] for g in groups]) for _ in range(n_boot)]

    def boot_ci(self, v, draws):
        ns = self.num_s(v)
        b = np.array([ns[d].sum() / self.den_s[d].sum() for d in draws])
        return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def holm(p):
    p = np.asarray(p, float); order = np.argsort(p); m = len(p)
    adj = np.empty(m); run = 0.0
    for k, i in enumerate(order):
        run = max(run, min(1.0, (m - k) * p[i])); adj[i] = run
    return adj


# ------------------------------------------------------------------ Family A
def family_a(F, names, signs, y, s, lab, n_perm=5000, n_boot=5000, seed=0, alpha=0.05):
    """F: (n, k) features (NaN = missing for that measure). Returns per-measure dict + Holm."""
    rng = np.random.default_rng(seed)
    out = {}
    pvals = []
    for j, (nm, sg) in enumerate(zip(names, signs)):
        rows = np.flatnonzero(np.isfinite(F[:, j]))
        yy, ss, ll = y[rows], s[rows], lab[rows]
        kb = keep_both(yy, ss)
        rows, yy, ss, ll = rows[kb], yy[kb], ss[kb], ll[kb]
        P = PairAUC(yy, ss, ll)
        v = sg * F[rows, j]
        a = P.auc(v)
        res = {"auc": a, "n": int(len(rows)), "n_subj": int(len(P.subs)), "n_lab": int(len(np.unique(ll)))}
        if n_perm:
            Y = P.perm_labels(n_perm, rng)
            null = P.perm_aucs(v, Y)
            res["p"] = float((1 + np.sum(np.abs(null - 0.5) >= abs(a - 0.5) - 1e-12)) / (1 + n_perm))
        if n_boot:
            res["ci95"] = P.boot_ci(v, P.boot_draws(n_boot, rng))
            res["bounded"] = bool(res["ci95"][0] > 0.40 and res["ci95"][1] < 0.60)
        res["per_lab"] = {str(l): PairAUC(yy[ll == l], ss[ll == l]).auc(v[ll == l]) for l in np.unique(ll)}
        out[nm] = res; pvals.append(res.get("p", np.nan))
    if n_perm:
        adj = holm(pvals)
        for nm, pa in zip(names, adj):
            out[nm]["p_holm"] = float(pa); out[nm]["holm_sig"] = bool(pa < alpha)
    return out


# ------------------------------------------------------------------ Family B
def centre_z(F, s):
    F = np.asarray(F, float).copy()
    if F.ndim == 1:
        F = F[:, None]
    for sb in np.unique(s):
        i = s == sb
        F[i] -= F[i].mean(0)
    sd = F.std(0); sd[sd == 0] = 1
    return (F - F.mean(0)) / sd


def logit_fit(X, y, iters=25, ridge=1e-4):
    """Newton-IRLS logistic regression with intercept; copy of t1_dream/t1lib.logit_fit. Returns (b0, w)."""
    Xi = np.c_[np.ones(len(X)), X]
    w = np.zeros(Xi.shape[1])
    R = ridge * np.eye(Xi.shape[1]); R[0, 0] = 0
    for _ in range(iters):
        z = np.clip(Xi @ w, -30, 30); p = 1 / (1 + np.exp(-z))
        g = Xi.T @ (y - p) - R @ w
        H = (Xi * (p * (1 - p))[:, None]).T @ Xi + R
        step = np.linalg.solve(H, g); w += step
        if np.abs(step).max() < 1e-7:
            break
    return w


def lolo_pred(X, y, lab, test_labs):
    """Held-out linear predictor for every row whose lab is in test_labs (leave one lab out).
    Training rows: every row not in the held-out lab (other test labs + any extra training labs)."""
    pred = np.full(len(y), np.nan)
    for l in test_labs:
        te = lab == l; tr = ~te
        w = logit_fit(X[tr], y[tr])
        pred[te] = w[0] + X[te] @ w[1:]
    return pred


def family_b(X0, M, names, y, s, lab, test_labs, n_perm=5000, n_boot=2000, seed=0, alpha=0.05):
    """X0: (n, p) baseline + covariates, already centre_z'd. M: (n, k) candidate measures, centre_z'd.
    Rows must be complete for X0; rows missing a measure are dropped for that measure only.
    ΔAUC = pair AUC(model 1 held-out preds) - pair AUC(model 0), scored on test-lab rows.
    Freedman-Lane: m ~ X0 by OLS over all rows (label-blind); residuals permuted within subject."""
    rng = np.random.default_rng(seed)
    out, pvals = {}, []
    for j, nm in enumerate(names):
        ok = np.isfinite(M[:, j])
        rows = np.flatnonzero(ok)
        yy, ss, ll = y[rows], s[rows], lab[rows]
        te = np.isin(ll, list(test_labs))
        # test rows must have both classes per subject; training rows are kept as they are
        kbt = keep_both(yy[te], ss[te])
        mask = np.ones(len(rows), bool); mask[np.flatnonzero(te)[~kbt]] = False
        rows, yy, ss, ll, te = rows[mask], yy[mask], ss[mask], ll[mask], te[mask]
        X0j, mj = X0[rows], M[rows, j]
        P = PairAUC(yy[te], ss[te], ll[te])
        p0 = lolo_pred(X0j, yy, ll, test_labs)[te]
        a0 = P.auc(p0)

        def delta(mv):
            p1 = lolo_pred(np.c_[X0j, mv], yy, ll, test_labs)[te]
            return P.auc(p1) - a0
        d = delta(mj)
        res = {"auc0": a0, "delta": d, "n_test": int(te.sum())}
        if n_perm:
            Xi = np.c_[np.ones(len(rows)), X0j]
            beta, *_ = np.linalg.lstsq(Xi, mj, rcond=None)
            fit = Xi @ beta; e = mj - fit
            grp = [np.flatnonzero(ss == sb) for sb in np.unique(ss)]
            null = np.empty(n_perm)
            for p in range(n_perm):
                ep = e.copy()
                for g in grp:
                    ep[g] = e[g][rng.permutation(len(g))]
                null[p] = delta(fit + ep)
            res["p"] = float((1 + np.sum(null >= d - 1e-12)) / (1 + n_perm))
        if n_boot:
            # subjects resampled within lab (all labs, training ones too); both models refitted
            sub_ids = np.unique(ss); sub_lab = np.array([ll[ss == sb][0] for sb in sub_ids])
            by_lab = {l: sub_ids[sub_lab == l] for l in np.unique(sub_lab)}
            rows_of = {sb: np.flatnonzero(ss == sb) for sb in sub_ids}
            bs = []
            for _ in range(n_boot):
                pick, newsub = [], []
                for l, subs in by_lab.items():
                    for k, sb in enumerate(rng.choice(subs, len(subs), replace=True)):
                        pick.append(rows_of[sb]); newsub.append(np.full(len(rows_of[sb]), f"{sb}#{k}", object))
                pk = np.concatenate(pick); ns = np.concatenate(newsub)
                yb, lb, teb = yy[pk], ll[pk], te[pk]
                Pb = PairAUC(yb[teb], ns[teb])
                q0 = lolo_pred(X0j[pk], yb, lb, test_labs)[teb]
                q1 = lolo_pred(np.c_[X0j[pk], mj[pk]], yb, lb, test_labs)[teb]
                bs.append(Pb.auc(q1) - Pb.auc(q0))
            res["ci95"] = (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))
            res["bounded"] = bool(res["ci95"][1] < 0.03)
        out[nm] = res; pvals.append(res.get("p", np.nan))
    if n_perm:
        for nm, pa in zip(names, holm(pvals)):
            out[nm]["p_holm"] = float(pa); out[nm]["holm_sig"] = bool(pa < alpha)
    return out


# ------------------------------------------------------------------ surrogate gate
def gate(v_real, v_ft, v_iaaft, sign, y, s):
    """Share kept = (AUC_surr - 0.5) / (AUC_real - 0.5) for FT and IAAFT; PASS if both <= 0.5.
    Rows: complete for all three, subjects with both classes."""
    ok = np.isfinite(v_real) & np.isfinite(v_ft) & np.isfinite(v_iaaft)
    yy, ss = y[ok], s[ok]
    kb = keep_both(yy, ss)
    P = PairAUC(yy[kb], ss[kb])
    a = P.auc(sign * v_real[ok][kb]); aft = P.auc(sign * v_ft[ok][kb]); aia = P.auc(sign * v_iaaft[ok][kb])
    sh_ft, sh_ia = (aft - 0.5) / (a - 0.5), (aia - 0.5) / (a - 0.5)
    return {"auc": a, "auc_ft": aft, "auc_iaaft": aia, "share_ft": sh_ft, "share_iaaft": sh_ia,
            "pass": bool(sh_ft <= 0.5 and sh_ia <= 0.5)}
