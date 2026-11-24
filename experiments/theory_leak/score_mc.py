"""Score the manipulation check (believed outcome cue) under the sealed rules.

Prereg: docs/prereg/2026-11-24_theory_leak_manipulation_check.md. The leak statistics, thresholds, bootstrap and
verdict logic are imported unchanged from the sealed score_leak.py.

  python -I score_mc.py                 # real ratings -> mc_result.json
  python -I score_mc.py --planted [N]   # planted gate with noise and base rates calibrated on the leak-probe data
                                        #   -> planted_mc.json
"""
import importlib.util
import json
import math
import os
import re
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("score_leak", os.path.join(HERE, "score_leak.py"))
SL = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SL)

MODELS, REAL, ALL_T, TAG_INST = SL.MODELS, SL.REAL, SL.ALL_T, SL.TAG_INST
BELIEF_Q = 0.75         # a finding passes if q toward the cued side >= 0.75
BELIEF_ITEMS = 8        # an instance passes if at least 8 of its 9 findings pass
MIN_INST = 3            # VOID if any model has fewer than 3 valid (or, for the primary analysis, passing) instances
EPS = 1e-9
WHY_RE = re.compile(r"\b(reported|observed|outcome|result)\b", re.I)


def parse_reply(path):
    """Ratings reply: a JSON object. A single surrounding markdown fence is stripped (disclosed in RESULTS)."""
    txt = open(path).read().strip()
    fenced = False
    mm = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", txt, flags=re.S | re.I)
    if mm:
        txt, fenced = mm.group(1), True
    return json.loads(txt), fenced


def load_mc(items):
    tag, belief, fences, why = {}, {}, [], {}
    loaded = {m: [] for m in MODELS}
    for m in MODELS:
        for k in range(1, TAG_INST + 1):
            fr = os.path.join(HERE, "ratings", f"mc_{m}_{k}.json")
            if not os.path.exists(fr):           # voided instance (two failed attempts), logged in RESULTS
                continue
            key = json.load(open(os.path.join(HERE, "packets", f"mc_{m}_{k}_key.json")))
            assert sorted(kk["item"] for kk in key.values()) == sorted(items), (m, k)
            obj, fenced = parse_reply(fr)
            if fenced:
                fences.append(f"mc_{m}_{k}")
            seen = set()
            for x in obj["ratings"]:
                fid, t = x["finding"], x["theory"]
                assert t in ALL_T and fid in key and (t, fid) not in seen, (m, k, t, fid)
                assert 0 <= float(x["p"]) <= 1, (m, k, t, fid, x["p"])
                seen.add((t, fid))
                kk = key[fid]
                p = SL.clipp(x["p"])
                tag[(m, k, t, kk["item"])] = (p if kk["real_is_a"] else 1 - p, kk["tag_real"])
                if t in REAL:
                    why[(m, k, t, kk["item"])] = bool(WHY_RE.search(str(x.get("why", ""))))
            assert len(seen) == len(key) * len(ALL_T), (m, k, len(seen))
            bq = {}
            for x in obj["belief"]:
                fid = x["finding"]
                assert fid in key and fid not in bq, (m, k, fid)
                q, qo = float(x["q"]), float(x["q_own"])
                assert 0 <= q <= 1 and 0 <= qo <= 1, (m, k, fid, q, qo)
                kk = key[fid]
                cued_is_a = kk["tag_real"] == kk["real_is_a"]
                bq[fid] = dict(item=kk["item"], q_cued=q if cued_is_a else 1 - q, q_own_cued=qo if cued_is_a else 1 - qo)
            assert sorted(bq) == sorted(key), (m, k)
            belief[(m, k)] = list(bq.values())
            loaded[m].append(k)
    return tag, belief, fences, loaded, why


def paired_dL(tag_mc, tag_old, items, clusters, scale, rng):
    """Descriptive: L_believed - L_disowned, paired within (model, item) on the same instances."""
    a_new = SL.cell_leaks(tag_mc, items, REAL, scale)
    a_old = SL.cell_leaks(tag_old, items, REAL, scale)
    diff = {t: a_new[t] - a_old[t] for t in REAL}
    cl = sorted(set(clusters[i] for i in items))
    ci_idx = {c: [y for y, i in enumerate(items) if clusters[i] == c] for c in cl}
    out = {}
    for t in REAL:
        bs = []
        for _ in range(SL.B):
            sm = rng.integers(0, len(MODELS), len(MODELS))
            si = np.concatenate([ci_idx[cl[c]] for c in rng.integers(0, len(cl), len(cl))])
            bs.append(diff[t][np.ix_(sm, si)].mean())
        out[t] = dict(dL=float(diff[t].mean()), ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))])
    return out


def dom_via_D(ev):
    th = SL.TH
    return all(ev[sc]["D"]["D"] >= th[sc]["DOM_D"] and ev[sc]["D"]["ci"][0] > 0 for sc in ("bits", "logit"))


