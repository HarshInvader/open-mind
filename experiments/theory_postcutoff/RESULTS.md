# Results: post-cutoff theory ledger (sealed run, 2026-11-24)

Prereg: `docs/prereg/2026-11-24_theory_postcutoff_ledger.md` (sealed 2026-11-24T19:23:41Z, commit 5ede8d9). Output: `result.json`.
Raters: three AI models (Fable, Opus, Sonnet), two runs each, blind and informed arms. Nothing here is a human expert judgement.

## Verdict: UNINFORMATIVE

- Only **4 of 15** kept post-cutoff findings split the theories (some real theory's mean |p − 0.5| ≥ 0.2): N02, N10, N13, N14, in **3 clusters**. The bar was ≥ 8 items and ≥ 6 clusters.
- **Elastic fraction 0.89**: for 89% of (theory, post-cutoff finding) cells the raters' mean p sat in [0.4, 0.6]. On the 10 famous findings in the same packets it was 0.42.
- The prereg named INCONCLUSIVE/UNINFORMATIVE as the expected outcome and predicted < 60% of post items would split. The outcome was worse than that: 27%.

## Gates (all pass)

| Gate | Bar | Result |
|---|---|---|
| G1 committed cells | ≥ 90% | blind 83/84, informed 30/30 |
| G2 placebo | \|bias\| ≤ 0.10 | 0.0 |
| G3 agreement (Krippendorff α) | ≥ 0.67 | 0.838 |
| Toy theory Z silent cells | report | spread 6% blind, 3% informed |
| Recognition control | ≥ 25/30 famous recognised | 30/30; N03, N04, N12 excluded (a model gave p_real ≥ 0.75) |

## Numbers (descriptive; the verdict is UNINFORMATIVE, so none of these is a test result)

lead = bits(IIT) − ½(bits(GNWT) + bits(HOT)); bits = log2(2·p_real). 95% CI = point ± t × bootstrap SD (3 models × clusters, B = 2000, seed 2511); percentile CI in brackets after.

| Set | Lead | 95% CI | Percentile |
|---|---|---|---|
| Post, splitting items (4) | −0.452 | [−0.913, 0.008] | [−0.709, −0.306] |
| Post, all kept (15) | −0.136 | [−0.287, 0.015] | [−0.262, −0.006] |
| Famous (10), same run | 0.495 | [−0.054, 1.044] | |
| Famous, splitting (8) | 0.437 | | |
| Famous minus post-split | 0.947 | [−0.20, 2.10] | [0.43, 1.50] |

- **Per-theory bits on all post items:** IIT −0.073, GNWT +0.107, RPT −0.027, HOT +0.020, PP −0.019, AST +0.019. Famous items: IIT +0.425 [0.077, 0.773].
- **What split:** three of the four splitting items split on GNWT alone (N10 surprise-induced blindness with a late parietal positivity, p_real 0.72; N13 and N14, the LLM "workspace" layers, 0.74 and 0.82). N02 (slow waves more frequent in minimally conscious patients) split against every theory, most against IIT (p_real 0.23). That is why the split-item lead is negative.

## Hindsight (informed − blind): BOUNDED

- D_H = H_IIT − ½(H_GNWT + H_HOT) = −0.006 [−0.061, 0.049]; bar 0.25.
- Per theory H: IIT 0.044 [0.002, 0.108], GNWT 0.087 [0.022, 0.155], RPT 0.057, HOT 0.012, PP 0.034, AST 0.012, toy Z −0.021, placebo Q 0.
- Sensitivity without the three items whose abstracts name a theory (N13–N15): BOUNDED, D_H 0.0.
- Reading: seeing the outcome and abstract moved the raters a little toward the observed outcome for every theory (about 0.01–0.09 bits), and not more for IIT.

## What this says, modestly

- As these AI raters read the theories, the six theories mostly do not commit on recent findings. The test the ledger was built for, whether IIT's lead on famous findings carries over to findings the raters could not have seen, could not run with 4 splitting items.
- In the same packets, IIT leads on the famous findings and does not lead on the new ones. That contrast is consistent with the famous-item lead coming partly from hindsight already baked into how the theories are known, but with 4 items in 3 clusters it is a description, not evidence.
- The informed arm shows no IIT-specific hindsight on the new items.

## Predictions vs outcome

| Prereg prediction | Outcome |
|---|---|
| Most likely verdict INCONCLUSIVE or UNINFORMATIVE | UNINFORMATIVE |
| < 60% of post items split | 27% (4/15) |
| Gates pass | all pass |
| Hindsight small | BOUNDED, D_H ≈ 0 |

## Run notes

- Sonnet's recognition reply came wrapped in a code fence; the JSON array was saved unchanged (`ratings/recog_sonnet.NOTE.txt`).
- Raters received packets under neutral file names and wrote their JSON answers to a scratch file; answers were copied into `ratings/` unchanged.
- Informed packets contain abstract text and are kept local (`datasets/local/postcutoff_packets/`, gitignored); their sha256 are in `packets/informed_hashes.json`.
- No re-runs. Sealed planted-data calibration is in `planted.json` (lead 0.55 with 0% elastic: SURVIVES 0.80; null: false SURVIVES 1–6%).

## What would make this informative

- A larger pool of post-cutoff findings chosen because they split the theories (with the drafter blind to outcomes), to reach ≥ 8 splitting items in ≥ 6 clusters.
- Human expert raters on the same packets, to check whether the elasticity is in the theories or in how AI models read them.
