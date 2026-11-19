"""Step 1 of task #42: label-blind file audit of the DREAM packages. Plan: docs/PLAN_2026-11-19_experience_benchmark.md

  python3 -I experiments/experience_benchmark/audit.py      -> audit.json

Reads only zip central directories and the first header bytes of EDF files (HTTP range reads).
No signal samples are read, so no feature can be related to a label. Awakening counts per
class come from the public DREAM metadata (experiments/dataset_audit/dream_records.csv),
which this project already holds.
Untrusted data: headers are parsed as ASCII fields only.
"""
import collections
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "experiments", "t1_dream"))
from ziprange import RemoteZip  # noqa: E402

FS = "https://ndownloader.figshare.com/files/"
# set id -> (name, zip download urls, exposed before this task?)
PKGS = {
    "9": ("Multiple awakenings (Rome)", [FS + "62751148"], False),
    "3": ("LODE", [FS + "39373088"], False),
    "16": ("DATA1 (Noreika)", [FS + "42196143"], False),
    "17": ("Aamodt evening", [FS + "43588656"], False),
    "18": ("Aamodt morning", [FS + "43588551"], False),
    "1": ("Zhang & Wamsley 2019", [FS + "39504757"], True),
    "11": ("Dream_YoungAdults (Rome)", [FS + "39673915"], True),
    "13": ("Tononi Serial Awakenings (s02 zip only, as a sample)", [FS + "41091467"], True),
}


def edf_header(z, member):
    h0 = z.read(member, max_out=256)
    ns = int(h0[252:256].decode("ascii", "replace").strip())
    h = z.read(member, max_out=256 * (ns + 1))
    f = lambda off, w: [h[256 + off * ns + i * w: 256 + off * ns + (i + 1) * w].decode("ascii", "replace").strip()
                        for i in range(ns)]
    labels = f(0, 16)
    # field offsets in units of ns: label 16, transducer 80, dim 8, pmin 8, pmax 8, dmin 8, dmax 8, prefilt 80, nsamp 8
    o = 16 + 80
    dims = [h[256 + o * ns + i * 8: 256 + o * ns + (i + 1) * 8].decode("ascii", "replace").strip() for i in range(ns)]
    o2 = 16 + 80 + 8 * 5
    pref = [h[256 + o2 * ns + i * 80: 256 + o2 * ns + (i + 1) * 80].decode("ascii", "replace").strip() for i in range(ns)]
    o3 = o2 + 80
    nsamp = [int(h[256 + o3 * ns + i * 8: 256 + o3 * ns + (i + 1) * 8].decode("ascii", "replace").strip() or 0)
             for i in range(ns)]
    rec_dur = float(h0[244:252].decode("ascii", "replace").strip() or 0)
    nrec = int(h0[236:244].decode("ascii", "replace").strip() or -1)
    return {"n_signals": ns, "labels": labels, "dims": sorted(set(dims)), "prefilter": sorted(set(pref))[:6],
            "fs": sorted({round(n / rec_dur, 3) for n in nsamp}) if rec_dur else None,
            "duration_s": nrec * rec_dur}


def main():
    recs = list(csv.DictReader(open(os.path.join(REPO, "experiments", "dataset_audit", "dream_records.csv"))))
    out = {}
    for sid, (name, urls, exposed) in PKGS.items():
        r = [x for x in recs if x["Set ID"] == sid]
        stage = lambda s: "N3" if s.startswith("N3") else s
        cnt = collections.Counter(f"{stage(x['Last sleep stage'])}|{x['Experience']}" for x in r)
        subj = collections.defaultdict(lambda: collections.Counter())
        for x in r:
            if stage(x["Last sleep stage"]) == "N2" and x["Experience"] in ("Experience", "No experience"):
                subj[x["Subject ID"]][x["Experience"]] += 1
        both = sum(1 for c in subj.values() if c["Experience"] and c["No experience"])
        info = {"name": name, "exposed_before": exposed, "n_records_meta": len(r), "counts": dict(sorted(cnt.items())),
                "N2_subjects": len(subj), "N2_subjects_with_both_classes": both,
                "meta_fs": sorted({x["EEG sample rate"] for x in r}), "meta_nch": sorted({x["Number of EEG channels"] for x in r}),
                "meta_min_duration_s": min(float(x["Duration"] or 0) for x in r)}
        try:
            z = RemoteZip(urls[0])
            edfs = [m for m in z.members if m.lower().endswith(".edf")]
            other = collections.Counter(os.path.splitext(m)[1].lower() for m in z.members if not m.lower().endswith(".edf"))
            base = {os.path.basename(m) for m in edfs}
            meta_files = {os.path.basename(x["Filename"]) for x in r}
            info.update({"zip_GB": round(z.size / 1e9, 3), "n_edf": len(edfs), "other_ext": dict(other.most_common(6)),
                         "meta_files_found": len(meta_files & base), "meta_files_total": len(meta_files),
                         "edf_GB_uncompressed": round(sum(z.members[m][2] for m in edfs) / 1e9, 3),
                         "compressed": sorted({z.members[m][0] for m in edfs})})
            if edfs:
                info["example_edf"] = edfs[0]
                info["header"] = edf_header(z, edfs[0])
            info["header_bytes_fetched"] = z.bytes_fetched
        except Exception as e:  # noqa: BLE001
            info["error"] = repr(e)[:200]
        out[sid] = info
        print(sid, json.dumps({k: v for k, v in info.items() if k not in ("header",)})[:600], flush=True)
        if "header" in info:
            print("   header", json.dumps(info["header"])[:700], flush=True)
    json.dump(out, open(os.path.join(HERE, "audit.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
