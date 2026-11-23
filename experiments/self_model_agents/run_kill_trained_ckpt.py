"""Checkpointed runner for the sealed AI2 kill test (kill_trained.py, sealed 2026-11-21).

Checks the sealed script's sha256, executes its definitions unchanged (everything before its main loop),
then runs the same 32 jobs (4 cells x {T, TF} x 4 seeds), appending one JSON line per job to
kill_trained_ckpt.jsonl and skipping jobs already there. The final assembly and verdict are copied
verbatim from the sealed script and written to kill_trained.json.

  .venv/bin/python -I experiments/self_model_agents/run_kill_trained_ckpt.py
"""
import hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEALED = os.path.join(HERE, "kill_trained.py")
SHA = "69a22e754090b24047deea608739760500009a624e7e569bad76ac2a6b114814"
CKPT = os.path.join(HERE, "kill_trained_ckpt.jsonl")
OUT = os.path.join(HERE, "kill_trained.json")

src = open(SEALED, "rb").read()
if hashlib.sha256(src).hexdigest() != SHA:
    sys.exit("sealed script changed; refusing to run")
text = src.decode()
cut = text.index('out = {"cells": []}')
ns = {"__name__": "sealed_defs"}
exec(compile(text[:cut], SEALED, "exec"), ns)
CELLS, run = ns["CELLS"], ns["run"]

done = {}
if os.path.exists(CKPT):
    for line in open(CKPT):
        j = json.loads(line)
        done[(tuple(j["cell"]), j["agent"], j["seed"])] = j["res"]

for cell in CELLS:
    for name, floor in (("T", False), ("TF", True)):
        for seed in range(4):
            key = (tuple(cell), name, seed)
            if key in done:
                continue
            res = run(cell, floor, seed)
            done[key] = res
            with open(CKPT, "a") as fh:
                fh.write(json.dumps({"cell": list(cell), "agent": name, "seed": seed, "res": res}) + "\n")
            print("done", cell, name, seed, flush=True)

# --- assembly and verdict: same logic as the sealed script ---
out = {"cells": []}
for cell in CELLS:
    row = {"cell": cell}
    for name, floor in (("T", False), ("TF", True)):
        rs = [done[(tuple(cell), name, seed)] for seed in range(4)]
        row[name] = {"seeds": rs, "n_show": sum(r["shows"] for r in rs), "cell_shows": sum(r["shows"] for r in rs) >= 3}
    out["cells"].append(row)
    print(cell, "T", [r["reversal"] for r in row["T"]["seeds"]], "TF", [r["reversal"] for r in row["TF"]["seeds"]], flush=True)
t_cells = sum(c["T"]["cell_shows"] for c in out["cells"])
tf_cells = sum(c["TF"]["cell_shows"] for c in out["cells"])
planted = tf_cells >= 3
out.update(T_cells=t_cells, TF_cells=tf_cells, planted_pass=planted,
           verdict="void" if not planted else ("step 0 holds: reversal needs a visibility floor" if t_cells <= 1 else "reviewer right: reversal not diagnostic"))
json.dump(out, open(OUT, "w"), indent=1)
print("T cells", t_cells, "TF cells", tf_cells, "->", out["verdict"])
