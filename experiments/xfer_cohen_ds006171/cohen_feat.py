"""Round 20 #1: Cohen 2024 training features (SOA-50 report-face epochs on disk). DRAFT, not sealed.

    python -I cohen_feat.py      # -> out/cohen_feat.npz

Labels (resp 1 seen, 2 unseen) were already read in the sealed VAN study; they are the training labels here.
Per epoch (study4.py's label-free rules): 4th-order Butterworth 30 Hz low-pass, zero phase (padlen 100); rejection
HEOG (62-63) p-p > 50 uV, VEOG (61 - 50) p-p > 150 uV, any covered scalp channel p-p > 150 uV. Then the 55 Cohen
sites covered by the ds006171 cap (out/montage.npz), average reference over them, baseline -100..0 ms, and the
same 12 bins of 50 ms over 0-600 ms as prep_full.py.
"""
from pathlib import Path

import numpy as np
from scipy.signal import butter, filtfilt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EP = ROOT / "datasets" / "local" / "cohen2024_epochs"
FS, TMIN = 500, -0.1
VEOG, HEOGL, HEOGR, FP1 = 61, 62, 63, 50
HEOG_PP, VEOG_PP, SCALP_PP = 50.0, 150.0, 150.0
BINS = [(i * 0.05, (i + 1) * 0.05) for i in range(12)]


def main():
    mz = np.load(HERE / "out" / "montage.npz")
    cov = mz["cohen_ch"][mz["covered"]]
    t = TMIN + np.arange(350) / FS
    bins = [(t >= a - 1e-9) & (t < b - 1e-9) for a, b in BINS]
    bb, aa = butter(4, 30 / (FS / 2))
    out, rows = {}, []
    for f in sorted(EP.glob("*.npz")):
        z = np.load(f)
        assert int(z["fs"]) == FS and float(z["tmin"]) == TMIN
        x = filtfilt(bb, aa, z["X"].astype(np.float64) * float(z["scale_uv"]), axis=2, padlen=100)
        ch = lambda c: x[:, c - 1, :]
        heog, veog = ch(HEOGL) - ch(HEOGR), ch(VEOG) - ch(FP1)
        sc = x[:, [c - 1 for c in cov], :]
        sc = sc - sc.mean(axis=1, keepdims=True)
        sc = sc - sc[:, :, t < 0].mean(axis=2, keepdims=True)
        keep = (np.ptp(heog, axis=1) <= HEOG_PP) & (np.ptp(veog, axis=1) <= VEOG_PP) & (np.ptp(sc, axis=2).max(axis=1) <= SCALP_PP)
        F = np.stack([sc[:, :, b].mean(axis=2) for b in bins], axis=2).astype(np.float32)
        out[f"{f.stem}|X"], out[f"{f.stem}|y"] = F[keep], (z["resp"][keep] == 1).astype(int)
        rows.append((f.stem, len(keep), int(keep.sum()), int((z["resp"][keep] == 1).sum())))
    np.savez_compressed(HERE / "out" / "cohen_feat.npz", **out)
    k = np.array([r[2] for r in rows]); s = np.array([r[3] for r in rows])
    print(f"{len(rows)} subjects; kept median {np.median(k):.0f} of {np.median([r[1] for r in rows]):.0f}; "
          f"seen median {np.median(s):.0f}, unseen median {np.median(k - s):.0f}")


if __name__ == "__main__":
    main()
