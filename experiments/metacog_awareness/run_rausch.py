"""Sealed analysis: does confidence track accuracy better on high-visibility trials than a
single-evidence observer predicts? Rausch & Zehetleitner (2016) data from the Confidence Database.
See docs/prereg/2026-11-23_metacog_awareness_rausch2016.md.

  .venv/bin/python -I experiments/metacog_awareness/run_rausch.py /path/to/data_Rausch_2016.csv
"""
import csv, json, sys, os
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm, rankdata

B_NULL = 1000
N_BOOT = 2000
SEED = 20261123
HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    out = []
    dropped = {"training": 0, "contrast0": 0, "unparsable": 0}
    for r in rows:
        try:
            if int(float(r["Training"])) == 1:
                dropped["training"] += 1
                continue
            con = float(r["contrast"])
            if con <= 0:
                dropped["contrast0"] += 1
                continue
            acc, cf, vis = float(r["Accuracy"]), float(r["Confidence"]), float(r["Visibility"])
            if not (np.isfinite(con) and np.isfinite(cf) and np.isfinite(vis)) or acc not in (0.0, 1.0):
                dropped["unparsable"] += 1
                continue
            out.append((r["Subj_idx"], con, acc, cf, vis, r["ScaleOrder"]))
        except (ValueError, KeyError):
            dropped["unparsable"] += 1
            continue
    subs = sorted({o[0] for o in out})
    cons = sorted({o[1] for o in out})
    s = np.array([subs.index(o[0]) for o in out])
    k = np.array([cons.index(o[1]) for o in out])
    y = np.array([o[2] for o in out])
    c = np.array([o[3] for o in out])
    v = np.array([o[4] for o in out])
    orders = {sub: {o[5] for o in out if o[0] == sub} for sub in subs}
    assert all(len(x) == 1 for x in orders.values()), "ScaleOrder varies within a subject"
    order = {sub: next(iter(x)) for sub, x in orders.items()}
    print("dropped rows:", dropped, "kept:", len(out), flush=True)
    return dict(subj=s, k=k, y=y, c=c, v=v, subs=subs, cons=cons, order=order, dropped=dropped)


def zsub(x, subj, n):
    out = np.empty_like(x, dtype=float)
    for i in range(n):
        m = subj == i
        out[m] = (x[m] - x[m].mean()) / (x[m].std() + 1e-12)
    return out


