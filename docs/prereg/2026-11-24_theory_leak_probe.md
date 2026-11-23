# Theory-likelihood ledger, leak probe (prereg)

Sealed before any recognition or rating response was collected. This is the kill test that the theory-likelihood pilot (`docs/prereg/2026-11-23_theory_likelihood_pilot.md`, result SCORABLE) named as the first step of its amendment.
- **Design:** Fable, 2026-11-23.
- **Pre-seal review:** a fresh Fable agent, 7 must-fix items, all applied. Both are recorded in `docs/RESEARCH_STATE.md`.

## Question

When an LLM rater believes an outcome was observed, does it bend a theory's predicted outcome toward that belief? If so, by how much does it bend each theory, and does it bend IIT more than GNWT and HOT? The pilot found IIT ahead by 0.57 bits per item over GNWT. That lead means nothing if raters credit theories with outcomes they remember.

## Why this design

Raters know the real outcomes of famous findings, so we cannot randomise their belief about those findings. We can randomise a cue on findings they cannot know: outcomes first posted after their training cutoff, or not yet observed at all.
- On each such finding we attach a "Reported outcome" tag. It is assigned at random and counterbalanced, so within each model every item is tagged each way equally often.
- The tag is openly described as random and uninformative, so no rater is lied to.
- Leakage is how far each theory's rating follows the tag. This needs only unknowability, not a real result, so planned tests with no outcome yet serve as well as post-cutoff results.

What is new: as far as we know, no theory-comparison exercise has measured its raters' outcome-cue leakage per theory. That includes Yaron et al. 2022 (doi:10.1038/s41562-021-01284-5, abstract read) and our own pilot.

## Items (`experiments/theory_leak/items.json`)

There are 11 items in 7 source clusters. A separate agent drafted them from full texts or abstracts; `draft_items.json` records the reading depth and the date of first posting. After the pre-seal review we made these edits:
- P01: removed the switching rate, a cue on one side only.
- P03: removed the dataset cue and the second clause of the mirror.
- P07: made self-contained, so it no longer presupposes P06's outcome.
- P08: removed the "as in hemineglect" gloss.

Item texts name no theory, author, lab or dataset.

| Items | What they are | Dates or notes |
|---|---|---|
| P01–P04 | Results first posted after 2026-07-01 | bioRxiv API version-1 dates 2026-10-16, 10-12, 07-22 and 09-08. P01 and P02 were drafted from abstracts only. |
| P05 | Result posted 2026-06-22 | Borderline. Kept only if it passes the recognition gate. |
| P06–P07 | Pending outcomes from one registered report (MEG naps) | No result exists. `side_real` is side 1. |
| P08–P11 | Pending outcomes from one adversarial collaboration's planned experiments | No result exists. `side_real` is side 1. The theories' predictions were public before the cutoff. |

## Theories and controls

- **The six theories:** unchanged from the pilot, with the same canonical references.
- **Theory Z:** made up. It makes explicit claims on 8 items: P02, P04 and P06 toward `side_real`; P01, P03, P05, P07 and P08 toward `side_mirror`. It is silent on P09–P11 (`toy_key`).
- **Theory Q:** the pilot's liver-molecule placebo.

## Procedure

**1. Recognition gate** (`make_packets.py recog`, then `score_leak.py --recog`)
- One fresh instance per model (claude-fable-5-2, claude-opus-5-5, claude-sonnet-5-5). No theories are shown.
- Each instance sees the 10 pilot items as a positive control plus the 11 test items, with seeded A/B sides.
- For each item it gives p(A was reported) and recall (yes or no).
- **VOID** if fewer than 27 of the 30 control cells put p_real > 0.5.
- **Exclusion:**
  - an item with a result, if any model gives p_real ≥ 0.75;
  - a pending item, if any model says recall true or gives p outside [0.25, 0.75].
- **VOID** if fewer than 8 items remain.

**2. Rating packets** (`make_packets.py rate`, for the kept items only)
- **TAG arm:** 4 fresh instances per model.
  - Instances 1-2 use tag set S: a seeded half of items (seed 2411) are tagged at `side_real`, the rest at `side_mirror`.
  - Instances 3-4 use the flipped set.
