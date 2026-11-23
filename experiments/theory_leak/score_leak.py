"""Leak probe for the theory-likelihood ledger: score the tagged-outcome ratings under the sealed rules.

Prereg: docs/prereg/2026-11-24_theory_leak_probe.md.
  - TAG arm: every finding carries "Reported outcome: A/B", assigned at random (counterbalanced: within each model every
    item is tagged toward side_real and toward side_mirror equally often).
  - NOTAG arm: same items, no tag (the forecast).
  - Leak index per theory t, on two scales (both sealed; verdicts need both):
      bits:  L_t = 1/2 * [mean bits when tagged side_real - mean bits when tagged side_mirror], bits = log2(2 p_real)
      logit: L_t = 1/2 * [mean logit(p_real) when tagged side_real - when tagged side_mirror]
    computed within (model, item), then averaged. D = L_IIT - mean(L_GNWT, L_HOT).
  - 95% CIs: bootstrap over models and over source clusters (items sharing a paper resample together).

Usage:
  python -I score_leak.py --recog              # recognition gate -> recog_result.json
  python -I score_leak.py                      # real ratings -> result.json
  python -I score_leak.py --planted [N_RUNS]   # planted gate on synthetic raters (cluster structure of the kept items)
"""
import json
import math
import os
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = ["fable", "opus", "sonnet"]
TAG_INST = 4          # per model: instances 1-2 use tag set S, 3-4 the flipped set
NOTAG_INST = 2
CLIP = (0.01, 0.99)
REAL = ["IIT", "GNWT", "RPT", "HOT", "PP", "AST"]
ALL_T = REAL + ["TOY_Z", "PLACEBO_Q"]
B = 2000

# Sealed thresholds. Pilot IIT-GNWT gap = 0.57 bits/item. Logit thresholds = bits thresholds / 0.58
# (d bits / d logit = (1 - p) / ln 2 = 0.58 at p = 0.6, the pilot's mean p_real).
TH = {
    "bits": dict(DOM_D=0.28, DOM_L=0.25, BND_D=0.14, BND_L=0.15),
    "logit": dict(DOM_D=0.48, DOM_L=0.43, BND_D=0.24, BND_L=0.26),
}
CTRL_TH = dict(bits=0.15, logit=0.26)   # content-free tag-following flag (Theory Q, Theory Z on its silent items)


def clipp(p):
    return min(max(float(p), CLIP[0]), CLIP[1])


def tr(p, scale):
    p = clipp(p)
    return math.log2(2 * p) if scale == "bits" else math.log(p / (1 - p))


def cell_leaks(tag, items, theories, scale):
    """arr[t][model_idx, item_idx] = 1/2 (mean when tagged real - mean when tagged mirror)."""
    grp = {}
    for (m, k, t, i), (p, tagged_real) in tag.items():
        grp.setdefault((m, t, i, tagged_real), []).append(tr(p, scale))
    arr = {}
    for t in theories:
        a = np.full((len(MODELS), len(items)), np.nan)
        for x, m in enumerate(MODELS):
            for y, i in enumerate(items):
                r, q = grp.get((m, t, i, True)), grp.get((m, t, i, False))
                assert r and q, ("missing tag direction", m, t, i)
                a[x, y] = 0.5 * (np.mean(r) - np.mean(q))
        arr[t] = a
    return arr


def leak_stats(tag, items, clusters, rng, scale, theories=REAL):
    arr = cell_leaks(tag, items, theories, scale)
    cl_names = sorted(set(clusters[i] for i in items))
    cl_idx = {c: [y for y, i in enumerate(items) if clusters[i] == c] for c in cl_names}

    def summ(sm, si):
        L = {t: float(arr[t][np.ix_(sm, si)].mean()) for t in theories}
        D = L["IIT"] - 0.5 * (L["GNWT"] + L["HOT"]) if {"IIT", "GNWT", "HOT"} <= set(L) else float("nan")
        return L, D

    L0, D0 = summ(np.arange(len(MODELS)), np.arange(len(items)))
    bL, bD = {t: [] for t in theories}, []
    for _ in range(B):
        sm = rng.integers(0, len(MODELS), len(MODELS))
        sc = rng.integers(0, len(cl_names), len(cl_names))
        si = np.concatenate([cl_idx[cl_names[c]] for c in sc])
        L, D = summ(sm, si)
        for t in theories:
            bL[t].append(L[t])
        bD.append(D)
    ci = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
    Ls = {t: dict(L=L0[t], ci=ci(bL[t])) for t in theories}
    Ds = dict(D=D0, ci=ci(bD))
    return Ls, Ds


