"""Round 19 #2 (ds006171, no-cue task): label-blind preprocessing. DRAFT, not sealed.
Prereg draft: docs/prereg/2026-11-26_ds006171_lateralised_van.md

    python -I prep.py SUB [SUB ...]   # -> out/prep/<sub>.npz   (stimulus codes 11-32 and photodiode 128 only)
    python -I prep.py all
    python -I prep.py labels          # AFTER SEALING ONLY: seen/unseen codes 124/125 -> out/labels.npz (refuses before)

Per trial it stores the contra-minus-ipsi waveform L(t) (mean over PO7/PO8, P7/P8, O1/O2), the bilateral ROI mean,
HEOG and VEOG, at 256 Hz from -200 to +600 ms after the photodiode, plus side, code, contrast and the rejection flags.
Catch trials (31/32) get the nominal side (31 left, 32 right). Downloaded BDFs are untrusted data, read with MNE only.
"""
import csv, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "datasets" / "local" / "r19_ds006171" / "files"
OUT = HERE / "out" / "prep"
PREREG = ROOT / "docs" / "prereg" / "2026-11-26_ds006171_lateralised_van.md"

PAIRS = [("PO7", "PO8"), ("P7", "P8"), ("O1", "O2")]        # (left hemisphere, right hemisphere)
STIM = {11: "L", 12: "L", 21: "R", 22: "R", 31: "L", 32: "R"}
PD, PD_MAX = 128, 0.100                                       # photodiode code; max lag after the trigger (s)
TMIN, TMAX, SF_OUT = -0.2, 0.6, 256
L_FREQ, H_FREQ = 0.1, 30.0
ROI_PP, VEOG_PP, HEOG_STEP = 150.0, 80.0, 20.0                # uV
REJ_WIN = (-0.1, 0.4)
STEP_W = 0.05                                                 # s, half-window of the HEOG step function
BAD_CH = 3.0


def subjects():
    return sorted(p.name for p in RAW.glob("sub-*") if (p / "eeg" / f"{p.name}_task-nocue_eeg.bdf").exists())


def events_tsv(sub):
    f = RAW / sub / "eeg" / f"{sub}_task-nocue_events.tsv"
    rows = [r for r in csv.DictReader(open(f), delimiter="\t") if r["trial_type"] in {str(k) for k in STIM}]
    return [(float(r["onset"]), int(r["trial_type"]), float(r["gabor_contrast"]) if r["gabor_contrast"] != "NaN" else np.nan)
            for r in rows]


def step(x, fs):
    """Max absolute difference between the means of adjacent STEP_W windows (split-half step), per trial."""
    w = int(round(STEP_W * fs))
    c = np.cumsum(np.pad(x, ((0, 0), (1, 0))), axis=1)
    m = (c[:, w:] - c[:, :-w]) / w                            # running means
    return np.abs(m[:, w:] - m[:, :-w]).max(axis=1)


