"""Task #42 label-blind feature extraction. Prereg: docs/prereg/2026-11-19_experience_benchmark.md (+ amendment 1).

  board/run.sh .venv/bin/python -I experiments/experience_benchmark/extract.py LAB [LAB ...]
  LAB in: Rome LODE DATA1 Aamodt Set19 Zhang Tononi

LABEL-BLIND. From the DREAM metadata it reads only the columns `Set ID`, `Filename`, `Amendment` and
`Last sleep stage` (usecols below). It never reads `Experience`. Records of every stage are processed
except W and N1, regardless of report. Raw EEG is held in memory only; nothing raw is written to disk.
Output per lab: features/<LAB>.jsonl (one row per record, keyed by Set ID + Filename), log/<LAB>.jsonl.

Rules fixed here, before any confirmation-lab sample is read (prereg §3 and amendment 1):
- End of record: trailing padding silence is trimmed first (0.5 s blocks in which every EEG channel has
  SD < 0.1 uV; Aamodt's README says its files end with such silence). Record dropped if < 32 s remain.
- Window: [-22, -2] s from the (trimmed) end of the record. Sensitivity windows [-20, 0] and [-30, -10] (primary
  measures only). Awakening = end of record for every lab; EDF+ annotation texts found in the tail are
  logged (label-blind) so the end-of-record rule can be checked before unblinding. Any change to the
  rule after that check is made by a sealed amendment.
- Units: physical dimension from the header (uV, mV, V, nV) converted to uV.
- Bad channel (main window, native rate, after unit conversion, before re-referencing):
  SD < 0.5 uV or SD > 200 uV or max |x| > 1000 uV. Record dropped if < 60% of EEG channels are good.
- Re-reference: average of good EEG channels (LODE: bipolar derivations kept as recorded).
- Native branch: notch at the lab's mains frequency (Q 30), Welch 4 s Hann 50%: posterior delta, posterior HF.
- 100 Hz branch: resample_poly to 100 Hz, then lz_slope.features.preprocess; all other measures.
- Line frequency: 50 Hz for Rome, LODE, DATA1, Aamodt, Set19; 60 Hz for Zhang & Wamsley, Tononi.
- Surrogates (N2 records only): 5 FT + 5 IAAFT of the main window for all non-spectral measures.
  Tier 1 N2 only: Study 3 gate draw = for each kind, one surrogate s of the window and
  m(s) - mean m(FT(s)) over 5 FT surrogates of s.
- Tononi montage: the EGI-256 electrodes nearest (on the unit sphere, mne montages) to the 10-10 positions
  of mne `standard_1020` that are in the 10-10 system (amendment 1, C7), recording reference dropped.
"""
import collections
import json
import os
import sys
import time
import zlib
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction

import numpy as np
import pandas as pd
from scipy.signal import resample_poly, welch

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "experiments", "t1_dream"))
import measures as M  # noqa: E402
from tailzip import parse_edf_header, read_tail  # noqa: E402
from ziprange import RemoteZip  # noqa: E402

