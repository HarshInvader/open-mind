"""Round 15 item 3 (behaviour only): does a stronger earlier showing of the same face make it easier to see later?
Prereg: docs/prereg/2026-11-25_cohen_prior_showings.md

Unit: report-block SOA-50 face trials with a seen/unseen response. For each, count earlier showings of the SAME face
(both blocks, one session timeline): strong = SOA 67/83 (mostly visible), weak = SOA 17/33 (mostly invisible).
D = strong - weak. Given the total number of earlier showings, D is set by the random SOA assignment.

    python -I prior_showings.py design      # label-free design statistics -> out/prior_design.json
    python -I prior_showings.py calibrate   # randomisation null + planted fake responses -> out/prior_calibration.json
    python -I prior_showings.py run         # real D on real responses; refuses unless sealed -> out/prior_result.json
"""
import csv, json, sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
PREREG = HERE.parents[1] / "docs" / "prereg" / "2026-11-25_cohen_prior_showings.md"
SEED = 20261130
RUNS = 300
PLANT = 0.015          # 1.5 percentage points per net strong showing
BOUND = 0.015          # NO EFFECT needs the 95% CI inside +-BOUND
STRONG, WEAK = {"67", "83"}, {"17", "33"}


def load():
    rows = [r for r in csv.DictReader(open(HERE / "trials.csv")) if r["kind"] == "face" and r["soa"]]
    S = defaultdict(list)
    for r in rows:
        S[r["sub"]].append(r)
    D = {}
    for s, rs in S.items():
        rs.sort(key=lambda r: int(r["onset"]))
        soa = np.array([r["soa"] for r in rs])
        ident = np.array([int(r["ident"]) for r in rs])
        block = np.array([r["block"] for r in rs])
        resp = np.array([r["resp"] for r in rs])
        D[s] = dict(soa=soa, ident=ident, block=block, resp=resp, rank=np.arange(len(rs)))
    return D


def features(d, soa=None):
    """Per target trial: D (strong - weak earlier showings of that face), total earlier showings, rank, ident."""
    soa = d["soa"] if soa is None else soa
    tgt = np.where((d["block"] == "report") & (d["soa"] == "50") & np.isin(d["resp"], ["1", "2"]))[0]
    st, wk, tot = defaultdict(int), defaultdict(int), defaultdict(int)
    out = {i: None for i in tgt}
    tset = set(tgt.tolist())
    for j in range(len(soa)):
        f = d["ident"][j]
        if j in tset:
            out[j] = (st[f] - wk[f], tot[f])
        st[f] += soa[j] in STRONG
        wk[f] += soa[j] in WEAK
        tot[f] += 1
    Dv = np.array([out[i][0] for i in tgt], float)
    T = np.array([out[i][1] for i in tgt], float)
    return tgt, Dv, T


def slope(y, Dv, T, rank, ident):
    """OLS of seen on D with intercept, total earlier showings and rank. No identity dummies: SOA order is randomised within
    face within cycle, so D is independent of image visibility; dummies would absorb most of D's variance (prereg 1)."""
    X = np.column_stack([Dv, np.ones(len(Dv)), T, rank / 1000.0])
    return np.linalg.lstsq(X, y, rcond=None)[0][0]


def tq(n):
    from scipy.stats import t
    return float(t.ppf(0.975, n - 1))


def group(b):
    b = np.array(b)
    n = len(b)
    se = b.std(ddof=1) / np.sqrt(n)
    lo, hi = b.mean() - tq(n) * se, b.mean() + tq(n) * se
    if lo > 0:
        v = "EFFECT+"
    elif hi < 0:
        v = "EFFECT-"
    elif -BOUND < lo and hi < BOUND:
        v = "NO EFFECT"
    else:
        v = "INCONCLUSIVE"
    return dict(n=n, mean=float(b.mean()), ci95=[float(lo), float(hi)], verdict=v)


SWAP = {"17": "83", "83": "17", "33": "67", "67": "33"}


def permuted_soa(d, rng):
    """Randomisation null: for each face, with probability 1/2 swap strong and weak SOAs (17<->83, 33<->67) on all of
    that face's showings. This keeps |D|, T, the SOA-50 showings and the design's per-cycle balance, and makes the
    null D independent of the real D (prereg 3a)."""
    soa = d["soa"].copy()
    flip = rng.random(41) < 0.5
    for j in np.where(flip[d["ident"]] & (soa != "50"))[0]:
        soa[j] = SWAP.get(soa[j], soa[j])
    return soa


