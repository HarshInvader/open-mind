# Likelihood-scored theory ledger, pilot (prereg)

Sealed on 2026-11-23, before any rating was collected. Track (a) of the owner's new main line, ranked first by Fable (round 13).

## Question

On the 10 ledger constraints that split the theories, how many bits does each of six theories of consciousness earn? A theory earns bits when its core commitments make the observed outcome more likely than its mirror image. A theory that fits either outcome ("elastic") earns nothing.

Our existing scorecard (`experiments/theory_scorecard/`) counts "explains" and "compatible" marks. It never penalises a theory that would have fitted the opposite result, and its marks were set by one agent who knew both the outcomes and the earlier marks. Yaron et al. 2022 (doi:10.1038/s41562-021-01284-5, abstract read in round 13) catalogue which experiments were run for which theory, but they do not score P(outcome | theory). What is new here:
- likelihood scoring against mirrored outcomes;
- blind, independent raters;
- explicit gates for whether such scoring can work at all.

## Design

- **Items** (`experiments/theory_likelihood/items.json`): C05, C08, C11, C14, C17, C21, C28, C31, C32 and C55 from `experiments/constraint_ledger/ledger.csv`. Fable picked these as the constraints that split the theories. Each has a mirrored outcome that we wrote; the mirrors are fixed in `items.json`.
- **Theories, each with one canonical reference** (DOIs checked on Crossref on 2026-11-23):
  - IIT: Albantakis 2023, doi:10.1371/journal.pcbi.1011465
  - GNWT: Mashour 2020, doi:10.1016/j.neuron.2020.01.026
  - RPT: Lamme 2006, doi:10.1016/j.tics.2006.09.001
  - HOT: Brown, Lau & LeDoux 2019, doi:10.1016/j.tics.2019.06.009
  - PP: Seth & Hohwy 2020, doi:10.1080/17588928.2020.1838467
  - AST: Graziano & Webb 2015, doi:10.3389/fpsyg.2015.00500
- **Controls:**
  - Theory Z: a made-up theory with explicit commitments. It predicts the real outcome for 3 items and the mirror for 6, and is silent on 1 (`toy_key` in `items.json`).
  - Theory Q: a placebo with no bearing on any item.
- **Raters:** three fresh AI agents of different models: r1 claude-fable-5-2, r2 claude-opus-5-5, r3 claude-sonnet-5-5. They are told to use no tools or files and have never seen the scorecard. Each gets a seeded packet (`make_packets.py`): theory order, item order and which side is labelled A are all randomised, and nothing says which outcome is real. Each rater gives p = P(A rather than B | theory) for all 80 theory × item pairs. Ratings are saved verbatim in `ratings/rater_<k>.json`. A malformed or incomplete answer is re-requested once with the same packet. A second failure voids that rater, and the pilot is void if fewer than 3 raters remain.
- **Score:** with p clipped to [0.01, 0.99], each cell earns bits = log2(2 · P(real outcome | theory)). That is +1 at most, 0 when indifferent, and negative when the theory favours the mirror. A theory's score is the sum over items, averaged over raters. The 95% CI comes from a bootstrap over raters and items (2,000 resamples, seed 2311).
- **Elastic cell:** rater-mean p in [0.4, 0.6].

## Gates (the kill test; `score.py`)

- **G1, toy recovery:** on Theory Z's 9 committed cells × 3 raters, at least 90% must be on the committed side with p ≥ 0.70 (or ≤ 0.30).
- **G2, placebo leak:** on Theory Q's 30 ratings, the mean of (P(real) − 0.5) must be ≤ 0.10, and at most 20% of ratings may fall outside [0.35, 0.65].
- **G3, agreement:** Krippendorff's α (interval, on logit p) over the 60 real-theory cells must be ≥ 0.67.

## Verdicts (sealed)

- G1 or G2 fails → **VOID**: these raters cannot score theories blind to the outcome. Logged in the atlas, and the full run is not attempted in this form.
- G1 and G2 pass, G3 fails → **UNDER-SPECIFIED**: the theories are too loosely specified for independent raters to agree on what they predict. This is a result in its own right and goes in the atlas.
- All pass → **SCORABLE**: report bits, CIs, elastic counts and the theory pairs whose bootstrap difference CI excludes 0. The full 59-constraint run then follows under a sealed amendment: mirrors for the other 49 items will be written and sealed before any of them is rated.

## Planted gate (run before sealing)

Synthetic raters with a known truth table were used:
- **`score.py --planted`:** SCORABLE. α = 0.81. IIT's planted advantage was recovered; every IIT pair separated.
- **`score.py --planted --leak`:** the placebo was planted to lean toward the real outcome (0.72). Result: VOID, G2 failed with bias 0.21.

So the scoring path and the leak gate both work. Output: `planted.json`, `planted_leak.json`.

## Prediction

- G1 passes.
- G2 is at risk: raters know which outcomes are real and may lean toward them even for the placebo.
- If scorable: at least half of each theory's cells are elastic. No pair of IIT, GNWT and RPT is separated on 10 items.
- HOT and AST are mostly elastic on these items.

## Limits stated now

- **The raters are language models that have read the literature.** They know the real outcomes and the proponents' after-the-fact explanations. G2 detects content-free leakage. It cannot detect theory-specific leakage, where a rater credits a theory because its proponents later explained the result.
- **Not human experts:** a human-expert version would be the stronger test.
- **The mirrors are ours.** A loaded mirror would bias every theory in the same direction for that item.
- **Small sample:** 10 items, so scores are coarse.
- **One reference per theory:** a single canonical reference stands for each theory.

## Sealed files

- `experiments/theory_likelihood/items.json`
- `experiments/theory_likelihood/make_packets.py`
- `experiments/theory_likelihood/score.py`
- `experiments/theory_likelihood/packets/` (prompts and keys)
- `experiments/theory_likelihood/planted.json`
- `experiments/theory_likelihood/planted_leak.json`
- This prereg.