FSH = "https://ndownloader.figshare.com/files/"
LABS = {
    "Rome": dict(sets=[9], urls=[FSH + "62751148"], line=50, tier=1),
    "LODE": dict(sets=[3], urls=[FSH + "39373088"], line=50, tier=1, bipolar=True),
    "DATA1": dict(sets=[16], urls=[FSH + "42196143"], line=50, tier=1),
    "Aamodt": dict(sets=[17, 18], urls=[FSH + "43588656", FSH + "43588551"], line=50, tier=1, tail=90.0),
    # Set19 (Kumral et al. 2023, FreiDATA, CC BY 4.0; licence checked 2026-11-19 before any EEG was read).
    # Its README: files end "right before awakening", but up to 1 min before waking may be cut (30 s scoring).
    "Set19": dict(sets=[19], urls=["https://freidata.uni-freiburg.de/api/records/31mg4-mfq53/files/"
                                   "Kumral%20et%20al.,%202023.zip/content"], line=50, tier=1),
    "Zhang": dict(sets=[1], urls=[FSH + "39504757"], line=60, tier=2),
    "Tononi": dict(sets=[13], urls=None, line=60, tier=2),        # members from t1_dream/tononi_members.csv
}
STAGES = {"N2", "REM", "N3"}
TAIL_S = 40.0           # seconds read from the end (Aamodt: 90 s, because its files end in padding silence)
SILENCE_SD = 0.1        # uV; a 0.5 s block is padding silence if every channel's SD is below this
BUDGET = 12e9
POST = ["P3", "P4", "PZ", "P7", "P8", "PO3", "PO4", "POZ", "PO7", "PO8", "O1", "O2", "OZ"]
S1020 = ["FP1", "FP2", "F7", "F3", "FZ", "F4", "F8", "T7", "C3", "CZ", "C4", "T8", "P7", "P3", "PZ", "P4", "P8", "O1", "O2"]
ALIAS = {"T3": "T7", "T4": "T8", "T5": "P7", "T6": "P8", "01": "O1"}
NON_EEG = ("EOG", "EMG", "ECG", "EKG", "LOC", "ROC", "ACCEL", "POX", "ANNOT", "STATUS", "M1", "M2", "A1", "A2", "SM")
OUT = os.environ.get("EB_OUT", os.path.join(HERE, "features")); LOGD = os.environ.get("EB_LOG", os.path.join(HERE, "log"))


def canon(label):
    s = label.strip()
    for p in ("EEG ", "EEG"):
        if s.upper().startswith(p):
            s = s[len(p):].strip()
    for suf in ("-REF", "-Ref", "-ref"):
        if s.endswith(suf):
            s = s[: -len(suf)]
    s = s.upper()
    return ALIAS.get(s, s)


def tononi_montage():
    import mne
    egi = mne.channels.make_standard_montage("GSN-HydroCel-256")
    std = mne.channels.make_standard_montage("standard_1020")
    pe = egi.get_positions()["ch_pos"]; ps = std.get_positions()["ch_pos"]
    def unit(d):
        P = np.array(list(d.values())); c = P.mean(0); V = P - c
        return dict(zip(d.keys(), V / np.linalg.norm(V, axis=1, keepdims=True)))
    ue, us = unit(pe), unit(ps)
    tenten = [n for n in us if not any(ch in n.upper() for ch in ("H", "'")) and n.upper() not in ("A1", "A2", "M1", "M2", "T9", "T10", "TP9", "TP10", "P9", "P10", "F9", "F10", "FT9", "FT10")]
    E = np.array([ue[k] for k in ue]); names = list(ue)
    m = {}
    for n in tenten:
        j = int(np.argmax(E @ us[n]))
        m[ALIAS.get(n.upper(), n.upper())] = names[j]             # 10-10 name -> 'E<k>'
    return m


def select_channels(lab, h):
    labels, nsamp = h["labels"], h["nsamp"]
    if lab == "Tononi":
        mp = tononi_montage(); inv = {v: k for k, v in mp.items()}
        idx = [i for i, l in enumerate(labels) if l.startswith("Chan ") and f"E{l.split()[1]}" in inv]
        names = [inv[f"E{labels[i].split()[1]}"] for i in idx]
    elif LABS[lab].get("bipolar"):
        idx = [i for i, l in enumerate(labels) if l.upper().startswith("EEG ") and "-" in l]
        names = [l[4:].strip().upper() for l in (labels[i] for i in idx)]
    else:
        idx, names = [], []
        for i, l in enumerate(labels):
            c = canon(l)
            if any(t in l.upper() for t in NON_EEG) or c in ("E1", "E2") or not c or "-" in c:
                continue
            idx.append(i); names.append(c)
    if not idx:
        return [], [], None
    fs_mode = collections.Counter(int(nsamp[i]) for i in idx).most_common(1)[0][0]
    keep = [k for k, i in enumerate(idx) if int(nsamp[i]) == fs_mode]
    return [idx[k] for k in keep], [names[k] for k in keep], fs_mode / h["recdur"]


