"""Write docs/library/LIBRARY.md from docs/library/library.json.

Run: python3 -I docs/library/make_library_md.py
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
RANK = {"core": 0, "useful": 1, "context": 2}


def main():
    data = json.loads((HERE / "library.json").read_text())
    papers = data["papers"]
    n_full = sum(p["read_depth"] == "full" for p in papers)
    out = [
        "# Open Mind library",
        "",
        f"Generated from `library.json` on {data['updated']}. Do not edit by hand.",
        "",
        f"{len(papers)} entries: {n_full} read in full, {len(papers) - n_full} from the abstract only. "
        "Every DOI was opened and its title and authors checked.",
        "",
        "Relevance: **core** bears on a current study; **useful** may shape one; **context** is background.",
        "",
    ]
    for topic in data["topics"]:
        group = sorted((p for p in papers if p["topic"] == topic),
                       key=lambda p: (RANK[p["relevance"]], -(p["year"] or 0), p["title"]))
        if not group:
            continue
        out += [f"## {topic} ({len(group)})", ""]
        for p in group:
            depth = "full text" if p["read_depth"] == "full" else "abstract only"
            out.append(f"### {p['title']}")
            out.append("")
            out.append(f"{p['authors']} ({p['year']}). *{p['venue']}*. [doi:{p['doi']}]({p['url']}). "
                       f"{p['kind']}, {depth}, **{p['relevance']}**.")
            out.append("")
            for label, key in [("Question", "question"), ("Idea tested", "tried"), ("Data and method", "method_data"),
                               ("Results", "key_results"), ("Limits", "limits"), ("For us", "ideas_for_us")]:
                if p.get(key):
                    out.append(f"- **{label}:** {p[key]}")
            if p.get("touches"):
                out.append(f"- **Touches:** {', '.join(p['touches'])}")
            out.append("")
    (HERE / "LIBRARY.md").write_text("\n".join(out))
    print(f"wrote LIBRARY.md: {len(papers)} entries")


if __name__ == "__main__":
    main()
