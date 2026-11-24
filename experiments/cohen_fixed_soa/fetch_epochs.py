"""Range-read face-locked epochs at SOA 50 ms (report block, seen or unseen answer) from Cohen et al. 2024 (OSF 6d5av).

    python -I fetch_epochs.py plan     # count trials and projected bytes; reads nothing over the network
    python -I fetch_epochs.py fetch    # epochs -> datasets/local/cohen2024_epochs/<sub>.npz (resumes)

Epoch: -0.1 to +0.6 s around face onset (350 samples at 500 Hz, all 63 channels, int16 x 0.1 uV, multiplexed).
One HTTP Range request per trial, at most one request per second. Whole .eeg files are never downloaded.
Budget: the project may download 1.5 GB in total. ds001810 used 1,254,488,064 bytes; the Cohen headers and markers
9,812,193 bytes. This script refuses to read more than what is left. Labels are stored but not looked at here.
Downloaded bytes are untrusted data: parsed as int16, never executed.
"""
import csv, json, re, sys, time, urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "datasets" / "local" / "cohen2024"
OUT = ROOT / "datasets" / "local" / "cohen2024_epochs"
HERE = Path(__file__).resolve().parent
UA = {"User-Agent": "open-research-site/1.0"}
TMIN, TMAX, FS, NCH = -0.1, 0.6, 500, 63
NS = int(round((TMAX - TMIN) * FS))
LEFT = int(1.5e9) - 1_254_488_064 - 9_812_193
_last = [0.0]


def get(url, rng):
    wait = 1.0 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    h = dict(UA, Range=f"bytes={rng[0]}-{rng[1]}")
    for attempt in range(5):
        try:
            wait = 1.0 - (time.time() - _last[0])
            if wait > 0:
                time.sleep(wait)
            _last[0] = time.time()                       # start-to-start spacing: at most one request per second
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=120) as r:
                if r.status != 206:
                    raise RuntimeError(f"no range support: HTTP {r.status}")
                return r.read()
        except RuntimeError:
            raise
        except Exception:
            time.sleep(2 ** attempt)
    raise RuntimeError(url)


def plan():
    """sub -> (eeg name, [(onset sample 1-based, resp, ident)]) for SOA-50 report face trials with a seen/unseen answer."""
    out = {}
    for r in csv.DictReader(open(HERE / "trials.csv")):
        if r["block"] == "report" and r["kind"] == "face" and r["soa"] == "50" and r["resp"] in ("1", "2"):
            out.setdefault(r["sub"], []).append((int(r["onset"]), int(r["resp"]), int(r["ident"])))
    eeg = {}
    for h in D.glob("delcul*.vhdr"):
        t = h.read_text(errors="replace")
        assert "BinaryFormat=INT_16" in t and "MULTIPLEXED" in t and "SamplingInterval=2000" in t
        assert f"NumberOfChannels={NCH}" in t
        res = [float(m.group(1)) for m in re.finditer(r"^Ch\d+=[^,]*,[^,]*,([\d.]+),", t, re.M)]
        assert len(res) == NCH and set(res) == {0.1}, h.name
        eeg[h.stem.replace("delcul", "")] = re.search(r"DataFile=(\S+)", t).group(1)
    return {s: (eeg[s], tr) for s, tr in sorted(out.items())}


def main(mode):
    p = plan()
    n = sum(len(t) for _, t in p.values())
    per = NS * NCH * 2
    print(f"subjects {len(p)}, trials {n}, projected {n * per / 1e6:.1f} MB; left in budget {LEFT / 1e6:.1f} MB")
    assert n * per <= LEFT, "over budget"
    if mode != "fetch":
        return
    idx = json.loads((HERE / "osf_index.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    a = int(round(TMIN * FS))
    used = 0
    for sub, (eeg, tr) in p.items():
        dst = OUT / f"{sub}.npz"
        if dst.exists():
            with np.load(dst) as d:
                used += d["X"].size * 2
            continue
        url = idx[eeg]["url"]
        size = idx[eeg]["size"]
        X, resp, ident, onset = [], [], [], []
        for s0, rp, idn in tr:
            s = s0 - 1 + a                               # .vmrk positions are 1-based
            lo, hi = s * NCH * 2, (s + NS) * NCH * 2 - 1
            if s < 0 or hi >= size:
                continue
            buf = get(url, (lo, hi))
            used += len(buf)
            if used > LEFT:
                raise SystemExit(f"budget hit at {used / 1e6:.1f} MB")
            x = np.frombuffer(buf, dtype="<i2")
            if x.size != NS * NCH:
                continue
            X.append(x.reshape(NS, NCH).T)
            resp.append(rp)
            ident.append(idn)
            onset.append(s0)
        np.savez_compressed(dst, X=np.stack(X), resp=np.array(resp), ident=np.array(ident), onset=np.array(onset),
                            fs=FS, tmin=TMIN, scale_uv=0.1)
        with open(OUT / "fetch_log.jsonl", "a") as f:
            f.write(json.dumps(dict(sub=sub, n=len(X), bytes_total=used)) + "\n")
        print(sub, len(X), f"{used / 1e6:.1f} MB", flush=True)
    print(f"done, {used} bytes read")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "plan")
