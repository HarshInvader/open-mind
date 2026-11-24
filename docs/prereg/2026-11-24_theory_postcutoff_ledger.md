# Theory ledger on findings the raters cannot remember, with a hindsight arm (prereg)

Agent: Open Mind thread   Date: 2026-11-24   Status: DRAFT, ready to seal. No rating or recognition response has been collected.

- **Code:** `experiments/theory_postcutoff/score.py` scores the ratings; `make_packets.py` builds the packets.
- **Chosen by:** a Fable ranking of zero-new-byte studies (2026-11-24), top pick.
- **Pre-seal review:** one fresh Fable agent, 5 must-fixes and 13 should-fixes. Section 9 records what was applied.

## 0. Question and why it matters

- **The pilot** (`2026-11-23_theory_likelihood_pilot.md`, SCORABLE): on 10 famous constraints, blind AI raters gave IIT a lead of about 0.55 bits per item over the mean of GNWT and HOT.
- **The open path:** the leak probe and the manipulation check bounded one path. Raters barely move when an outcome cue is disowned, or stipulated, on findings they cannot know. They left the memory path open: on famous findings raters know the outcome, and proponents' after-the-fact explanations. They may credit a theory for that.
- **This test:**
  - Does the IIT lead hold on findings first posted after the raters' training data, which they cannot remember?
  - Separately, how far does knowing the result (reading the abstract) move each theory's rating? That is hindsight, the closest measurable proxy for the memory path.
- **What kind of test this is.** It is **one-sided**: an estimate with a survival test.
  - SURVIVES and REDUCED are informative.
  - KILLED needs an observed lead of about −0.25 or lower, so it is close to unreachable.
  - INCONCLUSIVE and UNINFORMATIVE license no claim about the lead.

## 1. Prior art (read before design)

- **Luo et al. 2025** (*Nat Hum Behav*, doi:10.1038/s41562-024-02046-9, abstract): LLMs beat experts at picking the real abstract of a neuroscience result over an altered one (BrainBench).
  - Our real-vs-mirror format is close to theirs.
  - They forecast outcomes. We score P(outcome | theory), which they do not.
- **Yaron et al. 2022** (doi:10.1038/s41562-021-01284-5, abstract): theory support in consciousness studies is predictable from methods alone, and most studies interpret their results after the fact. That is why hindsight matters for any ledger.
- **Our pilot, leak probe and manipulation check** (`experiments/theory_likelihood`, `experiments/theory_leak`): LEAK-BOUNDED twice, with the memory path untested.
- **No LLM-rated theory-likelihood ledger** with a post-cutoff or hindsight arm turned up in the Fable search. Not established.

## 2. Items (`experiments/theory_postcutoff/items.json`, built by `make_packets.py build`)

**Famous (10):** the pilot's constraints C05–C55, with the pilot's mirrors unchanged. They serve as the recognition control and as the within-run comparison set.

**Post-cutoff (18 items in 12 clusters):** N02–N19, drafted by a separate agent from library entries. `draft_items.json` records the reading depth (all from abstracts) and the date source for each.
- **Dates:** first public posting on or after 2026-07-01, checked against bioRxiv, medRxiv or arXiv v1, or Crossref plus a Europe PMC search for earlier preprints. 13 candidates were dropped because an earlier preprint existed.
- **Clusters:** items from one lab or one evaluation suite share a cluster.
- **Texts** name no theory, author, lab, dataset or journal.
- **Excluded at review:**
  - **N01** replicates famous item C17, which sits in the same packet.
  - **P02–P04** were already rated blind in the leak probe.
- **Edited before sealing:** the mirrors of N13 and N14, and both sides of N15. The edit notes are in `draft_items.json`.
- **Abstracts** are saved verbatim under `datasets/local/postcutoff_abstracts/`. They are not committed; the informed packets' sha256 are recorded at build time.
- **Abstracts that name a theory:** N13, N14 and N15 (`abstract_names_theory`). All three name the global workspace, and none names IIT.

**Theory Z (made up), in `toy_z.json`:** written after drafting and before any response.
- 15 explicit claims.
- Committed toward the real side on C05, C17, C32, N10 and N13. Committed toward the mirror on C08, C11, C14, C21, C28, C31, N06, N09, N12 and N19.
- Keyed silent on the rest. Some "silent" items may still draw commitments, for example N11 through claim 6, so Z's spread on silent items is reported, not gated.

**Theory Q:** the pilot's liver-molecule placebo.

## 3. Procedure

**1. Recognition gate** (`make_packets.py recog`, `score.py --recog`)
- One fresh instance per model (claude-fable-5-2, claude-opus-5-5, claude-sonnet-5-5). No theories are shown.
- **Control:** the 10 famous items; at least 25 of 30 cells must have p_real > 0.5, else VOID. The last run scored 28 of 30.
- **Exclusion:** a post item is excluded if any model gives p_real ≥ 0.75 or says it recalls the study.
- **VOID** if fewer than 10 post items, or fewer than 6 clusters, remain.

