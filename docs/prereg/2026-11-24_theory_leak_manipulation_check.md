# Theory-likelihood ledger, leak probe manipulation check (prereg)

Sealed and hashed in `docs/prereg/HASHES.txt` before any manipulation-check rating was collected.
- **Design:** Fable's interpreting review of the leak probe (2026-11-23, recorded in `docs/RESEARCH_STATE.md`), built out by the Mind thread.
- **Pre-seal review:** a fresh Fable agent returned "seal after fixes" with 9 must-fix items, all applied:
  1. the cue note's closing sentence now matches the disowned note;
  2. the honesty wording is fixed;
  3. a Theory Z failure can no longer override DOMINATED;
  4. the belief gate is per item, with an all-instances sensitivity analysis;
  5. the two VOID reasons are separated;
  6. the "why"-string regex is implemented;
  7. ΔL is paired on the same instances;
  8. the kill has two branches (D and L-only);
  9. a q_own probe is added.

  Optional items applied: case-insensitive fence stripping, a float tolerance, an item and p range check, a sealed launch map, and the limits on power and constant planted leaks.

## Question

The leak probe (`docs/prereg/2026-11-24_theory_leak_probe.md`, result LEAK-BOUNDED, `experiments/theory_leak/RESULTS.md`) showed that AI raters ignore an outcome cue they are told is random. It could not tell "raters keep theory ratings apart from what they believe was observed" from "raters ignored a line labelled noise".

This check asks: **when a rater treats an outcome as observed, does it bend each theory's predicted outcome toward it, and IIT more than GNWT and HOT?** That is the situation in the pilot ledger, where raters remember the real outcomes of famous findings.

## Design: one change from the leak probe

The 12 packets are the leak probe's TAG packets (`packets/tag_{model}_{k}.txt`), with the same seeds, theory order, item order, A/B sides and tag letters. `make_mc_packets.py` makes exactly two text changes (asserted in code):

1. **The cue is believed, not disowned.** The note becomes:
   > Each finding carries a "Reported outcome" line. For this exercise, take it as the outcome that the experiment observed: treat it as the result, as you would a result you remember from the literature. You may not recognise some of these experiments; that does not matter here. Rate what the theory implies.

   - **The closing sentence is unchanged.** "Rate what the theory implies" is word for word the closing of the disowned note. So the only thing that differs is whether the cue is disowned or stipulated. No new warning sits next to the cue.
   - **The rater is not told the cue is true.** It is framed as the scenario for this exercise. Six items are pending, and half the cues on P02–P04 are false, so we do not say a result exists.
   - **The instruction against hindsight stays.** The pilot's line "Do not reward a theory for having been adjusted after the fact" is unchanged.
2. **A closing belief probe.** The reply becomes a JSON object, with `ratings` (the same 72 pairs) and `belief`. In `belief`, filled in last, the rater gives two numbers for each of the 9 findings:
   - **q:** P(A is the outcome that was observed, for this exercise). This is the gate.
   - **q_own:** "setting the exercise aside, your own probability that A is what the study actually found or will find". This is descriptive only.

The launch map `packets/mc_launch_map.json` (packet_NN → model and instance) is sealed with the packets.

Because everything else is identical, the result can also be compared pair by pair with the disowned-cue ratings.

- **Items:** the 9 kept items (P02–P04, P06–P11) in 6 clusters. No new recognition gate is needed, because the items are unchanged and the TAG arm saw them already.
- **Counterbalancing:** as in the leak probe. Instances 1–2 tag a seeded half of the items (seed 2411) at `side_real`, and instances 3–4 the flipped set.
- **Instances:** 4 fresh instances per model (claude-fable-5-2, claude-opus-5-5, claude-sonnet-5-5), 12 in all. No NOTAG arm: the leak index is a within-arm contrast, and the leak probe's NOTAG arm is the forecast baseline.
- **Launch:** each rater runs as a fresh agent and reads one neutral-named copy of its packet (`/tmp/oc_mc_packets/packet_NN.txt`, with no model, arm or key in the name). It uses no other tool. Launches go in batches of at most 6, because of gateway rate limits.
- **Failures:** each instance answers once. A malformed or incomplete answer is re-requested once with the same packet, and a second failure voids that instance. A single surrounding markdown fence is stripped and disclosed. Replies are saved verbatim in `experiments/theory_leak/ratings/mc_{model}_{k}.json`.

## Scoring (`score_mc.py`; statistics imported unchanged from the sealed `score_leak.py`)

