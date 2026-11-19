"""NE test feature extraction. Prereg: docs/prereg/2026-11-18_nonequilibrium_vs_spectrum.md

  board/run.sh .venv/bin/python -I experiments/nonequilibrium/extract.py sleepedf   # needs fetch_sleepedf.py first
  board/run.sh .venv/bin/python -I experiments/nonequilibrium/extract.py ds005620
  board/run.sh .venv/bin/python -I experiments/nonequilibrium/extract.py chennu

Appends to features.jsonl, one 'real' row and one 'surr' (multichannel phase-randomised) row per clean
epoch. Resumable by recording. Untrusted data: only parsed as numbers; raw EEG for ds005620 and
Chennu is never written to disk; Sleep-EDF raw npz files are deleted after extraction.
"""
import glob
import json
import os
import sys
import time
import urllib.request

import mne
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "experiments", "lz_slope"))
sys.path.insert(0, os.path.join(REPO, "experiments", "theory_tests"))
from features import band_powers, lz, perm_entropy, phase_surrogate, preprocess, spectral_exponent  # noqa: E402
from ne_measures import iaaft, ne_measures, tra  # noqa: E402

OUT = os.path.join(HERE, "features.jsonl")
UA = {"User-Agent": "open-research-site/1.0"}


def measures(x, rng):
    out = {"lz": lz(x), "slope": spectral_exponent(x), "perm_entropy": perm_entropy(x)}
    out.update(band_powers(x))
    out.update(ne_measures(x, rng, phase_surrogate))
    return out


def rows_for_epoch(x, base, rng):
    """x preprocessed. Returns real + surrogate rows (or one 'bad' row)."""
    ptp = np.ptp(x, axis=-1)
    clean = bool(ptp.max() <= 500 and x.std(-1).min() >= 0.5)
    if not clean:
        return [{**base, "kind": "real", "clean": False, "max_ptp": float(ptp.max())}]
    r = {**base, "kind": "real", "clean": True, **measures(x, rng)}
    r["tra_xi"] = r["tra"] - tra(iaaft(x, rng))          # secondary: excess over one IAAFT surrogate
    s = phase_surrogate(x, rng)
    return [r, {**base, "kind": "surr", "clean": True, **measures(s, rng)}]


def done(dataset):
    if not os.path.exists(OUT):
        return set()
    return {json.loads(l)["rec"] for l in open(OUT) if f'"dataset": "{dataset}"' in l}


def write(rows):
    with open(OUT, "a") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


# ------------------------------------------------------------------ Sleep-EDF
def sleepedf():
    dn = done("sleepedf")
    for fn in sorted(glob.glob(os.path.join(HERE, "raw", "*.npz"))):
        d = np.load(fn)
        rec, subj = str(d["rec"]), str(d["subject"])
        if rec in dn:
            os.remove(fn); continue
        rng = np.random.default_rng(1000 + int(subj))
        rows = []
        for i in range(len(d["stage"])):
            base = {"dataset": "sleepedf", "rec": rec, "subject": subj, "cls": str(d["stage"][i]),
                    "epoch": int(d["epoch"][i]),
                    "emg": float(np.log(np.mean(d["emg"][i]) + 1e-6)) if np.mean(d["emg"][i]) > 0 else None,
                    "eog": float(np.log(np.var(d["eog"][i]) + 1e-6))}
            rows += rows_for_epoch(preprocess(d["eeg"][i]), base, rng)
        write(rows)
        os.remove(fn)
        print("sleepedf", rec, len(rows), flush=True)


# ------------------------------------------------------------------ ds005620
S3 = "https://s3.amazonaws.com/openneuro.org/ds005620"
FS_DS, NCH_DS, WIN_S = 5000, 65, 40


def get(url, a=None, b=None, tries=5):
    for k in range(tries):
        try:
            h = dict(UA)
            if a is not None:
                h["Range"] = f"bytes={a}-{b}"
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=120) as r:
                data = r.read()
            if a is None or len(data) == b - a + 1:
                return data
            raise IOError("short read")
        except Exception as e:  # noqa: BLE001
            err = e; time.sleep(3 * (k + 1))
    raise err


def ds_list():
    keys = []
    tok = None
    while True:
        u = f"https://s3.amazonaws.com/openneuro.org?list-type=2&prefix=ds005620/sub-&max-keys=1000"
        if tok:
            u += "&continuation-token=" + urllib.request.quote(tok)
        t = get(u).decode()
        keys += [(k, int(s)) for k, s in zip(
            [x.split("</Key>")[0] for x in t.split("<Key>")[1:]],
            [x.split("</Size>")[0] for x in t.split("<Size>")[1:]])]
        if "<NextContinuationToken>" not in t:
            break
        tok = t.split("<NextContinuationToken>")[1].split("<")[0]
    return dict(keys)