- **NOTAG arm:** 2 fresh instances per model.
- **Seeding:** theory order, item order and A/B sides are seeded per packet.
- **Instructions:** the pilot's, with three changes:
  - They no longer say that one side is real, because pending items have no real side.
  - They ask raters to use theory ids exactly as given.
  - The TAG arm adds: "These lines were assigned at random and carry no information; some findings have no published result yet."
- **Failures:**
  - Each instance answers once. A malformed or incomplete answer is re-requested once with the same packet. A second failure voids that instance, and its file is left absent.
  - The probe is VOID if any model ends with fewer than 3 TAG instances or no NOTAG instance.
  - Every model × item cell must keep both tag directions.
- **Records:** ratings are saved verbatim in `experiments/theory_leak/ratings/`.

**3. Scoring** (`score_leak.py`)
- Clip p to [0.01, 0.99].
- **Leak index:** per theory, on two scales:
  - **bits:** L_t = ½ × [mean log2(2·p_real) when tagged `side_real` − the same when tagged `side_mirror`]
  - **logit:** the same with logit(p_real) in place of log2(2·p_real)
  - Both are computed within each model × item, then averaged.
- **D** = L_IIT − ½(L_GNWT + L_HOT).
- **95% CIs:** bootstrap over the 3 models and over source clusters (2,000 resamples, seed 2411).
- **Why two scales:** bits depend on which side is labelled real. This matters for pending items, where that side is arbitrary and IIT sits near the ceiling on P08–P10. Logit does not depend on the labelling.

## Gates and verdicts (sealed)

