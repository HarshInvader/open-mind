"""Round 20 #1: label-blind full-channel features for ds006171 (no-cue) and the fixed montage map onto Cohen's cap.
DRAFT, not sealed. Reads stimulus codes 11-32 and photodiode 128 only (never 124/125).

    python -I prep_full.py positions        # -> out/montage.npz (Cohen positioned channels, ds006171 128, map matrix)
    python -I prep_full.py SUB [SUB ...]    # -> out/feat/<sub>.npz
    python -I prep_full.py all

Per trial (stored with its stimulus-trigger sample `trig`, for joining answers after sealing, and VEOG p-p / HEOG
step values for the ocular checks): mean voltage in 12 bins of 50 ms over 0-600 ms after the photodiode, for the native 128 EEG channels
(average reference) and for the 60 Cohen positions (spherical-spline map of the 128, then average reference).
Same photodiode rule, filter, epoching and trial rejection as ../ds006171_van/prep.py (ROI p-p 150 uV, VEOG 80 uV;
the HEOG step flag is stored but the primary features are hemisphere-symmetrised, so it is not applied here).

Coordinate frames (checked 2026-11-26):
- ds006171 electrodes.tsv: x toward the nose (Fpz +x), y toward the left ear (T7 +y), z up; idealised sphere r 88.
- Coverage: 4 low-temporal Cohen sites (Ch 51, 52, 59, 60; z = -0.39) are 21-22 deg from the nearest ds006171
  electrode, below its cap. On a smooth test field the map's error there is large, so they are dropped (55 kept;
  median error < 1% of the field range, max about 16%). Rule: nearest electrode > 15 deg -> dropped.
- Cohen .vhdr [Coordinates] (BrainVision r, theta, phi; MNE's convention): x = sin(th)cos(ph) toward the right,
  y = sin(th)sin(ph) toward the front, z = cos(th). Ch61-63 have r = 0 (no position): left out.
Both are converted to unit vectors with x right, y front, z up.
"""
import csv, re, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "datasets" / "local" / "r19_ds006171" / "files"
VHDR = ROOT / "datasets" / "local" / "cohen2024"
OUT = HERE / "out"
sys.path.insert(0, str(ROOT / "experiments" / "ds006171_van"))
import prep as P                                                  # constants and step(); its prep() is not called

MAX_DEG = 15.0                                                # a Cohen site farther than this from every ds006171 electrode is extrapolated: dropped
BINS = [(i * 0.05, (i + 1) * 0.05) for i in range(12)]


def cohen_positions(f):
    txt = open(f, encoding="latin-1").read().split("[Coordinates]")[1]
    pos = {}
    for k, r, th, ph in re.findall(r"^Ch(\d+)=([-\d.]+),([-\d.]+),([-\d.]+)", txt, re.M):
        if float(r) == 0:
            continue
        t, p = np.deg2rad(float(th)), np.deg2rad(float(ph))
        pos[int(k)] = np.array([np.sin(t) * np.cos(p), np.sin(t) * np.sin(p), np.cos(t)])
    return pos


def ds_positions(sub, names):
    rows = {r["name"]: r for r in csv.DictReader(open(RAW / sub / "eeg" / f"{sub}_electrodes.tsv"), delimiter="\t")}
    xyz = np.array([[float(rows[n]["x"]), float(rows[n]["y"]), float(rows[n]["z"])] for n in names])
    ras = np.c_[-xyz[:, 1], xyz[:, 0], xyz[:, 2]]               # right = -left, front = nose, up
    return ras / np.linalg.norm(ras, axis=1, keepdims=True)


