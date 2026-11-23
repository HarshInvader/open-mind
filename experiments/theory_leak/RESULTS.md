# Theory-likelihood ledger, leak probe: results

Prereg: `docs/prereg/2026-11-24_theory_leak_probe.md`. It was sealed and hashed in `docs/prereg/HASHES.txt` at 2026-11-23T20:57:01Z, before any recognition or rating response. Scored with `score_leak.py` on 2026-11-23. The output is `result.json`. Every rater reply is saved in `ratings/`.

## Verdict: LEAK-BOUNDED (both scales, no control flag)

When the rater is told the cue is random, a "Reported outcome" cue on unknowable findings does not move AI raters' theory ratings.
- Every theory's leak index is within ±0.02 bits.
- Every 95% CI lies well inside the sealed BOUNDED limits.

**What this does not show:**
- **The cue is disowned, and there is no manipulation check.** So we cannot tell "raters resist outcome belief" apart from "raters ignored a line labelled noise".
- **It does not bound the memory path behind the pilot's IIT lead.** That path is confident recall of famous outcomes and of proponents' explanations.
- **Scaling to 59 items is not licensed.** See below.

## Gates

| Gate | Result |
|---|---|
| Recognition (`recog_result.json`) | PASS: 28 of 30 controls had p_real > 0.5. P01 and P05 were excluded (a model gave p_real ≥ 0.75). 9 items kept in 6 clusters: P02–P04 (post-cutoff results) and P06–P11 (pending outcomes). |
| Instances | Complete: 12 TAG (4 per model) and 6 NOTAG (2 per model). Every instance gave all 72 (theory, finding) pairs. |
| Counterbalancing | Exact: 2 instances tagged each way in every model × item cell. |
| Theory Z recovered in NOTAG | 36 of 36 committed cells, so not VOID. In the TAG arm, 71 of 72. |
| Control flag (Q; Z on its silent items) | Not raised. Every Q rating (162) and every Z-silent TAG rating (36) was exactly 0.5, so L = 0 with CI [0, 0]. |

## Leak indices (L_t: ½ × [tagged real − tagged mirror]; 95% CI over models × source clusters, B = 2000)

| | bits | 95% CI | logit | 95% CI |
|---|---|---|---|---|
| IIT | +0.007 | [−0.036, +0.038] | +0.014 | [−0.037, +0.058] |
| GNWT | −0.006 | [−0.049, +0.040] | +0.002 | [−0.056, +0.067] |
| RPT | −0.009 | [−0.042, +0.045] | −0.006 | [−0.036, +0.055] |
| HOT | −0.005 | [−0.043, +0.035] | +0.007 | [−0.028, +0.055] |
| PP | −0.013 | [−0.044, +0.015] | −0.011 | [−0.046, +0.025] |
| AST | −0.016 | [−0.050, +0.014] | −0.011 | [−0.040, +0.023] |
| **D** = L_IIT − ½(L_GNWT + L_HOT) | +0.012 | [−0.040, +0.063] | +0.009 | [−0.057, +0.065] |

The sealed BOUNDED limits were:
- **bits:** every L inside ±0.15 and D inside ±0.14;
- **logit:** every L inside ±0.26 and D inside ±0.24.

No CI lies wholly below 0, so there was no reactance. The probe rules out a leak larger than about 0.05 bits (0.07 logit) for any theory, along this path, at this cue strength.

## Why BOUNDED when the planted null gave BOUNDED only 14% of the time

`planted_kept.json` reran the planted gate on the 9 kept items:

| Planted | Result |
|---|---|
| No leak | BOUNDED 0.14, INCONCLUSIVE 0.86 |
| IIT leak of 0.25 bits | DOMINATED 0.41 |
| IIT leak of 0.40 bits | DOMINATED 1.00 |
| All theories, 0.25 bits | DOMINATED 0.96 |
| Ceiling-masked IIT leak of 0.75 logit | DOMINATED 0.92 |
| Contrarian rater | INCONCLUSIVE 1.00 |
| Placebo follows the cue | control flag 1.00 |

