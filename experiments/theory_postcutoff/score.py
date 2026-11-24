"""Post-cutoff theory ledger with a hindsight arm: score under the sealed rules.

Prereg: docs/prereg/2026-11-24_theory_postcutoff_ledger.md (draft until sealed).

Items: the 10 pilot constraints ("famous", ids C..) and post-cutoff findings first posted on or after 2026-07-01 that
pass the recognition gate ("post", ids N.. and P0x).
  BLIND arm    (2 instances per model): famous + post items, A/B sides seeded, nothing says which side is real.
  INFORMED arm (2 instances per model): post items only, each with the observed outcome and the study's abstract.
Cell bits = log2(2 * p_real), p clipped to [0.01, 0.99]; averaged over instances within a model, then over models.

Primary: lead = bits(IIT) - 1/2 [bits(GNWT) + bits(HOT)] per item, BLIND arm, post items that split the theories
  (an item splits if some real theory's rater-mean |p - 0.5| >= 0.2; symmetric in A/B, so blind to the real side).
  SURVIVES  lead >= 0.28 and CI lower bound > 0       (0.28 = half the pilot's 0.55 bits/item)
  KILLED    CI upper bound < 0.28
  INCONCLUSIVE otherwise.
Hindsight: H_t = bits(INFORMED) - bits(BLIND) on post items; D_H = H_IIT - 1/2 (H_GNWT + H_HOT).
  FAVOURS-IIT if D_H >= 0.25 and CI lower > 0; AGAINST-IIT if D_H <= -0.25 and CI upper < 0;
  BOUNDED if the CI lies inside (-0.25, 0.25); UNCLEAR otherwise.
CIs: bootstrap over the 3 models and over source clusters (famous items are one cluster each), B = 2000, seed 2511.
  Verdict CIs = estimate +/- t(0.975, clusters - 1) x bootstrap SD; percentile CIs are reported alongside.

Usage:
  python -I score.py --recog            # recognition gate -> recog_result.json
  python -I score.py                    # real ratings -> result.json
  python -I score.py --planted [N]      # planted gate on synthetic raters -> planted.json
"""
import json
import math
import os
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = ["fable", "opus", "sonnet"]
BLIND_INST, INF_INST = 2, 2
CLIP = (0.01, 0.99)
REAL = ["IIT", "GNWT", "RPT", "HOT", "PP", "AST"]
ALL_T = REAL + ["TOY_Z", "PLACEBO_Q"]
B = 2000
SEED = 2511
LEAD_BAR = 0.28
PILOT_LEAD = 0.55
H_BAR = 0.25
SPLIT = 0.2
MIN_SPLIT_ITEMS, MIN_SPLIT_CLUSTERS = 8, 6
MIN_ITEMS, MIN_CLUSTERS = 10, 6


def bits(p):
    p = min(max(float(p), CLIP[0]), CLIP[1])
    return math.log2(2 * p)


def ci(v):
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def tci(point, bt, n_clusters):
    """Verdict CI: point +/- t(0.975, n_clusters - 1) x bootstrap SD. Percentile intervals undercover with ~14
    clusters (planted gate: 5-10% false SURVIVES under a true lead of 0), so the verdict intervals use this wider form."""
    from scipy import stats
    h = stats.t.ppf(0.975, max(n_clusters - 1, 1)) * float(np.std(bt, ddof=1))
    return [float(point - h), float(point + h)]


def ncl(items, clusters):
    return len(set(clusters[i] for i in items))


def cell_mean(store, items, theories, f=bits):
    """arr[t][model, item] = mean over instances of f(p_real)."""
    g = {}
    for (m, k, t, i), p in store.items():
        g.setdefault((m, t, i), []).append(f(p))
    return {t: np.array([[np.mean(g[(m, t, i)]) for i in items] for m in MODELS]) for t in theories}


def lead_of(arr, sm, si):
    a = lambda t: arr[t][np.ix_(sm, si)].mean()
    return a("IIT") - 0.5 * (a("GNWT") + a("HOT"))


def boot_idx(rng, items, clusters):
    names = sorted(set(clusters[i] for i in items))
    idx = {c: [y for y, i in enumerate(items) if clusters[i] == c] for c in names}
    sc = rng.integers(0, len(names), len(names))
    return np.concatenate([idx[names[c]] for c in sc])


def splitting(blind, items):
    pm = cell_mean(blind, items, REAL, f=lambda p: p)
    return [i for y, i in enumerate(items) if max(abs(pm[t][:, y].mean() - 0.5) for t in REAL) >= SPLIT]