def prep(sub):
    import mne
    mne.set_log_level("ERROR")
    eeg = RAW / sub / "eeg"
    raw = mne.io.read_raw_bdf(eeg / f"{sub}_task-nocue_eeg.bdf", preload=False)
    names = [r["name"] for r in csv.DictReader(open(eeg / f"{sub}_task-nocue_channels.tsv"), delimiter="\t")]
    if len(raw.ch_names) == 272:          # 256-channel recording mode (sub-02, 04, 05): banks E-H unused; channels.tsv lists 144
        unused = [c for c in raw.ch_names if c[0] in "EFGH" and c[1:].isdigit()]
        seg = raw.get_data(picks=unused, start=0, stop=int(10 * raw.info["sfreq"]))
        assert float(seg.std(axis=1).max()) * 1e6 < 1.0, (sub, "bank E-H not empty")
        print(f"{sub}: dropping {len(unused)} unused bank E-H channels, max 10-s SD {seg.std(axis=1).max() * 1e6:.2f} uV")
        raw.drop_channels(unused)
    assert len(names) == len(raw.ch_names), (sub, len(names), len(raw.ch_names))
    ev = mne.find_events(raw, stim_channel="Status", shortest_event=1, initial_event=True)
    raw.rename_channels(dict(zip(raw.ch_names, names)))
    ev[:, 2] &= 0xFF
    fs = raw.info["sfreq"]
    # photodiode rule: each stimulus trigger's time is replaced by the next 128 within PD_MAX
    pd = ev[ev[:, 2] == PD, 0]
    trials = []
    for s, _, code in ev:
        if code in STIM:
            nxt = pd[(pd > s) & (pd <= s + PD_MAX * fs)]
            trials.append((s, code, int(nxt[0]) if len(nxt) else -1))
    # contrast from events.tsv, matched by onset (within 5 ms) and code
    tsv = events_tsv(sub)
    con = []
    for s, code, _ in trials:
        hit = [c for (o, k, c) in tsv if k == code and abs(o - s / fs) < 0.005]
        con.append(hit[0] if len(hit) == 1 else np.nan)
    eeg_names = names[:128]
    picks = eeg_names + ["VEOG1", "VEOG2", "HEOG1", "HEOG2"]
    raw.pick(picks).load_data()
    raw.set_channel_types({c: "eog" for c in ("VEOG1", "VEOG2", "HEOG1", "HEOG2")})
    pos = {r["name"]: [float(r["x"]), float(r["y"]), float(r["z"])]
           for r in csv.DictReader(open(eeg / f"{sub}_electrodes.tsv"), delimiter="\t") if r["name"] in eeg_names}
    raw.set_montage(mne.channels.make_dig_montage(ch_pos={k: np.array(v) / (1000.0 if max(map(abs, v)) > 1 else 1.0)
                                                          for k, v in pos.items()}, coord_frame="head"), on_missing="ignore")
    raw.filter(L_FREQ, H_FREQ, picks=["eeg", "eog"], method="fir", phase="zero", n_jobs=1)
    # bad channels (label-blind): median 1-s-window peak-to-peak > BAD_CH x the median over channels
    x = raw.get_data(picks="eeg") * 1e6
    nwin = x.shape[1] // int(fs)
    pp = np.median(np.ptp(x[:, :nwin * int(fs)].reshape(x.shape[0], nwin, int(fs)), axis=2), axis=1)
    bad = [eeg_names[i] for i in np.where(pp > BAD_CH * np.median(pp))[0]]
    raw.info["bads"] = bad
    if bad:
        raw.interpolate_bads(reset_bads=True)
    raw.set_eeg_reference("average", projection=False)
    ok_pd = np.array([p >= 0 for _, _, p in trials])
    onsets = np.array([p for _, _, p in trials])[ok_pd]
    evs = np.c_[onsets, np.zeros(len(onsets), int), np.array([c for _, c, _ in trials])[ok_pd]]
    ep = mne.Epochs(raw, evs, tmin=TMIN, tmax=TMAX, baseline=(TMIN, 0), preload=True, reject=None, flat=None,
                    event_repeated="drop")
    ep.resample(SF_OUT)
    t = ep.times
    d = ep.get_data(units={"eeg": "uV", "eog": "uV"})
    ix = {c: i for i, c in enumerate(ep.ch_names)}
    side = np.array([STIM[c] for c in ep.events[:, 2]])
    left_h = np.mean([d[:, ix[a], :] for a, _ in PAIRS], axis=0)
    right_h = np.mean([d[:, ix[b], :] for _, b in PAIRS], axis=0)
    L = np.where((side == "L")[:, None], right_h - left_h, left_h - right_h)   # contra minus ipsi
    bil = (left_h + right_h) / 2
    heog = d[:, ix["HEOG1"], :] - d[:, ix["HEOG2"], :]
    veog = d[:, ix["VEOG1"], :] - d[:, ix["VEOG2"], :]
    w = (t >= REJ_WIN[0]) & (t <= REJ_WIN[1])
    roi = [ix[c] for pr in PAIRS for c in pr]
    rej_roi = np.ptp(d[:, roi, :], axis=2).max(axis=1) > ROI_PP
    rej_veog = np.ptp(veog[:, w], axis=1) > VEOG_PP
    rej_heog = step(heog[:, w], SF_OUT) > HEOG_STEP
    keep = ~(rej_roi | rej_veog | rej_heog)
    con_all = np.array(con)[ok_pd]
    OUT.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT / f"{sub}.npz", L=L.astype(np.float32), bil=bil.astype(np.float32),
                        heog=heog.astype(np.float32), times=t, side=side, code=ep.events[:, 2],
                        sample=ep.events[:, 0], contrast=con_all, keep=keep, rej_roi=rej_roi, rej_veog=rej_veog,
                        rej_heog=rej_heog, bad=np.array(bad, dtype=str), n_no_pd=int((~ok_pd).sum()))
    print(f"{sub}: trials {len(trials)}, no-photodiode {int((~ok_pd).sum())}, kept {int(keep.sum())}/{len(keep)} "
          f"(roi {int(rej_roi.sum())}, veog {int(rej_veog.sum())}, heog {int(rej_heog.sum())}), "
          f"bad {bad}, contrast-matched {int(np.isfinite(con_all).sum())}", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["labels"]:
        raise SystemExit("labels: written after sealing")
    for s in (subjects() if a == ["all"] else a):
        if not (OUT / f"{s}.npz").exists():
            prep(s)