The synthetic raters had instance noise of 0.48 logit. Real instances of the same model differ by much less, and many cells sit at exactly 0.5 in every instance. So the real CIs are far narrower than planned, and the planted gate was pessimistic about noise, not lenient.

## Agreement, silence and the scaling rule (NOTAG arm)

| Statistic | Value | Prereg bar for scaling |
|---|---|---|
| Krippendorff α (logit) | 0.79 | ≥ 0.67 (pass) |
| Elastic fraction (theory × item cells with mean p in [0.4, 0.6]) | 0.63 | < 0.5 (fail) |

Most theory × item cells on these items are near-silent. That makes the bound less informative:
- 27% of real-theory TAG cells have a leak of exactly 0, which narrows the CIs.
- The Fable reviewer recomputed the leak on committed and near-silent cells separately. The committed cells also show no leak (mean −0.018 logit, against +0.010 in near-silent cells), so the null is not only an artefact of silence.

**Scaling to 59 items: not licensed.**
- The elastic fraction fails.
- The prereg already said BOUNDED alone does not license scaling.

## Forecast bits (descriptive only; NOTAG, 3 kept items with a real result, mean over 6 instances)

| Theory | Total bits, P02–P04 | Mean p_real: P02 / P03 / P04 |
|---|---|---|
| GNWT | +1.06 | 0.71 / 0.65 / 0.59 |
| HOT | +0.54 | 0.53 / 0.52 / 0.67 |
| PP | +0.32 | 0.44 / 0.58 / 0.61 |
| AST | +0.05 | 0.49 / 0.51 / 0.52 |
| IIT | −0.81 | 0.34 / 0.46 / 0.46 |
| RPT | −1.10 | 0.27 / 0.48 / 0.46 |

On these three post-cutoff findings the order is the reverse of the pilot, where IIT led. This is three items, one of them (P02) drafted from an abstract only. It is not a test of anything. We report it because the prereg said we would.

## Predictions vs outcome

| Sealed prediction | Outcome |
|---|---|
| The recognition control passes; P05 is the item most likely to be excluded | Passed (28/30). P05 was excluded, and so was P01. |
| L for Q near 0, so no control flag | Exactly 0; no flag |
| Real theories show at most a small uniform leak, L about 0.05–0.15 bits | Smaller than predicted: all within ±0.02 |
| D does not reach DOMINATED; the most likely verdict is INCONCLUSIVE | D did not reach DOMINATED, but the verdict was BOUNDED, not INCONCLUSIVE |

## Deviations and run notes

- **Rate limit:** the first launch of the 18 rating instances hit a gateway rate-limit (HTTP 503). Only 3 instances returned (TAG Fable 1–3). The other 15 were launched again in batches of 6. Those were their first answers, not re-requests, since no answer had been received. No instance was re-requested.
- **Fenced JSON:** two Sonnet instances (TAG 2 and NOTAG 1) wrapped their JSON array in a markdown code fence. The arrays inside were complete and well-formed, so they were saved unchanged. Notes are in `ratings/*.NOTE.txt`.
- **Instance prompts:** each rater read only its packet file, copied to a neutral filename with no key, model or arm in the name. Each rater ran in a fresh context with the instruction to use no other tool.

## Interpretation (Fable, interpreting review)

The probe shows that raters do not follow a disowned outcome cue. None of the 864 TAG "why" strings mentions the cue. The reviewer recomputed the statistics from the raw ratings and found no error that would change the verdict.

The next kill test is a **manipulation check**:
- **Packets:** the same 9 items and packets.
- **Cue:** framed as believed ("assume this outcome was observed").
- **Belief probe:** a closing p(A observed) question for each item.
- **Kill:** any real-theory leak ≥ 0.25 bits or 0.43 logit, or D ≥ 0.28 or 0.48, with its CI above 0. That demotes the ledger.
- **Void:** belief does not follow the cue.

The hypothesis-generator line (ds006394 screen, ds001785 confirm) can start in parallel. Human raters stay the only test of the memory path.
