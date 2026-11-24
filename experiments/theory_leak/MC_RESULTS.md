# Theory-likelihood ledger, manipulation check: results

Prereg: `docs/prereg/2026-11-24_theory_leak_manipulation_check.md`. It was sealed and hashed in `docs/prereg/HASHES.txt` at 2026-11-24T04:06:50Z, before any rating response. Scored with `score_mc.py`. The output is `mc_result.json`. Every rater reply is saved verbatim in `ratings/mc_*.json`.

## Verdict: LEAK-BOUNDED (primary and sensitivity analyses, both scales, no control flag)

The packets stated the outcome as one "the experiment observed". All 12 rater instances then confirmed that outcome in the belief probe. Even so, their ratings of what six consciousness theories predict moved very little.
- Every real theory's leak index is below +0.07 bits (+0.09 logit).
- Every 95% CI lies inside the sealed BOUNDED limits: L inside ±0.15 bits / ±0.26 logit, and D inside ±0.14 / ±0.24.
- D = +0.010 bits [−0.055, +0.081], so the leak does not favour IIT.

This narrows the gap the leak probe left, but does not close it. Raters do not just ignore a cue labelled as noise: their theory likelihoods also barely move when the outcome is stipulated and they repeat it back. They did not come to hold it, though (see the belief probe).

**What this does not show:**
- **The belief is stipulated, not held.** Raters encoded the scenario (q_cued 0.95–0.97), but their own belief barely moved (mean q_own toward the cued side = 0.57). A BOUNDED verdict bounds stipulated outcomes. It does not bound outcomes a rater recalls and actually believes.
- **The memory path is still untested.** Confident recall of famous outcomes and of proponents' post-hoc explanations could still drive the pilot's IIT lead. Only human raters, or genuinely unseen findings, test that.
- **It does not license scaling to 59 items.** The elastic-fraction rule from the leak probe still fails.

## Gates

| Gate | Result |
|---|---|
| Instances | Complete: 12 (4 per model), each with all 72 (theory, finding) pairs and 9 belief answers. No reply was fenced. |
| Belief gate (q toward the cued side ≥ 0.75 on ≥ 8 of 9 items; ≥ 3 passing instances per model) | PASS: 12 of 12 instances passed on 9 of 9 items. Mean q_cued was 0.97 (Opus 2 and 4: 0.95). |
| Primary vs sensitivity | Identical, because every valid instance passed the gate. |
| Theory Z | 72 of 72 committed cells were correct, and none failed on the cued side. Z read its stated claims, not the cue. |
| Control flag (Q; Z on its silent items) | Not raised. Q and Z-silent were exactly 0.5 everywhere, so L = 0 with CI [0, 0]. |

## Leak indices (L_t: ½ × [tagged real − tagged mirror]; 95% CI over models × source clusters, B = 2000, seed 2411)

| | bits | 95% CI | logit | 95% CI | Disowned cue (leak probe), bits |
|---|---|---|---|---|---|
| IIT | +0.039 | [−0.011, +0.078] | +0.063 | [−0.020, +0.123] | +0.007 |
| GNWT | +0.020 | [−0.045, +0.064] | +0.042 | [−0.062, +0.109] | −0.006 |
| RPT | +0.035 | [−0.013, +0.071] | +0.048 | [−0.020, +0.093] | −0.009 |
| HOT | +0.037 | [−0.014, +0.085] | +0.062 | [−0.002, +0.133] | −0.005 |
| PP | +0.062 | [+0.015, +0.118] | +0.086 | [+0.017, +0.150] | −0.013 |
| AST | +0.014 | [−0.026, +0.060] | +0.022 | [−0.015, +0.071] | −0.016 |
| **D** = L_IIT − ½(L_GNWT + L_HOT) | +0.010 | [−0.055, +0.081] | +0.010 | [−0.101, +0.124] | +0.012 |

L − L_Q equals L for every theory, because L_Q = 0 exactly.

**Reading:** stipulating the outcome adds a small, roughly uniform pull toward it.
- Every point estimate is positive, at +0.01 to +0.06 bits. Under the disowned cue they sat at about 0.
- Only PP's CI excludes 0. Even PP's upper bound (+0.118 bits) is below the BOUNDED limit of 0.15.
- The pull is spread across theories, so D stays near 0. Nothing here would manufacture an IIT lead.

## Paired comparison with the disowned cue (descriptive; same 12 packets, passing instances, seed 2412)

ΔL = L(stipulated) − L(disowned), per theory, bits [95% CI]:
- IIT +0.032 [−0.031, +0.106]
- GNWT +0.026 [−0.057, +0.096]
- RPT +0.043 [−0.016, +0.092]
- HOT +0.043 [−0.010, +0.104]
- PP +0.075 [+0.008, +0.137]
- AST +0.030 [−0.017, +0.095]

The logit-scale values have the same signs. PP is again the only CI above 0 (+0.097 [+0.009, +0.173]).

