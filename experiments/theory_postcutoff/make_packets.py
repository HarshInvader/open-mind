"""Build the post-cutoff ledger packets (seeded). Sealed with docs/prereg/2026-11-24_theory_postcutoff_ledger.md.

  python -I make_packets.py build    # items.json from draft_items.json (minus excluded items) + the 10 pilot items
  python -I make_packets.py recog    # recognition packets (no theories): 10 pilot items (control) + post items
  python -I make_packets.py rate     # BLIND and INFORMED packets for the kept post items (reads recog_result.json)

BLIND packets (2 per model): famous + kept post items, nothing says which side is real (the pilot's wording).
INFORMED packets (2 per model): kept post items only, each with "Observed outcome" and the study's abstract. They hold
abstract text, so they are written under datasets/local/postcutoff_packets/ (not committed); their sha256 go in
packets/informed_hashes.json. Keys never go to raters.
"""
import hashlib
import re
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PILOT = os.path.join(HERE, "..", "theory_likelihood", "items.json")
LOCAL = os.path.join(ROOT, "datasets", "local", "postcutoff_packets")
MODELS = {"fable": 11, "opus": 22, "sonnet": 33}
BLIND_INST, INF_INST = 2, 2

INSTR = """You are rating how strongly scientific theories of consciousness predict experimental outcomes.

Rules:
- Do not use any tools, files or web searches. Answer from your own knowledge of each theory.
- For each theory and each finding you see two possible outcomes, A and B. {obs}
- Give p = the probability that outcome A rather than B would be observed IF the theory (as stated in the canonical
  reference given, by its proponents' core commitments) were true. Use 0.01-0.99.
- p near 0.5 means the theory does not discriminate between A and B (it is silent, or it fits both equally well).
- Do not reward a theory for having been adjusted after the fact to fit one outcome unless that adjustment is part of
  the canonical reference. For the two made-up theories (Z and Q), use only the text given.
- Be calibrated: reserve values below 0.1 or above 0.9 for cases where the theory's core commitments clearly entail
  one outcome.

Return ONLY a JSON array, one object per (theory, finding) pair, with keys "theory", "finding", "p", "why"
("why" at most 10 words). Use each theory id exactly as given (for example "GNWT", "TOY_Z"). There are {n} pairs;
include every one.
"""
OBS_BLIND = ("Exactly one of them describes what was\n  observed in the real world, but you are not told which, and it "
             "does not matter: rate what the THEORY implies.")
OBS_INF = ("Each finding states which outcome was\n  observed and gives the published study's abstract. Still rate what "
           "the THEORY implies, not what was observed.")

RECOG_INSTR = """This is a memory check about published research. Do not use any tools, files or web searches.

For each finding below you see two possible outcomes, A and B. One of them was reported by a published study. For each,
give p = your probability that outcome A (rather than B) is what was actually reported, and say whether you
specifically recall the study ("recall": true or false). If you do not know, give 0.5 and recall false. Do not guess
from what theories predict; answer only from memory of the actual study.

Return ONLY a JSON array with keys "finding", "p", "recall". There are {n} findings; include every one.
"""


def build():
    pil = json.load(open(PILOT))
    dr = json.load(open(os.path.join(HERE, "draft_items.json")))
    extra = json.load(open(os.path.join(HERE, "toy_z.json")))          # toy Z text + toy_key, written after drafting
    post = [dict(id=it["id"], actual=it["actual"], mirror=it["mirror"], cluster=it["cluster"],
                 abstract_file=it["abstract_file"], doi=it["doi"], first_posted=it["first_posted"]) for it in dr["items"]
            if "excluded" not in it]
    # P02-P04 (leak probe) are left out: raters already rated them blind in that probe (pre-seal review must-fix 1).
    pat = re.compile(r"workspace|integrated information|recurrent processing|higher-order|predictive processing|"
                     r"attention schema|\bIIT\b|\bGNWT?\b|\bRPT\b|\bHOT\b", re.I)
    for it in post:                                  # hindsight sensitivity: abstracts that name a theory
        it["abstract_names_theory"] = bool(pat.search(open(os.path.join(ROOT, it["abstract_file"]), encoding="utf-8").read()))
    famous = [dict(id=it["id"], actual=it["actual"], mirror=it["mirror"]) for it in pil["items"]]
    toy = dict(pil["toy"])
    toy["text"] = extra["toy_text"]
    out = dict(note="Built by make_packets.py build", famous=famous, post=post, theories=pil["theories"], toy=toy,
               toy_key=extra["toy_key"], placebo=pil["placebo"])
    ids = [i["id"] for i in famous + post]
    assert len(ids) == len(set(ids)) and set(extra["toy_key"]) == set(ids), "toy_key must cover every item"
    for it in post:
        assert os.path.exists(os.path.join(ROOT, it["abstract_file"])), it["abstract_file"]
    json.dump(out, open(os.path.join(HERE, "items.json"), "w"), indent=1)
    print("items.json:", len(famous), "famous,", len(post), "post")


