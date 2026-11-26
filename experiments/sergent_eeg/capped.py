"""Orchestration only (NOT sealed): run a sealed item-2 script with Mind's 3-worker cap, without editing it.

    python -I capped.py sergent_gate run|rerun|summary [KT ...]
    python -I capped.py analyse measure|fit|readout

The sealed files (hashes in docs/prereg/HASHES.txt) are imported unchanged; their own require_sealed() checks still run.
Only the worker count changes:
- sergent_gate's module constant WORKERS: 4 -> 3. Per-study seeds come from a SeedSequence keyed by the cell, and
  Pool.map keeps order, so the results do not depend on the worker count;
- analyse's literal Pool(4), replaced by a Pool capped at 3 workers.
"""
import multiprocessing
import sys
from pathlib import Path

CAP = 3
sys.path.insert(0, str(Path(__file__).resolve().parent))


def capped_pool(processes=None, *a, **k):
    return multiprocessing.Pool(min(processes or CAP, CAP), *a, **k)


if __name__ == "__main__":
    mod, cmd, rest = sys.argv[1], sys.argv[2], sys.argv[3:]
    if mod == "sergent_gate":
        import sergent_gate as G
        G.WORKERS = CAP
        G.Pool = capped_pool
        {"run": lambda: G.run([float(k) for k in rest]), "rerun": G.rerun, "summary": G.summary}[cmd]()
    elif mod == "analyse":
        import analyse as An
        An.Pool = capped_pool
        {"measure": An.measure, "fit": An.fit, "readout": An.readout}[cmd]()
    else:
        raise SystemExit("unknown module")