def analyse(blind, inf, famous, post, clusters, rng, named=()):
    out = {}
    split = splitting(blind, post)
    out["post_items"], out["split_items"] = post, split
    out["split_clusters"] = len(set(clusters[i] for i in split))
    allm = np.arange(len(MODELS))
    ab = cell_mean(blind, famous + post, REAL + ["PLACEBO_Q"])
    pos = {i: y for y, i in enumerate(famous + post)}
    fsplit = splitting(blind, famous)
    sets = dict(post_split=split, post_all=post, famous_split=fsplit, famous=famous)
    res = {}
    for name, s in sets.items():
        if not s:
            res[name] = None
            continue
        si = np.array([pos[i] for i in s])
        l0 = lead_of(ab, allm, si)
        bt, bi = [], []
        for _ in range(B):
            sm = rng.integers(0, 3, 3)
            sub = boot_idx(rng, s, clusters)
            bt.append(lead_of(ab, sm, si[sub]))
            bi.append(ab["IIT"][np.ix_(sm, si[sub])].mean())
        per_t = {t: float(ab[t][:, si].mean()) for t in REAL}
        res[name] = dict(lead=float(l0), ci=tci(l0, bt, ncl(s, clusters)), ci_percentile=ci(bt), n_items=len(s),
                         bits_per_item=per_t, iit_bits=dict(b=per_t["IIT"], ci=tci(per_t["IIT"], bi, ncl(s, clusters))))
    # famous minus post (split), joint bootstrap
    if split:
        sf, sp = np.array([pos[i] for i in famous]), np.array([pos[i] for i in split])
        d0 = lead_of(ab, allm, sf) - lead_of(ab, allm, sp)
        bt = []
        for _ in range(B):
            sm = rng.integers(0, 3, 3)
            bt.append(lead_of(ab, sm, sf[boot_idx(rng, famous, clusters)]) - lead_of(ab, sm, sp[boot_idx(rng, split, clusters)]))
        res["famous_minus_post_split"] = dict(diff=float(d0), ci=tci(d0, bt, ncl(split, clusters)), ci_percentile=ci(bt))
    out["lead"] = res
    # verdict
    p = res["post_split"]
    if not split or len(split) < MIN_SPLIT_ITEMS or out["split_clusters"] < MIN_SPLIT_CLUSTERS:
        v = "UNINFORMATIVE: too few post-cutoff items split the theories"
    elif p["lead"] >= LEAD_BAR and p["ci"][0] > 0:
        v = "SURVIVES (REDUCED: CI excludes the pilot's 0.55)" if p["ci"][1] < PILOT_LEAD else "SURVIVES"
    elif p["ci"][1] < LEAD_BAR:
        v = "KILLED"
    elif p["ci"][1] < PILOT_LEAD:
        v = "REDUCED"
    else:
        v = "INCONCLUSIVE"
    out["primary_verdict"] = v
    # hindsight
    if inf is not None:
        out["hindsight"] = hindsight(blind, inf, post, clusters, rng)
        rest = [i for i in post if i not in set(named)]
        if named and len(rest) >= 2:
            out["hindsight_without_theory_naming_abstracts"] = dict(excluded=sorted(named), **hindsight(blind, inf, rest, clusters, rng))
    return out


def hindsight(blind, inf, post, clusters, rng):
    if True:
        bb = cell_mean(blind, post, ALL_T)
        ii = cell_mean(inf, post, ALL_T)
        H = {t: ii[t] - bb[t] for t in ALL_T}
        h0 = {t: float(H[t].mean()) for t in ALL_T}
        d0 = h0["IIT"] - 0.5 * (h0["GNWT"] + h0["HOT"])
        bH, bD = {t: [] for t in ALL_T}, []
        for _ in range(B):
            sm = rng.integers(0, 3, 3)
            si = boot_idx(rng, post, clusters)
            hh = {t: H[t][np.ix_(sm, si)].mean() for t in ALL_T}
            for t in ALL_T:
                bH[t].append(hh[t])
            bD.append(hh["IIT"] - 0.5 * (hh["GNWT"] + hh["HOT"]))
        c = tci(d0, bD, ncl(post, clusters))
        if d0 >= H_BAR and c[0] > 0:
            hv = "FAVOURS-IIT"
        elif d0 <= -H_BAR and c[1] < 0:
            hv = "AGAINST-IIT"
        elif -H_BAR < c[0] and c[1] < H_BAR:
            hv = "BOUNDED"
        else:
            hv = "UNCLEAR"
        return dict(H={t: dict(H=h0[t], ci=ci(bH[t])) for t in ALL_T}, D_H=dict(D=float(d0), ci=c), verdict=hv)


