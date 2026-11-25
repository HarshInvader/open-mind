"""Item 2: stream Sergent et al. 2021's preprocessed active-session EEG one subject at a time and keep decoder outputs only.
Prereg: docs/prereg/2026-11-25_sergent_eeg_five_models.md. Runs only after the design gate's tier is known (prereg §3).

    python -I stream_decode.py plan            # file list from the OSF Dropbox listing; no data bytes
    python -I stream_decode.py run             # needs gate tier 1 or 2 at DMAX 0.89 (out_gate/summary.json, tag d0.89)
    python -I stream_decode.py run tier3-ok    # F6 only: tier 3 and the coordinator's OK (stream for R1 and puzzle tests)

Their single-trial signal, ported from SoundConsciousEEG_MNE_GAT_SingleTrials.py (diagonal section; read, never run):
  - data_ref.trial, first 63 channels (their coi = range(63)), every sample at 500 Hz, no decimation;
  - per sample: StandardScaler + LogisticRegression() trained on snr 1 (no sound) vs 6 (-5 dB); decision_function;
  - StratifiedKFold(10, no shuffle) on the training trials; snr 2-5 trials split by the same splitter on a dummy label
    (contiguous chunks), chunk f scored by fold f's decoder.
  - Solver: their LogisticRegression() default depends on their sklearn version (unknown; < 1.0 since they pass
    random_state without shuffle). PRIMARY = liblinear (default before 0.22); lbfgs (default from 0.22) is decoded too
    and reported descriptively for R1 only (prereg §2).
Then (their ...ModelFitting_Twind30ms_batch.m): 12th-order Butterworth low-pass, half power 10 Hz, zero phase; 53 windows
of 30 ms, window j (1-based) = mean over samples with t in [-330 + 30j, -300 + 30j] ms, both ends inclusive (= their
TWOI = 101:15:901 on the standard -500 ms axis; placed by time so a different t0 is handled, F2).

Kept per subject (npz): diag / diag_lbfgs (trials x samples, float32), win / win_lbfgs (trials x 53), fold (decoder fold
per trial), trialinfo (block, snr, vowel, eval, respside, audibility), time. The .mat is deleted right after loading.
Every subject ends as an "ok" or a "skip" record in stream_log.jsonl; both are final (F1).
Downloaded data are untrusted: parsed with scipy.io.loadmat under python -I, never executed.
"""
import json, shutil, sys, time, urllib.error, urllib.request
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREREG = ROOT / "docs" / "prereg" / "2026-11-25_sergent_eeg_five_models.md"
LISTING = HERE / "dropbox_listing.json"
SCRATCH = ROOT / "datasets" / "local" / "sergent2021_stream"      # raw .mat lives here only while one subject loads
OUT = ROOT / "datasets" / "local" / "sergent2021_decoded"
LOG = OUT / "stream_log.jsonl"
UA = {"User-Agent": "open-research-site/1.0"}
MIN_FREE = 10 * 1024 ** 3
FILE_MAX = 1_500_000_000                                         # refuse a file larger than this
NCH, FS, LOWPASS, PADLEN = 63, 500, 10.0, 36                     # padlen 3*order, as MATLAB filtfilt
N_SUB, N_WIN = 20, 53
SOLVERS = ("liblinear", "lbfgs")                                 # first = primary


class Skip(Exception):
    pass


def plan():
    L = json.loads(LISTING.read_text())
    files = {}
    for f in L:
        name = f["path"].rsplit("/", 1)[-1]
        if f["path"].startswith("/Bifurcation_OSF_PreprocessedData/") and name.endswith("_Active_data_ref.mat"):
            files[int(name.split("_")[0][1:])] = f["dl"]
    assert sorted(files) == list(range(1, N_SUB + 1)), sorted(files)
    return files


def download(url, dst):
    """Chunked download with Range resume within one subject; 5 attempts, then Skip (F1)."""
    for attempt in range(5):
        try:
            have = dst.stat().st_size if dst.exists() else 0
            h = dict(UA, Range=f"bytes={have}-") if have else dict(UA)
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=300) as r:
                total = int(r.headers["Content-Range"].split("/")[1]) if r.status == 206 else int(r.headers["Content-Length"])
                if total > FILE_MAX:
                    raise Skip(f"file too large: {total}")
                if r.status == 200 and have:
                    have = 0
                with open(dst, "ab" if have else "wb") as f:
                    while True:
                        b = r.read(1 << 22)
                        if not b:
                            break
                        f.write(b)
            if dst.stat().st_size == total:
                return total
        except Skip:
            raise
        except Exception as e:
            print("retry", attempt, type(e).__name__, flush=True)
            time.sleep(2 ** attempt)
    raise Skip("download failed after 5 attempts")


def load(path):
    try:
        return _load(path)
    except Skip:
        raise
    except Exception as e:                            # corrupt / v7.3 / missing data_ref / ragged trials -> F1 skip
        raise Skip(f"load failed: {type(e).__name__}: {str(e)[:120]}")


def _load(path):
    import scipy.io as sio
    m = sio.loadmat(str(path), squeeze_me=True, struct_as_record=False)
    ft = m["data_ref"]
    if float(ft.fsample) != FS:
        raise Skip(f"fsample {ft.fsample}")
    trials = list(ft.trial)
    if min(np.asarray(t).shape[0] for t in trials) < NCH:
        raise Skip("fewer than 63 channels")
    X = np.stack([np.asarray(t, dtype=np.float64)[:NCH] for t in trials])     # trials x 63 x samples
    t0 = np.asarray(ft.time[0] if np.ndim(ft.time[0]) else ft.time, dtype=float).ravel()
    info = np.atleast_2d(np.asarray(ft.trialinfo, dtype=float))
    if info.shape[1] < 2 or len(info) != len(X) or len(t0) != X.shape[2]:
        raise Skip(f"shapes: info {info.shape}, X {X.shape}, time {t0.shape}")
    return X, t0, info


