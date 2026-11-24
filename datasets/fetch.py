"""Get the public datasets this project uses, on your own machine. Everything lands in datasets/local/, which git ignores.

    python3 -I datasets/fetch.py list                          # the catalogue, by tier
    python3 -I datasets/fetch.py index <id>                    # file list only (figshare, Zenodo, Dryad, OpenNeuro, zip directory): no data
    python3 -I datasets/fetch.py fetch <id> [--member PREFIX]  # a subset of one dataset we use
    python3 -I datasets/fetch.py fetch sleep_edfx --n 4        # the first 4 Sleep-EDF cassette nights (PSG + hypnogram)
    python3 -I datasets/fetch.py meta <id>                     # request-tier and reference-only sets: what it is and how to ask

Budget: the whole project may download 1.5 GB. Nearly every recording set is larger (ds005620 is 83 GB, the Tononi
DREAM set 8.4 GB), so `fetch` reads single members out of remote zips with HTTP range requests and refuses to go past
the budget. For the big sets you must name what you want with --member; run `index` first to see the names.
One request per second. Nothing fetched here is republished. The DREAM index's People.csv (contributor emails) is never fetched.
"""
import csv, json, re, struct, sys, time, urllib.parse, urllib.request, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "datasets"
LOCAL = HERE / "local"
UA = {"User-Agent": "open-mind-dataset-fetch (+https://github.com/HarshInvader/open-mind)"}
BUDGET = 1.5e9
# Budget log (outside this script):
# - ds001810 (2026-11-24): experiments/hypothesis_generator/fetch_ab_epochs.py range-read 8,391 T2-locked epochs
#   from 84 pre-tDCS blocks, exactly 1,254,488,064 bytes (1.2545 GB) of EEG plus small events/vhdr/channels files.
#   On disk, compressed: 0.63 GB in datasets/local/ds001810_epochs/. Inside the 1.5 GB budget; no exception used.
# - ds001785 (tactile): one-off exception approved by the coordinator only if the ds001810 kill test passes:
#   range-read epochs only, disk peak < 1 GB, exact GB to be logged here and in docs/RESEARCH_STATE.md.
CHENNU_ZIP = "https://api.repository.cam.ac.uk/server/api/core/bitstreams/e94a6722-da5b-4e53-8673-5e8ec106e0f7/content"

# id -> how to get the subset our results use.
#   ("figshare", article_id, [file names] or None)   whole files of a figshare article (None = all; only for small sets)
#   ("figzip", article_id)                            members of the article's zip(s), by range read; needs --member
#   ("zip", url)                                      members of one remote zip, by range read; needs --member
#   ("openneuro", dataset)                            files from the OpenNeuro S3 bucket; needs --member (a key prefix)
#   ("physionet", path, subdir)                       the first --n PSG records under subdir of a PhysioNet RECORDS list, with hypnograms
RECIPES = {
    "dream_index": ("figshare", 22133105, ["Datasets.csv", "Data records.csv"]),
    "dream_young_adults": ("figshare", 14899506, None),
    "dream_lode": ("figshare", 22147085, None),
    "dream_zhang_wamsley": ("figzip", 22226692),
    "dream_tononi": ("figzip", 23306054),
    "dream_multiple_awakenings": ("figzip", 22086266),
    "dream_data1": ("figzip", 24058740),
    "chennu2016": ("zip", CHENNU_ZIP),
    "ds005620": ("openneuro", "ds005620"),
    "ds004541": ("openneuro", "ds004541"),
    "ds006394": ("openneuro", "ds006394"),
    "sleep_edfx": ("physionet", "sleep-edfx/1.0.0/", "sleep-cassette/"),
}


def catalog():
    return list(csv.DictReader(open(HERE / "catalog.csv", encoding="utf-8")))


def row(i):
    r = {x["id"]: x for x in catalog()}.get(i)
    if not r:
        sys.exit(f"no catalogue id {i!r}; see `fetch.py list`")
    return r