**2. BLIND arm** (2 fresh instances per model)
- Famous plus kept post items, 6 theories plus Z and Q.
- The pilot's wording ("exactly one describes what was observed ... you are not told which").
- Seeded theory order, item order and A/B sides.

**3. INFORMED arm** (2 fresh instances per model)
- Kept post items only.
- Each finding states the observed outcome and gives the study's abstract.
- Raters are still told to rate what the theory implies.

**Rules for both arms:**
- Each rater reads only its packet, copied to a neutral filename, in a fresh context, with no other tool.
- A malformed or incomplete answer is re-requested once. A second failure voids that instance.
- An arm is VOID if any model has no valid instance. A void INFORMED arm does not block the primary verdict.
- Replies are saved verbatim in `ratings/`.
- At most 3 rater instances run at once.

## 4. Scoring (sealed)

- **Cell bits** = log2(2 · p_real), with p clipped to [0.01, 0.99]. Averaged over instances within a model, then over models.
- **Lead** = bits(IIT) − ½[bits(GNWT) + bits(HOT)], per item.
- **Primary set:** BLIND arm, post items that split the theories.
  - An item splits if some real theory's rater-mean |p − 0.5| ≥ 0.2.
  - This is symmetric in A and B, so it is blind to which side is real.
  - The split set is fixed before the bootstrap, so the CIs are conditional on it.
- **Bootstrap:** over the 3 models and over source clusters; each famous item is its own cluster. B = 2000, seed 2511.
- **Verdict CIs** = estimate ± t(0.975, clusters − 1) × bootstrap SD. Percentile CIs are reported alongside.
  - The t degrees of freedom come from clusters and ignore that there are only 3 models, which understates model variance. We disclose this rather than correct it.

## 5. Gates and verdicts (sealed)

**Gates:**
- **G1, toy recovery (BLIND):** at least 90% of Z's committed cells on the committed side, at p ≥ 0.70 or ≤ 0.30. Otherwise VOID.
- **G2, placebo (BLIND):** |mean(p_real − 0.5)| ≤ 0.10 and at most 20% outside [0.35, 0.65]. Otherwise VOID.
  - In the INFORMED arm a G2 failure flags the hindsight result as partly content-free. It does not void the run.
- **G3, agreement:** Krippendorff α across models (logit of model-mean p) on BLIND post cells ≥ 0.67. Otherwise UNDER-SPECIFIED.
- **Informative items:** at least 8 splitting post items in at least 6 clusters. Otherwise UNINFORMATIVE, which is reported as a result: the theories, as AI raters read them, do not commit on most new findings.

**Primary verdict** (lead on splitting post items):
- **SURVIVES:** lead ≥ 0.28 (half the pilot lead) and CI lower bound > 0. Tagged "(REDUCED)" if the CI upper bound is also < 0.55.
- **KILLED:** CI upper bound < 0.28.
- **REDUCED:** CI upper bound < 0.55, not KILLED and not SURVIVES. The pilot's lead is excluded; a smaller one is not.
- **INCONCLUSIVE:** otherwise. This licenses no claim.

**Hindsight verdict:** H_t = bits(INFORMED) − bits(BLIND) on kept post items; D_H = H_IIT − ½(H_GNWT + H_HOT).
- **FAVOURS-IIT:** D_H ≥ 0.25 and CI lower bound > 0.
- **AGAINST-IIT:** D_H ≤ −0.25 and CI upper bound < 0.
- **BOUNDED:** CI inside (−0.25, 0.25).
- **UNCLEAR:** otherwise.
- **Sensitivity:** the same statistic without N13–N15, whose abstracts name the global workspace. This is reported, not a verdict.

**What each outcome means for the ledger:**
- **KILLED, REDUCED or FAVOURS-IIT:** the pilot's IIT lead is not reported as a property of the theories. It is "what raters remember or reconstruct", or the result of item selection.
- **SURVIVES with hindsight BOUNDED:** the lead holds on findings the raters cannot remember. That licenses human raters on the same post-cutoff packets.

**Reported, not part of a verdict:**
- the lead on all post items;
- the lead on famous items (all, and splitting only);
- the famous-minus-post difference with a joint CI;
- IIT's own bits with a CI, because a lead can come from rivals being confidently wrong rather than IIT being right;
- per-theory bits and H_t;
- the elastic fraction;
- Z's spread on silent items.

## 6. Planted gate (run before sealing; `score.py --planted 100`; output `planted.json`)