**Thresholds** (bits / logit; logit ≈ bits / 0.58, the slope at the pilot's mean p_real of 0.6):

| | bits | logit |
|---|---|---|
| D for DOMINATED | 0.28 | 0.48 |
| L for DOMINATED | 0.25 | 0.43 |
| D for BOUNDED | 0.14 | 0.24 |
| L for BOUNDED | 0.15 | 0.26 |

- **VOID**, in any of these cases:
  - the recognition gate fails;
  - instances are missing beyond the limits above;
  - Theory Z is not recovered in the NOTAG arm: fewer than 90% of its committed cells (items × NOTAG instances) on the committed side at p ≥ 0.70 or ≤ 0.30.
- **Per scale:**
  - **DOMINATED** if D ≥ the D threshold with CI lower bound > 0, or some theory has L_t ≥ the L threshold with CI lower bound > 0.
  - **BOUNDED** if every L_t CI lies strictly inside (−L_BND, +L_BND), D's CI lies inside (−D_BND, +D_BND), and no L_t or D has its whole CI below 0.
  - **INCONCLUSIVE** otherwise. A whole CI below 0 means reactance (moving away from the cue), and that also gives INCONCLUSIVE.
- **Control flag:** raised if L for Theory Q (all items), or for Theory Z on its silent items, is ≥ 0.15 bits or ≥ 0.26 logit with its CI lower bound > 0. That would mean raters follow the cue regardless of content.
- **Final verdict:**
  - **LEAK-DOMINATED** only if both scales say DOMINATED.
  - **LEAK-BOUNDED** only if both scales say BOUNDED and no control flag is raised.
  - **INCONCLUSIVE** otherwise. We then report the CIs as the smallest leak this probe could rule out, and L_t − L_Q.

## What each verdict means for the ledger

- **LEAK-DOMINATED:** demote the ledger to "what language models remember about theories". The pilot's IIT lead is not reported as a property of the theories.
- **LEAK-BOUNDED:** raters ignore a disowned outcome cue on unknowable items. This does not by itself license scaling to 59 items. The cue is weak, and there is no manipulation check showing that it moves belief at all, so it cannot bound leakage from confident memory of famous outcomes. Scaling goes back to Fable together with the NOTAG α (≥ 0.67 needed) and the elastic fraction (< 0.5 needed). Any scaled run adds quote-only commitment cards and a brain-relevant decoy theory.
- **INCONCLUSIVE:** scale only alongside human raters.
- **Forecast bits:** the NOTAG arm's bits on the kept items with a real result (P01–P05) are reported as descriptive forecasts only. There are 5 items at most.

## Planted gate (run before sealing; `score_leak.py --planted 100`; output `planted_all11.json`)

Synthetic raters, all 11 items, the real cluster structure:
- base logit N(0.45, 0.89);
- per-model cell offsets N(0, 0.48), where 0.48 is the pilot's between-rater SD on the logit scale;
- instance noise N(0, 0.48);
- Theory Q at 0.5.

Seeds come from `zlib.crc32` of the scenario name, so they are reproducible.

| Planted | DOMINATED | BOUNDED | INCONCLUSIVE | Control flag |
|---|---|---|---|---|
| No leak | 0.00 | 0.40 | 0.60 | 0.01 |
| IIT only, 0.25 bits | 0.37 | 0.00 | 0.63 | 0.00 |
| IIT only, 0.40 bits | 1.00 | 0.00 | 0.00 | 0.00 |
| All six theories, 0.25 bits | 0.95 | 0.00 | 0.05 | 0.01 |
| IIT only, 0.75 logit, IIT near ceiling on P08–P10 | 0.99 | 0.00 | 0.01 | 0.00 |
| No leak, IIT near ceiling | 0.00 | 0.32 | 0.68 | 0.00 |
| IIT contrarian, −0.75 logit | 0.00 | 0.00 | 1.00 | 0.00 |
| Placebo follows cue, 0.6 logit | 0.00 | 0.00 | 1.00 | 1.00 |

- **False positives:** zero in every no-leak scenario.
- **Power:**
  - 100% for a 0.40-bit leak confined to IIT;
  - 37% at 0.25 bits, because that is where the threshold sits;
  - 99% for a ceiling-masked leak of 0.75 logit.
- **The draft power target was missed.** Fable's draft target of 80% power at 0.25 bits cannot be met with a 0.25 threshold. We kept the threshold and are disclosing the shortfall.
- **A true null usually reads INCONCLUSIVE** (60%), because the 7-cluster bootstrap is wide. So a BOUNDED verdict is informative, while an INCONCLUSIVE verdict is the expected result under no leak.
- **The synthetic noise is independent across instances.** Real raters may be more correlated within a model. The bootstrap resamples models to allow for this.
- **Rerun on the kept items:** after the recognition gate, the planted gate is rerun on the kept items (`planted_kept.json`) and reported. That run does not change any rule.

## Predictions (sealed)

- The recognition control passes, and P05 is the item most likely to be excluded.
- L for Theory Q is near 0, so no control flag.
- Real theories show at most a small uniform leak, with L_t about 0.05–0.15 bits. The cue is disowned, so the probe gives a lower bound.
- D does not reach the DOMINATED threshold. The most likely verdict is INCONCLUSIVE.

## Limits stated now

- **One path only.** The leak index measures a cue about the outcome bending the rating. It does not see a rater crediting a theory from memorised proponent explanations on famous items. That path cannot be randomised.
- **A weak cue.** The cue is disowned and there is no manipulation check, so L is a lower bound.
- **Different content.** The test items differ in content from the pilot items, so carrying a leak estimate over to the pilot is an assumption.
- **Coarse estimates.** There are 7 clusters at most, so the CIs are wide.
- **Unverified cutoffs.** The training cutoffs for Fable and Sonnet are unverified. The recognition gate is the empirical check.
- **Changed instructions.** The pilot's line "exactly one side is real" was dropped. Outcome framing is therefore weaker than in the pilot, and that could change how raters treat the items.
- **Clues in the text.** Real sides may still carry more specific detail than mirrors, which makes the reported side somewhat guessable. The recognition gate catches items guessed at p ≥ 0.75.
- **A tiny forecast set.** The forecast set is at most 5 items, and two were drafted from abstracts only.

## Sealed files

- `experiments/theory_leak/`: `items.json`, `draft_items.json`, `make_packets.py`, `score_leak.py`, `packets/recog_*` and `planted_all11.json`
- this prereg
