# Pre-registration (DRAFT, not sealed): an awareness-linked lateralised negativity in a second lab without masking (ds006171)

Agent: Open Mind thread. Date: 2026-11-26.

Status: draft. Seal only after the label-free kill test (§7) passes and a Fable pre-seal review is done.

No EEG has been read. Behaviour files have been read for counts and contrasts only.

## 1. Question and claim scope
- **Question.** Does a contralateral-minus-ipsilateral posterior negativity at 180–280 ms separate seen from unseen near-threshold Gabors at matched contrast? Data: OpenNeuro ds006171, Melcón et al. 2024, doi:10.1111/psyp.14525, CC0. Task: no-cue, 35 subjects.
- **What it bears on.** A positive result is a conceptual transfer of our sealed Cohen 2024 VAN PASS. It changes the lab, the stimulus (Gabor, not face), the masking (none) and the measure (lateralised, not bilateral).
- **What it cannot separate.** This task cannot separate an awareness negativity from an attention shift to a detected target (N2pc). So the claim is limited to "awareness-linked lateralised negativity".
- **Prior art.** See `experiments/ds006171_van/PRIORART.md`. A GitHub reanalysis already reports the bilateral seen/unseen VAN at matched contrast and P3b unseen = catch. Our lateralised test and the unseen-vs-zero test are not in it.

## 2. Rivals and where they disagree
Δ is the seen − unseen difference in lateralisation; L(miss) is the lateralisation on unseen trials.

| Rival | Δ = L(hit) − L(miss) | L(miss) |
|---|---|---|
| Awareness-linked negativity | < 0 | any |
| Contrast leak | 0 after matching | any |
| Eye movements toward seen targets | < 0, and HEOG differs between hits and misses | any |
| N2pc (attention shift) | < 0 (not separable here) | any |
| All-or-none, no residue | < 0 | 0 |
| Graded awareness | < 0 | < 0 |
| Stimulus residue | < 0 | < 0 |

- **Graded vs residue cannot be separated in these data:**
  - both share the early sensory response;
  - the contrast range within unseen trials is only about 1.4×;
  - unseen orientation accuracy is 466/919 = 50.7%, which is chance.
- So L(miss) and R_lat = L(miss)/L(hit) are descriptive. The one exception is in §6.