def decode(data, pos0, h, idx, fs, seconds):
    ns_rec = h["nsamp"].astype(int); recb = int(ns_rec.sum()) * 2
    nrec = (h["usize"] - h["hbytes"]) // recb
    nr = int(np.ceil(seconds / h["recdur"]))
    first = nrec - nr; off = h["hbytes"] + first * recb - pos0
    if off < 0:
        raise ValueError("tail too short")
    raw_i2 = np.frombuffer(data[off:off + nr * recb], "<i2").reshape(nr, -1)
    raw = raw_i2.astype(float)
    so = np.r_[0, np.cumsum(ns_rec)]
    X = np.stack([raw[:, so[i]:so[i + 1]].reshape(-1) * h["gain"][i] + h["offs"][i] for i in idx])
    unit = {"uv": 1.0, "µv": 1.0, "mv": 1e3, "v": 1e6, "nv": 1e-3}
    X *= np.array([unit.get(h["units"][i].strip().lower().replace("μ", "µ"), 1.0) for i in idx])[:, None]
    ann = []
    for i, l in enumerate(h["labels"]):
        if "annotation" in l.lower():
            txt = np.ascontiguousarray(raw_i2[:, so[i]:so[i + 1]]).tobytes().decode("latin-1", "replace")
            ann = [t for t in txt.replace("\x00", "\x14").split("\x14") if t.strip() and not t.strip().startswith("+")][:20]
    return X[:, -int(round(seconds * fs)):], ann


def to100(x, fs):
    fr = Fraction(100, int(round(fs))).limit_denominator(1000)
    return resample_poly(x, fr.numerator, fr.denominator, axis=-1)


def win(x, fs, a, b):
    n = x.shape[1]
    return x[:, n + int(round(a * fs)): n + int(round(b * fs)) if b < 0 else n]


def process(job):
    try:
        return _process(job)
    except Exception as e:  # noqa: BLE001
        lab, key = job[0], job[1]
        return {"set": key[0], "file": key[1], "lab": lab, "stage": job[2], "status": f"error {type(e).__name__}: {str(e)[:150]}"}