def verdict_scale(Ls, Ds, scale):
    th = TH[scale]
    dom = (Ds["D"] >= th["DOM_D"] and Ds["ci"][0] > 0) or any(v["L"] >= th["DOM_L"] and v["ci"][0] > 0 for v in Ls.values())
    bnd = (all(-th["BND_L"] < v["ci"][0] and v["ci"][1] < th["BND_L"] for v in Ls.values())
           and -th["BND_D"] < Ds["ci"][0] and Ds["ci"][1] < th["BND_D"])
    react = any(v["ci"][1] < 0 for v in Ls.values()) or Ds["ci"][1] < 0
    return "LEAK-DOMINATED" if dom else ("LEAK-BOUNDED" if bnd and not react else "INCONCLUSIVE")


def combine(vb, vl, ctrl_flag):
    """Both scales must agree for DOMINATED or BOUNDED; a content-free control flag bars BOUNDED."""
    if vb == vl == "LEAK-DOMINATED":
        return "LEAK-DOMINATED"
    if vb == vl == "LEAK-BOUNDED" and not ctrl_flag:
        return "LEAK-BOUNDED"
    return "INCONCLUSIVE"


# ---------------------------------------------------------------- planted gate
def synth(items, rng, leak, scale_plant, base_override=None, model_sd=0.48, inst_sd=0.48):
    """Synthetic TAG-arm ratings. Base logit P(real|t,i) ~ N(0.45, 0.89) (pilot) unless overridden; model offsets
    N(0, model_sd) per cell; instance noise N(0, inst_sd). Leak planted toward the tagged side, in bits or logit."""
    base = {(t, i): rng.normal(0.45, 0.89) for t in ALL_T for i in items}
    if base_override:
        base.update(base_override(rng))
    for i in items:                       # controls: Q at 0.5, Z at its usual spread
        base[("PLACEBO_Q", i)] = 0.0
    moff = {(m, t, i): rng.normal(0, model_sd) for m in MODELS for t in ALL_T for i in items}
    half = set(rng.permutation(items)[: len(items) // 2])
    tag = {}
    for m in MODELS:
        for k in range(1, TAG_INST + 1):
            for i in items:
                tagged_real = (i in half) == (k <= TAG_INST // 2)
                for t in ALL_T:
                    lg = base[(t, i)] + moff[(m, t, i)] + rng.normal(0, inst_sd) * (0 if t == "PLACEBO_Q" else 1)
                    if t == "PLACEBO_Q":
                        lg = moff[(m, t, i)] * 0.1
                    d = leak.get(t, 0.0)
                    s = 1 if tagged_real else -1
                    if d and scale_plant == "logit":
                        lg += s * d
                    p = clipp(1 / (1 + math.exp(-lg)))
                    if d and scale_plant == "bits":
                        p = clipp(2 ** (math.log2(2 * p) + s * d - 1))
                    tag[(m, k, t, i)] = (p, tagged_real)
    return tag


def evaluate(tag, items, clusters, rng, toy_silent):
    Lb, Db = leak_stats(tag, items, clusters, rng, "bits")
    Ll, Dl = leak_stats(tag, items, clusters, rng, "logit")
    vb, vl = verdict_scale(Lb, Db, "bits"), verdict_scale(Ll, Dl, "logit")
    flag, ctrl = False, {}
    for scale in ("bits", "logit"):
        Lq, _ = leak_stats(tag, items, clusters, rng, scale, theories=["PLACEBO_Q"])
        ctrl[f"Q_{scale}"] = Lq["PLACEBO_Q"]
        flag |= Lq["PLACEBO_Q"]["L"] >= CTRL_TH[scale] and Lq["PLACEBO_Q"]["ci"][0] > 0
        if toy_silent:
            Lz, _ = leak_stats(tag, toy_silent, clusters, rng, scale, theories=["TOY_Z"])
            ctrl[f"Z_silent_{scale}"] = Lz["TOY_Z"]
            flag |= Lz["TOY_Z"]["L"] >= CTRL_TH[scale] and Lz["TOY_Z"]["ci"][0] > 0
    return dict(bits=dict(L=Lb, D=Db, verdict=vb), logit=dict(L=Ll, D=Dl, verdict=vl), controls=ctrl,
                control_flag=bool(flag), verdict=combine(vb, vl, flag))


def planted(n_runs):
    d = json.load(open(os.path.join(HERE, "items.json")))
    keep = kept_items(d)
    clusters = {it["id"]: it["cluster"] for it in d["items"]}
    silent = [i for i in keep if d["toy_key"][i] == "silent"]
    ceil = lambda rng: {("IIT", i): 2.5 for i in keep if i in ("P08", "P09", "P10")}   # IIT near ceiling on these
    scen = {
        "zero": ({}, "bits", None),
        "iit_bits_0.25": ({"IIT": 0.25}, "bits", None),
        "iit_bits_0.40": ({"IIT": 0.40}, "bits", None),
        "uniform_bits_0.25": ({t: 0.25 for t in REAL}, "bits", None),
        "iit_logit_0.75_ceiling": ({"IIT": 0.75}, "logit", ceil),
        "zero_ceiling": ({}, "bits", ceil),
        "iit_contrarian_logit_-0.75": ({"IIT": -0.75}, "logit", None),
        "placebo_follows_logit_0.6": ({"PLACEBO_Q": 0.6}, "logit", None),
    }
    out = {}
    for name, (leak, sc, ov) in scen.items():
        rng = np.random.default_rng(zlib.crc32(name.encode()))
        counts = {"LEAK-DOMINATED": 0, "LEAK-BOUNDED": 0, "INCONCLUSIVE": 0}
        Db, Dl, flags = [], [], 0
        for _ in range(n_runs):
            tag = synth(keep, rng, leak, sc, ov)
            r = evaluate(tag, keep, clusters, np.random.default_rng(rng.integers(2**32)), silent)
            counts[r["verdict"]] += 1
            Db.append(r["bits"]["D"]["D"])
            Dl.append(r["logit"]["D"]["D"])
            flags += r["control_flag"]
        out[name] = dict(counts={k: v / n_runs for k, v in counts.items()}, mean_D_bits=float(np.mean(Db)),
                         mean_D_logit=float(np.mean(Dl)), control_flag_rate=flags / n_runs)
        print(name, out[name], flush=True)
    return dict(items=keep, n_runs=n_runs, scenarios=out)


# ---------------------------------------------------------------- recognition gate
def score_recog():
    """Control: the 10 pilot items; >= 27 of 30 (model x item) must put p_real > 0.5, else VOID.
    Exclude a test item with a result if any model gives p_real >= 0.75. Exclude a pending item if any model says
    recall true or gives p outside [0.25, 0.75]. VOID if fewer than 8 test items remain."""
    d = json.load(open(os.path.join(HERE, "items.json")))
    pend = {it["id"]: it["pending"] for it in d["items"]}
    ctrl_ok, ctrl_n, excl, per = 0, 0, set(), {}
    for m in MODELS:
        key = json.load(open(os.path.join(HERE, "packets", f"recog_{m}_key.json")))
        arr = json.load(open(os.path.join(HERE, "ratings", f"recog_{m}.json")))
        assert sorted(x["finding"] for x in arr) == sorted(key), m
        for x in arr:
            k = key[x["finding"]]
            p = float(x["p"])
            assert 0 <= p <= 1, (m, x)
            pr = p if k["real_is_a"] else 1 - p
            rec = x.get("recall") is True or str(x.get("recall")).lower() == "true"
            per.setdefault(k["item"], {})[m] = dict(p_real=round(pr, 3), recall=rec)
            if k["control"]:
                ctrl_n += 1
                ctrl_ok += pr > 0.5
            elif not pend[k["item"]]:
                if pr >= 0.75:
                    excl.add(k["item"])
            elif rec or pr < 0.25 or pr > 0.75:
                excl.add(k["item"])
    assert ctrl_n == 30, ctrl_n
    kept = [i for i in pend if i not in excl]
    if ctrl_ok < 27:
        v = "VOID: recognition control failed (raters do not identify the known pilot outcomes)"
    elif len(kept) < 8:
        v = "VOID: fewer than 8 unknowable items remain"
    else:
        v = "PASS"
    res = dict(verdict=v, control_correct=int(ctrl_ok), control_n=ctrl_n, excluded=sorted(excl), kept=kept, per_item=per)
    json.dump(res, open(os.path.join(HERE, "recog_result.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "per_item"}, indent=1))


def kept_items(d):
    p = os.path.join(HERE, "recog_result.json")
    if os.path.exists(p):
        return json.load(open(p))["kept"]
    return [it["id"] for it in d["items"]]          # before the recognition gate (planted gate only)


# ---------------------------------------------------------------- real ratings
def load_real():
    d = json.load(open(os.path.join(HERE, "items.json")))
    rr = json.load(open(os.path.join(HERE, "recog_result.json")))
    assert rr["verdict"] == "PASS"
    items = rr["kept"]
    tag, notag, loaded = {}, {}, {"tag": {}, "notag": {}}
    for arm, n, store in (("tag", TAG_INST, tag), ("notag", NOTAG_INST, notag)):
        for m in MODELS:
            loaded[arm][m] = []
            for k in range(1, n + 1):
                fr = os.path.join(HERE, "ratings", f"{arm}_{m}_{k}.json")
                if not os.path.exists(fr):          # voided instance (two failed attempts), logged in RESULTS.md
                    continue
                key = json.load(open(os.path.join(HERE, "packets", f"{arm}_{m}_{k}_key.json")))
                arr = json.load(open(fr))
                seen = set()
                for x in arr:
                    fid, t = x["finding"], x["theory"]
                    assert t in ALL_T, ("unknown theory id", arm, m, k, t)
                    assert fid in key and (t, fid) not in seen, (arm, m, k, t, fid)
                    seen.add((t, fid))
                    p = clipp(x["p"])
                    kk = key[fid]
                    pr = p if kk["real_is_a"] else 1 - p
                    if arm == "tag":
                        store[(m, k, t, kk["item"])] = (pr, kk["tag_real"])
                    else:
                        store[(m, k, t, kk["item"])] = pr
                assert len(seen) == len(key) * len(ALL_T), (arm, m, k, len(seen))
                assert sorted(kk["item"] for kk in key.values()) == sorted(items), (arm, m, k)
                loaded[arm][m].append(k)
    for m in MODELS:
        if len(loaded["tag"][m]) < 3 or len(loaded["notag"][m]) < 1:
            raise SystemExit(f"VOID: too few instances for {m}: {loaded}")
    return d, items, tag, notag, loaded


def kripp_interval(mat):
    mat = np.asarray(mat, float)
    n_u, m = mat.shape
    vals = mat.ravel()
    n = vals.size
    do = sum(((row[:, None] - row[None, :]) ** 2).sum() / (m - 1) for row in mat) / n
    de = ((vals[:, None] - vals[None, :]) ** 2).sum() / (n * (n - 1))
    return float(1 - do / de) if de > 0 else float("nan")


def finite(obj):
    if isinstance(obj, dict):
        return all(finite(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return all(finite(v) for v in obj)
    if isinstance(obj, float):
        return math.isfinite(obj)
    return True


def score_real():
    d, items, tag, notag, loaded = load_real()
    clusters = {it["id"]: it["cluster"] for it in d["items"]}
    tk = d["toy_key"]
    res = {"n_items": len(items), "items": items, "instances": loaded}
    ninst = [(m, k) for m in MODELS for k in loaded["notag"][m]]
    tinst = [(m, k) for m in MODELS for k in loaded["tag"][m]]
    # Gate: Theory Z recovery in the NOTAG arm
    com = [(m, k, i) for m, k in ninst for i in items if tk[i] != "silent"]
    ok = sum((notag[(m, k, "TOY_Z", i)] >= 0.70) if tk[i] == "real" else (notag[(m, k, "TOY_Z", i)] <= 0.30) for m, k, i in com)
    res["G_toy_notag"] = dict(correct=int(ok), of=len(com), pass_=ok / len(com) >= 0.90)
    comt = [(m, k, i) for m, k in tinst for i in items if tk[i] != "silent"]
    okt = sum((tag[(m, k, "TOY_Z", i)][0] >= 0.70) if tk[i] == "real" else (tag[(m, k, "TOY_Z", i)][0] <= 0.30) for m, k, i in comt)
    res["toy_tag_arm"] = dict(correct=int(okt), of=len(comt))
    silent = [i for i in items if tk[i] == "silent"]
    ev = evaluate(tag, items, clusters, np.random.default_rng(2411), silent)
    res.update(ev)
    assert finite(ev), "non-finite leak statistic"
    if not res["G_toy_notag"]["pass_"]:
        res["verdict"] = "VOID: Theory Z not recovered in the no-tag arm"
    # Excess over content-free tag-following (reported always)
    res["L_minus_LQ"] = {sc: {t: ev[sc]["L"][t]["L"] - ev["controls"][f"Q_{sc}"]["L"] for t in REAL} for sc in ("bits", "logit")}
    # NOTAG forecast (descriptive) and agreement
    real_items = [it["id"] for it in d["items"] if it["id"] in items and not it["pending"]]
    res["forecast_items"] = real_items
    res["forecast_bits"] = {t: dict(total=float(np.mean([sum(tr(notag[(m, k, t, i)], "bits") for i in real_items) for m, k in ninst])),
                                    per_item={i: round(float(np.mean([notag[(m, k, t, i)] for m, k in ninst])), 3) for i in real_items})
                            for t in REAL}
    mat = [[tr(notag[(m, k, t, i)], "logit") for m, k in ninst] for t in REAL for i in items]
    res["alpha_notag"] = kripp_interval(mat)
    pm = {t: np.array([np.mean([notag[(m, k, t, i)] for m, k in ninst]) for i in items]) for t in REAL}
    res["elastic_frac_notag"] = float(np.mean([np.mean((v >= 0.4) & (v <= 0.6)) for v in pm.values()]))
    json.dump(res, open(os.path.join(HERE, "result.json"), "w"), indent=1)
    print("VERDICT:", res["verdict"], "| bits:", ev["bits"]["verdict"], "| logit:", ev["logit"]["verdict"],
          "| control flag:", ev["control_flag"])
    for sc in ("bits", "logit"):
        print(f"[{sc}] D = {ev[sc]['D']['D']:+.3f} {['%+.3f' % x for x in ev[sc]['D']['ci']]}")
        for t, v in ev[sc]["L"].items():
            print(f"  L[{t}] = {v['L']:+.3f} [{v['ci'][0]:+.3f}, {v['ci'][1]:+.3f}]")
    print("controls:", json.dumps(ev["controls"]))
    print(json.dumps({k: res[k] for k in ("G_toy_notag", "toy_tag_arm", "alpha_notag", "elastic_frac_notag")}))


def main():
    if "--planted" in sys.argv:
        i = sys.argv.index("--planted")
        n_runs = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 and sys.argv[i + 1].isdigit() else 200
        res = planted(n_runs)
        tagname = "planted_kept.json" if os.path.exists(os.path.join(HERE, "recog_result.json")) else "planted_all11.json"
        json.dump(res, open(os.path.join(HERE, tagname), "w"), indent=1)
        return
    if "--recog" in sys.argv:
        return score_recog()
    score_real()


if __name__ == "__main__":
    main()