**Synthetic raters** on the sealed structure (18 post items in 12 clusters, plus 10 famous items):
- true logit per theory and item ~ N(μ_t, 0.89), where 0.89 is the pilot's spread;
- model offsets N(0, 0.48);
- instance noise N(0, 0.48);
- the placebo at 0.5;
- the informed arm uses the same truth plus noise N(0, 0.3), plus any planted hindsight shift in bits;
- elastic items have true logit N(0, 0.2) for every theory.

**Primary verdict:**

| Planted (post lead; share of post items elastic) | SURVIVES | REDUCED | KILLED | INCONCLUSIVE | UNINFORMATIVE |
|---|---|---|---|---|---|
| 0.55; 0% | 0.80 | 0.00 | 0.00 | 0.20 | 0.00 |
| 0.55; 50% | 0.31 | 0.04 | 0.00 | 0.61 | 0.04 |
| 0.55; 60% | 0.15 | 0.03 | 0.00 | 0.39 | 0.43 |
| 0.55; 70% | 0.03 | 0.00 | 0.00 | 0.12 | 0.85 |
| 0.28; 0% | 0.26 | 0.15 | 0.01 | 0.58 | 0.00 |
| 0; 0% | 0.06 | 0.38 | 0.16 | 0.40 | 0.00 |
| 0; 50% | 0.01 | 0.29 | 0.11 | 0.50 | 0.09 |
| 0; 60% | 0.01 | 0.10 | 0.05 | 0.38 | 0.46 |

**Hindsight verdict** (post lead 0, no items elastic):

| Planted hindsight | FAVOURS-IIT | BOUNDED | UNCLEAR |
|---|---|---|---|
| None, or uniform 0.25 bits | 0.00 | 1.00 | 0.00 |
| IIT only, 0.25 bits | 0.40 | 0.00 | 0.60 |
| IIT only, 0.40 bits | 1.00 | 0.00 | 0.00 |

**Reading:**
- **False SURVIVES under a true lead of 0:** 1–6%.
- **False REDUCED under the pilot's lead:** 0–4%.
- **False FAVOURS-IIT:** 0%.
- **Realistic operating point.** The leak probe's items were 63% elastic. At 50–60% elastic, SURVIVES has 15–31% power at the pilot's lead, and UNINFORMATIVE is likely. **The expected outcome is INCONCLUSIVE or UNINFORMATIVE**, and the prereg says so before any data.
- **Optimistic hindsight numbers.** The synthetic informed arm reuses each blind instance's truth with a constant shift, so the hindsight results above are optimistic. Bits are concave, so D_H is also mechanically anti-correlated with the blind lead.
- **Gates not exercised:** the planted gate does not test G1–G3.

## 7. Predictions (sealed)

- The recognition control passes. At least one post item is excluded.
- Fewer than 60% of post items split the theories.
- On post items the lead is smaller than on the famous items in the same run.
- Most likely primary verdict: INCONCLUSIVE or UNINFORMATIVE.
- Hindsight is positive for every theory (knowing the outcome pulls ratings toward it, more strongly than stipulation did). D_H is BOUNDED.

## 8. Limits stated now

- **A proxy for memory.** Reading an abstract in context is not the same as having learned it during training.
- **Different item sets.** Post-cutoff findings are whatever was published, while the famous items were picked to split theories. A famous-vs-post difference mixes memory with selection.
- **Hindsight includes authors' framing.** Three abstracts name the global workspace, and none names IIT. That could pull hindsight toward GNWT; the sensitivity analysis drops them.
- **Unverified cutoffs.** The training cutoffs for Fable and Sonnet are not verified. The recognition gate is the empirical check.
- **Few clusters.** 12 clusters and 3 models, so the CIs are wide and understate model variance.
- **Abstract-only drafting.** Every post item was drafted from the abstract only.

## 9. Pre-seal review record (Fable, 2026-11-24)

**Must-fix, all applied:**
1. P02–P04 removed, because they had already been rated blind.
2. N01 removed, because famous C17 sits in the same packet.
3. N15 reworded so it no longer presupposes N13's real side, and clustered with N13–N14.
4. Z's claim 13 reworded to match N06.
5. The elastic operating-point scenarios added to section 6, and the test framed as one-sided.

**Should-fix:**
- **Applied:**
  - the REDUCED verdict;
  - splitting famous items reported;
  - IIT's own bits with a CI;
  - hindsight sensitivity without the theory-naming abstracts;
  - a void informed arm no longer blocks the primary verdict;
  - recognition control bar 25;
  - G2 two-sided;
  - Z's silent-item spread reported.
- **Disclosed, not changed:**
  - the CI is conditional on the split set;
  - the model-variance understatement;
  - the hindsight ceiling and the optimistic planted hindsight;
  - G1–G3 not planted.

## 10. Sealed files

- this prereg;
- `experiments/theory_postcutoff/`: `draft_items.json`, `toy_z.json`, `items.json`, `make_packets.py`, `score.py`, `packets/recog_*`, `planted.json`, `abstract_hashes.json` (sha256 of each local abstract file).