def analyse(tag, insts, items, clusters, silent, tk, seed):
    t = {kk: v for kk, v in tag.items() if (kk[0], kk[1]) in insts}
    ev = SL.evaluate(t, items, clusters, np.random.default_rng(seed), silent)
    assert SL.finite(ev)
    # Theory Z check on committed cells: a failure never overrides DOMINATED; it turns BOUNDED into INCONCLUSIVE
    com = [(m, k, i) for m, k in sorted(insts) for i in items if tk[i] != "silent"]
    fails = [(m, k, i) for m, k, i in com if not ((t[(m, k, "TOY_Z", i)][0] >= 0.70) if tk[i] == "real"
                                                    else (t[(m, k, "TOY_Z", i)][0] <= 0.30))]
    # a failing cell is "on the cued side" if Z moved toward the tag: tag_real and Z committed to mirror, or vice versa
    cued = sum(1 for m, k, i in fails if t[(m, k, "TOY_Z", i)][1] == (tk[i] == "mirror"))
    z_ok = 1 - len(fails) / len(com) >= 0.90 - EPS
    ev["toy"] = dict(correct=len(com) - len(fails), of=len(com), failing_on_cued_side=cued, pass_=z_ok)
    if ev["verdict"] == "LEAK-BOUNDED" and not z_ok:
        ev["verdict"] = "INCONCLUSIVE"
    ev["L_minus_LQ"] = {sc: {th: ev[sc]["L"][th]["L"] - ev["controls"][f"Q_{sc}"]["L"] for th in REAL}
                        for sc in ("bits", "logit")}
    ev["dominated_via_D"] = ev["verdict"] == "LEAK-DOMINATED" and dom_via_D(ev)
    ev["instances"] = sorted(f"{m}_{k}" for m, k in insts)
    return t, ev


def score_real():
    d = json.load(open(os.path.join(HERE, "items.json")))
    items = json.load(open(os.path.join(HERE, "recog_result.json")))["kept"]
    clusters = {it["id"]: it["cluster"] for it in d["items"]}
    silent = [i for i in items if d["toy_key"][i] == "silent"]
    tk = d["toy_key"]
    tag, belief, fences, loaded, why = load_mc(items)
    res = dict(items=items, loaded=loaded, fenced=fences)
    short = [m for m in MODELS if len(loaded[m]) < MIN_INST]
    if short:
        res["verdict"] = f"VOID: too few valid instances for {short}"
        return finish(res)
    npass = {mk: sum(b["q_cued"] >= BELIEF_Q - EPS for b in bl) for mk, bl in belief.items()}
    passing = {mk for mk, n in npass.items() if n >= BELIEF_ITEMS}
    res["belief"] = {f"{m}_{k}": dict(n_items_pass=npass[(m, k)],
                                      mean_q_cued=round(float(np.mean([b["q_cued"] for b in bl])), 3),
                                      mean_q_own_cued=round(float(np.mean([b["q_own_cued"] for b in bl])), 3),
                                      per_item={b["item"]: [round(b["q_cued"], 3), round(b["q_own_cued"], 3)] for b in bl})
                     for (m, k), bl in sorted(belief.items())}
    res["passing"] = sorted(f"{m}_{k}" for m, k in passing)
    short = [m for m in MODELS if sum(m == mk[0] for mk in passing) < MIN_INST]
    if short:
        res["verdict"] = f"VOID: belief did not follow the cue (fewer than {MIN_INST} passing instances for {short})"
        return finish(res)
    allinst = set(belief)
    t_p, prim = analyse(tag, passing, items, clusters, silent, tk, 2411)
    t_a, sens = analyse(tag, allinst, items, clusters, silent, tk, 2411)
    res["primary"], res["sensitivity_all_instances"] = prim, sens
    vs = (prim["verdict"], sens["verdict"])
    if "LEAK-DOMINATED" in vs:
        res["verdict"] = "LEAK-DOMINATED"
        res["kill_branch"] = "D" if (prim if prim["verdict"] == "LEAK-DOMINATED" else sens)["dominated_via_D"] else "L-only"
    elif vs == ("LEAK-BOUNDED", "LEAK-BOUNDED"):
        res["verdict"] = "LEAK-BOUNDED"
    else:
        res["verdict"] = "INCONCLUSIVE"
    _, _, tag_old, _, _ = SL.load_real()
    tag_old = {kk: v for kk, v in tag_old.items() if (kk[0], kk[1]) in passing}
    res["vs_disowned"] = {sc: paired_dL(t_p, tag_old, items, clusters, sc, np.random.default_rng(2412))
                          for sc in ("bits", "logit")}
    wv = [v for (m, k, t, i), v in why.items() if (m, k) in passing]
    res["why_mentions_outcome"] = dict(n=int(sum(wv)), of=len(wv), regex=WHY_RE.pattern)
    finish(res)
    print("primary:", prim["verdict"], "| sensitivity:", sens["verdict"], "| control flag:", prim["control_flag"])
    for sc in ("bits", "logit"):
        print(f"[{sc}] D = {prim[sc]['D']['D']:+.3f} {['%+.3f' % x for x in prim[sc]['D']['ci']]}")
        for t, v in prim[sc]["L"].items():
            print(f"  L[{t}] = {v['L']:+.3f} [{v['ci'][0]:+.3f}, {v['ci'][1]:+.3f}]")