class Design:
    def __init__(self, subj, k, nsub, nk, c_raw=None, v_raw=None):
        self.subj, self.k, self.nsub, self.nk = subj, k, nsub, nk
        # Each subject's observed rating values, sorted: simulated ratings are mapped onto them by rank,
        # so the null reproduces each subject's marginal distribution (floors, ceilings, ties).
        self.c_sorted = None if c_raw is None else [np.sort(c_raw[subj == i]) for i in range(nsub)]
        self.v_sorted = None if v_raw is None else [np.sort(v_raw[subj == i]) for i in range(nsub)]
        self.cells = [(i, j, (subj == i) & (k == j)) for i in range(nsub) for j in range(nk)]
        self.cells = [(i, j, m) for i, j, m in self.cells if m.sum() >= 5]

    def simulate(self, d, sc, sv, gamma, rng, lam=0.0):
        dd = d[self.subj, self.k]
        e = dd / 2 + rng.standard_normal(dd.size)
        y = (e > 0).astype(float)
        a = np.abs(e)
        v = zsub(a + gamma * dd + sv * rng.standard_normal(dd.size), self.subj, self.nsub)
        c = a + sc * np.exp(-lam * v) * rng.standard_normal(dd.size)
        if self.c_sorted is not None:
            c, v = self.qmap(c, self.c_sorted), self.qmap(v, self.v_sorted)
        return y, zsub(c, self.subj, self.nsub), zsub(v, self.subj, self.nsub)

    def qmap(self, x, sorted_obs):
        out = np.empty_like(x)
        for i in range(self.nsub):
            m = self.subj == i
            r = np.argsort(np.argsort(x[m]))  # simulated values are continuous: no ties
            out[m] = sorted_obs[i][r]
        return out

    def moments(self, y, c, v):
        acc = np.zeros(3); n = 0
        for _, _, m in self.cells:
            if y[m].std() == 0 or c[m].std() == 0 or v[m].std() == 0:
                continue
            acc += [np.corrcoef(c[m], y[m])[0, 1], np.corrcoef(v[m], y[m])[0, 1], np.corrcoef(c[m], v[m])[0, 1]]
            n += 1
        cv = np.nanmean([np.corrcoef(v[self.subj == i], self.k[self.subj == i])[0, 1]
                         if v[self.subj == i].std() > 0 else np.nan for i in range(self.nsub)])
        return np.append(acc / max(n, 1), cv)

    def d_from_acc(self, y):
        d = np.zeros((self.nsub, self.nk))
        for i, j, m in self.cells:
            n = m.sum()
            acc = np.clip(y[m].mean(), 0.5 + 0.5 / n, 1 - 0.5 / n)
            d[i, j] = 2 * norm.ppf(acc)
        return d

    def logit_int(self, y, c, v):
        n = y.size
        X = [np.ones(n), c, v, c * v] + [(self.k == j).astype(float) for j in range(1, self.nk)] + \
            [(self.subj == i).astype(float) for i in range(1, self.nsub)]
        X = np.column_stack(X)
        b = np.zeros(X.shape[1])
        for _ in range(25):
            p = 1 / (1 + np.exp(-np.clip(X @ b, -30, 30)))
            w = p * (1 - p) + 1e-9
            step = np.linalg.solve(X.T @ (X * w[:, None]) + 1e-6 * np.eye(X.shape[1]), X.T @ (y - p))
            b += step
            if np.max(np.abs(step)) < 1e-6:
                break
        return b[3]

    def gap_by_subject(self, y, c, v):
        """Per subject: mean over contrasts of AUROC2(c) in the high-v half minus the low-v half."""
        g = [[] for _ in range(self.nsub)]
        for i, j, m in self.cells:
            hi = v[m] >= np.median(v[m])
            a1, a0 = auroc(c[m][hi], y[m][hi]), auroc(c[m][~hi], y[m][~hi])
            if not (np.isnan(a1) or np.isnan(a0)):
                g[i].append(a1 - a0)
        return np.array([np.mean(x) if x else np.nan for x in g])