def recog():
    d = json.load(open(os.path.join(HERE, "items.json")))
    pool = [dict(it, control=True) for it in d["famous"]] + [dict(it, control=False) for it in d["post"]]
    os.makedirs(os.path.join(HERE, "packets"), exist_ok=True)
    for m, seed in MODELS.items():
        rng = np.random.default_rng(seed + 900)
        order = [pool[i] for i in rng.permutation(len(pool))]
        lines, key = [RECOG_INSTR.format(n=len(order)), "FINDINGS"], {}
        for k, it in enumerate(order):
            fid = f"R{k + 1:02d}"
            ra = bool(rng.integers(2))
            a, b = (it["actual"], it["mirror"]) if ra else (it["mirror"], it["actual"])
            key[fid] = dict(item=it["id"], real_is_a=ra, control=it["control"])
            lines.append(f"{fid}\n  A: {a}\n  B: {b}")
        open(os.path.join(HERE, "packets", f"recog_{m}.txt"), "w").write("\n".join(lines) + "\n")
        json.dump(key, open(os.path.join(HERE, "packets", f"recog_{m}_key.json"), "w"), indent=1)
    print("recognition packets written:", len(pool), "findings each")


def theory_lines(th, rng):
    out = ["THEORIES"]
    for t in [th[i] for i in rng.permutation(len(th))]:
        desc = f"- {t['id']}: {t['name']}. Canonical reference: {t['ref']}."
        if "text" in t:
            desc += " " + t["text"]
        out.append(desc)
    return out


def rate():
    d = json.load(open(os.path.join(HERE, "items.json")))
    rr = json.load(open(os.path.join(HERE, "recog_result.json")))
    if rr["verdict"] != "PASS":
        raise SystemExit("recognition gate did not pass; no rating packets")
    post = [it for it in d["post"] if it["id"] in set(rr["kept"])]
    th = d["theories"] + [d["toy"], d["placebo"]]
    os.makedirs(LOCAL, exist_ok=True)
    hashes = {}
    for arm, n in (("blind", BLIND_INST), ("informed", INF_INST)):
        items = d["famous"] + post if arm == "blind" else post
        for m, seed in MODELS.items():
            for k in range(1, n + 1):
                rng = np.random.default_rng(seed * 100 + k + (0 if arm == "blind" else 50))
                lines = [INSTR.format(n=len(th) * len(items), obs=OBS_BLIND if arm == "blind" else OBS_INF)]
                lines += theory_lines(th, rng)
                lines.append("\nFINDINGS (use the finding id in your answer)")
                key = {}
                for j, it in enumerate([items[i] for i in rng.permutation(len(items))]):
                    fid = f"F{j + 1:02d}"
                    ra = bool(rng.integers(2))
                    a, b = (it["actual"], it["mirror"]) if ra else (it["mirror"], it["actual"])
                    key[fid] = dict(item=it["id"], real_is_a=ra)
                    block = f"{fid}\n  A: {a}\n  B: {b}"
                    if arm == "informed":
                        ab = open(os.path.join(ROOT, it["abstract_file"]), encoding="utf-8").read().strip()
                        block += f"\n  Observed outcome: {'A' if ra else 'B'}\n  Abstract of the published study: {ab}"
                    lines.append(block)
                txt = "\n".join(lines) + "\n"
                if arm == "blind":
                    open(os.path.join(HERE, "packets", f"{arm}_{m}_{k}.txt"), "w").write(txt)
                else:
                    open(os.path.join(LOCAL, f"{arm}_{m}_{k}.txt"), "w").write(txt)
                    hashes[f"{arm}_{m}_{k}.txt"] = hashlib.sha256(txt.encode()).hexdigest()
                json.dump(key, open(os.path.join(HERE, "packets", f"{arm}_{m}_{k}_key.json"), "w"), indent=1)
    json.dump(hashes, open(os.path.join(HERE, "packets", "informed_hashes.json"), "w"), indent=1)
    print("rating packets written:", len(d["famous"]), "famous +", len(post), "post; excluded:", rr["excluded"])


if __name__ == "__main__":
    {"build": build, "recog": recog, "rate": rate}[sys.argv[1]]()
