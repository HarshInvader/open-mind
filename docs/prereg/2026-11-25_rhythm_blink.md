# Pre-registration: are blink trials more alpha-band phase-locked at T2? (Zauner et al. 2012 on ds001810)

Agent: Open Mind thread   Date: 2026-11-25   Script: `experiments/rhythm_blink/rhythm_blink.py`   Source: Fable round 17, study 1

- **Zero new bytes.** The ds001810 T2-locked epochs are already on disk: OpenNeuro, licence CC0. They are not Cohen data, so the Cohen hold does not apply.
- **Outcome:** "T2 identified" vs "T2 not identified" given T1 correct, at lag 3. This is identification, not seen/unseen. "Blink" below means a T2 identification error.

## 0. The claim and prior art (texts in `datasets/local/r17_priorart/`)

- **Zauner, Fellinger, Gross, Hanslmayr, Shapiro, Gruber, Müller & Klimesch 2012** (NeuroImage, doi:10.1016/j.neuroimage.2012.06.075, full text).
  - **Prediction:** entrainment "during the time window of T2 presentation – is larger for AB than NoAB trials".
  - **Conclusion:** "alpha entrainment may be considered the critical factor underlying the attentional blink phenomenon".
  - **Measure:** the phase-locking index, from 7-cycle Morlet wavelets, 8–12 Hz, ±50 ms around T2.
  - **Where the PLI effects were:** central, centro-parietal, parietal and parieto-occipital ROIs, not occipital. They were largest at P4.
  - **Their own pairwise PLI tests** were significant for AB vs control only, not AB vs NoAB ("pairwise comparisons yielded significant differences between AB and control trials only"). So the AB > NoAB phase-locking prediction is stated, and supported by the means, but not by a significant pairwise test.
  - **They also report** that the PLI is broadband ("phase locking around T2 is a broad-band phenomenon").
  - **Reference:** linked ears.
  - **Design:** 14 analysed subjects, lag about 300 ms.
  - They also note that "the magnitude of the PLI is known to decrease with increasing sample size". Their control-trial comparison was not count-matched.
- **Conflicting evidence:**
  - Kranczioch et al. 2017 (PLOS ONE, doi:10.1371/journal.pone.0178934, full text): 51 subjects, between-subject only, opposite sign.
  - Janson et al. 2014 (JoCN, doi:10.1162/jocn_a_00551, abstract): an opposite trend.
  - Petro & Keil 2015 (doi:10.1007/s00221-015-4418-2, abstract): incorrect trials showed greater ssVEP phase locking, in Zauner's direction, but pre-T1.
- **No within-subject, trial-level, count-matched test at more than 14 subjects** was found.
- **ds001810:** its only paper (Reteig et al. 2022, PLOS ONE, doi:10.1371/journal.pone.0262718, full text) "refrained from further analysis of the EEG data".
- **Stream timing:** 91.7 ms per letter with no gap (Reteig 2022), so the stream frequency is 10.9 Hz and lag 3 is 275 ms.

## 1. Data and measure

- **Blocks and trials:** exactly the sealed hypothesis-generator preprocessing and block eligibility, imported unchanged from `experiments/hypothesis_generator/ab_killtest.py` (`preprocess`, `eligible_blocks`):
  - 30 Hz zero-phase low-pass;
  - bad and outlier channels dropped;
  - average reference and whole-epoch mean removal;
  - the 150 µV and VEOG rules;
  - the block floor;
  - at least 15 trials per class per block.
  - This gives 42 subjects and 76 pre-tDCS blocks.
- **ROI:** Zauner's significant PLI region (central, centro-parietal, parietal): C1, Cz, C2, CP1, CPz, CP2, P3, Pz, P4.
  - Every eligible block keeps 8 or 9 of them. A block needs at least 6.
  - An occipital/parieto-occipital ROI was used in the first draft and replaced before sealing, after the pre-seal review pointed to Zauner's null occipital ROI.
- **Wavelet:** complex Morlet at 10.9 Hz, σ_t = 3/(2π·10.9) = 43.8 ms, truncated at ±3σ (±131 ms).
  - Its frequency SD is 3.6 Hz, so it passes about 7–15 Hz. The measure is therefore alpha-band phase-locking, not specifically locking to the 10.9 Hz stream.
  - The pre-seal reviewer found label-free ITC of 0.30 at 8, 10.9 and 14 Hz carriers alike.
  - A 7-cycle wavelet would need data from about −370 ms, but the epoch starts at −200 ms. That is why the wavelet is shorter.
