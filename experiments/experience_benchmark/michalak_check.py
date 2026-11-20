"""Out-of-lab spectral check on Michalak et al. 2026 (amendment 3 §3, made mandatory and extended by amendment 5).

  python -I experiments/experience_benchmark/michalak_check.py <fulldatatable_10-Nov-2025_w90.mat>  -> michalak.json

Data: Zenodo 10.5281/zenodo.15372992 (CC BY 4.0), file fulldatatable_10-Nov-2025_w90.mat. Untrusted download:
kept outside the repo, read with scipy only (no MATLAB, no third-party .mat parsers).

Reader. The file holds struct `data` (1 x 256 channels) whose field `mytable` is a MATLAB `table` (MCOS object),
plus `chanlocs`. scipy leaves MCOS objects opaque, so the subsystem (`__function_workspace__`) is decoded here:
its FileWrapper__ cell array holds, per table, 13 cells in a fixed order: 3 categoricals (Subj, Study, Night;
categories + codes each), the table's 17 columns, row/col counts, row names, a scalar, the variable names and
a properties struct. Table k is object 4k+1 (read from the opaque references), so block k is channel k.
Checked before any label is used: every block has the expected variable names and 17 columns; Subj, Study,
Stage, Recall agree across all 256 blocks; and (label-free) the Delta of each ROI channel correlates more with
its nearest neighbour than with the farthest channel in the majority of ROI channels. If any check fails, stop.

Columns used: Subj + Study (subject key), Stage (2 = N2), Recall (2 = contentful experience, 0 = no
experience; 1 = experience without recall is left out), Delta and Gamma (log power, log(uV^2), per the
authors' code; their Ratio is Gamma - Delta).

ROI: for each of P3 P4 Pz P7 P8 PO3 PO4 POz PO7 PO8 O1 O2 Oz (mne standard_1020), the nearest of the 256
electrodes on the unit sphere (EEGLAB X,Y,Z -> MNE head frame (-Y, X, Z)); duplicates kept once.

Scores per awakening (mean over ROI channels):
  ratio = mean(Gamma - Delta)  (rank-equivalent to the sealed log10(gamma/delta) for any log base)  [primary, +]
  gamma = mean(Gamma) [+],   delta = mean(Delta) [-]
Statistics (N2, subjects with both classes, subject key (Study, Subj)):
  within-subject pair AUC (stats.PairAUC), oriented by the sign above;
  p: one-sided for ratio, two-sided for gamma and delta, 5,000 within-subject label permutations;
  95% CI: 5,000 subject bootstrap draws within Study.
  Pooled (between-subject, not centred) AUC: plain Mann-Whitney over all N2 CE vs NCE awakenings (all subjects
  with any N2 CE/NCE awakening), 95% CI from 5,000 subject bootstrap draws within Study. Descriptive.
Reading (amendment 5):
  NULL_SETTLED  every within-subject 95% CI (ratio, gamma, delta) lies inside [0.43, 0.57]
  LIVE          any within-subject AUC >= 0.60 with lower 95% bound > 0.50
  OTHER         anything else, reported as it falls
"""
import io
import json
import os
import sys

import numpy as np
import scipy.io as sio
from scipy.io.matlab._mio5 import MatFile5Reader
from scipy.stats import rankdata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stats as S  # noqa: E402

VARS = ['Subj', 'Study', 'Night', 'Time', 'TimeLo', 'Stage', 'Recall', 'AddSpec', 'Depth', 'Sleep', 'Vivid',
        'Perc', 'Bizar', 'Lucid', 'Arousal', 'Delta', 'Gamma']
ROI = ["P3", "P4", "Pz", "P7", "P8", "PO3", "PO4", "POz", "PO7", "PO8", "O1", "O2", "Oz"]
SIGN = {"ratio": 1, "gamma": 1, "delta": -1}
N_PERM = N_BOOT = 5000


def read_tables(path):
    m = sio.loadmat(path)
    fw = m["__function_workspace__"].ravel().tobytes()
    r = MatFile5Reader(io.BytesIO(b"MATLAB 5.0 MAT-file".ljust(116, b" ") + b"\x00" * 8 + fw[0:4] + fw[8:]))
    r.mat_stream.seek(128); r.initialize_read(); h, _ = r.read_var_header()
    cells = r.read_var_array(h, process=True)[0, 0]["MCOS"][0]["_ObjectMetadata"].ravel()
    nch = m["data"].shape[1]
    ids = [int(np.asarray(m["data"][0, i]["mytable"].ravel()[0][2]).ravel()[4]) for i in range(nch)]
    assert ids == [4 * k + 1 for k in range(nch)], "unexpected object ids"
    tabs = []
    for k in range(nch):
        b = cells[2 + 13 * k: 2 + 13 * (k + 1)]
        names = [str(np.squeeze(c)) for c in b[11].ravel()]
        assert names == VARS, f"block {k}: variable names {names}"
        cols = b[6].ravel()
        assert len(cols) == 17
        t = {}
        for j, (cat, code) in enumerate(((b[0], b[1]), (b[2], b[3]), (b[4], b[5]))):
            labels = np.array([str(np.squeeze(c)) for c in cat.ravel()] + ["<undef>"], object)
            cd = np.asarray(code).ravel().astype(int)          # 0 = undefined, else 1-based category
            t[VARS[j]] = labels[np.where(cd > 0, cd - 1, len(labels) - 1)]
        for j in range(3, 17):
            t[VARS[j]] = np.asarray(cols[j], float).ravel()
        tabs.append(t)
    return m, tabs


