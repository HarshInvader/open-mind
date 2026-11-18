"""Fetch open full text from Europe PMC (if any) for a DOI and print sentences matching keywords.
Usage: python3 -I epmc_fulltext_grep.py DOI kw1,kw2,... [maxper]"""
import json, sys, re, urllib.request, urllib.parse, os
d, kws = sys.argv[1], sys.argv[2].lower().split(",")
maxper = int(sys.argv[3]) if len(sys.argv) > 3 else 4
UA = {"User-Agent": "open-mind-check/1.0"}
cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw_ft")
os.makedirs(cache, exist_ok=True)
fn = os.path.join(cache, re.sub(r"[^A-Za-z0-9]", "_", d) + ".txt")
if not os.path.exists(fn):
    q = urllib.parse.quote(f'DOI:"{d}"')
    r = json.load(urllib.request.urlopen(urllib.request.Request(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&resultType=lite&format=json", headers=UA), timeout=30))
    res = r["resultList"]["result"]
    pmcid = res[0].get("pmcid") if res else None
    if not pmcid: print(f"{d}: no PMC full text"); sys.exit()
    try:
        x = urllib.request.urlopen(urllib.request.Request(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML", headers=UA), timeout=60).read().decode("utf8", "ignore")
    except Exception:
        x = urllib.request.urlopen(urllib.request.Request(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid[3:]}", headers=UA), timeout=60).read().decode("utf8", "ignore")
    x = re.sub(r"<ref-list.*?</ref-list>", " ", x, flags=re.S)
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x))
    open(fn, "w").write(t)
t = open(fn).read()
sents = re.split(r"(?<=[.!?])\s+(?=[A-Z])", t)
print(f"== {d} ({len(t)} chars)")
for k in kws:
    hits = [s for s in sents if k in s.lower()]
    print(f"-- {k}: {len(hits)} hits")
    for s in hits[:maxper]: print("   * " + s[:420])