**1. Valid instances.** VOID ("too few valid instances") if any model ends with fewer than 3 instances after the failure rule. This is reported apart from the belief gate.

**2. Manipulation check (VOID gate).**
- **q_cued:** q toward the cued side, per finding.
- **A finding passes** if q_cued ≥ 0.75.
- **An instance passes** if at least 8 of its 9 findings pass. A per-item rule, so a few rejected items cannot hide inside a high mean.
- **VOID** ("belief did not follow the cue") if any model has fewer than 3 passing instances.
- **Reported:** per-item q_cued and q_own toward the cued side, for every instance.

**3. Leak indices (primary: passing instances; sensitivity: all valid instances).**
- **As sealed in the leak probe:** L_t, D, both scales, the 95% CIs (models × source clusters, B = 2000, seed 2411), the control flag (Theory Q on all items, Theory Z on its silent items P09–P11) and the per-analysis verdict logic.
- **Thresholds** (bits / logit):

  | | bits | logit |
  |---|---|---|
  | D for DOMINATED | 0.28 | 0.48 |
  | L for DOMINATED | 0.25 | 0.43 |
  | D for BOUNDED | 0.14 | 0.24 |
  | L for BOUNDED | 0.15 | 0.26 |

- **Per analysis:** LEAK-DOMINATED only if both scales say DOMINATED. LEAK-BOUNDED only if both scales say BOUNDED, there is no control flag and the Theory Z check passes. INCONCLUSIVE otherwise.
- **Theory Z check:** among Theory Z's committed cells, at least 90% must sit on the committed side (p ≥ 0.70 or ≤ 0.30).
  - A failure never overrides DOMINATED, because Z bending toward a believed cue is itself a leak. It turns BOUNDED into INCONCLUSIVE.
  - The scorer reports how many failing cells sit on the cued side.
- **Final verdict:**
  - **LEAK-DOMINATED** if either analysis says DOMINATED.
  - **LEAK-BOUNDED** only if both say BOUNDED.
  - **INCONCLUSIVE** otherwise.
- **Kill branch:** **D** if the DOMINATED analysis meets the D criterion on both scales, **L-only** otherwise.
- **L_t − L_Q** is always reported. It separates theory-specific leak from content-free cue-following.

**4. Descriptive only.**
- **ΔL_t = L_believed − L_disowned.** Paired within model × item on the same passing instances (the disowned ratings are restricted to the same model × instance set), with a bootstrap CI (seed 2412).
- **"Why" strings that mention the cue.** The share of real-theory "why" strings in passing instances that match the sealed regex `\b(reported|observed|outcome|result)\b` (case-insensitive).

## What each verdict means for the ledger (sealed)

- **LEAK-DOMINATED: kill.** Raters credit theories with outcomes they take as observed. There are two branches.
  - **Branch D** (D ≥ 0.28 bits and ≥ 0.48 logit, CI > 0): a believed outcome favours IIT over GNWT and HOT.
    - The ledger is demoted to "what language models remember about theories".
    - The pilot's IIT lead is not reported as a property of the theories.
    - AI rating of famous findings is dropped. Only human raters, or AI raters on unknowable items, stay.
  - **Branch L-only** (some L_t ≥ 0.25 bits and ≥ 0.43 logit, CI > 0, without the D criterion):
    - Absolute ledger bits are untrustworthy, and AI rating of famous findings is dropped.
    - A uniform leak adds about the same bits to every theory, so the pilot's IIT lead is reported as "not explained by this path", not as demoted.
- **LEAK-BOUNDED:** even a stipulated outcome moves theory ratings by less than 0.15 bits (0.26 logit) per theory. It bounds stipulated outcomes only, not outcomes the rater actually holds (see q_own). Together with the leak probe, this bounds the cue path. It still does not bound recall of proponents' explanations for famous findings. Scaling goes back to Fable. The elastic-fraction bar (0.63 against < 0.5) still fails, so scaling would need new, more committing items, not just a clean bill on leakage.
- **INCONCLUSIVE:** the CIs are reported as the smallest leak ruled out. AI ratings of famous findings are used only alongside human raters.

## Planted gate (run before sealing: `score_mc.py --planted 100`, output `planted_mc.json`)

This gate is calibrated on the leak-probe data:
- **Base rates:** each (theory, item) cell takes its mean NOTAG logit.
- **Instance SD:** 0.250 logit, pooled within model × theory × item × tag direction.
- **Model SD:** 0.249 logit, the SD of model means within each cell. This figure includes part of the instance variance, and model offsets cancel in L anyway, so only the instance SD is a real calibration.

