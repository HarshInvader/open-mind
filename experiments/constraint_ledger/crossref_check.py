"""Resolve DOIs on Crossref; print title, first author, year, journal, volume, pages.
Usage: python3 -I crossref_check.py dois.txt [out.jsonl]   (one DOI per line; '#' comments)
       python3 -I crossref_check.py --search "query words"
"""
import json, sys, time, urllib.request, urllib.parse

UA = {"User-Agent": "open-mind-citation-check/1.0"}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def summ(m):
    a = m.get("author") or [{}]
    y = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
    return {"doi": m.get("DOI"), "title": " ".join(m.get("title") or [""]).replace("\n", " "),
            "first": a[0].get("family"), "n_auth": len(m.get("author") or []), "year": y,
            "journal": (m.get("container-title") or [""])[0], "vol": m.get("volume"), "page": m.get("page") or m.get("article-number")}

if sys.argv[1] == "--search":
    q = urllib.parse.quote(" ".join(sys.argv[2:]))
    for it in get(f"https://api.crossref.org/works?query.bibliographic={q}&rows=4")["message"]["items"]:
        s = summ(it); print(f"{s['doi']} | {s['first']} {s['year']} | {s['title'][:110]} | {s['journal']} {s['vol']}:{s['page']}")
    sys.exit()
out = open(sys.argv[2], "a") if len(sys.argv) > 2 else None
for line in open(sys.argv[1]):
    d = line.split("#")[0].strip()
    if not d: continue
    try:
        s = summ(get("https://api.crossref.org/works/" + urllib.parse.quote(d))["message"]); s["ok"] = True
    except Exception as e:
        s = {"doi": d, "ok": False, "err": str(e)[:60]}
    print(f"{d} | {s.get('first')} {s.get('year')} | {s.get('title','')[:100]} | {s.get('journal','')} {s.get('vol')}:{s.get('page')}" if s["ok"] else f"{d} | FAIL {s['err']}")
    if out: out.write(json.dumps(s) + "\n")
    time.sleep(1.0)