def positions():
    from mne.channels.interpolation import _make_interpolation_matrix
    files = sorted(VHDR.glob("delcul*.vhdr"))
    ref = cohen_positions(files[0])
    for f in files[1:]:
        p = cohen_positions(f)
        assert p.keys() == ref.keys() and all(np.allclose(p[k], ref[k]) for k in ref), f"cap differs: {f.name}"
    ck = sorted(ref)
    cpos = np.array([ref[k] for k in ck])
    names = [r["name"] for r in csv.DictReader(open(RAW / "sub-01" / "eeg" / "sub-01_task-nocue_channels.tsv"),
                                               delimiter="\t")][:128]
    dpos = ds_positions("sub-01", names)
    for s in sorted(p.name for p in RAW.glob("sub-*")):
        assert np.allclose(ds_positions(s, names), dpos), f"ds006171 positions differ: {s}"
    M = _make_interpolation_matrix(dpos, cpos)                   # (60, 128) spherical spline
    # checks: each Cohen channel's nearest ds006171 electrode, and the map reproduces a smooth field
    near = np.degrees(np.arccos(np.clip(cpos @ dpos.T, -1, 1))).min(axis=1)
    field = dpos[:, 1] + 0.5 * dpos[:, 2]                         # a smooth test field
    err = np.abs(M @ field - (cpos[:, 1] + 0.5 * cpos[:, 2])).max()
    OUT.mkdir(exist_ok=True)
    covered = near <= MAX_DEG                                     # Cohen sites the ds006171 cap covers; used for features
    np.savez(OUT / "montage.npz", cohen_ch=np.array(ck), cohen_pos=cpos, ds_names=np.array(names), ds_pos=dpos, M=M,
             covered=covered, nearest_deg=near)
    print(f"covered (nearest <= {MAX_DEG} deg): {int(covered.sum())}; dropped Cohen Ch {np.array(ck)[~covered].tolist()}")
    print(f"Cohen {len(ck)} positioned channels (same in {len(files)} headers); ds006171 128 (same in all subjects)")
    print(f"nearest-electrode distance: median {np.median(near):.1f} deg, max {near.max():.1f}; smooth-field max error {err:.3f}")