def gates(blind, inf, famous, post, toy_key):
    g = {}
    for arm, store, items in (("blind", blind, famous + post), ("informed", inf, post)):
        if store is None:
            continue
        com = [(m, k, i, p) for (m, k, t, i), p in store.items() if t == "TOY_Z" and toy_key.get(i) in ("actual", "mirror")]
        ok = sum((p >= 0.70) if toy_key[i] == "actual" else (p <= 0.30) for m, k, i, p in com)
        q = [p for (m, k, t, i), p in store.items() if t == "PLACEBO_Q"]
        sil = [p for (m, k, t, i), p in store.items() if t == "TOY_Z" and toy_key.get(i) == "silent"]
        g[arm] = dict(G1_toy=dict(ok=int(ok), n=len(com), pass_=bool(com) and ok / len(com) >= 0.9),
                      Z_silent_report=dict(n=len(sil), frac_outside_0p35_0p65=float(np.mean([abs(x - 0.5) > 0.15 for x in sil])) if sil else None),
                      G2_placebo=dict(bias=float(np.mean(q) - 0.5), out_frac=float(np.mean([abs(x - 0.5) > 0.15 for x in q])),
                                      pass_=bool(abs(np.mean(q) - 0.5) <= 0.10 and np.mean([abs(x - 0.5) > 0.15 for x in q]) <= 0.20)))
    # G3: Krippendorff alpha over models, blind arm, post items, real theories, logit of model-mean p
    pm = cell_mean(blind, post, REAL, f=lambda p: p)
    lg = lambda p: math.log(min(max(p, CLIP[0]), CLIP[1]) / (1 - min(max(p, CLIP[0]), CLIP[1])))
    mat = np.array([[lg(pm[t][m, y]) for m in range(3)] for t in REAL for y in range(len(post))])
    g["G3_alpha"] = dict(alpha=kripp(mat), pass_=kripp(mat) >= 0.67)
    return g


def kripp(mat):
    mat = np.asarray(mat, float)
    n_u, m = mat.shape
    v = mat.ravel()
    do = sum(((r[:, None] - r[None, :]) ** 2).sum() / (m - 1) for r in mat) / v.size
    de = ((v[:, None] - v[None, :]) ** 2).sum() / (v.size * (v.size - 1))
    return float(1 - do / de) if de > 0 else float("nan")


def final(g, an):
    if not (g["blind"]["G1_toy"]["pass_"] and g["blind"]["G2_placebo"]["pass_"]):
        return "VOID: blind-arm toy recovery or placebo gate failed"
    if not g["G3_alpha"]["pass_"]:
        return "UNDER-SPECIFIED: raters do not agree on what the theories predict for post-cutoff findings"
    return an["primary_verdict"]


# ---------------------------------------------------------------- synthetic raters (planted gate)
def synth(items, rng, mu, sd_item, elastic, model_sd=0.48, inst_sd=0.48, ninst=2, shift=None):
    """p_real per (model, inst, theory, item). True logit ~ N(mu[t], sd_item) (N(0, 0.2) on elastic items).
    shift: extra bits per theory (hindsight) applied after the logit draw."""
    out = {}
    base = {}
    for t in ALL_T:
        for i in items:
            base[(t, i)] = rng.normal(0, 0.2) if i in elastic else rng.normal(mu.get(t, 0.0), sd_item)
    for m in MODELS:
        for t in ALL_T:
            for i in items:
                mo = rng.normal(0, model_sd)
                for k in range(1, ninst + 1):
                    if t == "PLACEBO_Q":
                        out[(m, k, t, i)] = 0.5
                        continue
                    lg = base[(t, i)] + mo + rng.normal(0, inst_sd)
                    p = 1 / (1 + math.exp(-lg))
                    if shift and shift.get(t):
                        p = 2 ** (math.log2(2 * min(max(p, CLIP[0]), CLIP[1])) + shift[t] - 1)
                    out[(m, k, t, i)] = min(max(p, CLIP[0]), CLIP[1])
    return out, base


