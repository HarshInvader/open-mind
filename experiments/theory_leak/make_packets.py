"""Build the leak-probe packets (seeded). Sealed with the prereg docs/prereg/2026-11-24_theory_leak_probe.md.

  python -I make_packets.py recog   # recognition packets: no theories; 10 pilot items (positive control) + test items
  python -I make_packets.py rate    # rating packets for the items that pass the recognition gate (reads recog_result.json)

Rating packets: TAG arm, 4 instances per model (instances 1-2 use tag set S, 3-4 the flipped set) and NOTAG arm,
2 instances per model. Theory order, item order and A/B sides are seeded per packet. Keys never go to raters.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.join(HERE, "..", "theory_likelihood", "items.json")
MODELS = {"fable": 11, "opus": 22, "sonnet": 33}
TAG_INST, NOTAG_INST = 4, 2
SEED_S = 2411

RATE_INSTR = """You are rating how strongly scientific theories of consciousness predict experimental outcomes.

Rules:
- Do not use any tools, files or web searches. Answer from your own knowledge of each theory.
- For each theory and each finding you see two possible outcomes, A and B. Rate what the THEORY implies.
- Give p = the probability that outcome A rather than B would be observed IF the theory (as stated in the canonical
  reference given, by its proponents' core commitments) were true. Use 0.01-0.99.
- p near 0.5 means the theory does not discriminate between A and B (it is silent, or it fits both equally well).
- Do not reward a theory for having been adjusted after the fact to fit one outcome unless that adjustment is part of
  the canonical reference. For the two made-up theories (Z and Q), use only the text given.
- Be calibrated: reserve values below 0.1 or above 0.9 for cases where the theory's core commitments clearly entail
  one outcome.
{tagnote}
Return ONLY a JSON array, one object per (theory, finding) pair, with keys "theory", "finding", "p", "why"
("why" at most 15 words). Use each theory id exactly as given (for example "GNWT", "TOY_Z"). There are {n} pairs;
include every one.
"""

TAGNOTE = """- Each finding carries a "Reported outcome" line. These lines were assigned at random and carry no information;
  some findings have no published result yet. Rate what the theory implies.
"""

RECOG_INSTR = """This is a memory check about published research. Do not use any tools, files or web searches.

For each finding below you see two possible outcomes, A and B. Some findings come from published studies; others may
not have a published result yet. For each, give p = your probability that outcome A (rather than B) is what was
actually reported, and say whether you specifically recall the study ("recall": true or false). If you do not know,
give 0.5 and recall false. Do not guess from what theories predict; answer only from memory of the actual study.

Return ONLY a JSON array with keys "finding", "p", "recall". There are {n} findings; include every one.
"""


def load():
    d = json.load(open(os.path.join(HERE, "items.json")))
    pil = json.load(open(PILOT))
    return d, pil


def recog():
    d, pil = load()
    pool = [dict(id=it["id"], real=it["actual"], mirror=it["mirror"], control=True) for it in pil["items"]]
    pool += [dict(id=it["id"], real=it["side_real"], mirror=it["side_mirror"], control=False) for it in d["items"]]
    for m, seed in MODELS.items():
        rng = np.random.default_rng(seed + 900)
        order = [pool[i] for i in rng.permutation(len(pool))]
        lines, key = [RECOG_INSTR.format(n=len(order)), "FINDINGS"], {}
        for k, it in enumerate(order):
            fid = f"R{k + 1:02d}"
            ra = bool(rng.integers(2))
            a, b = (it["real"], it["mirror"]) if ra else (it["mirror"], it["real"])
            key[fid] = dict(item=it["id"], real_is_a=ra, control=it["control"])
            lines.append(f"{fid}\n  A: {a}\n  B: {b}")
        os.makedirs(os.path.join(HERE, "packets"), exist_ok=True)
        open(os.path.join(HERE, "packets", f"recog_{m}.txt"), "w").write("\n".join(lines) + "\n")
        json.dump(key, open(os.path.join(HERE, "packets", f"recog_{m}_key.json"), "w"), indent=1)
    print("recognition packets written")


def rate():
    d, _ = load()
    rr = json.load(open(os.path.join(HERE, "recog_result.json")))
    if rr["verdict"] != "PASS":
        raise SystemExit("recognition gate did not pass; no rating packets")
    keep = [it for it in d["items"] if it["id"] not in set(rr["excluded"])]
    th = d["theories"] + [d["toy"], d["placebo"]]
    rs = np.random.default_rng(SEED_S)
    ids = [it["id"] for it in keep]
    S = set(ids[i] for i in rs.permutation(len(ids))[: len(ids) // 2])   # tagged real in instances 1-2
    for arm, n in (("tag", TAG_INST), ("notag", NOTAG_INST)):
        for m, seed in MODELS.items():
            for k in range(1, n + 1):
                rng = np.random.default_rng(seed * 100 + k + (0 if arm == "tag" else 50))
                ot = [th[i] for i in rng.permutation(len(th))]
                oi = [keep[i] for i in rng.permutation(len(keep))]
                lines = [RATE_INSTR.format(n=len(th) * len(keep), tagnote=TAGNOTE if arm == "tag" else ""), "THEORIES"]
                for t in ot:
                    desc = f"- {t['id']}: {t['name']}. Canonical reference: {t['ref']}."
                    if "text" in t:
                        desc += " " + t["text"]
                    lines.append(desc)
                lines.append("\nFINDINGS (use the finding id in your answer)")
                key = {}
                for j, it in enumerate(oi):
                    fid = f"F{j + 1:02d}"
                    ra = bool(rng.integers(2))
                    a, b = (it["side_real"], it["side_mirror"]) if ra else (it["side_mirror"], it["side_real"])
                    entry = dict(item=it["id"], real_is_a=ra)
                    block = f"{fid}\n  A: {a}\n  B: {b}"
                    if arm == "tag":
                        tag_real = (it["id"] in S) == (k <= TAG_INST // 2)
                        tag_letter = ("A" if ra else "B") if tag_real else ("B" if ra else "A")
                        entry["tag_real"] = tag_real
                        block += f"\n  Reported outcome: {tag_letter}"
                    key[fid] = entry
                    lines.append(block)
                open(os.path.join(HERE, "packets", f"{arm}_{m}_{k}.txt"), "w").write("\n".join(lines) + "\n")
                json.dump(key, open(os.path.join(HERE, "packets", f"{arm}_{m}_{k}_key.json"), "w"), indent=1)
    print("rating packets written for", len(keep), "items; excluded:", rr["excluded"])


if __name__ == "__main__":
    {"recog": recog, "rate": rate}[sys.argv[1]]()
