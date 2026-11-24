"""Parse Cohen 2024 BrainVision markers into trials, and check the seen/unseen mapping against the authors' sheet.

Marker structure (report block; no-report adds 60 to the face code and uses S253):
  S101-S140 face onset (identity 1-40) | S150 mask only | S151/S152 other
  SOA code at mask onset: S16/S33/S49/S66/S83 (= SOA 17/33/50/67/83 ms)
  S153 100 ms after mask onset | response S1 / S2 (report block only)

    python -I count_trials.py    # -> trials.csv (one row per trial), trial_counts.csv, mapping check
"""
import csv, glob, re, statistics as st, sys, zipfile, xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "datasets" / "local" / "cohen2024"
HERE = Path(__file__).resolve().parent
SOA = {16: 17, 33: 33, 49: 50, 66: 67, 83: 83}


def subjects():
    """vhdr name -> (subject id, eeg file, marker file); the header names the real data file."""
    out = {}
    for h in sorted(D.glob("delcul*.vhdr")):
        t = h.read_text(errors="replace")
        eeg = re.search(r"DataFile=(\S+)", t).group(1)
        mrk = re.search(r"MarkerFile=(\S+)", t).group(1)
        out[h.stem.replace("delcul", "")] = (h.name, eeg, mrk)
    return out


def trials(mrk):
    t = (D / mrk).read_text(encoding="utf-8", errors="replace")
    ev = []
    for m in re.finditer(r"Mk\d+=Stimulus,S\s*(\d+),(\d+),", t):
        ev.append((int(m.group(1)), int(m.group(2))))
    rows, i = [], 0
    while i < len(ev):
        c, s = ev[i]
        face_rep, face_nr = 101 <= c <= 140, 161 <= c <= 200
        other = c in (150, 151, 152, 250, 251, 252)
        if not (face_rep or face_nr or other):
            i += 1
            continue
        block = "report" if c < 160 else "noreport"
        kind = "face" if (face_rep or face_nr) else str(c)
        ident = (c - 100 if face_rep else c - 160) if kind == "face" else 0
        soa, mask, resp, j = None, None, None, i + 1
        while j < len(ev) and j <= i + 3:
            cj, sj = ev[j]
            if cj in SOA and soa is None:
                soa, mask = SOA[cj], sj
            elif cj in (153, 253):
                j += 1
                break
            elif cj >= 100:
                break
            j += 1
        rt = None
        if j < len(ev) and ev[j][0] in (1, 2) and block == "report":
            resp, rt = ev[j][0], ev[j][1] - s
        rows.append(dict(block=block, kind=kind, ident=ident, soa=soa or "", onset=s, mask=mask or "",
                         resp=resp or "", rt_samples=rt if rt is not None else ""))
        i = j
    return rows


def sheet():
    z = zipfile.ZipFile(D / "_behaviour.xlsx")
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    ss = ["".join(x.itertext()) for x in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns)]
    out = {}
    for r in ET.fromstring(z.read("xl/worksheets/sheet1.xml")).findall(".//m:row", ns)[2:]:
        v = []
        for c in r.findall("m:c", ns):
            x = c.find("m:v", ns)
            x = x.text if x is not None else ""
            v.append(ss[int(x)] if c.get("t") == "s" else x)
        if v and v[0].isdigit():
            out[v[0]] = {s: float(v[k + 1]) for k, s in enumerate((17, 33, 50, 67, 83)) if v[k + 1] != ""}
    return out


def main():
    subs, sh = subjects(), sheet()
    allrows, counts, diffs = [], [], []
    for sid, (_, eeg, mrk) in subs.items():
        rows = trials(mrk)
        for r in rows:
            r["sub"] = sid
        allrows += rows
        rep = [r for r in rows if r["block"] == "report" and r["kind"] == "face"]
        c = dict(sub=sid, eeg=eeg)
        for s in (17, 33, 50, 67, 83):
            seen = sum(1 for r in rep if r["soa"] == s and r["resp"] == 1)
            uns = sum(1 for r in rep if r["soa"] == s and r["resp"] == 2)
            c[f"soa{s}_seen"], c[f"soa{s}_unseen"] = seen, uns
            if sid in sh and s in sh[sid] and seen + uns:
                diffs.append(abs(seen / (seen + uns) - sh[sid][s]))
        mo = [r for r in rows if r["block"] == "report" and r["kind"] == "150"]
        c["maskonly_seen"] = sum(r["resp"] == 1 for r in mo)
        c["maskonly_unseen"] = sum(r["resp"] == 2 for r in mo)
        c["nr_face_soa50"] = sum(1 for r in rows if r["block"] == "noreport" and r["kind"] == "face" and r["soa"] == 50)
        counts.append(c)
    with open(HERE / "trials.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["sub", "block", "kind", "ident", "soa", "onset", "mask", "resp", "rt_samples"])
        w.writeheader()
        w.writerows(allrows)
    with open(HERE / "trial_counts.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(counts[0]))
        w.writeheader()
        w.writerows(counts)
    s50 = [(c["soa50_seen"], c["soa50_unseen"]) for c in counts]
    print(f"subjects {len(counts)}; sheet rows matched {sum(1 for c in counts if c['sub'] in sh)}")
    print(f"mapping check (resp 1 = seen): max |hit rate - sheet| = {max(diffs):.4f} over {len(diffs)} cells")
    print(f"SOA50 seen/unseen median {st.median(a for a, _ in s50)}/{st.median(b for _, b in s50)}, "
          f"totals {sum(a for a, _ in s50)}/{sum(b for _, b in s50)}")
    for thr in (20, 30, 40):
        print(f"  subjects with >= {thr} per cell: {sum(1 for a, b in s50 if a >= thr and b >= thr)}")


if __name__ == "__main__":
    main()