def features(sub):
    import mne
    mne.set_log_level("ERROR")
    mz = np.load(OUT / "montage.npz")
    M = mz["M"]
    eeg = RAW / sub / "eeg"
    raw = mne.io.read_raw_bdf(eeg / f"{sub}_task-nocue_eeg.bdf", preload=False)
    names = [r["name"] for r in csv.DictReader(open(eeg / f"{sub}_task-nocue_channels.tsv"), delimiter="\t")]
    if len(raw.ch_names) == 272:
        unused = [c for c in raw.ch_names if c[0] in "EFGH" and c[1:].isdigit()]
        seg = raw.get_data(picks=unused, start=0, stop=int(10 * raw.info["sfreq"]))
        assert float(seg.std(axis=1).max()) * 1e6 < 1.0
        raw.drop_channels(unused)
    assert len(names) == len(raw.ch_names)
    ev = mne.find_events(raw, stim_channel="Status", shortest_event=1, initial_event=True)
    raw.rename_channels(dict(zip(raw.ch_names, names)))
    ev[:, 2] &= 0xFF
    fs = raw.info["sfreq"]
    pd = ev[ev[:, 2] == P.PD, 0]
    trials = []
    for s, _, code in ev:
        if code in P.STIM:
            nxt = pd[(pd > s) & (pd <= s + P.PD_MAX * fs)]
            trials.append((s, code, int(nxt[0]) if len(nxt) else -1))
    tsv = P.events_tsv(sub)
    con = []
    for s, code, _ in trials:
        hit = [c for (o, k, c) in tsv if k == code and abs(o - s / fs) < 0.005]
        con.append(hit[0] if len(hit) == 1 else np.nan)
    eeg_names = names[:128]
    assert list(eeg_names) == list(mz["ds_names"]), sub
    raw.pick(eeg_names + ["VEOG1", "VEOG2", "HEOG1", "HEOG2"]).load_data()
    raw.set_channel_types({c: "eog" for c in ("VEOG1", "VEOG2", "HEOG1", "HEOG2")})
    pos = dict(zip(eeg_names, mz["ds_pos"] * 0.088))
    raw.set_montage(mne.channels.make_dig_montage(ch_pos=pos, coord_frame="head"), on_missing="ignore")
    raw.filter(P.L_FREQ, P.H_FREQ, picks=["eeg", "eog"], method="fir", phase="zero", n_jobs=1)
    x = raw.get_data(picks="eeg") * 1e6
    nwin = x.shape[1] // int(fs)
    pp = np.median(np.ptp(x[:, :nwin * int(fs)].reshape(x.shape[0], nwin, int(fs)), axis=2), axis=1)
    bad = [eeg_names[i] for i in np.where(pp > P.BAD_CH * np.median(pp))[0]]
    raw.info["bads"] = bad
    if bad:
        raw.interpolate_bads(reset_bads=True)
    raw.set_eeg_reference("average", projection=False)
    ok_pd = np.array([p >= 0 for _, _, p in trials])
    evs = np.c_[np.array([p for _, _, p in trials])[ok_pd], np.zeros(ok_pd.sum(), int),
                np.array([c for _, c, _ in trials])[ok_pd]]
    ep = mne.Epochs(raw, evs, tmin=P.TMIN, tmax=P.TMAX, baseline=(P.TMIN, 0), preload=True, reject=None, flat=None,
                    event_repeated="drop")
    ep.resample(P.SF_OUT)
    t = ep.times
    d = ep.get_data(units={"eeg": "uV", "eog": "uV"})
    ix = {c: i for i, c in enumerate(ep.ch_names)}
    E = d[:, [ix[c] for c in eeg_names], :]                       # (n, 128, t), average reference
    Em = np.einsum("ck,nkt->nct", M, E)
    Em = Em[:, mz["covered"], :]
    Em -= Em.mean(axis=1, keepdims=True)                          # average reference on the covered Cohen positions
    bins = [(t >= a) & (t < b) for a, b in BINS]
    fn = np.stack([E[:, :, b].mean(axis=2) for b in bins], axis=2).astype(np.float32)
    fm = np.stack([Em[:, :, b].mean(axis=2) for b in bins], axis=2).astype(np.float32)
    side = np.array([P.STIM[c] for c in ep.events[:, 2]])
    veog = d[:, ix["VEOG1"], :] - d[:, ix["VEOG2"], :]
    heog = d[:, ix["HEOG1"], :] - d[:, ix["HEOG2"], :]
    w = (t >= P.REJ_WIN[0]) & (t <= P.REJ_WIN[1])
    roi = [ix[c] for pr in P.PAIRS for c in pr]
    rej_roi = np.ptp(d[:, roi, :], axis=2).max(axis=1) > P.ROI_PP
    rej_veog = np.ptp(veog[:, w], axis=1) > P.VEOG_PP
    rej_heog = P.step(heog[:, w], P.SF_OUT) > P.HEOG_STEP
    (OUT / "feat").mkdir(parents=True, exist_ok=True)
    sel = ep.selection                                            # indices into the photodiode-ok trials (drops, if any)
    con_ok, trig_ok = np.array(con)[ok_pd][sel], np.array([s for s, _, _ in trials])[ok_pd][sel]
    assert len(con_ok) == len(fn) == len(trig_ok), sub
    np.savez_compressed(OUT / "feat" / f"{sub}.npz", native=fn, mapped=fm, code=ep.events[:, 2], side=side,
                        sample=ep.events[:, 0], trig=trig_ok, contrast=con_ok, keep=~(rej_roi | rej_veog),
                        rej_roi=rej_roi, rej_veog=rej_veog, rej_heog=rej_heog, bad=np.array(bad, dtype=str),
                        veog_pp=np.ptp(veog[:, w], axis=1).astype(np.float32),
                        heog_step=P.step(heog[:, w], P.SF_OUT).astype(np.float32))
    print(f"{sub}: trials {len(ep)}, kept {int((~(rej_roi | rej_veog)).sum())}, bad {bad}", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["positions"]:
        positions()
    else:
        subs = P.subjects() if a == ["all"] else a          # subjects with a no-cue BDF (35)
        for s in subs:
            if not (OUT / "feat" / f"{s}.npz").exists():
                features(s)
