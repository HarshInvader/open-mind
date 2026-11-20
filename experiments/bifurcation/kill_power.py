"""Kill test, cut to the decisive question: can the T4 planted two-state pipeline detect a real mixture
at the d' these datasets likely have (about 1; Sergent 2021 report AUC > 0.75 implies d' ~ 0.95)?

  python -I experiments/bifurcation/kill_power.py   -> kill_power.jsonl (one line per rep; resumes)

Each job is one rep (one simulated study at the design's real counts) of a planted MIX scenario from
kill_planted.py. Kill rule (from the coordinator's brief): power below 80% kills the study. With 10 reps,
<= 5 passes gives a one-sided 95% upper bound below 0.80 (Clopper-Pearson upper for 5/10 = 0.78).
Null false-pass scenarios are run only if power survives.
"""
import json, os, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kill_planted as K  # noqa: E402

OUT = os.path.join(HERE, "kill_power.jsonl")
GRID = [("cohen", 1.0), ("cohen", 1.25), ("cohen", 1.5), ("sergent", 1.0), ("sergent", 1.25)]
N_REP = 10


def job(a):
    dname, d, r = a
    t = time.time()
    _, rate = K.one(("x", dname, ("mix", d), 1, 50000 + int(d * 100) * 100 + r + (0 if dname == "cohen" else 7000)))
    return dict(design=dname, d=d, rep=r, passed=bool(rate == 1.0), sec=round(time.time() - t, 1))


def main():
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            j = json.loads(line); done.add((j["design"], j["d"], j["rep"]))
    jobs = [(dn, d, r) for r in range(N_REP) for dn, d in GRID if (dn, d, r) not in done]
    print(len(done), "done,", len(jobs), "to run", flush=True)
    with ProcessPoolExecutor(max_workers=3) as ex:
        for f in as_completed([ex.submit(job, j) for j in jobs]):
            res = f.result()
            with open(OUT, "a") as fh:
                fh.write(json.dumps(res) + "\n")
            print(res, flush=True)


if __name__ == "__main__":
    main()
