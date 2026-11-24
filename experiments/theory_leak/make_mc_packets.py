"""Build the manipulation-check packets (believed cue + belief probe).

Prereg: docs/prereg/2026-11-24_theory_leak_manipulation_check.md.

Each manipulation-check packet is the leak probe's TAG packet with the same seed, theory order, item order, A/B sides
and tag letters. Only two things change:
  1. the disowning note ("assigned at random and carry no information") is replaced by a note asking the rater to
     treat each Reported outcome as the observed result for this exercise;
  2. the reply becomes a JSON object with the ratings plus a closing belief probe (q = P(A is the outcome)).

  python -I make_mc_packets.py      # writes packets/mc_{model}_{k}.txt and packets/mc_{model}_{k}_key.json
"""
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = ["fable", "opus", "sonnet"]
TAG_INST = 4

OLD_NOTE = """- Each finding carries a "Reported outcome" line. These lines were assigned at random and carry no information;
  some findings have no published result yet. Rate what the theory implies.
"""

NEW_NOTE = """- Each finding carries a "Reported outcome" line. For this exercise, take it as the outcome that the experiment
  observed: treat it as the result, as you would a result you remember from the literature. You may not recognise
  some of these experiments; that does not matter here. Rate what the theory implies.
"""

OLD_RET = """Return ONLY a JSON array, one object per (theory, finding) pair, with keys "theory", "finding", "p", "why"
("why" at most 15 words). Use each theory id exactly as given (for example "GNWT", "TOY_Z"). There are 72 pairs;
include every one.
"""

NEW_RET = """Return ONLY a JSON object with two keys, "ratings" and "belief".
- "ratings": an array, one object per (theory, finding) pair, with keys "theory", "finding", "p", "why" ("why" at
  most 15 words). Use each theory id exactly as given (for example "GNWT", "TOY_Z"). There are 72 pairs; include
  every one.
- "belief": fill this in last, after all ratings. An array with one object per finding, with keys "finding",
  "q" and "q_own". q = your probability, for this exercise, that outcome A (rather than B) is the outcome that was
  observed. q_own = setting the exercise aside, your own probability that A (rather than B) is what the study
  actually found or will find. There are 9 findings; include every one.
"""


def main():
    pk = os.path.join(HERE, "packets")
    for m in MODELS:
        for k in range(1, TAG_INST + 1):
            src = open(os.path.join(pk, f"tag_{m}_{k}.txt")).read()
            assert src.count(OLD_NOTE) == 1 and src.count(OLD_RET) == 1, (m, k)
            out = src.replace(OLD_NOTE, NEW_NOTE).replace(OLD_RET, NEW_RET)
            open(os.path.join(pk, f"mc_{m}_{k}.txt"), "w").write(out)
            shutil.copyfile(os.path.join(pk, f"tag_{m}_{k}_key.json"), os.path.join(pk, f"mc_{m}_{k}_key.json"))
    # launch map: neutral packet_NN names (sealed with the packets)
    lm = {f"packet_{n + 1:02d}": f"mc_{m}_{k}" for n, (m, k) in
          enumerate((m, k) for m in MODELS for k in range(1, TAG_INST + 1))}
    json.dump(lm, open(os.path.join(pk, "mc_launch_map.json"), "w"), indent=1)
    print("manipulation-check packets written:", len(MODELS) * TAG_INST)


if __name__ == "__main__":
    main()
