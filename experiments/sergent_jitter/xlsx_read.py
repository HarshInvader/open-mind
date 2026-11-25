"""Minimal stdlib reader for an untrusted .xlsx (zip + XML only, no macros, no external packages).

    python -I xlsx_read.py <file.xlsx> list            # sheet names, sizes, first rows
    python -I xlsx_read.py <file.xlsx> dump <sheet> <out.csv>
"""
import csv, re, sys, zipfile
import xml.etree.ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
RNS = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def col_idx(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def open_book(path):
    z = zipfile.ZipFile(path)
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            ss.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels")).iter(RNS + "Relationship")}
    sheets = []
    for s in wb.find("m:sheets", NS).findall("m:sheet", NS):
        tgt = rels[s.get("{%s}id" % NS["r"])]
        tgt = tgt.lstrip("/")
        sheets.append((s.get("name"), tgt if tgt.startswith("xl/") else "xl/" + tgt))
    return z, ss, sheets


def rows(z, ss, target):
    root = ET.fromstring(z.read(target))
    for row in root.iter("{%s}row" % NS["m"]):
        out = {}
        for c in row.findall("m:c", NS):
            v = c.find("m:v", NS)
            t = c.get("t")
            if t == "inlineStr":
                val = "".join(x.text or "" for x in c.iter("{%s}t" % NS["m"]))
            elif v is None:
                continue
            elif t == "s":
                val = ss[int(v.text)]
            else:
                val = v.text
            out[col_idx(c.get("r"))] = val
        if out:
            yield [out.get(i, "") for i in range(max(out) + 1)]


def main():
    path, cmd = sys.argv[1], sys.argv[2]
    z, ss, sheets = open_book(path)
    if cmd == "list":
        for name, tgt in sheets:
            R = list(rows(z, ss, tgt))
            print("==", repr(name), "rows", len(R), "max cols", max((len(r) for r in R), default=0))
            for r in R[:5]:
                print("   ", r[:12])
    elif cmd == "dump":
        name, outp = sys.argv[3], sys.argv[4]
        tgt = dict(sheets)[name]
        with open(outp, "w", newline="") as f:
            csv.writer(f).writerows(rows(z, ss, tgt))


if __name__ == "__main__":
    main()
