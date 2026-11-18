"""Print Europe PMC abstract for each DOI. Usage: python3 -I epmc_abstract.py DOI [DOI...] [--n 1500]"""
import json, sys, time, re, urllib.request, urllib.parse
n = 1500
args = sys.argv[1:]
if "--n" in args:
    i = args.index("--n"); n = int(args[i+1]); del args[i:i+2]
for d in args:
    q = urllib.parse.quote(f'DOI:"{d}"')
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&resultType=core&format=json"
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "open-mind-check/1.0"}), timeout=30))
        res = r["resultList"]["result"]
        if not res: print(f"## {d}: NOT IN EPMC\n"); continue
        a = res[0]; ab = re.sub("<[^>]+>", "", a.get("abstractText", "(no abstract)"))
        print(f"## {d} | {a.get('authorString','')[:80]} | {a.get('pubYear')} | {a.get('title')}\n{ab[:n]}\n")
    except Exception as e:
        print(f"## {d}: ERR {e}\n")
    time.sleep(0.4)