def ds_read(key, size, start_s):
    """Read WIN_S seconds starting at start_s from a multiplexed float32 BrainVision file -> (ch, n) in uV."""
    hdr = get(f"{S3}/{key[len('ds005620/'):].replace('_eeg.eeg', '_eeg.vhdr')}").decode("utf-8", "replace")
    assert "DataOrientation=MULTIPLEXED" in hdr and "IEEE_FLOAT_32" in hdr and "SamplingInterval=200" in hdr
    nch = int(hdr.split("NumberOfChannels=")[1].split()[0])  # amendment 1: most files 65, some 64
    res = np.array([float(l.split("=", 1)[1].split(",")[2] or 1) for l in hdr.splitlines()
                    if l.startswith("Ch") and "=" in l and l.split("=")[0][2:].isdigit()])
    assert len(res) == nch
    n_tot = size // (4 * nch)
    s0 = max(0, min(int(start_s * FS_DS), n_tot - WIN_S * FS_DS))
    a = s0 * 4 * nch
    b = a + WIN_S * FS_DS * 4 * nch - 1
    x = np.frombuffer(get(f"{S3}/{key[len('ds005620/'):]}", a, b), "<f4").reshape(-1, nch).T.astype(np.float64)
    return x * res[:, None]


def ds005620():
    keys = ds_list()
    dn = done("ds005620")
    subs = sorted({k.split("/")[1] for k in keys})
    for sub in subs:
        if sub == "sub-1037":      # excluded in participants.tsv
            continue
        ec = f"ds005620/{sub}/eeg/{sub}_task-awake_acq-EC_eeg.eeg"
        sed = [f"ds005620/{sub}/eeg/{sub}_task-sed2_acq-rest_run-{r}_eeg.eeg" for r in (1, 2, 3)]
        sed = [s for s in sed if s in keys]
        if ec not in keys or not sed:
            print("skip", sub, "missing files", flush=True); continue
        rng = np.random.default_rng(int(sub.split("-")[1]))
        for cls, key, start in (("awake", ec, 130.0), ("sed2", sed[0], 1e9)):  # awake: 130-170 s; sed2: last 40 s
            rec = f"{sub}_{cls}"
            if rec in dn:
                continue
            try:
                x = ds_read(key, keys[key], start)
            except Exception as e:  # noqa: BLE001  (prereg: unreadable files are skipped and listed)
                print("skip unreadable", rec, repr(e)[:120], flush=True); continue
            x = x - x.mean(0, keepdims=True)                                    # average reference
            x = mne.filter.resample(x, up=100.0 / FS_DS, verbose=False)        # anti-aliased, 100 Hz
            rows = []
            for k in range(WIN_S // 10):
                base = {"dataset": "ds005620", "rec": rec, "subject": sub, "cls": cls, "epoch": k,
                        "file": key.split("/")[-1]}
                rows += rows_for_epoch(preprocess(x[:, k * 1000:(k + 1) * 1000]), base, rng)
            write(rows)
            print("ds005620", rec, sum(r["kind"] == "real" and r["clean"] for r in rows), "clean", flush=True)


# ------------------------------------------------------------------ Chennu
CH_URL = "https://api.repository.cam.ac.uk/server/api/core/bitstreams/e94a6722-da5b-4e53-8673-5e8ec106e0f7/content"
CH_SIZE, CH_NCH, CH_SF, CH_EP, CH_NEP = 3694326663, 91, 250.0, 2500, 12


def chennu():
    import scipy.io as sio
    from ziprange import RemoteZip
    info = sio.loadmat(os.path.join(REPO, "experiments", "theory_tests", "raw", "meta", "chennu_datainfo.mat"),
                       squeeze_me=True)["datainfo"]
    rows_info = [(str(r[0]), int(r[1])) for r in info if int(r[1]) in (1, 3)]
    dn = done("chennu")
    z = RemoteZip(CH_URL, CH_SIZE)
    for name, level in rows_info:
        if name in dn:
            continue
        member = f"Sedation-RestingState/{name}.fdt"
        nep = min(CH_NEP, z.members[member][2] // (CH_NCH * 4 * CH_EP))
        raw = z.read(member, max_out=nep * CH_NCH * 4 * CH_EP)
        x = np.frombuffer(raw, dtype="<f4").reshape(-1, CH_NCH).T.astype(np.float64)
        x = x - x.mean(0, keepdims=True)
        x = mne.filter.resample(x, up=100.0 / CH_SF, verbose=False)
        rng = np.random.default_rng(int(name[:2]) * 10 + level)
        rows = []
        for k in range(nep):
            base = {"dataset": "chennu", "rec": name, "subject": name[:2], "cls": f"L{level}", "epoch": k}
            rows += rows_for_epoch(preprocess(x[:, k * 1000:(k + 1) * 1000]), base, rng)
        write(rows)
        print("chennu", name, level, sum(r["kind"] == "real" and r["clean"] for r in rows), "clean",
              round(z.bytes_fetched / 1e6, 1), "MB fetched", flush=True)


if __name__ == "__main__":
    {"sleepedf": sleepedf, "ds005620": ds005620, "chennu": chennu}[sys.argv[1]]()
