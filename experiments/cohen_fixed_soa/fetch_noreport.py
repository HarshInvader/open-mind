"""Item 4 (Cohen no-report block, option B). Range-read the trials the double difference needs from Cohen et al. 2024 (OSF 6d5av).

    python -I fetch_noreport.py plan     # trial list, bytes, disk check; no network
    python -I fetch_noreport.py fetch    # -> datasets/local/cohen2024_nr_epochs/<sub>.npz (resumes per subject)

Trials (report-block face SOA-50 epochs are already on disk from fetch_epochs.py):
  - no-report face trials at SOA 50 (all of them);
  - mask-only trials, 60 per subject per block (report S150, no-report S250), picked label-free as
    round(linspace(0, n-1, 60)) over the block's mask-only trials in time order.
Time-locking: S150/S250 mark MASK onset (S153/S253 follows 50 samples later, as after the mask on face trials).
On SOA-50 face trials the mask starts 25 samples (50 ms) after the face. Mask-only epochs are therefore locked to
S150/S250 - 25 samples, a virtual face onset, so the mask sits at +50 ms in every epoch.
Epoch -0.1 to +0.3 s (200 samples at 500 Hz, 63 channels, int16 x 0.1 uV, multiplexed): 25,200 bytes per trial.
One HTTP Range request per trial, at most one request per second. Whole .eeg files are never downloaded.
Guards: total bytes <= BUDGET; stops before a subject if free disk after it would fall below 10 GB.
Downloaded bytes are untrusted data: parsed as int16, never executed.
"""
import csv, json, re, shutil, sys, time, urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "datasets" / "local" / "cohen2024"
OUT = ROOT / "datasets" / "local" / "cohen2024_nr_epochs"
HERE = Path(__file__).resolve().parent
UA = {"User-Agent": "open-research-site/1.0"}
TMIN, TMAX, FS, NCH = -0.1, 0.3, 500, 63
NS = int(round((TMAX - TMIN) * FS))
PER = NS * NCH * 2
MASK_SHIFT = 25                     # samples from virtual face onset to mask onset at SOA 50
N_MASK = 60
BUDGET = 260_000_000                # option B is 250,588,800 bytes
MIN_FREE = 10 * 1024 ** 3
_last = [0.0]


def get(url, rng):
    h = dict(UA, Range=f"bytes={rng[0]}-{rng[1]}")
    for attempt in range(5):
        try:
            wait = 1.0 - (time.time() - _last[0])
            if wait > 0:
                time.sleep(wait)
            _last[0] = time.time()
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
    """sub -> (eeg name, [(epoch zero sample 1-based, cond, block, marker sample, ident)])."""
    rows = list(csv.DictReader(open(HERE / "trials.csv")))
    out = {}
    for r in rows:
        if r["block"] == "noreport" and r["kind"] == "face" and r["soa"] == "50":
            out.setdefault(r["sub"], []).append((int(r["onset"]), "face50", "noreport", int(r["onset"]), int(r["ident"])))
    for blk, code in (("report", "150"), ("noreport", "250")):
        by = {}
        for r in rows:
            if r["block"] == blk and r["kind"] == code:
                by.setdefault(r["sub"], []).append(int(r["onset"]))
        for sub, ons in by.items():
            ons = sorted(ons)
            assert len(ons) >= N_MASK, (sub, blk, len(ons))
            pick = sorted(set(int(round(v)) for v in np.linspace(0, len(ons) - 1, N_MASK)))
            assert len(pick) == N_MASK
            for i in pick:
                out.setdefault(sub, []).append((ons[i] - MASK_SHIFT, "mask", blk, ons[i], 0))
    eeg = {}
    for h in D.glob("delcul*.vhdr"):
        t = h.read_text(errors="replace")
        assert "BinaryFormat=INT_16" in t and "MULTIPLEXED" in t and "SamplingInterval=2000" in t
        assert f"NumberOfChannels={NCH}" in t
        res = [float(m.group(1)) for m in re.finditer(r"^Ch\d+=[^,]*,[^,]*,([\d.]+),", t, re.M)]
        assert len(res) == NCH and set(res) == {0.1}, h.name
        eeg[h.stem.replace("delcul", "")] = re.search(r"DataFile=(\S+)", t).group(1)
    return {s: (eeg[s], sorted(tr)) for s, tr in sorted(out.items())}


def main(mode):
    p = plan()
    n = sum(len(t) for _, t in p.values())
    cnt = {}
    for _, tr in p.values():
        for t in tr:
            cnt[(t[2], t[1])] = cnt.get((t[2], t[1]), 0) + 1
    free = shutil.disk_usage(ROOT).free
    print(f"subjects {len(p)}, trials {n}, {cnt}, projected {n * PER:,} bytes (budget {BUDGET:,}); "
          f"free disk {free / 1e9:.1f} GB; projected time {n / 3600:.2f} h at 1 req/s")
    assert n * PER <= BUDGET, "over budget"
    if mode != "fetch":
        return
    idx = json.loads((HERE / "osf_index.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    a = int(round(TMIN * FS))
    used = 0
    for sub, (eeg, tr) in p.items():
        dst = OUT / f"{sub}.npz"
        if dst.exists():
            try:
                with np.load(dst) as d:
                    used += d["X"].size * 2
                continue
            except Exception:                            # partial write from a killed run: fetch again
                dst.unlink()
        if shutil.disk_usage(ROOT).free - len(tr) * PER < MIN_FREE:
            raise SystemExit(f"disk guard: free disk would fall below 10 GB before subject {sub}")
        url, size = idx[eeg]["url"], idx[eeg]["size"]
        X, cond, block, marker, ident = [], [], [], [], []
        for z0, c, b, mk, idn in tr:
            s = z0 - 1 + a                                   # .vmrk positions are 1-based
            lo, hi = s * NCH * 2, (s + NS) * NCH * 2 - 1
            if s < 0 or hi >= size:
                continue
            buf = get(url, (lo, hi))
            used += len(buf)
            if used > BUDGET:
                raise SystemExit(f"budget hit at {used:,} bytes")
            x = np.frombuffer(buf, dtype="<i2")
            if x.size != NS * NCH:
                continue
            X.append(x.reshape(NS, NCH).T)
            cond.append(c); block.append(b); marker.append(mk); ident.append(idn)
        tmp = OUT / f"{sub}.tmp.npz"
        np.savez_compressed(tmp, X=np.stack(X), cond=np.array(cond), block=np.array(block), marker=np.array(marker),
                            ident=np.array(ident), fs=FS, tmin=TMIN, scale_uv=0.1, mask_shift=MASK_SHIFT)
        tmp.replace(dst)                                 # atomic: a kill never leaves a partial <sub>.npz
        with open(OUT / "fetch_log.jsonl", "a") as f:
            f.write(json.dumps(dict(sub=sub, n=len(X), bytes_total=used)) + "\n")
        print(sub, len(X), f"{used / 1e6:.1f} MB", flush=True)
    print(f"done, {used} bytes read")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "plan")