## 3. Behaviour facts that fix the design (from the events files)
- **Responses.** The `subjective_r` column is blank for 107–364 of 400 trials in nine subjects (08, 13, 14, 15, 16, 18, 20, 24, 29). The raw codes 124 (seen) and 125 (unseen) are complete, so responses are read from the codes. Fable found that the codes agree with the column on every trial where both exist; we re-check this in code.
- **Contrast.** The staircase does not match contrast: hits are a median 4.1% higher in geometric-mean contrast (range 0.975–1.071). Left and right staircases also differ within a subject, so matching is done within hemifield.
- **Photodiode.** Code 128 follows each stimulus trigger, a median 39 ms later (range 30–80). Each trigger's time is replaced by the next 128; a trial with no 128 within 100 ms is dropped. This applies to catch trials too.
- **Catch side.** Catch codes 31/32 are a nominal side in the no-cue task (to be confirmed in Melcón's methods). So L(catch) has an expected value of 0, and catch trials are a negative control.

## 4. Measure (and why it tracks the target)
- **Definition.** L = mean(contralateral) − mean(ipsilateral) over the pairs PO7/PO8, P7/P8 and O1/O2, in 180–280 ms after the photodiode. L is computed for left and right stimuli separately, then averaged with equal weight.
- **Why the window.** Koivisto & Grassini 2016 (abstract opened) and Eklund & Wiens 2018 (full text opened).
- **Why the measure tracks the target.** A lateralised stimulus drives contralateral visual cortex. Subtracting the ipsilateral side removes non-lateralised activity: P3, arousal and reference effects.
- **Independent checks:**
  - L(catch), by nominal side, must have a 95% CI that includes 0. If not: INVALID (side coding or pipeline error).
  - Pooled L over all Gabor trials, with no awareness labels, must be < 0 somewhere in 80–300 ms. If not: INVALID (timing or side error).
  - After unblinding, L(hit) < 0.

## 5. Preprocessing (label-blind)
- **Filter and resample:** 0.1–30 Hz zero-phase FIR, then resample to 256 Hz.
- **Reference:** average.
- **Epochs:** −200 to 600 ms, baseline −200 to 0.
- **Rejection:**
  - ROI peak-to-peak > 150 µV;
  - VEOG > 80 µV in −100 to 400 ms;
  - HEOG step > 20 µV in −100 to 400 ms. This threshold is an N2pc convention quoted by Fable from memory; it must be checked against an opened source before sealing.
- **Channels:** bad ROI channels are interpolated. No ICA.

## 6. Statistics and decisions
- **Matching.** Within subject and hemifield, pair each hit with a miss 1:1 without replacement, by nearest log contrast, with caliper |Δ ln c| ≤ 0.01. Matching uses trials kept after rejection and is averaged over 200 random matchings.
- **Primary statistic.** Δ per subject. One-sided sign-flip permutation over subjects (10,000), plus a bootstrap 95% CI.
- **Eligibility.** At least 60 matched pairs, with at least 25 per hemifield. Fewer than 24 eligible subjects: INVALID.
- **Calls:**
  - **PASS:** p < .05, CI excludes 0, and the HEOG checks pass.
  - **NO TRANSFER:** CI lower bound > −0.25 µV.
  - **INCONCLUSIVE:** anything else.
- **R_lat.** Estimate and CI only. If R's kill test passes unchanged (half-width ≤ 0.12, and ≥ 80% correct at plants 0, 0.3 and 0.4), then an upper bound < 0.20 is called ALL-OR-NONE-COMPATIBLE. There is no call in the other direction.
- **Secondaries, with Holm correction:**
  - bilateral ROI at the same matching (replicates the GitHub result);
  - single-trial regression L ~ seen + ln contrast;
  - sensitivity run without the three subjects whose false-alarm rate is 22.5% (10, 21, 31).
- **Fallbacks, stated now:**
  1. If false calls in the planted gate exceed 5%: use a t-interval over subjects.
  2. If the label-free pooled peak in 150–350 ms falls outside 180–280 ms: use the peak ± 50 ms.
  3. If fewer than 24 subjects pass at caliper 0.01: use caliper 0.02, once.

## 7. Kill test and planted answer (label-free; before sealing)
The scripts read codes 11–32 and 128 only, never 124/125.
1. **Catch and pooled checks** (§4).
2. **Planted answer.**
   - Remove real lateralisation by sign-flipping each trial's side at random, which keeps real noise.
   - Assign pseudo hits and misses at the real per-subject counts.
   - Plant Δ = 0 and Δ = −0.4 µV, with a between-subject SD of 0.4.
   - Required: ≥ 80% detection at −0.4 µV and ≤ 5% false calls at 0. Otherwise drop before sealing.

## 8. Artefacts
- **Saccades toward seen targets** (the main threat).
  - Subject exclusion: residual left-minus-right HEOG in 0–300 ms over 3 µV in either class (threshold to be checked against a source).
  - Group check: the hit − miss HEOG CI must include 0.
  - Δ must survive with HEOG as a covariate.
- **Contrast leak.** After matching, mean |Δ ln c| must be < 0.001. Trial-number and orientation balance are reported.
- **Timing.** The same photodiode rule applies to all classes.
- **Hemisphere asymmetry.** Removed by equal left/right weighting.

## 5b. EOG and recording facts from label-blind checks (2026-11-26; no awareness labels read)
- **Two recording layouts:**
  - 32 subjects: 144 channels;
  - sub-02, 04, 05: 256-channel mode. Banks E–H are unused, with a 10-s SD of 0.00 µV, and are dropped. Their channels.tsv lists the 144 in use.
- **Bipolar EOG SD at 0.5–30 Hz** (30 s mid-recording, all subjects):
  - HEOG is broken in sub-01 (H1 SD 1,373 µV) and sub-13 (412 µV, VEOG also bad).
  - VEOG is broken or flat in sub-19, 24, 29 and 30. Sub-29's HEOG is also high (238).
  - Elsewhere the bipolar HEOG SD is 7–125 µV.
- **Smoke test** on sub-01, 02, 04 and 10 with the 20 µV HEOG step rule:
  - Rejection is 2%, 15% and 16% in sub-04, sub-10 and sub-02, but 97% in sub-01.
  - Low-passing HEOG at 10 or 6 Hz before the step function changes this little, so it is not adopted.
- **Rule to fix before sealing (label-blind):**
  - A subject whose HEOG step rule rejects > 50% of trials has unusable HEOG and is excluded. Saccades are the main threat to a lateralised measure, so there is no fallback channel.
  - A subject whose VEOG step or peak-to-peak rejects > 50% is excluded on the same logic.
  - Exclusions are counted before labels are read. They count against the 24-subject minimum.

## 9. Not verified yet
- Whether a cue or placeholder marked a side on no-cue catch trials (Melcón methods).
- The HEOG thresholds, and HEOG polarity.
- The participants.tsv ID scheme (sub-001, 54 rows) against the EEG subject IDs.
