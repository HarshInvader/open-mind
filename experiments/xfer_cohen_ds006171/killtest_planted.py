"""Round 20 #1, kill test steps 2-3 (DESIGN.md §6.2-6.3; label-free on ds006171). DRAFT, not sealed.

    python -I killtest_planted.py [smoke]    # -> out/killtest_planted.json

3. Cohen ceiling: leave-one-subject-out seen/unseen AUC within Cohen, early (150-300) and late (300-600) windows.
2. Planted transfer: decoders trained on all Cohen subjects (symmetrised 55-site features, z-scored per subject,
   shrinkage LDA). In ds006171, pseudo seen/unseen labels at each subject's real counts (behaviour only); onto pseudo-seen
   trials add a_s * c * P_w, where P_w is Cohen's pooled seen - unseen mean pattern (uV) in window w, c scales the
   early pattern so its posterior-ROI mean (Cohen sites nearest PO7/PO8/P7/P8/O1/O2) is -0.69 uV (the sourced
   ds006171 bilateral VAN), and the same c is used for the late window (conservative: the sourced P3b is far larger).
   a_s ~ N(1, sd_rel), sd_rel set so the total between-subject SD of the early ROI difference matches dz 0.46.
   Sensitivity (reported, not gating): the plant restricted to the ROI groups, and at half size.
   Contrast matching within hemifield (caliper 0.01; 5 matchings per run here, 200 in the real run).
   Late-window spread set to the sourced P3b dz 1.67 at the Cohen site nearest Pz (DESIGN 6.2). Calls: Holm over the two
   windows on one-sided sign-flip p (as DESIGN 5), and
   bootstrap 95% CI of mean AUC excluding 0.5. Required: detection >= 0.80 in each window, false calls <= 0.05 at no plant.
"""
import json, sys
from pathlib import Path

import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "experiments" / "ds006171_van"))   # prep.py, imported by killtest_montage's neighbours
import killtest_montage as KM
import importlib.util


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


VK = _load("van_kt", ROOT / "experiments" / "ds006171_van" / "killtest.py")   # match() (caliper 0.01)
counts = _load("r_kt", ROOT / "experiments" / "ds006171_r" / "killtest.py").counts   # behaviour counts only

WIN = {"early": slice(3, 6), "late": slice(6, 12)}
ROI_NAMES = ["PO7", "PO8", "P7", "P8", "O1", "O2"]
HM, DZ, DZ_P3 = -0.69, 0.46, 1.67
NRUN, NMATCH, NPERM, NBOOT, SEED = 200, 5, 2000, 2000, 20261129


def zs(X):
    return (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-9)