def planted(n_runs):
    d = json.load(open(os.path.join(HERE, "items.json"))) if os.path.exists(os.path.join(HERE, "items.json")) else None
    if d:
        famous = [it["id"] for it in d["famous"]]
        post = [it["id"] for it in d["post"]]
        clusters = {it["id"]: it["cluster"] for it in d["post"]}
    else:                                   # placeholder structure until the items exist: 20 post items, 14 clusters
        famous = [f"C{j:02d}" for j in range(10)]
        post = [f"N{j:02d}" for j in range(20)]
        clusters = {i: f"c{j if j < 14 else j - 14}" for j, i in enumerate(post)}
    clusters.update({i: i for i in famous})
    # mu for IIT chosen so the planted lead in bits is close to the target; calibrated numerically below
    def mu_for(lead):
        return dict(IIT=lead * 1.55, GNWT=0.0, HOT=0.0, RPT=0.3, PP=0.1, AST=0.0)
    scen = {
        "lead_0.55_everywhere": (0.55, 0.55, 0.0, None),
        "lead_0.55_famous_0_post": (0.55, 0.0, 0.0, None),
        "lead_0.55_famous_0.28_post": (0.55, 0.28, 0.0, None),
        "lead_0_post_half_elastic": (0.55, 0.0, 0.5, None),
        "lead_0.55_post_70pct_elastic": (0.55, 0.55, 0.7, None),
        "hindsight_iit_0.25": (0.55, 0.0, 0.0, {"IIT": 0.25}),
        "hindsight_uniform_0.25": (0.55, 0.0, 0.0, {t: 0.25 for t in REAL}),
        "hindsight_iit_0.40": (0.55, 0.0, 0.0, {"IIT": 0.40}),
        "lead_0.55_post_50pct_elastic": (0.55, 0.55, 0.5, None),
        "lead_0.55_post_60pct_elastic": (0.55, 0.55, 0.6, None),
        "lead_0_post_60pct_elastic": (0.55, 0.0, 0.6, None),
    }
    out = {}
    for name, (lf, lp, ef, hs) in scen.items():
        rng = np.random.default_rng(zlib.crc32(name.encode()))
        counts, hcounts, leads, Ds, real_leads = {}, {}, [], [], []
        for _ in range(n_runs):
            el = set(rng.permutation(post)[: int(round(ef * len(post)))])
            bf, basef = synth(famous, rng, mu_for(lf), 0.89, set())
            bp, basep = synth(post, rng, mu_for(lp), 0.89, el)
            blind = {**bf, **bp}
            # informed arm: same truth as blind + shift, fresh noise
            inf = {}
            for (m, k, t, i), p in bp.items():
                if t == "PLACEBO_Q":
                    inf[(m, k, t, i)] = 0.5
                    continue
                lg = math.log(p / (1 - p)) + rng.normal(0, 0.3)
                q = 1 / (1 + math.exp(-lg))
                if hs and hs.get(t):
                    q = 2 ** (math.log2(2 * min(max(q, CLIP[0]), CLIP[1])) + hs[t] - 1)
                inf[(m, k, t, i)] = min(max(q, CLIP[0]), CLIP[1])
            an = analyse(blind, inf, famous, post, clusters, np.random.default_rng(rng.integers(2**32)))
            v = an["primary_verdict"].split(":")[0]
            counts[v] = counts.get(v, 0) + 1
            hcounts[an["hindsight"]["verdict"]] = hcounts.get(an["hindsight"]["verdict"], 0) + 1
            if an["lead"]["post_split"]:
                leads.append(an["lead"]["post_split"]["lead"])
            Ds.append(an["hindsight"]["D_H"]["D"])
            tb = lambda t: np.mean([bits(1 / (1 + math.exp(-basep[(t, i)]))) for i in post if i not in el] or [0])
            real_leads.append(tb("IIT") - 0.5 * (tb("GNWT") + tb("HOT")))
        out[name] = dict(primary={k: v / n_runs for k, v in counts.items()}, hindsight={k: v / n_runs for k, v in hcounts.items()},
                         mean_lead_post_split=float(np.mean(leads)) if leads else None,
                         true_lead_post_nonelastic=float(np.mean(real_leads)), mean_D_H=float(np.mean(Ds)))
        print(name, out[name], flush=True)
    return dict(n_runs=n_runs, n_post=len(post), n_clusters=len(set(clusters[i] for i in post)), scenarios=out)