def auroc(x, y):
    pos, neg = x[y == 1], x[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    r = rankdata(np.concatenate([pos, neg]))
    return (r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def fit_null(D, y, c, v, seed):
    target = D.moments(y, c, v)
    d = D.d_from_acc(y)

    def loss(p):
        tot = 0
        for r in range(4):
            tot += np.sum((D.moments(*D.simulate(d, np.exp(p[0]), np.exp(p[1]), p[2], np.random.default_rng(seed + r))) - target) ** 2)
        return tot
    best = None
    for x0 in ([0.0, 0.5, 0.3], [-0.5, 1.0, 0.0], [0.5, 0.0, 0.8], [0.0, 1.5, 0.5]):
        # Explicit simplex (steps of 0.3): scipy's default step for a zero start coordinate is 0.00025,
        # too small to move on the step-shaped loss that rank-mapped ratings produce.
        x0 = np.array(x0)
        simplex = np.vstack([x0] + [x0 + 0.3 * np.eye(3)[i] for i in range(3)])
        r = minimize(loss, x0, method="Nelder-Mead",
                     options={"maxiter": 300, "xatol": 1e-2, "fatol": 1e-6, "initial_simplex": simplex})
        if best is None or r.fun < best.fun:
            best = r
    return d, float(np.exp(best.x[0])), float(np.exp(best.x[1])), float(best.x[2]), target


def analyse(dat, label):
    nsub, nk = len(dat["subs"]), len(dat["cons"])
    s, k, y = dat["subj"], dat["k"], dat["y"]
    c, v = zsub(dat["c"], s, nsub), zsub(dat["v"], s, nsub)
    D = Design(s, k, nsub, nk, c_raw=dat["c"], v_raw=dat["v"])
    d, sc, sv, g, target = fit_null(D, y, c, v, SEED)
    obs = D.logit_int(y, c, v)
    gap_obs = D.gap_by_subject(y, c, v)
    null_b, null_gap, null_mom = [], [], []
    for b in range(B_NULL):
        ys, cs, vs = D.simulate(d, sc, sv, g, np.random.default_rng(SEED + 10_000 + b))
        null_b.append(D.logit_int(ys, cs, vs))
        null_gap.append(D.gap_by_subject(ys, cs, vs))
        if b < 200:
            null_mom.append(D.moments(ys, cs, vs))
    null_b = np.array(null_b); null_gap = np.array(null_gap); null_mom = np.array(null_mom)
    p = float((1 + np.sum(null_b >= obs)) / (B_NULL + 1))
    excess_gap_subj = gap_obs - np.nanmean(null_gap, axis=0)
    rng = np.random.default_rng(SEED + 1)
    ok = ~np.isnan(excess_gap_subj)
    es = excess_gap_subj[ok]
    boots = [np.mean(rng.choice(es, es.size)) for _ in range(N_BOOT)]
    ci = [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]
    mom_z = ((target - null_mom.mean(0)) / (null_mom.std(0) + 1e-12)).tolist()
    return dict(label=label, n_subjects=int(nsub), n_trials=int(y.size), contrasts=dat["cons"],
                fit=dict(sc=sc, sv=sv, gamma=g), moments_obs=target.tolist(), moments_null_mean=null_mom.mean(0).tolist(),
                moment_z=mom_z, beta_int_obs=float(obs), beta_int_null_mean=float(null_b.mean()),
                beta_int_excess=float(obs - null_b.mean()), p_one_sided=p,
                auroc2_gap_obs=float(np.nanmean(gap_obs)), auroc2_gap_null=float(np.nanmean(null_gap)),
                auroc2_gap_excess=float(np.mean(es)), auroc2_gap_excess_ci95=ci, n_subjects_gap=int(ok.sum()))


def verdict(r):
    if r["n_subjects_gap"] < 15 or max(abs(z) for z in r["moment_z"]) > 3:
        return "void"
    if r["p_one_sided"] < 0.05 and r["auroc2_gap_excess"] >= 0.03:
        return "supports: rejects the single-evidence null (consistent with awareness-linked metacognition)"
    if r["auroc2_gap_excess_ci95"][1] < 0.03:
        return "refutes: no awareness-linked metacognition beyond the single-evidence null at excess >= 0.03"
    return "inconclusive"


def main():
    dat = load(sys.argv[1])
    res = {"primary": analyse(dat, "all subjects")}
    res["primary"]["verdict"] = verdict(res["primary"])
    for order in sorted(set(dat["order"].values())):
        keep = [i for i, sub in enumerate(dat["subs"]) if dat["order"][sub] == order]
        m = np.isin(dat["subj"], keep)
        sub = {kk: dat[kk][m] for kk in ("k", "y", "c", "v")}
        remap = {old: new for new, old in enumerate(keep)}
        sub["subj"] = np.array([remap[x] for x in dat["subj"][m]])
        sub["subs"] = [dat["subs"][i] for i in keep]
        sub["cons"] = dat["cons"]
        sub["order"] = {s_: order for s_ in sub["subs"]}
        res[f"secondary_order_{order}"] = analyse(sub, f"ScaleOrder {order}")
    m = dat["k"] > 0
    sub = {kk: dat[kk][m] for kk in ("subj", "y", "c", "v")}
    sub["k"] = dat["k"][m] - 1
    sub.update(subs=dat["subs"], cons=dat["cons"][1:], order=dat["order"])
    res["secondary_without_lowest_contrast"] = analyse(sub, "without lowest contrast")
    json.dump(res, open(os.path.join(HERE, "rausch_result.json"), "w"), indent=1)
    print(json.dumps({k: {kk: v[kk] for kk in ("n_subjects", "beta_int_excess", "p_one_sided", "auroc2_gap_obs",
                                                 "auroc2_gap_null", "auroc2_gap_excess", "auroc2_gap_excess_ci95", "moment_z")}
                      for k, v in res.items()}, indent=1))
    print("VERDICT:", res["primary"]["verdict"])


if __name__ == "__main__":
    main()