def main(smoke=False):
    nrun = 10 if smoke else NRUN
    rng = np.random.default_rng(SEED)
    mz = np.load(KM.MONT)
    cpos = mz["cohen_pos"][mz["covered"]]
    groups = KM.sym_pairs(cpos)
    # posterior ROI on the Cohen side: groups holding the covered site nearest each ds006171 ROI electrode
    dn = list(mz["ds_names"])
    near = {int(np.argmax(cpos @ mz["ds_pos"][dn.index(n)])) for n in ROI_NAMES}
    roi_g = [i for i, g in enumerate(groups) if set(g) & near]
    # Cohen
    cz = np.load(HERE / "out" / "cohen_feat.npz")
    csubs = sorted({k.split("|")[0] for k in cz.files})
    C = {s: (KM.symmetrise(cz[f"{s}|X"], groups), cz[f"{s}|y"]) for s in csubs}
    out = dict(n_cohen=len(csubs), roi_groups=roi_g, ceiling={}, planted={}, null={})
    dec, pat = {}, {}
    for w, sl in WIN.items():
        flat = {s: (X[:, :, sl].reshape(len(y), -1), y) for s, (X, y) in C.items()}
        auc = []
        for s in csubs:
            Xtr = np.vstack([zs(flat[t][0]) for t in csubs if t != s]); ytr = np.concatenate([flat[t][1] for t in csubs if t != s])
            clf = LDA(solver="lsqr", shrinkage="auto").fit(Xtr, ytr)
            auc.append(roc_auc_score(flat[s][1], clf.decision_function(zs(flat[s][0]))))
        auc = np.array(auc)
        I = rng.integers(0, len(auc), (NBOOT, len(auc)))
        out["ceiling"][w] = dict(mean=float(auc.mean()), ci95=np.percentile(auc[I].mean(axis=1), [2.5, 97.5]).tolist())
        dec[w] = LDA(solver="lsqr", shrinkage="auto").fit(np.vstack([zs(v[0]) for v in flat.values()]),
                                                           np.concatenate([v[1] for v in flat.values()]))
        pat[w] = np.mean([X[y == 1].mean(axis=0) - X[y == 0].mean(axis=0) for X, y in C.values()], axis=0)[:, sl]
    roi_early = float(pat["early"][roi_g].mean())
    out["cohen_roi_early_uV"] = roi_early
    assert roi_early < 0, f"Cohen early ROI seen-unseen is {roi_early:.2f} uV (not negative): plant sign undefined"
    c = HM / roi_early
    out["scale_c"] = c
    print("ceiling", out["ceiling"], "roi_early", round(roi_early, 3), "c", round(c, 3), flush=True)
    # ds006171
    D = {}
    for f in sorted((HERE / "out" / "feat").glob("sub-*.npz")):
        d = np.load(f)
        code = d["code"]; gab = np.isin(code, KM.GAB)
        if d["rej_veog"][gab].mean() > KM.REJ_MAX:
            continue
        k = d["keep"] & gab & np.isfinite(d["contrast"])
        h, m, _, _ = counts(f.stem)
        D[f.stem] = dict(X=KM.symmetrise(d["mapped"][k], groups), con=d["contrast"][k], side=d["side"][k],
                         nh=int(round(k.sum() * h / (h + m))))
    v = np.mean([np.var(dd["X"][:, roi_g, :][:, :, WIN["early"]].mean(axis=(1, 2)), ddof=1) *
                 (1 / dd["nh"] + 1 / (len(dd["con"]) - dd["nh"])) for dd in D.values()])
    sd_rel = float(np.sqrt(max(0.0, (abs(HM) / DZ) ** 2 - v)) / abs(HM))
    pz = [i for i, g in enumerate(groups) if int(np.argmax(cpos @ mz["ds_pos"][dn.index("Pz")])) in g]
    m_late = float(c * pat["late"][pz].mean())
    v_l = np.mean([np.var(dd["X"][:, pz, :][:, :, WIN["late"]].mean(axis=(1, 2)), ddof=1) *
                   (1 / dd["nh"] + 1 / (len(dd["con"]) - dd["nh"])) for dd in D.values()])
    sd_late = float(np.sqrt(max(0.0, (abs(m_late) / DZ_P3) ** 2 - v_l)) / abs(m_late))
    SD = {"early": sd_rel, "late": sd_late}
    out.update(n_ds=len(D), sd_rel=sd_rel, sd_rel_late=sd_late, late_pz_plant_uV=m_late, late_pz_sampling_sd=float(np.sqrt(v_l)),
               late_dz_reachable=bool((abs(m_late) / DZ_P3) ** 2 > v_l))
    print(f"ds006171 subjects {len(D)}; sd_rel {sd_rel:.2f}", flush=True)

    def one_run(plant):
        auc = {w: [] for w in WIN}
        for dd in D.values():
            n = len(dd["con"])
            lab = np.zeros(n, bool); lab[rng.choice(n, dd["nh"], replace=False)] = True
            a = {w: rng.normal(1, SD[w]) * (0.5 if plant == "half" else 1.0) if plant else 0.0 for w in WIN}
            pr_all = []
            for _ in range(NMATCH):
                pr = []
                for hemi in ("L", "R"):
                    hh = np.where(lab & (dd["side"] == hemi))[0]; mm = np.where(~lab & (dd["side"] == hemi))[0]
                    pr += [(hh[i], mm[j]) for i, j in VK.match(dd["con"][hh], dd["con"][mm], rng)]
                pr_all.append(pr)
            for w, sl in WIN.items():
                X = dd["X"][:, :, sl].copy()
                if plant:
                    X[lab] += a[w] * c * (pat_roi[w] if plant == "roi" else pat[w])
                s = dec[w].decision_function(zs(X.reshape(n, -1)))
                auc[w].append(np.mean([roc_auc_score(np.r_[np.ones(len(pr)), np.zeros(len(pr))],
                                                     np.r_[s[[i for i, _ in pr]], s[[j for _, j in pr]]]) for pr in pr_all if len(pr) > 5]))
        calls, P, LO = {}, {}, {}
        for w in WIN:
            x = np.array(auc[w]) - 0.5
            sf = rng.choice([-1, 1], (NPERM, len(x)))
            P[w] = float(((sf * x).mean(axis=1) >= x.mean()).mean())
            LO[w] = np.percentile(x[rng.integers(0, len(x), (NBOOT, len(x)))].mean(axis=1), 2.5)
            calls[w + "_auc"] = float(x.mean() + 0.5)
        order = sorted(WIN, key=lambda w: P[w])                      # Holm: smallest p at .05/2, next at .05
        ok = P[order[0]] < 0.025
        calls[order[0]] = ok and LO[order[0]] > 0
        calls[order[1]] = ok and P[order[1]] < 0.05 and LO[order[1]] > 0
        return calls

    pat_roi = {w: np.where(np.isin(np.arange(len(groups)), roi_g)[:, None], pat[w], 0.0) for w in WIN}
    # primary: the full Cohen pattern (best case for transfer). Sensitivity, reported, not gating: ROI-only, half size.
    for plant, key in (("full", "planted"), (None, "null"), ("roi", "planted_roi_only"), ("half", "planted_half")):
        res = [one_run(plant) for _ in range(nrun)]
        out[key] = {w: float(np.mean([r[w] for r in res])) for w in WIN}
        out[key].update({w + "_mean_auc": float(np.mean([r[w + "_auc"] for r in res])) for w in WIN})
        print(key, out[key], flush=True)
    out["PASS"] = bool(all(out["planted"][w] >= 0.80 for w in WIN) and all(out["null"][w] <= 0.05 for w in WIN))
    print("KILLTEST", "PASS" if out["PASS"] else "FAIL")
    json.dump(out, open(HERE / "out" / ("killtest_planted_smoke.json" if smoke else "killtest_planted.json"), "w"), indent=1)


if __name__ == "__main__":
    main(smoke=len(sys.argv) > 1 and sys.argv[1] == "smoke")