def unit(v):
    v = np.asarray(v, float); return v / np.linalg.norm(v, axis=-1, keepdims=True)


def roi_channels(m):
    import mne
    cl = m["chanlocs"][0]
    xyz = np.array([[float(np.squeeze(c["X"])), float(np.squeeze(c["Y"])), float(np.squeeze(c["Z"]))] for c in cl])
    pos = unit(np.c_[-xyz[:, 1], xyz[:, 0], xyz[:, 2]])
    ref = mne.channels.make_standard_montage("standard_1020").get_positions()["ch_pos"]
    roi = []
    for nm in ROI:
        k = int(np.argmax(pos @ unit(ref[nm])))
        if k not in roi:
            roi.append(k)
    return roi, pos


def pooled_auc(v, y):
    r = rankdata(v); n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def main(path):
    m, tabs = read_tables(path)
    for key in ("Subj", "Study", "Stage", "Recall"):
        for t in tabs[1:]:
            assert np.array_equal(np.asarray(t[key]), np.asarray(tabs[0][key]), equal_nan=key in ("Stage", "Recall")), key
    roi, pos = roi_channels(m)
    # label-free mapping check: nearest neighbour vs farthest channel, Delta across all awakenings
    D = np.array([t["Delta"] for t in tabs]); ok = np.isfinite(D).all(0)
    wins = 0
    for k in roi:
        d = pos @ pos[k]; d[k] = -9
        near, far = int(np.argmax(d)), int(np.argmin(np.where(np.arange(len(d)) == k, 9, d)))
        wins += np.corrcoef(D[k, ok], D[near, ok])[0, 1] > np.corrcoef(D[k, ok], D[far, ok])[0, 1]
    mapping_ok = wins > len(roi) / 2
    out = {"roi_channels": [str(np.squeeze(m["chanlocs"][0][k]["labels"])) for k in roi],
           "mapping_check": {"nearest_beats_farthest": int(wins), "of": len(roi), "pass": bool(mapping_ok)}}
    if not mapping_ok:
        json.dump(out, open(os.path.join(HERE, "michalak.json"), "w"), indent=1); sys.exit("mapping check failed")

    t0 = tabs[0]
    G = np.array([tabs[k]["Gamma"] for k in roi]).mean(0); Dl = np.array([tabs[k]["Delta"] for k in roi]).mean(0)
    score = {"ratio": np.array([tabs[k]["Gamma"] - tabs[k]["Delta"] for k in roi]).mean(0), "gamma": G, "delta": Dl}
    sel = (t0["Stage"] == 2) & np.isin(t0["Recall"], (0, 2)) & np.isfinite(G) & np.isfinite(Dl)
    y = (t0["Recall"][sel] == 2).astype(int)
    s = np.array([f"{a}|{b}" for a, b in zip(t0["Study"][sel], t0["Subj"][sel])], object)
    study = np.asarray(t0["Study"][sel], object)
    kb = S.keep_both(y, s)
    P = S.PairAUC(y[kb], s[kb], study[kb])
    rng = np.random.default_rng(20261120)
    Y = P.perm_labels(N_PERM, rng); draws = P.boot_draws(N_BOOT, rng)
    out["counts"] = {"n2_ce_nce": int(sel.sum()), "n_ce": int(y.sum()), "within_n": int(kb.sum()),
                     "within_subjects": int(len(P.subs)), "all_subjects": int(len(np.unique(s)))}
    # pooled bootstrap: subjects within study
    subs = np.unique(s); sub_study = np.array([study[s == u][0] for u in subs], object)
    groups = [np.flatnonzero(sub_study == g) for g in np.unique(sub_study)]
    rows = [np.flatnonzero(s == u) for u in subs]
    pdraws = [np.concatenate([rows[i] for g in groups for i in g[rng.integers(0, len(g), len(g))]]) for _ in range(N_BOOT)]
    res = {}
    for nm, sg in SIGN.items():
        v = sg * score[nm][sel]; vw = v[kb]
        a = P.auc(vw); pa = P.perm_aucs(vw, Y)
        p = (1 + (pa >= a).sum()) / (N_PERM + 1) if nm == "ratio" else (1 + (np.abs(pa - 0.5) >= abs(a - 0.5)).sum()) / (N_PERM + 1)
        lo, hi = P.boot_ci(vw, draws)
        pb = [pooled_auc(v[d], y[d]) for d in pdraws]
        res[nm] = {"sign": sg, "within_auc": a, "p": float(p), "sided": "one" if nm == "ratio" else "two",
                   "ci95": [lo, hi], "pooled_auc": float(pooled_auc(v, y)),
                   "pooled_ci95": [float(np.percentile(pb, 2.5)), float(np.percentile(pb, 97.5))]}
    out["scores"] = res
    if all(0.43 <= r["ci95"][0] and r["ci95"][1] <= 0.57 for r in res.values()):
        out["reading"] = "NULL_SETTLED"
    elif any(r["within_auc"] >= 0.60 and r["ci95"][0] > 0.50 for r in res.values()):
        out["reading"] = "LIVE"
    else:
        out["reading"] = "OTHER"
    json.dump(out, open(os.path.join(HERE, "michalak.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
