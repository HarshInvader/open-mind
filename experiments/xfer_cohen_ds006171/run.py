"""Round 20 #1 real run: Cohen masked-face seen/unseen decoder applied zero-shot to ds006171 seen/unseen (prereg: DESIGN.md).

    python -I run.py check    # before sealing: joins each kept trial to its events.tsv stimulus row (code + onset
                              # vs trigger/fs) and prints counts; reads NO answer (124/125)
    python -I run.py run      # sealed only: -> out/result.json (gitignored; Cohen hold until 2026-12-08)

Everything follows DESIGN.md §5 (as amended in §9). Seeds fixed. Writes only to out/.
"""
import csv, hashlib, json, sys
from pathlib import Path

import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "datasets" / "local" / "r19_ds006171" / "files"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "experiments" / "ds006171_van"))
import killtest_montage as KM
import importlib.util

_sp = importlib.util.spec_from_file_location("van_kt", ROOT / "experiments" / "ds006171_van" / "killtest.py")
VK = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(VK)          # match(): 1:1, caliper 0.01

WIN = {"early": slice(3, 6), "late": slice(6, 12)}                 # 150-300, 300-600 ms
POST_Y = -0.25                                                    # posterior groups: mean site y (front axis) < this
NMATCH, MIN_PAIRS, MIN_SUBJ = 200, 20, 24
NPERM, NBOOT, SEED = 10000, 10000, 20261130
NO_TRANSFER_HI = 0.53
FILES_SEALED = ["experiments/xfer_cohen_ds006171/DESIGN.md", "experiments/xfer_cohen_ds006171/run.py",
                "experiments/xfer_cohen_ds006171/killtest_montage.py", "experiments/ds006171_van/killtest.py",
                "experiments/xfer_cohen_ds006171/prep_full.py", "experiments/xfer_cohen_ds006171/cohen_feat.py"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def zs_fit(X):
    return X.mean(axis=0), X.std(axis=0) + 1e-9


def stim_rows(sub):
    rows = list(csv.DictReader(open(RAW / sub / "eeg" / f"{sub}_task-nocue_events.tsv"), delimiter="\t"))
    return rows


def bdf_fs(sub):
    import mne
    mne.set_log_level("ERROR")
    return float(mne.io.read_raw_bdf(RAW / sub / "eeg" / f"{sub}_task-nocue_eeg.bdf", preload=False).info["sfreq"])


def join(sub, trig, code, read_answers):
    """Index of each trial's stimulus row (same code, |onset - trig/fs| < 5 ms, as prep.py's contrast join; the
    events.tsv `sample` column is not used: it has unparseable entries in every file); answers only if read_answers."""
    rows = stim_rows(sub)
    fs = bdf_fs(sub)
    stim = [(i, int(r["trial_type"]), float(r["onset"])) for i, r in enumerate(rows) if int(r["trial_type"]) in (11, 12, 21, 22, 31, 32)]
    idx = []
    for t, c in zip(trig, code):
        hit = [i for i, k, o in stim if k == c and abs(o - t / fs) < 0.005]
        idx.append(hit[0] if len(hit) == 1 else -1)
    if not read_answers:
        return np.array(idx), None
    ans = []
    for i in idx:
        a = -1
        if i >= 0:
            for r in rows[i + 1:]:
                k = int(r["trial_type"])
                if k in (11, 12, 21, 22, 31, 32):
                    break
                if k in (124, 125):
                    a = 1 if k == 124 else 0
                    break
        ans.append(a)
    return np.array(idx), np.array(ans)


def load_ds(groups, read_answers):
    D, excl = {}, {}
    for f in sorted((HERE / "out" / "feat").glob("sub-*.npz")):
        d = np.load(f)
        code = d["code"]; gab = np.isin(code, KM.GAB); cat = np.isin(code, KM.CATCH)
        if d["rej_veog"][gab].mean() > KM.REJ_MAX:
            excl[f.stem] = f"VEOG rejection {d['rej_veog'][gab].mean():.2f} > {KM.REJ_MAX}"
            continue
        idx, ans = join(f.stem, d["trig"], code, read_answers)
        D[f.stem] = dict(X=KM.symmetrise(d["mapped"], groups), code=code, gab=gab & d["keep"], cat=cat & d["keep"],
                         side=d["side"], con=d["contrast"], veog=d["veog_pp"], idx=idx, ans=ans)
    return D, excl


def cohen_decoders(groups, sel):
    cz = np.load(HERE / "out" / "cohen_feat.npz")
    subs = sorted({k.split("|")[0] for k in cz.files})
    dec = {}
    for w, sl in WIN.items():
        Xs, ys = [], []
        for s in subs:
            X = KM.symmetrise(cz[f"{s}|X"], groups)[:, sel, sl].reshape(len(cz[f"{s}|y"]), -1)
            m, sd = zs_fit(X); Xs.append((X - m) / sd); ys.append(cz[f"{s}|y"])
        dec[w] = LDA(solver="lsqr", shrinkage="auto").fit(np.vstack(Xs), np.concatenate(ys))
    return dec


def scores(dec, dd, sel, w):
    """Decoder output for every trial; z-scored with the subject's kept Gabor trials (transductive, label-free)."""
    X = dd["X"][:, sel, WIN[w]].reshape(len(dd["code"]), -1)
    m, sd = zs_fit(X[dd["gab"]])
    return dec[w].decision_function((X - m) / sd)


def auc_pairs(s, pairs):
    return float(roc_auc_score(np.r_[np.ones(len(pairs)), np.zeros(len(pairs))],
                               np.r_[s[[i for i, _ in pairs]], s[[j for _, j in pairs]]]))


def group(x, rng):
    x = np.asarray(x) - 0.5
    sf = rng.choice([-1, 1], (NPERM, len(x)))
    k = int(((sf * x).mean(axis=1) >= x.mean()).sum())
    ci = np.percentile(x[rng.integers(0, len(x), (NBOOT, len(x)))].mean(axis=1), [2.5, 97.5]) + 0.5
    return dict(mean=float(x.mean() + 0.5), p=(1 + k) / (1 + NPERM), ci95=[float(ci[0]), float(ci[1])])


def check():
    mz = np.load(KM.MONT)
    groups = KM.sym_pairs(mz["cohen_pos"][mz["covered"]])
    D, excl = load_ds(groups, read_answers=False)
    cpos = mz["cohen_pos"][mz["covered"]]
    post = [i for i, g in enumerate(groups) if cpos[g, 1].mean() < POST_Y]
    print(f"eligible by VEOG: {len(D)}; excluded {excl}")
    print(f"posterior groups ({len(post)}): {post}; Cohen channels {[mz['cohen_ch'][mz['covered']][g].tolist() for g in [groups[i] for i in post]]}")
    tot = dict(g=0, c=0)
    for s, dd in D.items():
        ug = dd["gab"] & (dd["idx"] < 0); uc = dd["cat"] & (dd["idx"] < 0)
        print(f"{s}: kept Gabor {int(dd['gab'].sum())}, kept catch {int(dd['cat'].sum())}, unjoined Gabor {int(ug.sum())}, "
              f"unjoined catch {int(uc.sum())}")
        # an unjoined Gabor trial must already lack contrast (same 5 ms rule as prep.py), so matching never used it
        assert not np.isfinite(dd["con"][ug]).any(), s
        tot["g"] += int(ug.sum()); tot["c"] += int(uc.sum())
    print("total unjoined kept trials: Gabor", tot["g"], "catch", tot["c"])


def run():
    sys.path.insert(0, str(ROOT / "experiments" / "rules"))
    from evidence import require_sealed
    for f in FILES_SEALED:
        require_sealed(str(ROOT / f))
    rng = np.random.default_rng(SEED)
    mz = np.load(KM.MONT)
    cpos = mz["cohen_pos"][mz["covered"]]
    groups = KM.sym_pairs(cpos)
    ALL = list(range(len(groups)))
    POST = [i for i, g in enumerate(groups) if cpos[g, 1].mean() < POST_Y]
    D, excl = load_ds(groups, read_answers=True)
    dec = {"full": cohen_decoders(groups, ALL), "post": cohen_decoders(groups, POST)}
    # matchings (shared by all windows and variants), eligibility
    M, elig = {}, {}
    for s, dd in D.items():
        g = dd["gab"] & np.isfinite(dd["con"]) & (dd["ans"] >= 0)
        ms = []
        for _ in range(NMATCH):
            pr = {}
            for hemi in ("L", "R"):
                hh = np.where(g & (dd["ans"] == 1) & (dd["side"] == hemi))[0]
                mm = np.where(g & (dd["ans"] == 0) & (dd["side"] == hemi))[0]
                pr[hemi] = [(hh[i], mm[j]) for i, j in VK.match(dd["con"][hh], dd["con"][mm], rng)]
            ms.append(pr)
        npairs = float(np.median([len(p["L"]) + len(p["R"]) for p in ms]))
        if npairs < MIN_PAIRS:
            excl[s] = f"median matched pairs {npairs} < {MIN_PAIRS}"
            continue
        M[s], elig[s] = ms, npairs
    out = dict(sha={f: sha(ROOT / f) for f in FILES_SEALED}, data_sha={k: sha(HERE / "out" / k) for k in ("cohen_feat.npz", "montage.npz")},
               n_eligible=len(M), excluded=excl, median_pairs=elig, posterior_groups=POST)
    if len(M) < MIN_SUBJ:
        out["verdict"] = "INCONCLUSIVE"; out["reason"] = f"fewer than {MIN_SUBJ} eligible"
        json.dump(out, open(HERE / "out" / "result.json", "w"), indent=1); print(out["verdict"]); return
    # present-vs-catch LOSO decoders per window (rival F residual)
    def pc_scores(s, w):
        tr = [t for t in M if t != s]
        Xs, ys = [], []
        for t in tr:
            dd = D[t]; X = dd["X"][:, :, WIN[w]].reshape(len(dd["code"]), -1)
            m, sd = zs_fit(X[dd["gab"]]); k = dd["gab"] | dd["cat"]
            Xs.append(((X - m) / sd)[k]); ys.append(dd["gab"][k].astype(int))
        clf = LDA(solver="lsqr", shrinkage="auto").fit(np.vstack(Xs), np.concatenate(ys))
        dd = D[s]; X = dd["X"][:, :, WIN[w]].reshape(len(dd["code"]), -1); m, sd = zs_fit(X[dd["gab"]])
        return clf.decision_function((X - m) / sd)

    per = {w: {k: [] for k in ("auc", "post", "resid", "hemiL", "hemiR", "unseen_vs_cr", "dlnc", "veog")} for w in WIN}
    for s in M:
        dd = D[s]
        for w in WIN:
            sc, sp = scores(dec["full"], dd, ALL, w), scores(dec["post"], dd, POST, w)
            q = pc_scores(s, w)
            gi = np.where(dd["gab"])[0]
            A = np.c_[np.ones(len(gi)), q[gi]]
            res = np.full(len(sc), np.nan); res[gi] = sc[gi] - A @ np.linalg.lstsq(A, sc[gi], rcond=None)[0]
            P = per[w]
            P["auc"].append(np.mean([auc_pairs(sc, p["L"] + p["R"]) for p in M[s]]))
            P["post"].append(np.mean([auc_pairs(sp, p["L"] + p["R"]) for p in M[s]]))
            P["resid"].append(np.mean([auc_pairs(res, p["L"] + p["R"]) for p in M[s]]))
            P["hemiL"].append(np.mean([auc_pairs(sc, p["L"]) for p in M[s] if len(p["L"]) > 5]))
            P["hemiR"].append(np.mean([auc_pairs(sc, p["R"]) for p in M[s] if len(p["R"]) > 5]))
            un = dd["gab"] & (dd["ans"] == 0); cr = dd["cat"] & (dd["ans"] == 0)
            P["unseen_vs_cr"].append(float(roc_auc_score(np.r_[np.ones(un.sum()), np.zeros(cr.sum())], np.r_[sc[un], sc[cr]]))
                                     if cr.sum() >= 5 else np.nan)
            P["dlnc"].append(np.mean([np.mean([np.log(dd["con"][i]) - np.log(dd["con"][j]) for i, j in p["L"] + p["R"]]) for p in M[s]]))
            k = dd["gab"] & (dd["ans"] >= 0)
            P["veog"].append(float(roc_auc_score(dd["ans"][k], dd["veog"][k])))
    res = {}
    for w in WIN:
        P = per[w]
        res[w] = dict(primary=group(P["auc"], rng), posterior=group(P["post"], rng), residual_F=group(P["resid"], rng),
                      hemi_L=group(P["hemiL"], rng), hemi_R=group(P["hemiR"], rng),
                      unseen_vs_cr=group([x for x in P["unseen_vs_cr"] if np.isfinite(x)], rng),
                      veog_seen_vs_unseen=group(P["veog"], rng), mean_matched_dlnc=float(np.mean(P["dlnc"])),
                      per_subject_auc=dict(zip(M, map(float, P["auc"]))))
    # Holm over the two primary tests
    order = sorted(WIN, key=lambda w: res[w]["primary"]["p"])
    ok0 = res[order[0]]["primary"]["p"] < 0.025 and res[order[0]]["primary"]["ci95"][0] > 0.5
    ok1 = ok0 and res[order[1]]["primary"]["p"] < 0.05 and res[order[1]]["primary"]["ci95"][0] > 0.5
    passed = {order[0]: ok0, order[1]: ok1}
    if passed["early"] and passed["late"]:
        verdict = "EARLY TRANSFER"
    elif passed["early"]:
        verdict = "EARLY ONLY"
    elif passed["late"]:
        verdict = "LATE ONLY"
    elif all(res[w]["primary"]["ci95"][1] < NO_TRANSFER_HI for w in WIN):
        verdict = "NO TRANSFER"
    else:
        verdict = "INCONCLUSIVE"
    tags = {}
    for w in WIN:
        if passed[w]:
            t = []
            if res[w]["residual_F"]["p"] >= 0.05:
                t.append("F not excluded")
            if res[w]["posterior"]["p"] >= 0.05:
                t.append("ocular not excluded")
            if not (res[w]["hemi_L"]["mean"] > 0.5 and res[w]["hemi_R"]["mean"] > 0.5):
                t.append("hemifield")
            tags[w] = t
    out.update(windows=res, passed=passed, verdict=verdict, tags=tags,
               reading=("A null in the early window, or LATE ONLY, is uninformative about rival A (early power 0.815 at "
                        "full-pattern size, 0.30 if ROI-local). NO TRANSFER excludes only transfer of about full-pattern "
                        "size; an ROI-local effect in either window is not excluded. F cannot be fully separated from A."))
    json.dump(out, open(HERE / "out" / "result.json", "w"), indent=1)
    print(verdict, tags, {w: res[w]["primary"] for w in WIN})


if __name__ == "__main__":
    {"check": check, "run": run}[sys.argv[1]]()