The gate exercises the sealed `evaluate()` used in each analysis. The belief gate, the Theory Z override and the two-analysis combination were tested separately: the leak probe's own ratings were reformatted as manipulation-check replies, with one instance made to fail the belief gate and one wrapped in a `JSON` fence. They reproduced LEAK-BOUNDED, dropped the failing instance, stripped the fence, and gave ΔL = 0 exactly.

Synthetic raters use the sealed `synth()`, with 4 instances per model. Seeds come from `zlib.crc32("mc_" + scenario)`.

| Planted | DOMINATED | BOUNDED | INCONCLUSIVE | Control flag |
|---|---|---|---|---|
| No leak | 0.00 | 0.90 | 0.10 | 0.00 |
| IIT only, 0.15 bits | 0.00 | 0.00 | 1.00 | 0.00 |
| IIT only, 0.25 bits | 0.42 | 0.00 | 0.58 | 0.00 |
| IIT only, 0.40 bits | 1.00 | 0.00 | 0.00 | 0.00 |
| All six theories, 0.15 bits | 0.00 | 0.00 | 1.00 | 0.00 |
| All six theories, 0.25 bits | 0.96 | 0.00 | 0.04 | 0.00 |
| IIT only, 0.43 logit | 0.44 | 0.00 | 0.56 | 0.00 |
| All six theories, 0.43 logit | 0.99 | 0.00 | 0.01 | 0.00 |
| IIT contrarian, −0.75 logit | 0.00 | 0.00 | 1.00 | 0.00 |
| Placebo follows cue, 0.6 logit | 0.00 | 0.00 | 1.00 | 1.00 |

- **False positives:** no DOMINATED under no leak.
- **BOUNDED is never given when a leak at the BOUNDED limit (0.15 bits) is planted.**
- **Power:**
  - 100% for a 0.40-bit IIT-only leak;
  - 96% for a uniform 0.25-bit leak;
  - 42% for an IIT-only leak at the 0.25-bit threshold, where the threshold sits by construction.
- **The calibrated noise is about half the leak probe's planned 0.48.** Real instances share many exact 0.5 cells. The synthetic raters add noise to every cell, so this gate is still mildly pessimistic.

## Predictions (sealed)

- **The manipulation check passes:** q_cued ≥ 0.9 in most instances. The probe is close to a comprehension check, because the cue is the stated scenario.
- **Real theories show a small uniform leak:** L_t about 0.05–0.20 bits. That is larger than under the disowned cue (all within ±0.02), but most likely below the DOMINATED threshold.
- **D stays below 0.28 bits.** We have no specific reason to expect a believed outcome to favour IIT.
- **Verdict:** INCONCLUSIVE or BOUNDED, with INCONCLUSIVE the more likely.
- **The control flag is not raised.** Theory Q stays at 0.5.

## Limits stated now

- **The belief is stipulated, not held.** An instructed scenario may be weaker than real recall, or stronger: it is salient and sits right next to the item. The q gate confirms only that the scenario was encoded. q_own shows whether the rater actually came to hold it (descriptive). A BOUNDED verdict bounds stipulated outcomes, not held ones.
- **Power at the threshold is modest.** An IIT-only leak exactly at the 0.25-bit threshold gives DOMINATED only 42% of the time. So INCONCLUSIVE is the most likely verdict for a real leak of threshold size.
- **The planted leaks are constant.** The gate does not plant a leak in one model only, or in near-silent cells only. A leak confined to one model would most likely read INCONCLUSIVE, because the model bootstrap often drops that model.
- **The belief probe comes after the ratings.** It cannot show that belief was formed before rating, only that the scenario was understood by the end.
- **Same items and clusters.** There are 6 clusters, the elastic fraction is high (63% of cells near-silent), and silent cells could still bend. L averages over committed and near-silent cells.
- **The memory path is untouched.** Crediting a theory from proponents' published explanations of a famous outcome is not randomised here. Only human raters test it.
- **Unequal rater pools.** Instances that fail the check are dropped, so the scored pool can differ in size by model.

## Sealed files

- `experiments/theory_leak/`: `make_mc_packets.py`, `score_mc.py`, `packets/mc_*` (12 packets, 12 keys, `mc_launch_map.json`), `planted_mc.json`
- this prereg