def req(url, rng=None):
    time.sleep(1.0)
    h = dict(UA)
    if rng:
        h["Range"] = f"bytes={rng[0]}-{rng[1]}"
    return urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=120)


def get(url, rng=None):
    return req(url, rng).read()


def get_json(url):
    return json.loads(get(url))


def used_bytes():
    return sum(p.stat().st_size for p in LOCAL.rglob("*") if p.is_file()) if LOCAL.exists() else 0


def spend(n, what):
    left = BUDGET - used_bytes()
    if n > left:
        sys.exit(f"{what}: {n / 1e6:.0f} MB would exceed the 1.5 GB budget ({left / 1e6:.0f} MB left in datasets/local/)")


def size_of(url):
    r = req(url, (0, 0))
    cr = r.headers.get("Content-Range", "")
    return int(cr.split("/")[-1]) if "/" in cr else int(r.headers.get("Content-Length", 0))


# ---- remote zip, read by range
def zip_directory(url):
    """Central directory of a remote zip, read with two or three range requests. Returns total, [(name, offset, csize, method, usize)]."""
    total = size_of(url)
    tail = get(url, (max(0, total - 66000), total - 1))
    i = tail.rfind(b"PK\x05\x06")
    cd_size, cd_off = struct.unpack("<II", tail[i + 12:i + 20])
    if cd_off == 0xFFFFFFFF:  # zip64
        j = tail.rfind(b"PK\x06\x06")
        cd_size, cd_off = struct.unpack("<QQ", tail[j + 40:j + 56])
    cd = get(url, (cd_off, cd_off + cd_size - 1))
    out, p = [], 0
    while p < len(cd) and cd[p:p + 4] == b"PK\x01\x02":
        method, = struct.unpack("<H", cd[p + 10:p + 12])
        csize, usize, nlen, xlen, clen = struct.unpack("<IIHHH", cd[p + 20:p + 34])
        off, = struct.unpack("<I", cd[p + 42:p + 46])
        name = cd[p + 46:p + 46 + nlen].decode("utf-8", "replace")
        extra = cd[p + 46 + nlen:p + 46 + nlen + xlen]
        if 0xFFFFFFFF in (csize, usize, off):  # zip64 extra field
            q, vals = 0, []
            while q < len(extra):
                hid, ln = struct.unpack("<HH", extra[q:q + 4])
                if hid == 1:
                    vals = list(struct.unpack("<" + "Q" * (ln // 8), extra[q + 4:q + 4 + ln - ln % 8]))
                q += 4 + ln
            if usize == 0xFFFFFFFF and vals: usize = vals.pop(0)
            if csize == 0xFFFFFFFF and vals: csize = vals.pop(0)
            if off == 0xFFFFFFFF and vals: off = vals.pop(0)
        out.append((name, off, csize, method, usize))
        p += 46 + nlen + xlen + clen
    return total, out


def zip_member(url, off, csize, method):
    head = get(url, (off, off + 29))
    nlen, xlen = struct.unpack("<HH", head[26:30])
    start = off + 30 + nlen + xlen
    data = get(url, (start, start + csize - 1)) if csize else b""
    return zlib.decompress(data, -15) if method == 8 else data


def figshare_files(art):
    return [dict(name=f["name"], size=f["size"], url=f["download_url"]) for f in get_json(f"https://api.figshare.com/v2/articles/{art}")["files"]]


def openneuro_keys(ds, prefix=""):
    """Keys and sizes under ds/prefix in the public OpenNeuro bucket (S3 ListObjectsV2, no account)."""
    import xml.etree.ElementTree as ET
    ns = "{http://s3.amazonaws.com/doc/2006-03-01/}"
    out, token = [], None
    while True:
        u = f"https://s3.amazonaws.com/openneuro.org?list-type=2&prefix={urllib.parse.quote(ds + '/' + prefix)}"
        if token:
            u += "&continuation-token=" + urllib.parse.quote(token)
        x = ET.fromstring(get(u))
        out += [(c.find(ns + "Key").text, int(c.find(ns + "Size").text)) for c in x.iter(ns + "Contents")]
        t = x.find(ns + "NextContinuationToken")
        if t is None:
            return out
        token = t.text


# ---- commands
def cmd_list():
    rows = catalog()
    for tier, label in (("included", "In this repository (datasets/open/)"), ("fetch", "Public: fetch a subset or follow the link"),
                        ("request", "On request or behind an account: metadata only here"), ("reference-only", "No data record: cited only")):
        sel = [r for r in rows if r["tier"] == tier]
        print(f"\n{label}: {len(sel)}")
        for r in sel:
            flag = ("*" if r["used_by_us"] == "yes" else " ") + ("" if r["verified"] == "yes" else " (unverified)")
            print(f"  {r['id'][:26]:26}{flag[:1]} {r['title'][:90]}{flag[1:]}")
    print("\n* = used by our results.  `fetch <id>` works for:", ", ".join(sorted(RECIPES)))


def cmd_meta(i):
    r = row(i)
    for k in ("title", "tier", "origin", "terms", "size", "n", "labels", "serves_tasks", "notes"):
        if r[k]:
            print(f"{k:13} {r[k]}")
    if r["tier"] == "request":
        print("\nThis set is on request or behind an account. Agents never apply, sign up or write to anyone: the human lead decides and asks.")


def cmd_index(i):
    """File list only. Writes datasets/local/<id>/INDEX.json; downloads no data."""
    r = row(i)
    o, files = r["origin"], []
    kind = RECIPES.get(i, ("",))[0]
    if kind in ("figshare", "figzip"):
        files = figshare_files(RECIPES[i][1])
        for f in list(files):
            if kind == "figzip" and f["name"].endswith(".zip"):
                _, d = zip_directory(f["url"])
                files += [dict(name=f["name"] + "/" + n, size=u, compressed=c) for n, _, c, _, u in d]
    elif kind == "zip":
        total, d = zip_directory(RECIPES[i][1])
        files = [dict(name=n, size=u, compressed=c) for n, _, c, _, u in d]
        print(f"remote zip: {total / 1e6:.0f} MB, {len(files)} members")
    elif kind == "openneuro":
        files = [dict(name=k, size=s) for k, s in openneuro_keys(RECIPES[i][1])]
    elif kind == "physionet":
        base = "https://physionet.org/files/" + RECIPES[i][1]
        files = [dict(name=n) for n in get(base + "RECORDS").decode().split() if n.startswith(RECIPES[i][2])]
    elif "zenodo" in o:
        rec = o.rstrip("/").split("zenodo.")[-1]
        files = [dict(name=f["key"], size=f["size"]) for f in get_json(f"https://zenodo.org/api/records/{rec}").get("files", [])]
    elif "figshare" in o:
        art = o.rstrip("/").split("figshare.")[-1].split(".v")[0]
        files = figshare_files(art)
    elif "dryad" in o:
        doi = o.split("doi.org/")[-1]
        j = get_json("https://datadryad.org/api/v2/datasets/" + urllib.parse.quote("doi:" + doi, safe=""))
        v = get_json("https://datadryad.org" + j["_links"]["stash:version"]["href"] + "/files")
        files = [dict(name=f["path"], size=f["size"]) for f in v["_embedded"]["stash:files"]]
    elif "openneuro" in o:
        ds = o.split("openneuro.")[-1].split(".")[0]
        files = [dict(name=k, size=s) for k, s in openneuro_keys(ds)]
    else:
        sys.exit(f"{i}: no machine-readable index; open {o}")
    files = [f for f in files if f["name"] != "People.csv"]
    out = LOCAL / i; out.mkdir(parents=True, exist_ok=True)
    json.dump(dict(id=i, origin=o, files=files), open(out / "INDEX.json", "w"), indent=1)
    print(f"{len(files)} files listed, {sum(f.get('size') or 0 for f in files) / 1e6:.1f} MB -> datasets/local/{i}/INDEX.json")


def cmd_fetch(i, members, n):
    r = row(i)
    if r["tier"] in ("request", "reference-only"):
        return cmd_meta(i)
    if i not in RECIPES:
        sys.exit(f"{i}: no fetch recipe (not used by our results yet). `index {i}` lists its files; origin: {r['origin']}")
    out = LOCAL / i; out.mkdir(parents=True, exist_ok=True)
    kind, *a = RECIPES[i]
    if kind in ("figzip", "zip", "openneuro") and not members:
        sys.exit(f"{i} is large: name what you want with --member PREFIX (see `index {i}`)")
    if kind == "figshare":
        art, names = a
        for f in figshare_files(art):
            if (names is None or f["name"] in names) and f["name"] != "People.csv":
                spend(f["size"], i)
                (out / f["name"]).write_bytes(get(f["url"]))
    elif kind in ("figzip", "zip"):
        urls = [f["url"] for f in figshare_files(a[0]) if f["name"].endswith(".zip")] if kind == "figzip" else [a[0]]
        got = 0
        for url in urls:
            _, d = zip_directory(url)
            want = [m for m in d if any(m[0].startswith(p) or m[0].split("/")[-1].startswith(p) for p in members) and not m[0].endswith("/")]
            spend(sum(m[2] for m in want), i)
            for name, off, csize, method, _ in want:
                p = out / name; p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(zip_member(url, off, csize, method)); got += 1
        print(f"{got} zip members read by range")
    elif kind == "openneuro":
        keys = [(k, s) for p in members for k, s in openneuro_keys(a[0], p)]
        spend(sum(s for _, s in keys), i)
        for k, _ in keys:
            p = out / k.split("/", 1)[1]; p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(get("https://s3.amazonaws.com/openneuro.org/" + urllib.parse.quote(k)))
        print(f"{len(keys)} files from OpenNeuro")
    elif kind == "physionet":
        base, sub = "https://physionet.org/files/" + a[0], a[1]
        names = [x for x in get(base + "RECORDS").decode().split() if x.startswith(sub) and x.endswith("-PSG.edf")][:n]
        listing = get(base + sub).decode("utf-8", "replace")
        for psg in names:
            stem = psg[len(sub):len(sub) + 7]  # SC4001E0-PSG.edf -> hypnogram SC4001E?-Hypnogram.edf
            hyp = next(iter(sorted(set(re.findall(r'href="(' + stem + r'[A-Z0-9]-Hypnogram\.edf)"', listing)))), None)
            for f in [psg] + ([sub + hyp] if hyp else []):
                url = base + f
                spend(size_of(url), i)
                (out / f.split("/")[-1]).write_bytes(get(url))
        print(f"{len(names)} nights")
    json.dump(dict(id=i, origin=r["origin"], terms=r["terms"], recipe=[kind, *map(str, a)], members=members, n=n,
                   fetched=time.strftime("%Y-%m-%d")), open(out / "SOURCE.json", "w"), indent=1)
    print(f"{i}: done -> datasets/local/{i}/  ({used_bytes() / 1e6:.0f} MB of the 1.5 GB budget used)")


if __name__ == "__main__":
    a = sys.argv[1:] or ["list"]
    mem = [a[k + 1] for k in range(len(a) - 1) if a[k] == "--member"]
    n = int(a[a.index("--n") + 1]) if "--n" in a else 2
    if a[0] == "list":
        cmd_list()
    elif a[0] == "fetch" and len(a) > 1:
        cmd_fetch(a[1], mem, n)
    elif a[0] in ("index", "meta") and len(a) > 1:
        {"index": cmd_index, "meta": cmd_meta}[a[0]](a[1])
    else:
        print(__doc__)