# ---------------------------------------------------------------- recognition gate
def score_recog():
    """Control: the 10 pilot items; >= 25 of 30 (model x item) must put p_real > 0.5, else VOID.
    Exclude a post item if any model gives p_real >= 0.75 or says recall true.
    VOID if fewer than 10 post items or 6 clusters remain."""
    d = json.load(open(os.path.join(HERE, "items.json")))
    cl = {it["id"]: it["cluster"] for it in d["post"]}
    ok, n, excl, per = 0, 0, set(), {}
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
                n += 1
                ok += pr > 0.5
            elif pr >= 0.75 or rec:
                excl.add(k["item"])
    assert n == 30, n
    kept = [i for i in cl if i not in excl]
    if ok < 25:
        v = "VOID: recognition control failed"
    elif len(kept) < MIN_ITEMS or len(set(cl[i] for i in kept)) < MIN_CLUSTERS:
        v = "VOID: too few unknowable post-cutoff items remain"
    else:
        v = "PASS"
    res = dict(verdict=v, control_correct=int(ok), control_n=n, excluded=sorted(excl), kept=kept, per_item=per)
    json.dump(res, open(os.path.join(HERE, "recog_result.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "per_item"}, indent=1))


# ---------------------------------------------------------------- real ratings
def load_arm(arm, n, items_expected):
    store, loaded = {}, {m: [] for m in MODELS}
    for m in MODELS:
        for k in range(1, n + 1):
            fr = os.path.join(HERE, "ratings", f"{arm}_{m}_{k}.json")
            if not os.path.exists(fr):
                continue
            key = json.load(open(os.path.join(HERE, "packets", f"{arm}_{m}_{k}_key.json")))
            seen = set()
            for x in json.load(open(fr)):
                fid, t = x["finding"], x["theory"]
                assert t in ALL_T and fid in key and (t, fid) not in seen, (arm, m, k, t, fid)
                seen.add((t, fid))
                p = min(max(float(x["p"]), CLIP[0]), CLIP[1])
                store[(m, k, t, key[fid]["item"])] = p if key[fid]["real_is_a"] else 1 - p
            assert len(seen) == len(key) * len(ALL_T), (arm, m, k, len(seen))
            assert sorted(v["item"] for v in key.values()) == sorted(items_expected), (arm, m, k)
            loaded[m].append(k)
        if not loaded[m]:
            raise SystemExit(f"VOID: no {arm} instance for {m}")
    return store, loaded


def score_real():
    d = json.load(open(os.path.join(HERE, "items.json")))
    rr = json.load(open(os.path.join(HERE, "recog_result.json")))
    assert rr["verdict"] == "PASS"
    famous = [it["id"] for it in d["famous"]]
    post = rr["kept"]
    clusters = {it["id"]: it["cluster"] for it in d["post"]}
    clusters.update({i: i for i in famous})
    blind, lb = load_arm("blind", BLIND_INST, famous + post)
    try:
        inf, li = load_arm("informed", INF_INST, post)
    except SystemExit as e:                          # a void informed arm does not block the primary verdict
        inf, li = None, str(e)
    g = gates(blind, inf, famous, post, d["toy_key"])
    named = [it["id"] for it in d["post"] if it.get("abstract_names_theory") and it["id"] in post]
    an = analyse(blind, inf, famous, post, clusters, np.random.default_rng(SEED), named)
    pm = cell_mean(blind, post, REAL, f=lambda p: p)
    elastic = float(np.mean([0.4 <= pm[t][:, y].mean() <= 0.6 for t in REAL for y in range(len(post))]))
    res = dict(verdict=final(g, an), gates=g, analysis=an, elastic_fraction_post=elastic, instances=dict(blind=lb, informed=li))
    if g.get("informed") and not g["informed"]["G2_placebo"]["pass_"]:
        res["hindsight_flag"] = "placebo moved in the informed arm: part of the hindsight shift is content-free"
    json.dump(res, open(os.path.join(HERE, "result.json"), "w"), indent=1)
    print(json.dumps(dict(verdict=res["verdict"], lead=an["lead"], hindsight=an.get("hindsight", {}).get("D_H")), indent=1))


if __name__ == "__main__":
    if "--recog" in sys.argv:
        score_recog()
    elif "--planted" in sys.argv:
        n = int(sys.argv[sys.argv.index("--planted") + 1]) if len(sys.argv) > sys.argv.index("--planted") + 1 else 100
        r = planted(n)
        json.dump(r, open(os.path.join(HERE, "planted.json"), "w"), indent=1)
    else:
        score_real()
