"""Prior-art search for item 3 (cross-paradigm awareness decoder). OpenAlex metadata only.
Key read from OPENALEX_API_KEY or ~/.config/openalex/api_key; never printed or stored.
    python -I oa_search.py OUT.jsonl
"""
import json, os, sys, urllib.parse, urllib.request

QUERIES = [
    "decoding conscious perception across tasks generalization EEG",
    "cross-task decoding visual awareness EEG MEG",
    "supramodal signature conscious perception decoding",
    "attentional blink decoding seen unseen EEG multivariate",
    "backward masking decoding awareness temporal generalization",
    "neural signature of consciousness generalizes across paradigms",
    "cross-dataset EEG decoding perceptual awareness transfer",
    "P3b no-report decoding awareness generalization",
]


def key():
    k = os.environ.get("OPENALEX_API_KEY", "").strip()
    p = os.path.expanduser("~/.config/openalex/api_key")
    if not k and os.path.exists(p):
        k = open(p).read().strip()
    return k


def main(out):
    k = key()
    seen = {}
    for q in QUERIES:
        params = {"search": q, "per-page": "25", "filter": "type:article,from_publication_date:2010-01-01",
                  "select": "id,doi,title,publication_year,cited_by_count,primary_location,authorships,type"}
        if k:
            params["api_key"] = k
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": "open-research-site/1.0"})
        data = json.load(urllib.request.urlopen(req, timeout=60))
        for w in data.get("results", []):
            if w["id"] in seen:
                seen[w["id"]]["queries"].append(q); continue
            src = ((w.get("primary_location") or {}).get("source") or {})
            seen[w["id"]] = {"doi": w.get("doi"), "title": w.get("title"), "year": w.get("publication_year"),
                             "cites": w.get("cited_by_count"), "venue": src.get("display_name"),
                             "first_author": (w["authorships"][0]["author"]["display_name"] if w.get("authorships") else ""),
                             "queries": [q]}
    with open(out, "w") as f:
        for v in sorted(seen.values(), key=lambda v: -(v["cites"] or 0)):
            f.write(json.dumps(v, ensure_ascii=False) + "\n")
    print(len(seen), "works")


if __name__ == "__main__":
    main(sys.argv[1])
