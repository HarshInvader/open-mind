"""Part A3: blind selector. Prints counts only.

    python -I select.py packet   # selector packet (A/B seeded random, seed 1125; six real theories) -> local dir
    python -I select.py apply    # inclusion rule on the selector's answers -> selected.json (ids only, no outcomes)
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOC = ROOT / "datasets" / "local" / "splitfirst_writer"
PC = ROOT / "experiments" / "theory_postcutoff"
sys.path.insert(0, str(PC))
import make_packets as mp  # noqa: E402

SEED = 1125
BAR = 0.25
CAP = 2


def packet():
    items = json.load(open(LOC / "items_full.json"))["items"]
    th = json.load(open(PC / "items.json"))["theories"]
    rng = np.random.default_rng(SEED)
    lines = [mp.INSTR.format(n=len(th) * len(items), obs=mp.OBS_BLIND)]
    lines += mp.theory_lines(th, rng)
    lines.append("\nFINDINGS (use the finding id in your answer)")
    key = {}
    for j, it in enumerate([items[i] for i in rng.permutation(len(items))]):
        fid = f"F{j + 1:02d}"
        ra = bool(rng.integers(2))
        a, b = (it["actual"], it["mirror"]) if ra else (it["mirror"], it["actual"])
        key[fid] = dict(item=it["id"], real_is_a=ra, cluster=it["cluster"])
        lines.append(f"{fid}\n  A: {a}\n  B: {b}")
    (LOC / "selector_packet.txt").write_text("\n".join(lines) + "\n")
    (LOC / "selector_key.json").write_text(json.dumps(key, indent=1))
    print("selector packet:", len(items), "items x", len(th), "theories =", len(items) * len(th), "pairs")


def apply():
    key = json.load(open(LOC / "selector_key.json"))
    ans = json.load(open(LOC / "selector_answer.json"))
    real = {t["id"] for t in json.load(open(PC / "items.json"))["theories"]}
    commit = {}
    bad = 0
    for r in ans:
        if r.get("theory") not in real or r.get("finding") not in key:
            bad += 1
            continue
        f = r["finding"]
        commit[f] = max(commit.get(f, 0.0), abs(float(r["p"]) - 0.5))
    cand = [(commit.get(f, 0.0), key[f]["item"], key[f]["cluster"]) for f in key]
    passed = sorted([c for c in cand if c[0] >= BAR], reverse=True)
    per, sel = {}, []
    for m, it, cl in passed:
        if per.get(cl, 0) < CAP:
            per[cl] = per.get(cl, 0) + 1
            sel.append(dict(item=it, max_commit=round(m, 3), cluster=cl))
    out = dict(bar=BAR, cap=CAP, n_items=len(key), answers=len(ans), unusable_rows=bad, n_pass_bar=len(passed),
               n_selected=len(sel), n_clusters=len({s["cluster"] for s in sel}), selected=sorted(s["item"] for s in sel),
               max_commit_distribution=[round(c[0], 2) for c in sorted(cand, reverse=True)])
    (HERE / "selected.json").write_text(json.dumps(out, indent=1))
    print({k: v for k, v in out.items() if k not in ("selected", "max_commit_distribution")})


if __name__ == "__main__":
    {"packet": packet, "apply": apply}[sys.argv[1]]()