Stipulating the outcome raised the leak by a few hundredths of a bit, mostly for PP. PP's rationales lean on active sampling and on priors carrying over, so PP is the theory raters can most easily stretch toward a stated result.

## Belief probe (descriptive)

| | Mean over instances | Range |
|---|---|---|
| q toward the cued side (the gate) | 0.966 | 0.95–0.97 |
| q_own toward the cued side | 0.566 | 0.483–0.617 |

The cued side was counterbalanced, so a q_own of 0.5 means "unmoved". Raters repeated the stipulated outcome almost perfectly, but their own credence moved only about 0.07 toward it. So this test is closer to "what if this were the result?" than to "I know this is the result".

## Rationales

The sealed regex `\b(reported|observed|outcome|result)\b` matched 1 of 648 real-theory "why" strings. The match was "Prefrontal workspace ignition should accompany reported experience." (Fable 1, GNWT). That is about reportability, not the cue, so in effect no rationale cites the stated outcome.

Silence was about the same as under the disowned cue. 33.5% of real-theory cells were exactly 0.5, against 35.2% in the leak-probe TAG arm.

## Predictions vs outcome

| Sealed prediction | Outcome |
|---|---|
| The belief gate passes, with q_cued ≥ 0.9 in most instances | Passed in all 12 instances; q_cued 0.95–0.97 |
| Real theories show a small uniform leak, L about 0.05–0.20 bits | Smaller: +0.01 to +0.06. Uniform in sign, and only PP clearly above 0 |
| D stays below 0.28 bits | +0.010 |
| INCONCLUSIVE or BOUNDED, with INCONCLUSIVE more likely | BOUNDED |
| No control flag | No flag; Q is exactly 0.5 |

## Deviations and run notes

- **Batches:** raters were launched in two batches of 6, as the prereg requires. Batch 1 was packets 01, 02, 05, 06, 09 and 10; batch 2 was 03, 04, 07, 08, 11 and 12. There were no 503s and no re-requests. Every reply is a first answer, saved verbatim.
- **Isolation:** each rater read only its neutral-named packet (`/tmp/oc_mc_packets/packet_NN.txt`), followed the sealed launch map, ran in a fresh context and used no other tool.
- **Format:** no reply was fenced and no repair was needed.

## What follows

- **The ledger is not demoted.** Neither kill branch fired. The AI-rater ledger survives both a disowned cue and a stipulated cue at these 9 items.
- **The 59-item amendment stays parked.** The elastic-fraction rule (0.63 against < 0.5) still fails. Before any scaling, the item set must change toward findings where theories commit.
- **The remaining threat is the memory path.** Raters still recall famous outcomes and proponents' explanations, and this study cannot see that. Unseen findings remove that path rather than test it. Human raters can test it, and so can an AI-only knowledge-cutoff contrast (below). The hypothesis-generator line (ds006394 screen, ds001785 confirm) goes next.

## Interpreting review (Fable, after scoring)

No computational error. The reviewer recomputed from the raw `mc_*.json` files every L_t and D point estimate on both scales, mean q_cued (0.967), mean q_own (0.566) and the exact-0.5 share (33.5%). All matched. The CIs were not re-run.

**The ledger may claim:**
- On 9 unknowable items, stipulating an outcome as observed moves every theory's rating by less than 0.12 bits (upper CI), and IIT relative to GNWT/HOT by less than 0.08 bits.
- Stipulation adds a small, same-sign pull. In the reviewer's own unsealed bootstrap, it pools to +0.034 bits [+0.003, +0.069].
- Neither the disowned nor the stipulated cue favours IIT, so a text-level outcome cue does not produce the pilot's IIT lead.

**The ledger may not claim:**
- **"Raters hold steady when they believe the outcome."** No rater held it: 0 of 108 q_own values reach 0.9, and 35 sit at or below 0.5.
- **"The leak stays small under real recall."** In an exploratory check, the pull toward the cue rises with q_own, from +0.03 to +0.06 logit (r = 0.13). The held-belief range was never sampled.
- **"The pilot's IIT lead is leak-free."** Recall of proponents' explanations was not manipulated.
- **"The bound generalises."** Most of the pull comes from Fable (0.067 bits, against 0.017 for Opus and 0.019 for Sonnet), and most cells are near-silent.

**Suggested public wording:** "When we tell AI raters to assume an unknown experiment came out a certain way, their ratings of what each theory predicts barely move, but this does not yet test outcomes they actually remember."

**Next test of the memory path: a knowledge-cutoff difference-in-differences** (AI-only).
- **Items:** findings published between an older model's training cutoff and the current raters' cutoff.
- **Sorting:** use the recognition gate to split models into knowers and non-knowers per item.
- **Measure:** compare each theory's bits between knowers and non-knowers on the same NOTAG packet.
- **Control:** subtract the same contrast on the 9 unknowable items, which removes plain model differences.

This tests held belief and recalled explanations together.