- **ITC:** |mean over trials of unit phasors|, averaged over ROI channels and over every sample whose centre lies in [−50, +50] ms re T2.
- **Count matching, per block:** m = min(n_blink, n_noblink).
  - Draw m trials of each class, 100 times (seeded).
  - Δ_block = mean over draws of ITC(blink) − ITC(no-blink).
  - Subject Δ = mean over that subject's eligible blocks.

## 2. Gate (label-free and count-independent; runs first)

- **Per block:** debiased all-trial phase-locking ρ² = (n·R² − 1)/(n − 1), with R the all-trial ITC per channel and centre in the window, averaged.
- **Per subject:** the mean over blocks.
- **GATE PASS:** group mean ρ² > 0 with one-sided t > t_crit (df 41, α .05), AND median subject ρ = √max(ρ², 0) ≥ 0.10. Otherwise **METHOD BLIND**, and the real labels are not analysed.
- **This is a sanity floor.** It shows that alpha-band phase-locking at T2 is measurable at all. It does not show specificity to the stream frequency.
- **It replaces a count-dependent ITC/chance ratio from the first draft.** The pre-seal reviewer predicted that ratio would sit at the threshold, about 2.07 against 2, from trial counts alone.

## 3. Primary test (real labels, once, only after GATE PASS)

Subject Δ, group two-sided one-sample t (α .05), plus TOST against ±0.02 (each side one-sided α .05). Verdicts, checked in order:

