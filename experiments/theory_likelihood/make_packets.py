"""Build one blinded rating packet per rater (seeded). Each packet:
  - lists the 8 theories (6 real + toy Z + placebo Q) in a seeded order;
  - lists the 10 findings as pairs "Outcome A / Outcome B" where A/B is a seeded coin flip between the real finding
    and its mirror, and never says which one is real;
  - asks, for every theory x finding, P(A rather than B | the theory as stated in its canonical reference).
Writes packets/rater_<k>.txt (the prompt) and packets/rater_<k>_key.json (which side is real; never shown to raters).
Usage: python3 -I make_packets.py
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RATERS = {"r1": 101, "r2": 202, "r3": 303}

INSTR = """You are rating how strongly scientific theories of consciousness predict experimental outcomes.

Rules:
- Do not use any tools, files or web searches. Answer from your own knowledge of each theory.
- For each theory and each finding you see two possible outcomes, A and B. Exactly one of them describes what was
  observed in the real world, but you are not told which, and it does not matter: rate what the THEORY implies.
- Give p = the probability that outcome A rather than B would be observed IF the theory (as stated in the canonical
  reference given, by its proponents' core commitments) were true. Use 0.01-0.99.
- p near 0.5 means the theory does not discriminate between A and B (it is silent, or it fits both equally well).
- Do not reward a theory for having been adjusted after the fact to fit one outcome unless that adjustment is part of
  the canonical reference. For the two made-up theories (Z and Q), use only the text given.
- Be calibrated: reserve values below 0.1 or above 0.9 for cases where the theory's core commitments clearly entail
  one outcome.

Return ONLY a JSON array, one object per (theory, finding) pair, with keys "theory", "finding", "p", "why"
("why" at most 15 words). There are {n} pairs; include every one.
"""


def main():
    d = json.load(open(os.path.join(HERE, "items.json")))
    th = d["theories"] + [d["toy"], d["placebo"]]
    os.makedirs(os.path.join(HERE, "packets"), exist_ok=True)
    for name, seed in RATERS.items():
        rng = np.random.default_rng(seed)
        order_t = [th[i] for i in rng.permutation(len(th))]
        order_i = [d["items"][i] for i in rng.permutation(len(d["items"]))]
        key = {}
        lines = [INSTR.format(n=len(th) * len(d["items"])), "THEORIES"]
        for t in order_t:
            desc = f"- {t['id']}: {t['name']}. Canonical reference: {t['ref']}."
            if "text" in t:
                desc += " " + t["text"]
            lines.append(desc)
        lines.append("\nFINDINGS (use the finding id in your answer)")
        for k, it in enumerate(order_i):
            fid = f"F{k + 1:02d}"
            real_is_a = bool(rng.integers(2))
            a, b = (it["actual"], it["mirror"]) if real_is_a else (it["mirror"], it["actual"])
            key[fid] = dict(item=it["id"], real_is_a=real_is_a)
            lines.append(f"{fid}\n  A: {a}\n  B: {b}")
        open(os.path.join(HERE, "packets", f"rater_{name}.txt"), "w").write("\n".join(lines) + "\n")
        json.dump(key, open(os.path.join(HERE, "packets", f"rater_{name}_key.json"), "w"), indent=1)
    print("packets written:", list(RATERS))


if __name__ == "__main__":
    main()