def decode(X, snr, solver):
    """Diagonal single-trial decision values, their CV scheme. Returns (values, fold id per trial)."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    n, _, T = X.shape
    train_cond = np.where((snr == 1) | (snr == 6))[0]
    gen_cond = np.where((snr > 1) & (snr < 6))[0]
    cv = StratifiedKFold(n_splits=10)
    tr_te = [(train_cond[a], train_cond[b]) for a, b in cv.split(np.zeros(len(train_cond)), snr[train_cond])]
    gens = [gen_cond[b] for _, b in cv.split(np.zeros(len(gen_cond)), np.ones(len(gen_cond)))]
    y = np.full((n, T), np.nan)
    fold = np.full(n, -1)
    for f, ((tr, te), ge) in enumerate(zip(tr_te, gens)):
        assert set(snr[tr]) == {1, 6}
        idx = np.r_[te, ge]
        fold[idx] = f
        for t in range(T):
            clf = make_pipeline(StandardScaler(), LogisticRegression(solver=solver))
            clf.fit(X[tr, :, t], snr[tr])
            y[idx, t] = clf.decision_function(X[idx, :, t])
    return y, fold


def windows(diag, t):
    """53 window means of the 10 Hz low-passed diagonal, placed by time (ms, both ends inclusive)."""
    from scipy.signal import butter, sosfiltfilt
    sos = butter(12, LOWPASS / (FS / 2), output="sos")
    f = sosfiltfilt(sos, diag, axis=1, padlen=PADLEN)
    tm = np.round(t * 1000, 3)
    out = np.full((len(diag), N_WIN), np.nan)
    for j in range(1, N_WIN + 1):
        m = (tm >= -330 + 30 * j) & (tm <= -300 + 30 * j)
        if m.sum() == 16:
            out[:, j - 1] = f[:, m].mean(axis=1)
    return out


def done_subjects():
    if not LOG.exists():
        return set()
    return {json.loads(l)["sub"] for l in LOG.read_text().splitlines() if l.strip()}


def tier_guard(arg):
    S = json.loads((HERE / "out_gate" / "summary.json").read_text())
    tier = S.get("d0.89", {}).get("TIER")
    if tier in (1, 2):
        return tier
    if tier == 3 and arg == "tier3-ok":
        return tier
    raise SystemExit(f"gate tier at DMAX 0.89 is {tier}: streaming not allowed (prereg §3)")


def run(arg=None):
    sys.path.insert(0, str(HERE.parents[0] / "rules"))
    from evidence import require_sealed
    require_sealed(str(PREREG)); require_sealed(str(Path(__file__)))
    tier = tier_guard(arg)
    files = plan()
    SCRATCH.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    total, done = 0, done_subjects()
    for s, url in files.items():
        if s in done:
            continue
        if shutil.disk_usage(ROOT).free - FILE_MAX - 1_000_000_000 < MIN_FREE:
            raise SystemExit(f"disk guard before S{s} (F9): stop; rerun later resumes here")
        raw = SCRATCH / f"S{s}.mat"
        raw.unlink(missing_ok=True)                                   # never trust a leftover partial file
        t = time.time()
        rec = dict(sub=s, gate_tier=tier)
        try:
            nb = download(url, raw)
            total += nb
            X, t0, info = load(raw)
            raw.unlink()                                              # raw bytes gone before any compute
            block, snr = info[:, 0].astype(int), info[:, 1].astype(int)
            if not set(np.unique(snr)) <= set(range(1, 7)) or not set(np.unique(block)) <= set(range(1, 21)):
                raise Skip(f"coding: snr {np.unique(snr).tolist()}, block {np.unique(block).tolist()}")   # F3
            if np.bincount(snr - 1, minlength=6).min() < 60:
                raise Skip(f"level counts {np.bincount(snr - 1, minlength=6).tolist()}")                # F3
            keep = dict(trialinfo=info, time=t0)
            for i, solver in enumerate(SOLVERS):
                diag, fold = decode(X, snr, solver)
                suf = "" if i == 0 else "_" + solver
                keep["diag" + suf] = diag.astype(np.float32)
                keep["win" + suf] = windows(diag, t0).astype(np.float32)
                keep["fold"] = fold
            tmp = OUT / f"S{s}.tmp.npz"
            np.savez_compressed(tmp, **keep)
            tmp.replace(OUT / f"S{s}.npz")
            rec.update(status="ok", bytes=nb, trials=int(len(X)), samples=int(X.shape[2]), t_first_ms=float(t0[0] * 1000),
                       windows_ok=int(np.isfinite(keep["win"][0]).sum()), seconds=round(time.time() - t))
        except Skip as e:
            raw.unlink(missing_ok=True)
            rec.update(status="skip", reason=str(e), seconds=round(time.time() - t))
        with open(LOG, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"S{s}: {rec}; total {total / 1e9:.2f} GB", flush=True)
    print("done")


if __name__ == "__main__":
    if sys.argv[1] == "plan":
        print(len(plan()), "files")
    else:
        run(sys.argv[2] if len(sys.argv) > 2 else None)