| Verdict | Condition |
|---|---|
| BLINK TRIALS MORE ALPHA-BAND PHASE-LOCKED AT T2 | p < .05, mean Δ > 0 (Zauner's direction) |
| BLINK TRIALS LESS ALPHA-BAND PHASE-LOCKED AT T2 | p < .05, mean Δ < 0 (Kranczioch/Janson direction) |
| NO DIFFERENCE: EQUIVALENT WITHIN ±0.02 | both TOST p < .05 |
| INCONCLUSIVE | otherwise |
| UNRESOLVED | more than 3 subjects with a non-finite Δ (checked first) |

**Reported in every case:**
- mean Δ, SE, 95% CI, t, p and TOST p;
- a flag for a significant Δ smaller than the ±0.02 bound;
- the log power ratio, blink vs no-blink (Zauner: phase, not power, differs);
- the count-matched log evoked-amplitude ratio (|mean coefficient|);
- the descriptive Δ time course (centres −50 to +660 ms in 20 ms steps);
- the secondary between-subject Pearson r of label-free ρ² vs blink rate (Kranczioch 2017's design; two-sided, n = 42, no verdict);
- per-subject values.

## 4. Calibration

Shuffled labels within block; run before sealing; output in `out/calibration.json`. Final ROI, 42 subjects, 76 blocks.

- **200 shuffled-label runs:**
  - "more" 4 and "less" 7, so the directional false-positive rate is 5.5% (nominal 5%);
  - EQUIVALENT 140 (70%), INCONCLUSIVE 49;
  - SD of the group mean Δ: 0.0075.
- **Planted effects, 25 runs each, shuffled labels, "blink" trials only:**

  | Plant | Phase 0 | π/2 | π | 3π/2 |
  |---|---|---|---|---|
  | 1 µV additive, Δ (MORE rate) | 0.090 (1.00) | 0.138 (1.00) | 0.086 (1.00) | 0.029 (0.72) |
  | 2 µV additive, Δ (MORE rate) | 0.244 (1.00) | 0.298 (1.00) | 0.247 (1.00) | 0.180 (1.00) |

  - The additive plant is a 10.9 Hz cosine with a fixed phase re T2 and a Gaussian envelope (SD 100 ms, peak at T2), on every ROI channel.
  - **Amplitude-preserving plant** (each phase's deviation from the block's circular mean shrunk by κ, |coefficient| unchanged, as in Zauner's "phase, not power" claim): κ 0.05 gives Δ 0.037 (MORE 1.00); κ 0.10 gives Δ 0.078 (MORE 1.00).
- **What the ±0.02 bound means:** EQUIVALENT rules out effects smaller than a 1 µV phase-locked addition at any tested phase (Δ 0.029–0.138). It also rules out an amplitude-preserving phase concentration of about 3% (κ ≈ 0.03).

## 5. Fallbacks and disclosures (stated before any real-label ITC)

- **Gate fails:** METHOD BLIND. There is no change to the wavelet, window, ROI, bound or thresholds.
- **Run guards:** `run` refuses if `gate.json` was not written by the sealed script and prereg, and refuses to run a second time.
- **Non-finite subject Δ:** that subject is dropped and the count is reported. More than 3 dropped makes the verdict UNRESOLVED.
- **Equivalence bound changed after a calibration, before sealing:** first set at ±0.05 from the round-17 planner's simulated SE (0.017).
  - The first shuffled-label calibration (old ROI) then showed an SD of 0.007, under which ±0.05 would call effects larger than a 1 µV plant "equivalent". It was tightened to ±0.02.
  - No fallback for this was stated in advance. It is disclosed as a post-calibration change, made before sealing, with shuffled labels only. It makes EQUIVALENT harder to reach.
- **Label exposure:** the same epochs and labels were used in the sealed hypothesis-generator kill test (2026-11-24; INVALID at its P3b gate).
  - That test showed real-label near-null results for ERP window means: pre-T2, P1 and N1 at AUC 0.49–0.51, on channels overlapping this ROI. It also showed P3b and N2 effects.
  - No phase, ITC or spectral measure was ever computed on real labels.
- **The round-17 planner's label-free checks** on these epochs:
  - ITC at 10.9 Hz over posterior channels, median about 0.42 against chance of about 0.10;
  - the grand ERP shape;
  - trial SD 3.39 µV;
  - a zero-data power simulation (SE 0.017, power 0.83 at Δ 0.05).
- **Pre-seal reviewer's checks** (shuffled labels or label-free; listed for disclosure):
  - the wavelet frequency response;
  - all-trial label-free ITC at six carriers (about 0.30 at each), with old ROI, raw and 7 Hz high-passed;
  - the block-mean ERP spectrum (peak 10–11 Hz);
  - 12 shuffled-label runs for each of 11 plants: a 1 µV additive plant gives Δ 0.016–0.070 across four phases, and non-rhythmic 2 µV ERP bumps move Δ by at most 0.004;
  - a predicted gate ratio of about 2.07 from all-trial debiased ρ of about 0.275 and the label counts.
- **The author's mechanics checks** used shuffled labels and printed only timing (12 s load, about 1 s per pass), finiteness, ROI sizes and a NaN test of the verdict rule.
- **Compute:** 1 process, nice 20.
- **Review history:** one Fable pre-seal review found three blockers:
  - the count-dependent gate;
  - "locked to the stream" overclaimed;
  - the UNRESOLVED rule was not implemented.
- **Fixes applied before sealing:**
  - the gate became count-independent;
  - the verdicts were renamed to alpha-band;
  - the UNRESOLVED rule and run guards were added;
  - the ROI was moved to Zauner's region;
  - the evoked-amplitude readout and phase/concentration plants were added;
  - calibration was re-run.
- The fixes were not re-reviewed.
- **Sealed inputs:** this prereg, the script, the imported `ab_killtest.py` (unchanged since its 2026-11-24 seal) and `out/calibration.json`.
- Any other change after sealing makes the study INVALID.

## 6. What a result would and would not mean

- **MORE:** supports Zauner's direction with count-matched trials at 3× their sample, on alpha-band phase-locking. Read it together with the power and evoked-amplitude ratios: their claim is phase without power. It does not show that the locking causes the blink.
- **LESS:** contradicts Zauner within subjects and agrees in sign with Kranczioch 2017's between-subject finding.
- **EQUIVALENT:** at lag 3 in these data, alpha-band phase-locking at T2 does not differ by more than ±0.02 between identified and missed T2. This counts against "the critical factor".
- **Limits:**
  - Identification, not awareness; lag 3 only; a different stimulus set and lab from Zauner.
  - The short wavelet blurs 7–15 Hz and reaches 131 ms past T2, so T2's own early evoked response enters the window, as it does in Zauner's 7-cycle measure. The reviewer's ERP-bump checks found this moves Δ little.
  - Average reference, not linked ears.
  - Count matching attenuates a real effect more in small blocks; pairwise phase consistency would avoid that.
  - The T1 response (at −275 ms) overlaps the epoch start.
  - Pre-tDCS blocks only.
