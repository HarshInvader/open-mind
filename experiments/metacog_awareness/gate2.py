"""Gate 2 (after Fable's pre-seal review): run the exact analysis code (run_rausch.analyse/verdict)
on synthetic datasets in the Rausch format, including bounded, floored and tied ratings.
No real data is read.

Conditions (R datasets each, B_NULL = 200 null simulations per dataset instead of the sealed 1000):
  null        continuous ratings, lam = 0
  null_t3     heavy-tailed confidence noise, lam = 0
  null_floor  ratings censored at a per-subject low quantile (visibility 35%, confidence 15%),
              mapped to -12..12 and rounded to 0.1, lam = 0
  planted_floor       the same floor, lam = lam* (AUROC2 excess ~0.05)
  planted_half_floor  the same floor, lam = lam*/2
Pass: rejection ("supports") rate <= 0.05 for every null condition; void rate <= 0.10 for every
null condition; "supports" rate >= 0.80 for planted_floor.
"""
import json, os, sys, time
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import power_gate as pg
import run_rausch as rr

rr.B_NULL = 200
CONS = [2.2, 3.9, 5.0, 5.5, 6.9]
LAM_STAR = 0.4977


def to_scale(x, subj, q):
    out = np.empty_like(x)
    for i in range(pg.NSUB):
        m = subj == i
        xi = x[m].copy()
        if q > 0:
            xi = np.maximum(xi, np.quantile(xi, q))
        lo, hi = xi.min(), xi.max()
        out[m] = np.round(-12 + 24 * (xi - lo) / (hi - lo + 1e-12), 1)
    return out


def make(cond, r):
    rng = np.random.default_rng(1000 + r + 100_000 * ["null", "null_t3", "null_floor", "planted_floor", "planted_half_floor"].index(cond))
    lam = {"planted_floor": LAM_STAR, "planted_half_floor": LAM_STAR / 2}.get(cond, 0.0)
    tail = "t3" if cond == "null_t3" else None
    floor = cond.endswith("floor")
    d = pg.design(rng)
    s, k, y, c, v = pg.simulate(d, 0.8, 1.5, 0.5, lam, rng, tail=tail)
    c = to_scale(c, s, 0.15 if floor else 0.0)
    v = to_scale(v, s, 0.35 if floor else 0.0)
    subs = [str(i + 1) for i in range(pg.NSUB)]
    return dict(subj=s, k=k, y=y, c=c, v=v, subs=subs, cons=CONS, order={x: "1" for x in subs})


def job(args):
    cond, r = args
    rr.SEED = 20261123 + r
    res = rr.analyse(make(cond, r), cond)
    res["verdict"] = rr.verdict(res)
    return cond, r, {kk: res[kk] for kk in ("verdict", "p_one_sided", "auroc2_gap_excess", "auroc2_gap_excess_ci95", "moment_z", "fit")}


def main():
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    conds = ["null", "null_t3", "null_floor", "planted_floor", "planted_half_floor"]
    jobs = [(c, r) for c in conds for r in range(R)]
    out = {c: [] for c in conds}
    t0 = time.time()
    ck = os.path.join(HERE, "gate2_ckpt.jsonl")
    done = set()
    if os.path.exists(ck):
        for line in open(ck):
            j = json.loads(line); out[j["cond"]].append(j["res"]); done.add((j["cond"], j["r"]))
    todo = [j for j in jobs if j not in done]
    with Pool(3) as pool:
        for cond, r, res in pool.imap_unordered(job, todo):
            out[cond].append(res)
            with open(ck, "a") as fh:
                fh.write(json.dumps({"cond": cond, "r": r, "res": res}) + "\n")
            if len(out[cond]) == R:
                print(cond, "done", round(time.time() - t0), flush=True)
    summ = {}
    for c, rows in out.items():
        n = len(rows)
        summ[c] = dict(n=n, supports=sum(x["verdict"].startswith("supports") for x in rows) / n,
                       refutes=sum(x["verdict"].startswith("refutes") for x in rows) / n,
                       void=sum(x["verdict"] == "void" for x in rows) / n,
                       mean_excess=float(np.mean([x["auroc2_gap_excess"] for x in rows])))
        print(c, summ[c], flush=True)
    nulls = ["null", "null_t3", "null_floor"]
    gate = all(summ[c]["supports"] <= 0.05 and summ[c]["void"] <= 0.10 for c in nulls) and summ["planted_floor"]["supports"] >= 0.80
    print("GATE2", "PASS" if gate else "FAIL", flush=True)
    json.dump(dict(R=R, B_NULL=rr.B_NULL, summary=summ, gate_pass=gate, rows=out), open(os.path.join(HERE, "gate2.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