def _process(job):
    lab, key, stage, X, names, fs = job
    rng = np.random.default_rng(zlib.crc32(f"{key[0]}/{key[1]}".encode()))
    out = {"set": key[0], "file": key[1], "lab": lab, "stage": stage, "fs": fs, "n_ch": len(names)}
    blk = int(fs // 2); nb = X.shape[1] // blk
    sil = X[:, X.shape[1] - nb * blk:].reshape(X.shape[0], nb, blk).std(2).max(0) < SILENCE_SD
    k = 0
    while k < nb and sil[nb - 1 - k]:
        k += 1
    out["trim_s"] = k * blk / fs
    if k:
        X = X[:, :X.shape[1] - k * blk]
    if X.shape[1] < 32 * fs:
        out["status"] = "dropped: < 32 s after trimming silence"; return out
    w = win(X, fs, -22, -2)
    sd = w.std(1); good = (sd >= 0.5) & (sd <= 200) & (np.abs(w).max(1) <= 1000)
    out["n_good"] = int(good.sum())
    if good.mean() < 0.6:
        out["status"] = "dropped: < 60% good channels"; return out
    names = [n for n, g in zip(names, good) if g]; X = X[good]
    if not LABS[lab].get("bipolar"):
        X = X - X.mean(0, keepdims=True)
    if LABS[lab].get("bipolar"):
        roi = [i for i, n in enumerate(names) if n.endswith("O1") or n.endswith("O2")]
        i1020 = list(range(len(names)))
    else:
        roi = [i for i, n in enumerate(names) if n in POST]
        i1020 = [i for i, n in enumerate(names) if n in S1020]
    out["n_roi"], out["n_1020"] = len(roi), len(i1020)
    x100_all = to100(X, fs)
    def feats(a, b, secondary):
        r = {}
        if roi:
            r.update(M.native(win(X, fs, a, b)[roi], fs, LABS[lab]["line"]))
        x = M.preprocess(win(x100_all, 100.0, a, b))
        r.update(M.m100(x, x[i1020] if len(i1020) >= 3 else x[:0], rng, secondary))
        return r, x
    main, x = feats(-22, -2, True)
    out.update(main)
    # 1-30 Hz baseline variant and the label-blind PSD for the low-pass rule
    raw100 = win(x100_all, 100.0, -22, -2)
    f, p = welch(raw100, fs=100.0, nperseg=200, noverlap=100, axis=-1)
    out["psd_log10"] = [round(float(v), 4) for v in np.log10(p.mean(0) + 1e-30)]
    fp, pp = M.psd(x); m30 = (fp >= 1) & (fp <= 30)
    out["exponent_1_30"] = float(np.mean([np.polyfit(np.log10(fp[m30]), np.log10(c[m30]), 1)[0] for c in pp]))
    tot = pp[:, m30].sum(1)
    for b, (lo, hi) in {"delta": (1, 4), "theta": (4, 8), "alpha": (8, 12), "sigma": (12, 15), "beta": (15, 30)}.items():
        mm = (fp >= lo) & (fp < hi) if hi < 30 else (fp >= lo) & (fp <= hi)
        out["bp30_" + b] = float(np.mean(np.log10(pp[:, mm].sum(1) / tot)))
    # pre-awakening arousal index: final 5 s of the window
    xa = x[:, -500:]; fa, pa = welch(xa, fs=100.0, nperseg=200, noverlap=100, axis=-1)
    out["arousal_idx"] = float(np.mean(np.log10(pa[:, (fa >= 8) & (fa <= 12)].sum(1) / pa[:, (fa >= 1) & (fa < 4)].sum(1))))
    for tag, (a, b) in {"w0": (-20, 0), "w10": (-30, -10)}.items():
        r, _ = feats(a, b, False)
        out.update({f"{k}__{tag}": v for k, v in r.items() if not k.startswith("bp_")})
    if stage == "N2":
        x1 = x[i1020] if len(i1020) >= 3 else x[:0]
        out.update(M.surrogate_block(x, x1, i1020 if len(i1020) >= 3 else None, rng, 5, True))
        if LABS[lab]["tier"] == 1:
            for kind in ("ft", "iaaft"):
                s = M.phase_surrogate(x, rng) if kind == "ft" else M.iaaft(x, rng)
                s1 = s[i1020] if len(i1020) >= 3 else s[:0]
                ms = M.m100(s, s1, rng, True)
                fsur = [M.m100(t, t[i1020] if len(i1020) >= 3 else t[:0], rng, True)
                        for t in (M.phase_surrogate(s, rng) for _ in range(5))]
                for k in M.NONSPECTRAL_100:
                    out[f"{k}__s3x_{kind}"] = float(ms[k] - np.nanmean([v[k] for v in fsur]))
    out["status"] = "ok"
    return out


def records(lab):
    d = pd.read_csv(os.path.join(REPO, "experiments", "dataset_audit", "dream_records.csv"),
                    usecols=["Set ID", "Filename", "Amendment", "Last sleep stage"])   # NOT 'Experience'
    d = d.sort_values("Amendment").drop_duplicates(["Set ID", "Filename"], keep="last")
    d["st"] = [("N3" if str(s).startswith("N3") else str(s)) for s in d["Last sleep stage"]]
    d = d[d["Set ID"].isin(LABS[lab]["sets"]) & d.st.isin(STAGES)]
    return [(int(r["Set ID"]), r.Filename, r.st) for _, r in d.iterrows()]


def member_index(lab):
    idx = {}
    if lab == "Tononi":
        for m in pd.read_csv(os.path.join(REPO, "experiments", "t1_dream", "tononi_members.csv")).to_dict("records"):
            idx[m["file"]] = (m["url"], m["member"], int(m["offset"]), int(m["csize"]), int(m["usize"]), int(m["zipsize"]))
        return idx
    for url in LABS[lab]["urls"]:
        z = RemoteZip(url)
        for name, (meth, csz, usz, off) in z.members.items():
            if name.lower().endswith(".edf"):
                idx[name] = (url, name, off, csz, usz, z.size)
    return idx


def find_member(idx, fname):
    if fname in idx:
        return idx[fname]
    hits = [v for k, v in idx.items() if k.endswith("/" + fname) or k == fname or os.path.basename(k) == os.path.basename(fname)]
    return hits[0] if len(hits) == 1 else None


def main(labs):
    os.makedirs(OUT, exist_ok=True); os.makedirs(LOGD, exist_ok=True)
    spent = 0
    for lab in labs:
        if lab == "Set19" and not LABS[lab]["urls"]:
            print("Set19: no URL (licence/access not yet confirmed); skipped", flush=True); continue
        logf = os.path.join(LOGD, f"{lab}.jsonl"); outf = os.path.join(OUT, f"{lab}.jsonl")
        done = set()
        if os.path.exists(outf):
            done |= {json.loads(ln)["file"] for ln in open(outf)}
        if os.path.exists(logf):
            for ln in open(logf):
                r = json.loads(ln); spent += r.get("bytes", 0)
                if r.get("status") != "submitted":
                    done.add(r["file"])
        recs = [r for r in records(lab) if r[1] not in done]
        idx = member_index(lab); zips = {}
        print(lab, "records to do:", len(recs), flush=True)
        with ProcessPoolExecutor(max_workers=2) as ex:
            pending = []
            for (sid, fname, st) in recs:
                if spent > BUDGET:
                    print("BUDGET reached", flush=True); break
                info = find_member(idx, fname); rec = {"file": fname, "set": sid}
                if info is None:
                    rec["status"] = "member not found"
                    open(logf, "a").write(json.dumps(rec) + "\n"); continue
                url, member, off, csz, usz, zsize = info
                try:
                    if url not in zips:
                        zips[url] = RemoteZip(url, size=zsize)
                    z = zips[url]; b0 = z.bytes_fetched
                    h0 = z.read(member, max_out=256, chunk=64 * 1024)
                    ns = int(h0[252:256]); hdr = z.read(member, max_out=256 * (ns + 1), chunk=64 * 1024)
                    h = parse_edf_header(hdr); h["usize"] = usz
                    ch, names, fs = select_channels(lab, h)
                    if not ch:
                        raise ValueError("no EEG channels")
                    recb = int(h["nsamp"].sum()) * 2
                    tail_s = LABS[lab].get("tail", TAIL_S)
                    pos0, data, taint, fetched = read_tail(url, off, csz, usz, int(tail_s / h["recdur"] + 2) * recb + 65536)
                    lt = int(np.nonzero(taint)[0].max()) + 1 if taint.any() else 0
                    X, ann = decode(data[lt:], pos0 + lt, h, ch, fs, tail_s)
                    rec.update(bytes=fetched + (z.bytes_fetched - b0) + 30, fs=fs, n_ch=len(ch), annotations=ann,
                               rec_s=float((usz - h["hbytes"]) // recb * h["recdur"]))
                    pending.append(ex.submit(process, (lab, (sid, fname), st, X, names, fs)))
                    rec["status"] = "submitted"
                except Exception as e:  # noqa: BLE001
                    rec["status"] = f"error {type(e).__name__}: {str(e)[:150]}"; rec.setdefault("bytes", 0)
                spent += rec.get("bytes", 0)
                open(logf, "a").write(json.dumps(rec) + "\n")
                while len(pending) >= 4:
                    fut = pending.pop(0); r = fut.result()
                    open(outf, "a").write(json.dumps(r) + "\n"); print(lab, r["file"], r["status"], round(spent / 1e6), "MB", flush=True)
            for fut in pending:
                r = fut.result(); open(outf, "a").write(json.dumps(r) + "\n"); print(lab, r["file"], r["status"], flush=True)
    print("total fetched MB", round(spent / 1e6, 1), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