def design():
    D = load()
    res = {}
    for s, d in D.items():
        tgt, Dv, T = features(d)
        r = d["rank"][tgt]
        X = np.column_stack([np.ones(len(T)), T, r / 1000.0])
        resid = Dv - X @ np.linalg.lstsq(X, Dv, rcond=None)[0]
        res[s] = dict(n=len(tgt), mean_total=float(T.mean()), sd_D=float(Dv.std()), resid_sd_D=float(resid.std()))
    agg = dict(subjects=len(res), trials=int(sum(v["n"] for v in res.values())),
               median_trials=float(np.median([v["n"] for v in res.values()])),
               mean_earlier_showings=float(np.mean([v["mean_total"] for v in res.values()])),
               mean_resid_sd_D=float(np.mean([v["resid_sd_D"] for v in res.values()])))
    (OUT / "prior_design.json").write_text(json.dumps(dict(aggregate=agg, per_subject=res), indent=1) + "\n")
    print(json.dumps(agg, indent=1))


def fake_resp(d, tgt, Dv, T, rng, beta):
    """Fake seen/unseen: subject rate ~ U(0.2, 0.85), linear drift over the session, per-image offsets, AR(1) streaks,
    and item-specific practice (logit +0.03 per earlier showing of that face, i.e. rising with T but not with D)."""
    n = len(tgt)
    base = rng.uniform(0.2, 0.85)
    logit = np.log(base / (1 - base))
    drift = rng.normal(0, 0.5) * (np.arange(n) / n - 0.5)
    img = rng.normal(0, 0.8, 41)[d["ident"][tgt]]
    e = np.zeros(n)
    for k in range(1, n):
        e[k] = 0.3 * e[k - 1] + rng.normal(0, 0.5)
    p = 1 / (1 + np.exp(-(logit + drift + img + e + 0.03 * (T - T.mean()))))
    p = np.clip(p + beta * (Dv - Dv.mean()), 0, 1)
    return (rng.random(n) < p).astype(float)


def calibrate():
    D = load()
    rng = np.random.default_rng(SEED)
    T = {"null_real_resp": {}, "null_fake": {}, "planted": {}}
    for k in range(RUNS):
        bn, bf, bp = [], [], []
        for s, d in D.items():
            tgt, Dv0, Tt = features(d)
            r, idn = d["rank"][tgt], d["ident"][tgt]
            # (a) randomisation null on the real responses: real D is never regressed on real responses here
            _, Dp, Tp = features(d, permuted_soa(d, rng))
            y = (d["resp"][tgt] == "1").astype(float)
            bn.append(slope(y, Dp, Tp, r, idn))
            # (b) fake responses, no effect; (c) fake responses with planted effect on the real sequence's D
            bf.append(slope(fake_resp(d, tgt, Dv0, Tt, rng, 0.0), Dv0, Tt, r, idn))
            bp.append(slope(fake_resp(d, tgt, Dv0, Tt, rng, PLANT), Dv0, Tt, r, idn))
        for w, b in (("null_real_resp", bn), ("null_fake", bf), ("planted", bp)):
            v = group(b)["verdict"]
            T[w][v] = T[w].get(v, 0) + 1
    rates = {w: {v: n / RUNS for v, n in t.items()} for w, t in T.items()}
    res = dict(runs=RUNS, plant=PLANT, bound=BOUND, rates=rates,
               false_effect_null_real=rates["null_real_resp"].get("EFFECT+", 0) + rates["null_real_resp"].get("EFFECT-", 0),
               false_effect_null_fake=rates["null_fake"].get("EFFECT+", 0) + rates["null_fake"].get("EFFECT-", 0),
               power=rates["planted"].get("EFFECT+", 0))
    res["PASS"] = bool(res["false_effect_null_real"] <= 0.05 and res["false_effect_null_fake"] <= 0.05 and res["power"] >= 0.80)
    (OUT / "prior_calibration.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


def run():
    sys.path.insert(0, str(HERE.parents[0] / "rules"))
    from evidence import require_sealed
    for f in (PREREG, Path(__file__), OUT / "prior_calibration.json"):
        require_sealed(str(f))
    assert json.loads((OUT / "prior_calibration.json").read_text())["PASS"], "calibration failed: no run"
    D = load()
    b, b_nr = [], []
    for s, d in D.items():
        tgt, Dv, T = features(d)
        y = (d["resp"][tgt] == "1").astype(float)
        b.append(slope(y, Dv, T, d["rank"][tgt], d["ident"][tgt]))
        # secondary (descriptive): D from no-report-block showings only, for subjects who did that block first
        if d["block"][0] == "noreport":
            soa_nr = np.where(d["block"] == "noreport", d["soa"], "50")      # report-block showings neutralised
            _, Dn, Tn = features(d, soa_nr)
            b_nr.append(slope(y, Dn, T, d["rank"][tgt], d["ident"][tgt]))
    sec = None
    if len(b_nr) > 2:
        g = group(b_nr)
        sec = dict(n=g["n"], mean=g["mean"], ci95=g["ci95"])           # descriptive: no verdict (prereg 5)
    res = dict(primary=group(b), secondary_noreport_first=sec,
               per_subject=[float(x) for x in b])
    (OUT / "prior_result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "per_subject"}, indent=1))


if __name__ == "__main__":
    {"design": design, "calibrate": calibrate, "run": run}[sys.argv[1]]()
