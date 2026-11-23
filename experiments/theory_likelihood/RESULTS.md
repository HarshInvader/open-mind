# Likelihood-scored theory ledger, pilot: results

Prereg: `docs/prereg/2026-11-23_theory_likelihood_pilot.md` (sealed in fa07647, before any rating). Scored with `score.py` on 2026-11-23. Output: `result.json`. The ratings are saved verbatim in `ratings/`.

## Verdict: SCORABLE

All three gates passed:
- **G1, toy recovery:** 27 of 27 committed cells were on the right side with p ≥ 0.70 or ≤ 0.30.
- **G2, placebo:** mean bias 0.00. Every one of the 30 placebo ratings was exactly 0.5.
- **G3, agreement:** Krippendorff's α = 0.762 (the bar was 0.67).

So blind AI raters agree well enough on what the six theories predict for these 10 constraints to score them. Under the sealed rules, the full 59-constraint run may now follow.

## Scores (bits; +1 per item at most; 95% bootstrap CI over raters and items)

| Theory | Bits | 95% CI | Elastic | Predicts real | Predicts mirror |
|---|---|---|---|---|---|
| IIT | 4.58 | [1.70, 7.33] | 1 | 8 | 1 |
| RPT | 3.11 | [−0.15, 6.14] | 2 | 6 | 2 |
| PP | 1.66 | [0.21, 3.35] | 7 | 3 | 0 |
| AST | 0.94 | [−0.85, 2.84] | 7 | 3 | 0 |
| HOT | −0.80 | [−4.56, 2.86] | 4 | 3 | 3 |
| GNWT | −1.09 | [−5.59, 3.17] | 3 | 3 | 4 |

Pairs whose bootstrap difference CI excludes 0 are all IIT ahead of another theory: GNWT [0.38, 11.09], RPT [0.45, 2.90], HOT [0.82, 9.97], PP [0.05, 5.26] and AST [0.73, 6.08]. No other pair separates.

## Where the bits come from (rater-mean P(real outcome | theory))

- **IIT and RPT gain** on the posterior-versus-prefrontal items:
  - C05, cerebellum
  - C08, prefrontal lesions
  - C17, posterior dream signature
  - C28, P3b tracks report
  - C31, frontal rivalry activity tracks report
- **IIT and RPT lose** on two items:
  - C32: prefrontal neurons decode no-report rivalry contents (0.35 and 0.33).
  - C55: hydranencephaly (0.45 and 0.33).
- **GNWT and HOT** run the other way:
  - They gain on C32 (0.81 and 0.70).
  - They gain on C05 and C21, the wake/awareness split.
  - They lose on C11, C28, C31 and C55.
- **PP and AST** are mostly elastic (7 of 10 cells each). They earn small positive scores and never favour a mirror.

## Prediction check (sealed)

- G1 passes: **held**.
- G2 at risk: **wrong**. The placebo stayed at exactly 0.5.
- At least half of each theory's cells elastic: **held only for PP and AST**. IIT had 1 elastic cell, RPT 2, GNWT 3 and HOT 4.
- No pair among IIT, GNWT and RPT separates: **failed**. IIT separates from both GNWT and RPT.
- HOT and AST mostly elastic: **held for AST, not for HOT**. HOT committed on 6 of 10 items, half of them the wrong way.

## What this does and does not show

This shows that the scoring machinery works: blind raters recover a made-up theory, ignore a placebo, and agree with each other. It does **not** yet show that IIT is the better theory. There are four reasons.

1. **Theory-specific leakage is not measured.** The raters are language models that know the real outcomes and how proponents explained them afterwards. G2 only catches content-free leaning toward the real outcome. A perfect 0.5 on a liver-molecule placebo is the easy case. A rater crediting IIT because IIT papers later claimed the cerebellum result is exactly the leak this design cannot see.
2. **Item selection.** Fable chose the 10 items as constraints that split theories. Six of the ten are posterior-versus-prefrontal contrasts. That favours any posterior theory by construction. The 59-item run is the fix.
3. **One reference per theory.** GNWT's rater disagreement is large. For example, on C28 (P3b) one rater gave 0.70 toward the P3b being a GNWT marker, and another gave 0.35. A different canonical text could move GNWT a lot.
4. **The raters are LLMs, not experts.** A human-expert panel is the stronger test.

## Next (per the sealed rules, with additions)

The full 59-constraint run goes under a sealed amendment. Mirrors for the other 49 items will be written and sealed before any rating. Leak controls to add before sealing:
- **(a) A retrodiction split.** Tag each constraint by whether the outcome was published before or after the theory's canonical statement. Report bits separately for predictions and retrodictions.
- **(b) A theory-specific leak probe.** Use counterfactual "fictional twin" items with invented outcomes that no proponent has explained. Ratings on these should look like ratings on matched real items.
- **(c) Human raters,** if any can be recruited.
