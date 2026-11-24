"""Part A1: frozen Europe PMC search. Saves up to 200 records with abstracts to datasets/local/splitfirst_abstracts/
(gitignored) and a local index. Prints counts only (the orchestrator does not read titles or abstracts).

    python -I search.py
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "datasets" / "local" / "splitfirst_abstracts"
PREV = ROOT / "experiments" / "theory_postcutoff" / "draft_items.json"
UA = {"User-Agent": "open-research-site/1.0"}
QUERY = ('(consciousness OR "conscious perception" OR "conscious access" OR "visual awareness" OR "perceptual awareness" '
         'OR "disorders of consciousness" OR "loss of consciousness" OR "inattentional blindness" OR "backward masking" '
         'OR "no-report" OR dreaming OR "global workspace" OR "integrated information") '
         'AND FIRST_PDATE:[2026-07-01 TO 2026-11-24] AND HAS_ABSTRACT:Y')
N = 200
PREV_DOIS_EXTRA = []   # P02-P04 DOIs are read from the earlier pool's abstract files' index below if present


def get(params):
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(params)
    for k in range(6):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except Exception:
            if k == 5:
                raise
            time.sleep(10 * (k + 1))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    prev = {it["doi"].lower() for it in json.load(open(PREV))["items"] if it.get("doi")}
    recs, cursor = [], "*"
    while len(recs) < N:
        d = get(dict(query=QUERY, resultType="core", format="json", pageSize=100, cursorMark=cursor))
        res = d.get("resultList", {}).get("result", [])
        if not res:
            break
        recs += res
        nxt = d.get("nextCursorMark")
        if not nxt or nxt == cursor:
            break
        cursor = nxt
        time.sleep(1)
    total = d.get("hitCount")
    recs = recs[:N]
    index, dropped = [], 0
    for k, r in enumerate(recs):
        doi = (r.get("doi") or "").lower()
        if doi and doi in prev:
            dropped += 1
            continue
        rid = f"S{k + 1:03d}"
        (OUT / f"{rid}.txt").write_text(f"{r.get('title', '')}\n\n{r.get('abstractText', '')}\n", encoding="utf-8")
        index.append(dict(id=rid, rank=k + 1, doi=doi, source=r.get("source"), ext_id=r.get("id"),
                          first_pdate=r.get("firstPublicationDate"), pub_type=r.get("pubTypeList", {}).get("pubType")))
    (OUT / "index.json").write_text(json.dumps(dict(query=QUERY, hit_count=total, retrieved=len(recs),
                                                    dropped_prev_pool=dropped, records=index), indent=1))
    print(f"hits {total}; kept {len(index)} of first {len(recs)}; dropped (earlier pool) {dropped}")


if __name__ == "__main__":
    main()
