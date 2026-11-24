"""Cohen et al. 2024 (Cereb Cortex, doi:10.1093/cercor/bhae415) raw EEG from OSF node 6d5av.

    python -I fetch_cohen.py index      # list Data/EEG files -> osf_index.json (sizes, download URLs)
    python -I fetch_cohen.py headers    # .vhdr + .vmrk only (about 10 MB) -> datasets/local/cohen2024/

Epochs are range-read later by a separate, budgeted step; whole .eeg files are never downloaded.
At most one request per second. Downloaded files are untrusted data: parse them, never execute them.
"""
import json, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "datasets" / "local" / "cohen2024"
HERE = Path(__file__).resolve().parent
UA = {"User-Agent": "open-research-site/1.0"}
API = "https://api.osf.io/v2/nodes/6d5av/files/osfstorage/"
_last = [0.0]


def get(url, raw=False):
    wait = 1.0 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                _last[0] = time.time()
                b = r.read()
                return b if raw else json.loads(b)
        except Exception:
            time.sleep(2 ** attempt)
    raise RuntimeError(url)


def listing(url):
    out = []
    while url:
        d = get(url)
        out += d["data"]
        url = d["links"].get("next")
    return out


def index():
    root = listing(API + "?page%5Bsize%5D=100")
    data = next(x for x in root if x["attributes"]["name"] == "Data")
    sub = listing(data["relationships"]["files"]["links"]["related"]["href"] + "?page%5Bsize%5D=100")
    eeg = next(x for x in sub if x["attributes"]["name"] == "EEG")
    files = listing(eeg["relationships"]["files"]["links"]["related"]["href"] + "?page%5Bsize%5D=100")
    idx = {x["attributes"]["name"]: dict(size=x["attributes"]["size"], url=x["links"]["download"]) for x in files}
    beh = next((x for x in sub if x["attributes"]["name"].endswith(".xlsx")), None)
    if beh:
        idx["_behaviour.xlsx"] = dict(size=beh["attributes"]["size"], url=beh["links"]["download"])
    (HERE / "osf_index.json").write_text(json.dumps(idx, indent=1, sort_keys=True) + "\n")
    print(len(idx), "files;", sum(v["size"] for k, v in idx.items() if k.endswith(".eeg")) / 1e9, "GB of .eeg")


def headers():
    idx = json.loads((HERE / "osf_index.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for name, v in sorted(idx.items()):
        if not (name.endswith(".vhdr") or name.endswith(".vmrk") or name.endswith(".xlsx")):
            continue
        dst = OUT / name
        if not dst.exists():
            dst.write_bytes(get(v["url"], raw=True))
        n += 1
    print(n, "header/marker files in", OUT)


if __name__ == "__main__":
    {"index": index, "headers": headers}[sys.argv[1]]()