def finish(res):
    json.dump(res, open(os.path.join(HERE, "mc_result.json"), "w"), indent=1)
    print("VERDICT:", res["verdict"])
    if "belief" in res:
        print("belief:", {k: (v["n_items_pass"], v["mean_q_cued"]) for k, v in res["belief"].items()})


# ---------------------------------------------------------------- calibrated planted gate
def calibrate():
    """Noise and base rates from the leak-probe ratings (already collected; contain no believed-cue data)."""
    d, items, tag, notag, loaded = SL.load_real()
    lg = lambda p: SL.tr(p, "logit")
    # instance SD: within (model, theory, item, tag direction), across the 2 instances
    grp = {}
    for (m, k, t, i), (p, tr_) in tag.items():
        if t in REAL:
            grp.setdefault((m, t, i, tr_), []).append(lg(p))
    inst_sd = float(np.sqrt(np.mean([np.var(v, ddof=1) for v in grp.values() if len(v) > 1])))
    # model SD: per (theory, item), SD of the 3 model means in NOTAG
    mm = []
    for t in REAL:
        for i in items:
            means = [np.mean([lg(notag[(m, k, t, i)]) for k in loaded["notag"][m]]) for m in MODELS]
            mm.append(np.var(means, ddof=1))
    model_sd = float(np.sqrt(np.mean(mm)))
    base = {(t, i): float(np.mean([lg(notag[(m, k, t, i)]) for m in MODELS for k in loaded["notag"][m]]))
            for t in ALL_T for i in items}
    return items, base, inst_sd, model_sd


def planted(n_runs):
    d = json.load(open(os.path.join(HERE, "items.json")))
    items, base, inst_sd, model_sd = calibrate()
    clusters = {it["id"]: it["cluster"] for it in d["items"]}
    silent = [i for i in items if d["toy_key"][i] == "silent"]
    emp = lambda rng: dict(base)
    scen = {
        "zero": ({}, "bits"),
        "iit_bits_0.15": ({"IIT": 0.15}, "bits"),
        "iit_bits_0.25": ({"IIT": 0.25}, "bits"),
        "iit_bits_0.40": ({"IIT": 0.40}, "bits"),
        "uniform_bits_0.15": ({t: 0.15 for t in REAL}, "bits"),
        "uniform_bits_0.25": ({t: 0.25 for t in REAL}, "bits"),
        "iit_logit_0.43": ({"IIT": 0.43}, "logit"),
        "uniform_logit_0.43": ({t: 0.43 for t in REAL}, "logit"),
        "iit_contrarian_logit_-0.75": ({"IIT": -0.75}, "logit"),
        "placebo_follows_logit_0.6": ({"PLACEBO_Q": 0.6}, "logit"),
    }
    out = dict(items=items, n_runs=n_runs, inst_sd=inst_sd, model_sd=model_sd, scenarios={})
    print(f"calibrated inst_sd={inst_sd:.3f} model_sd={model_sd:.3f}")
    for name, (leak, sc) in scen.items():
        rng = np.random.default_rng(zlib.crc32(("mc_" + name).encode()))
        counts = {"LEAK-DOMINATED": 0, "LEAK-BOUNDED": 0, "INCONCLUSIVE": 0}
        flags = 0
        for _ in range(n_runs):
            # the believed arm drops failing instances; plant with all 4 per model (the expected case)
            tag = SL.synth(items, rng, leak, sc, emp, model_sd=model_sd, inst_sd=inst_sd)
            r = SL.evaluate(tag, items, clusters, np.random.default_rng(rng.integers(2**32)), silent)
            counts[r["verdict"]] += 1
            flags += r["control_flag"]
        out["scenarios"][name] = dict(counts={k: v / n_runs for k, v in counts.items()},
                                      control_flag_rate=flags / n_runs)
        print(name, out["scenarios"][name], flush=True)
    json.dump(out, open(os.path.join(HERE, "planted_mc.json"), "w"), indent=1)


if __name__ == "__main__":
    if "--planted" in sys.argv:
        i = sys.argv.index("--planted")
        planted(int(sys.argv[i + 1]) if len(sys.argv) > i + 1 and sys.argv[i + 1].isdigit() else 100)
    else:
        score_real()
