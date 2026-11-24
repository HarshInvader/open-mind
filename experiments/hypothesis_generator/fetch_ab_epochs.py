"""Range-read T2-locked epochs from OpenNeuro ds001810 (attentional blink, Biosemi BrainVision, v1.1.0).

Only the pre-tDCS blocks (ses-anodalpre, ses-cathodalpre) are used. Whole raw files are never downloaded:
for each lag-3 trial with T1 identified correctly, one HTTP Range request reads the T2-locked window
straight out of the multiplexed float32 .eeg file on S3.

    python -I fetch_ab_epochs.py count      # events only; writes ab_trial_counts.csv and the projected bytes
    python -I fetch_ab_epochs.py fetch      # epochs -> datasets/local/ds001810_epochs/sub-XX_<ses>.npz

Outcome label: T2 identification (correct vs incorrect), NOT seen vs unseen.
Rate: at most one request per second (project rule). Budget: refuses to go past BUDGET bytes in total.
"""
import csv, io, json, re, struct, sys, time, urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "datasets" / "local" / "ds001810_epochs"
HERE = Path(__file__).resolve().parent
S3 = "https://s3.amazonaws.com/openneuro.org/ds001810"
UA = {"User-Agent": "open-research-site/1.0"}
SESSIONS = ["anodalpre", "cathodalpre"]
TMIN, TMAX = -0.2, 0.8          # seconds around T2 onset
BUDGET = 1.5e9                  # bytes, epochs only (project budget)
LAG3, LAG8, T2_ON = 61463, 61468, 61472
T1_WRONG, T1_RIGHT = 61500, 61501
T2_WRONG, T2_RIGHT = 61510, 61511
_last = [0.0]


def get(url, rng=None):
    wait = 1.0 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    h = dict(UA)
    if rng:
        h["Range"] = f"bytes={rng[0]}-{rng[1]}"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=60) as r:
                _last[0] = time.time()
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(2 ** attempt)
        except Exception:
            time.sleep(2 ** attempt)
    raise RuntimeError(url)


def base(sub, ses):
    return f"{S3}/sub-{sub}/ses-{ses}/eeg/sub-{sub}_ses-{ses}_task-attentionalblink"


def trials(sub, ses):
    """Lag-3 trials with T1 correct: (T2 onset sample, T2 correct) list, or None if the block is missing."""
    raw = get(base(sub, ses) + "_events.tsv")
    if raw is None:
        return None
    rows = list(csv.DictReader(io.StringIO(raw.decode()), delimiter="\t"))
    out, cur = [], None
    for r in rows:
        if r["type"] != "STATUS":
            continue
        v = int(float(r["value"]))
        s = int(float(r["sample"]))
        if v in (LAG3, LAG8):
            cur = dict(lag=3 if v == LAG3 else 8, t2=None, t1=None)
        elif cur is None:
            continue
        elif v == T2_ON:
            cur["t2"] = s
        elif v in (T1_WRONG, T1_RIGHT):
            cur["t1"] = v == T1_RIGHT
        elif v in (T2_WRONG, T2_RIGHT):
            if cur["lag"] == 3 and cur["t1"] and cur["t2"] is not None:
                out.append((cur["t2"], v == T2_RIGHT))
            cur = None
    return out


def header(sub, ses):
    t = get(base(sub, ses) + "_eeg.vhdr").decode()
    nch = int(re.search(r"NumberOfChannels=(\d+)", t).group(1))
    si = float(re.search(r"SamplingInterval=([\d.e+-]+)", t).group(1))
    assert "IEEE_FLOAT_32" in t and "MULTIPLEXED" in t
    names = [m.group(1) for m in re.finditer(r"^Ch\d+=([^,]*),", t, re.M)]
    return nch, 1e6 / si, names


def main(mode):
    subs = [f"{i:02d}" for i in range(1, 48)]
    counts, plan = [], []
    for sub in subs:
        for ses in SESSIONS:
            tr = trials(sub, ses)
            if tr is None:
                continue
            counts.append(dict(sub=sub, ses=ses, n=len(tr), correct=sum(c for _, c in tr),
                               incorrect=sum(not c for _, c in tr)))
            plan.append((sub, ses, tr))
    with open(HERE / "ab_trial_counts.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(counts[0]))
        w.writeheader()
        w.writerows(counts)
    n = sum(c["n"] for c in counts)
    per = int(round((TMAX - TMIN) * 512)) * 73 * 4
    print(f"blocks {len(counts)}, trials {n}, projected {n * per / 1e9:.3f} GB")
    if mode != "fetch":
        return
    assert n * per <= BUDGET, "over budget"
    OUT.mkdir(parents=True, exist_ok=True)
    used = 0
    log = OUT / "fetch_log.jsonl"
    for sub, ses, tr in plan:
        dst = OUT / f"sub-{sub}_{ses}.npz"
        if dst.exists():                         # count bytes read over the network, not compressed size
            with np.load(dst) as d:
                used += d["X"].size * 4
            continue
        nch, fs, names = header(sub, ses)
        a, b = int(round(TMIN * fs)), int(round(TMAX * fs))
        ep, lab = [], []
        for s0, ok in tr:
            s = s0 - 1 + a                       # events.tsv samples are 1-based
            if s < 0:
                continue
            lo = s * nch * 4
            hi = (s + (b - a)) * nch * 4 - 1
            buf = get(base(sub, ses) + "_eeg.eeg", (lo, hi))
            used += len(buf)
            if used > BUDGET:
                raise SystemExit(f"budget hit at {used / 1e9:.3f} GB")
            x = np.frombuffer(buf, dtype="<f4")
            if x.size != (b - a) * nch:
                continue
            ep.append(x.reshape(b - a, nch).T)
            lab.append(ok)
        np.savez_compressed(dst, X=np.stack(ep).astype(np.float32), y=np.array(lab), ch=np.array(names),
                            fs=fs, tmin=TMIN)
        with open(log, "a") as f:
            f.write(json.dumps(dict(sub=sub, ses=ses, n=len(ep), bytes_total=used)) + "\n")
        print(sub, ses, len(ep), f"{used / 1e9:.3f} GB", flush=True)
    print(f"done, {used / 1e9:.3f} GB read")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "count")
