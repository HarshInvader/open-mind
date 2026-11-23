# Task #5: where do frozen wake-vs-N3 cutoffs place REM? (sealed run, 2026-11-23)

Prereg: `docs/prereg/2026-11-23_transfer5_rem_placement.md` (sealed in 8b08564; amendment 1, a mirror URL for the record list, in 89e5172, before any HMC data). The full output is in `results.json`.

## Headline

For 5 of the 9 measures, cutoffs frozen on Sleep-EDF wake vs N3 carry over to a second hospital's hardware (HMC, 143 subjects). **All 5 put REM on the wake side**, at 83% to 104% of the way from N3 to wake. **No measure carries REM information beyond the power spectrum**: every eligible phase-surrogate call is "same".

## Sealed verdict

> measures disagree on REM (vs baseline): rel_delta (wake side, surrogate same) | comparator: baseline | subjects: 143

The verdict follows the sealed rule, but there is little behind it. It rests on relative delta alone, a band the baseline already contains. The disagreement is one of degree (1.04 vs 0.875), not of side. Of the two pre-registered outcomes, "one axis, spectral" did not hold. The other, "a disagreement only among spectral measures", did.

Our placement prediction failed. We expected most measures to put REM in between or on the N3 side. Every eligible measure put it on the wake side.

## Primary (HMC, 143 subjects; 4,199 training epochs, 16,080 test epochs, 5,729 surrogate epochs)

Position = (REM − N3) / (W − N3), using subject-mean wake-side fractions with a joint subject bootstrap (2,000 resamples). 1 = wake, 0 = N3.

| Measure | Train BA (Sleep-EDF) | HMC BA | Eligible | REM position [95% CI] | Surrogate | vs baseline (difference CI) |
|---|---|---|---|---|---|---|
| exponent | 0.960 | 0.953 | yes | 0.829 [0.779, 0.872] | same | same |
| lz | 0.932 | 0.841 | yes | 0.856 [0.804, 0.905] | same | same |
| perm_entropy | 0.927 | 0.853 | yes | 0.966 [0.896, 1.032] | same | inconclusive [+0.039, +0.147] |
| rel_delta | 0.924 | 0.810 | yes | 1.037 [1.006, 1.069] | same | **different** [+0.122, +0.207] |
| rel_beta | 0.964 | 0.899 | yes | 0.979 [0.954, 0.998] | same | inconclusive [+0.076, +0.136] |
| baseline (LDA, exponent + 6 bands) | 0.970 | 0.978 | yes | 0.875 [0.836, 0.908] | same | — |
| spectral_entropy | — | 0.786 | no: hardware-bound | | | |
| dfa | — | 0.735 | no: hardware-bound | | | |
| rel_alpha | 0.802 | 0.647 | no: hardware-bound | | | |
| wsmi | 0.665 | — | no: fails in-dataset | | | |

No sign mismatches against the prior signs.

## What we can and cannot claim

- **Can claim:**
  - A frozen-cutoff transfer table across two sleep labs. Five measures transfer; three are hardware-bound; wSMI at this montage fails even within Sleep-EDF.
  - At a wake-vs-N3 cutoff, REM is called "wake" by every transferable measure.
  - Anything that separates REM from wake in these measures is spectral.
- **Cannot claim:**
  - That these measures track experience. HMC has no dream reports, and "REM looks awake" may only mean "REM lacks slow waves".
  - That this contradicts Lendner 2020 (slope separates REM from wake). A cutoff set on wake vs N3 is too coarse to separate REM from wake.
- **Novelty:** this is atlas-grade, not a discovery. Single-measure REM placement is already reported (Lendner 2020; Ugail & Howard 2026). What is new is the frozen cross-dataset cutoffs, the spectral competitor and the surrogate gate.

## Secondary (reported, not gating)

**Sleep-EDF REM** (52 subjects; in-sample cutoffs, so optimistic): exponent 0.747, baseline 0.739, perm_entropy 0.789, lz 0.934, rel_beta 0.926, rel_delta 1.036, wsmi 0.20. All are on the wake side except wsmi, which is not viable.

**ds005620 propofol** (20 subjects, 0 skipped). These are raw wake-side fractions, because the set has no W/N3 anchors. Values are awake → sed2.

| Measure | awake | sed2 |
|---|---|---|
| exponent | 0.95 | 0.29 |
| baseline | 0.95 | 0.30 |
| perm_entropy | 0.68 | 0.03 |
| lz | 0.43 | 0.53 |
| rel_delta | 1.00 | 0.74 |
| rel_beta | 1.00 | 0.79 |
| rel_alpha (ineligible) | 1.00 | 0.87 |
| spectral_entropy (ineligible) | 0.95 | 0.61 |

- **Sealed secondary prediction (ρ > 0) is not confirmed.** Spearman between the HMC REM position and the sed2 fraction, over the 5 eligible measures: ρ = 0.6, p = 0.28.
- **Unsealed observation (a hypothesis, not a claim):** the exponent and the baseline call REM awake but call propofol sed2 N3-like (0.95 → 0.29), although about 83% of informative sed2 awakenings in this dataset reported experience. If real, the exponent follows slow-wave state, not experience. The limits:
  - 20 subjects with only 1-3 sed2 epochs each;
  - behavioural labels (RASS −4) and only group-level report rates, so no epoch is tied to a report;
  - LZ's cutoff already fails on awake (0.43), and perm_entropy's awake fraction is only 0.68, so only the exponent and baseline rows are readable.

## Next

- #5 is closed and logged in `docs/NEGATIVE_ATLAS.md`. There will be no paper.
- The only live thread is whether the exponent follows slow waves rather than experience under propofol. Testing it needs a propofol set with power and per-awakening reports. DOSE-I is the candidate, but it has a Data Use Agreement that needs owner sign-off. Before asking for that, confirm that DOSE-I has per-awakening reports.

## Files

- `measures.py`, `analyse.py`, `fetch_hmc.py`, `extract_ds.py` and `planted.py` are sealed.
- Planted gate: `planted.json` (attempt 3 passed); earlier attempts are in `planted_attempt1.json` and `planted_attempt2.json`.
- Features: `feats_sedf_wn.jsonl`, `feats_sedf_r.jsonl`, `feats_hmc.jsonl`, `feats_hmc_surr.jsonl`, `feats_planted_surr.jsonl`, `ds005620_feats.jsonl`.
- Logs: `fetch_hmc_log.jsonl` (151 fetched, 0 skipped) and `ds005620_log.json`.
- Raw HMC epochs (`raw_hmc/`) are not committed. They can be re-fetched with `fetch_hmc.py`, which is seeded.
