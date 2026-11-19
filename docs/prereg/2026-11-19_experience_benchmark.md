# Pre-registration: the experience benchmark (Study 1) and the sealed residual model (Study 3)

Agent: mind-ne   Task: #42   Date: 2026-11-19
Plan: `docs/PLAN_2026-11-19_experience_benchmark.md`. Audit: `experiments/experience_benchmark/AUDIT.md`.

Seal this file BEFORE any EEG sample from a confirmation lab is read. The extraction script, the analysis script and the Study 3 model file are sealed separately, each before its own step (section 11).

## 1. Question and hypotheses

At a fixed sleep stage (N2), does any published EEG consciousness marker tell apart awakenings with a report of experience from awakenings with no experience, within subject, in labs this project has never opened? If one does, does it add anything over the frozen spectral baseline, and does it survive phase-randomised surrogates?

- **H1 (per measure m, family A).** Within-subject AUC of m for experience vs no experience differs from 0.5. Predicted directions (from the literature; used to orient the AUC and to count signs, while the test is two-sided):

  | Measure | Predicted with experience | Source of the prediction |
  |---|---|---|
  | posterior delta | lower | Siclari 2017 |
  | posterior high-frequency | higher | Siclari 2017 |
  | spectral exponent | flatter (less negative) | arousal and E/I accounts |
  | LZ76 | higher | complexity accounts |
  | permutation entropy | higher | complexity accounts |
  | Higuchi fractal dimension | higher | complexity accounts |
  | wSMI | higher | King 2013 / GNW accounts |
  | Gaussian total correlation | lower | integration proxies (slow-wave synchrony) |

- **H2 (per non-spectral measure, family B).** Adding m to the frozen spectral baseline raises the lab-held-out AUC. The family is LZ76, permutation entropy, Higuchi FD and wSMI (total correlation is excluded; see §5).
- **H3 (Study 3).** A frozen model on surrogate-excess features, fitted only on the discovery labs, predicts experience in the confirmation labs.
- **H0 we take seriously:** published markers track arousal (wake vs N3) and not experience at fixed stage. The double-dissociation outcome in section 9 tests this.

## 2. Data

DREAM database (figshare, CC BY 4.0), per-awakening metadata `experiments/dataset_audit/dream_records.csv`.

- **Confirmation labs (never opened by this project):**
  - Rome multiple awakenings (set 9);
  - LODE (set 3);
  - DATA1 / Noreika (set 16);
  - Aamodt (sets 17 + 18), counted as **one lab**.
- **Discovery labs (Study 3 fitting only; exposed before):**
  - Tononi Serial Awakenings (set 13);
  - Zhang & Wamsley (set 1).
- Rome young adults (set 11) is not used: no subject has both classes.
- **Metadata rows.** Only the highest `Amendment` per (`Set ID`, `Filename`) is used. Tononi is listed three times (809 rows, 287 files). After de-duplication, the discovery N2 counts are Tononi 124 / 107 (39 subjects) and Zhang & Wamsley 50 / 31 (16). The audit's 344 / 309 counted every copy. Confirmation labs have no duplicates.
- **Subject key.** (lab, `Subject ID`). Aamodt sets 17 (evening) and 18 (morning) come from one study with one ID numbering, and IDs 10, 11, 14, 15 and 16 appear in both, so they are treated as the same people. That gives 25 / 20 awakenings in 9 subjects. Sensitivity check: key (`Set ID`, `Subject ID`), 22 / 17.
- **Labels.** `Experience` = 1, `No experience` = 0. `Without recall`, `No experience or without recall` and `Unknown` are excluded.
- **Stage.** `Last sleep stage` = N2 for the primary family. REM is secondary (section 8).
- **Inclusion.** For an awakening to be used, its subject must have at least one of each class at that stage after exclusions.
- **Expected N2 counts.** 252 experience / 151 no-experience awakenings, 47 subjects, 4 labs (before artefact exclusion; Rome 171 / 85 in 18, LODE 41 / 28 in 15, DATA1 15 / 18 in 5, Aamodt 25 / 20 in 9).
- **Fragility.** DATA1 has 5 subjects and blank artefact and time fields. If artefact exclusion leaves fewer than 2 DATA1 subjects with both classes, only 3 labs remain and the major-negative outcome (which needs 4 labs) becomes impossible. This is stated now.
- **Ground truth.** Report on awakening (behaviour, not delayed report).
- **Kill rule K1, rechecked after artefact exclusion.** If fewer than 300 N2 awakenings, fewer than 120 no-experience awakenings or fewer than 3 labs remain, there is no confirmatory claim. The result goes to the negative atlas as underpowered.

## 3. Preprocessing (identical code for every lab; per-lab channel maps are fixed in the extraction script before any sample is read)

1. **Window.** The 20 s ending 2 s before the awakening.
   - The awakening is the EDF annotation of the call where the EDF+ annotation channel has one; otherwise it is the end of the record.
   - The per-lab rule, and its source (DREAM documentation or the lab's paper), is written into the extraction script before it is sealed.
   - Sensitivity checks: the last 20 s exactly; the 20 s ending 10 s before the awakening.
   - Arousal guard: a label-blind pre-awakening arousal index (log alpha/delta power ratio of the final 5 s of the window, all channels) is extracted. It is used as a covariate in a Family A sensitivity check (§8).
2. **Channels.**
   - Keep EEG channels only. Drop EOG, EMG, ECG, accelerometer, pulse-oximeter, mastoid and `SM` channels.
   - Rome's `01` is read as O1.
   - LODE keeps its 7 bipolar headband derivations.
   - All other labs are re-referenced to the average of their EEG channels.
3. **Units.** Signals are converted to µV from the EDF header's physical dimension before any threshold.
4. **Artefacts.**
   - A channel is bad in an awakening if its SD is < 0.5 µV or > 200 µV, or its absolute value exceeds 1000 µV.
   - An awakening is dropped if fewer than 60% of its channels are good, or if DREAM's `Proportion artifacts` > 0.5.
5. **Native-rate branch** (posterior spectral measures):
   - 50 Hz notch (Q 30) for the European labs, 60 Hz for the US labs;
   - Welch, 4 s Hann windows, 50% overlap.
6. **100 Hz branch** (all other measures and the baseline):
   - anti-alias and resample to 100 Hz;
   - then `experiments/lz_slope/features.py: preprocess` (linear detrend, 4th-order zero-phase 40 Hz low-pass).
   - This is the exact pipeline of the Sleep-EDF work, so the positive control and the benchmark share code.
7. **Posterior ROI.** Whichever of P3, P4, Pz, P7, P8, PO3, PO4, POz, PO7, PO8, O1, O2, Oz are present and good. LODE has no posterior-only channels, so its ROI is its 4 derivations that include O1 or O2. This is a stated limitation.
8. **10-20 subset for the pairwise measures** (wSMI, total correlation). The good channels among Fp1, Fp2, F7, F3, Fz, F4, F8, T7/T3, C3, Cz, C4, T8/T4, P7/T5, P3, Pz, P4, P8/T6, O1, O2. LODE uses its 7 derivations.
9. **Channel maps.** Appendix A lists, per lab, the EEG channels, the posterior ROI and the 10-20 subset, read from the EDF headers (which hold no signal).
   - Tononi (EGI 257) and Zhang & Wamsley use the nearest EGI/10-10 electrode to each 10-20 position, from the cap's `.sfp` file, fixed in the extraction script.
   - EGI positions are matched by standard coordinates, not by inspecting the signal.
10. **Missing values.** If a measure cannot be computed for an awakening (for example an empty ROI, or fewer than 3 good channels for a pairwise measure), the awakening is dropped for that measure only. The both-class rule is then re-applied per measure.

## 4. Measures

All measures are computed per awakening. Channel-wise values are averaged over good channels.

| # | Measure | Branch | Definition |
|---|---|---|---|
| 1 | posterior delta | native | log10 of relative power 1-4 Hz over 1-40 Hz, posterior ROI |
| 2 | posterior high-frequency | native | log10 of relative power 20-45 Hz over 1-45 Hz, posterior ROI (Sleep-EDF control: 20-40 Hz) |
| 3 | spectral exponent | 100 Hz | `lz_slope/features.py: spectral_exponent` (1-40 Hz), all channels |
| 4 | LZ76 | 100 Hz | per channel: binarise at the median, `antropy.lziv_complexity(normalize=True)` |
| 5 | permutation entropy | 100 Hz | order 3, delay 1, normalised (`antropy.perm_entropy`) |
| 6 | Higuchi FD | 100 Hz | kmax 10 (`antropy.higuchi_fd`) |
| 7 | wSMI | 100 Hz | King et al. 2013: symbols of 3 samples, tau 3 samples (30 ms), weights 0 for identical and opposite symbol pairs, averaged over all channel pairs of the 10-20 subset |
| 8 | Gaussian total correlation | 100 Hz | −0.5 · log det(0.9 R + 0.1 I) / n_channels, where R is the channel correlation matrix of the 10-20 subset |

- **Secondary measures** (family C, exploratory, N2):
  - sample entropy (m 2, r 0.2 SD);
  - multiscale entropy (scales 1-5, mean);
  - 0-1 chaos test K;
  - DFA alpha (4-200 samples);
  - `tra_x` (as in `experiments/nonequilibrium/ne_measures.py`);
  - CSER;
  - catch22 (Wong 2025 replication, REM).
- **Frozen spectral baseline.** `spectral_exponent` plus the 6 relative band powers of `band_powers` (delta, theta, alpha, sigma, beta, 30-40 Hz), all channels, 100 Hz branch.
  - The 1-30 Hz variant (exponent 1-30 Hz; drop 30-40 Hz) replaces it **for all labs at once** if any confirmation lab triggers the rule. That keeps the model columns identical in every leave-one-lab-out fold.
  - Trigger: the lab's mean log10 PSD (all awakenings, all good channels, 100 Hz branch before the 40 Hz low-pass) averaged over 30-40 Hz lies more than 2 log10 units (20 dB) below the ordinary least-squares log-log line fitted over 2-25 Hz.
  - The check is label-blind and is recorded before unblinding.
- **Covariates in the baseline.**
  - Clock time of awakening (hours after 18:00).
  - Awakening index within the subject's session.
  - Where a lab lacks them, the subject mean is used, which contributes 0 after centring. DATA1 has no times. LODE awakenings are morning home naps (08:58-10:02), so clock time means something different there; this is stated as a limitation.
- **Spectral measures cannot be a major positive.** Measures 1-3 are spectral by construction: they are scored in Family A (replication and dissociation) but are not eligible for the major-positive mark.

## 5. Split and normalisation

- **Centring.** Every feature is centred within subject, then z-scored with a global SD, exactly as `t1lib.centre_z` does. Between-subject and between-lab offsets therefore cannot drive a result.
- **The AUC statistic used everywhere** (Families A and B, per-lab AUCs, bootstrap, gate, Study 3): the Mann-Whitney AUC over **within-subject pairs only**. Each experience/no-experience pair from the same subject counts once, and the pairs are pooled over subjects (weighted by the number of pairs). No pair crosses subjects or labs, so scale differences between labs cannot enter.
- **Family A.** No fitting: the AUC is oriented by the predicted direction, so it uses no parameters and needs no held-out split.
- **Family B.** Leave one lab out over the 4 confirmation labs. Gaussian total correlation is **removed from Family B**: it depends only on the channel correlation matrix, which multichannel FT surrogates preserve, so it can never pass the gate. Family B is therefore LZ76, permutation entropy, Higuchi FD and wSMI (**Holm over 4**).
  - Training data: the other confirmation labs plus the discovery labs (Tononi, Zhang & Wamsley). Whether the discovery labs are included is fixed when the analysis script is sealed (K4), before unblinding.
  - Logistic regression with ridge 1e-4 (`t1lib.logit_fit`).
  - Model 0: baseline + covariates. Model 1: model 0 + m.
  - In each fold, the held-out linear predictors of model 0 and model 1 are scored with the within-subject pair AUC. The held-out predictors of all four folds are pooled before scoring (each awakening is held out exactly once).
  - ΔAUC = AUC(model 1) − AUC(model 0).
- **Leak check.** `evidence.check_split(mode="transfer")` on every fold.

## 6. Statistics

- **Family A, primary, 8 tests.**
  - Within-subject pair AUC over all confirmation-lab N2 awakenings.
  - Null: labels permuted within subject, **5,000 permutations**, two-sided on |AUC − 0.5|.
  - **Holm over 8** at α = 0.05.
  - 95% CI from a subject bootstrap (5,000), resampling subjects **within lab** so each lab's share stays fixed.
- **Family B, primary, 4 tests.**
  - ΔAUC with a Freedman-Lane null. m is regressed on the model-0 regressors using all rows; this step is label-blind. The residuals are permuted within subject across all rows and added back to the fitted values, then model 1 is refitted in every fold. 5,000 permutations.
  - One-sided (ΔAUC > 0). **Holm over 4.**
  - Subject bootstrap within lab (2,000), refitting both models in each draw.
- **Equivalence (a bounded null).**
  - Family A: the 95% CI of the oriented AUC lies inside [0.40, 0.60].
  - Family B: the upper 95% bound of ΔAUC is < 0.03.
- **Per-lab AUCs** with their signs, for K3 and the 3-lab rule.
- **Surrogate gate** (any measure that passes H1 or H2):
  - 5 FT (multichannel, shared phases) and 5 IAAFT surrogates per awakening; the measure is recomputed on each and averaged.
  - share kept = (AUC_surr − 0.5) / (AUC_real − 0.5) for each surrogate type.
  - PASS if the share is ≤ 0.5 for both types.
- **Seeds.** All random seeds are fixed in the sealed scripts.

## 7. Positive control and planted checks (must pass before the confirmation labels are opened)

- **PC1, Sleep-EDF wake vs N3.**
  - Same code, 100 Hz, Fpz-Cz and Pz-Oz, 20 s windows; 60 subjects as in task #41.
  - Within-subject AUC per measure in the predicted direction (wake standing in for "experience").
  - A measure with AUC < 0.75 is flagged as a possible implementation fault. It may be fixed only before unblinding, by a sealed amendment.
  - Measures with AUC ≥ 0.90 count as **arousal-tracking** for the double dissociation.
- **PC2, Sleep-EDF REM vs N3**, reported as given.
- **P1, synthetic EEG** at the real per-lab channel counts, fs and awakening counts:
  - (a) Plant a non-spectral difference (the experience class gets extra phase coupling between channels or a nonlinear waveform with matched power spectrum). Families A and B must detect it for the measures built to see it, and the gate must PASS.
  - (b) Plant a purely spectral difference (a 1/f slope change). Family B must not detect it beyond 5%, and the gate must FAIL.
  - (c) Plant no difference. The family-wise FPR in families A and B (Holm-corrected, 200 synthetic datasets) must be ≤ 0.05 + 1.96 · SE, where SE is the binomial SE (≈ 0.015), i.e. ≤ 0.08.
- **P2, power, on the realised post-exclusion counts.**
  - It reports power at AUC 0.60 under Holm-8.
  - It reports the probability that the 95% CI lies inside [0.40, 0.60] when the true AUC is 0.50 and 0.53.
  - **K2:** if power at AUC 0.60 is below 80%, no major-positive claim can be made from this sample. Bounded nulls are still reported, since they are CI statements.
  - Realistic expectation: with a within-lab subject bootstrap on 47 subjects, two thirds from Rome, the CI half-width may be about 0.07-0.08, not 0.06. Bounded nulls may then be reachable only if the true AUC is about 0.52 or less. P2 will say which.
- **The pairwise measures in PC1.** wSMI and total correlation on 2-channel Sleep-EDF are one pair. For them, arousal-tracking is judged instead on BOAS ds005555 wake vs N3, a multichannel subset streamed within the approved budget. If that cannot be done before unblinding, they are excluded from the 6-of-8 count.

## 8. Secondary analyses (reported, not used for the publish gate)

- REM: family A on the same 8 measures, Holm over 8 (underpowered: 58% at AUC 0.59).
- N2 family C, with no correction.
- Without recall vs no experience, N2.
- Last-20-s-exactly window.
- Family A restricted to the Rome lab, and to the three other labs together.
- Family A on residuals of m after a label-blind within-subject regression on clock time, awakening index and the pre-awakening arousal index.
- Aamodt subject key (`Set ID`, `Subject ID`).

## 9. What counts (publish gate; packaging stays off until the unblinded result is red-teamed)

- **Major positive.** A non-spectral measure (4-8) that:
  - passes Holm in family A (and family B, if it is in it);
  - passes the gate;
  - has a family A AUC ≥ 0.65 **in the predicted direction** and ΔAUC ≥ 0.03;
  - shows the same sign in ≥ 3 of the 4 labs;
  - and K2 is met.

  Gaussian total correlation cannot be a major positive (it can never pass the gate).
- **Major negative (clean double dissociation).**
  - At least 6 of the 8 primary measures have a PC1 arousal AUC ≥ 0.90 **and** a family A 95% CI inside [0.40, 0.60].
  - No measure passes Holm in family A.
  - At least 4 labs and at least 300 N2 awakenings remain after exclusion.
  - This is narrower than the plan's version (about 14 markers, more than 1,000 awakenings); the plan's numbers counted discovery-lab duplicates and REM.
- **K3, lab artefact.** If a pooled family A effect is not the same sign in ≥ 3 labs, it is reported as lab-dependent and does not count as positive.
- **Messy middle.** Anything else, for example a significant AUC below 0.65, a measure that fails the gate, or fewer than 6 bounded nulls. It goes to the negative atlas and ledger, with no paper.
- **Stated limits.** Report is not experience (recall); scalp is not source; LODE is a forehead headband; two thirds of the N2 data comes from Rome.

## 10. Study 3: the sealed residual model (spec frozen here; weights frozen and hashed before confirmation unblinding)

- **Features.** Surrogate excess (real minus the mean of 5 FT surrogates) of the non-spectral measures LZ76, permutation entropy, Higuchi FD, wSMI, sample entropy, multiscale entropy, 0-1 K, DFA alpha and `tra_x` (total correlation is left out: its FT-surrogate excess is zero by construction). Each is computed on all channels and on the posterior ROI where it is defined, giving at most 18 features, z-scored within subject.
- **ROI.** The posterior ROI for Tononi and Zhang & Wamsley comes from the coordinate map in Appendix A.
- **Fit.** Discovery labs only (Tononi and Zhang & Wamsley, de-duplicated, N2, subjects with both classes). L2 logistic regression.
- **Nested cross-validation (5 × 5, subject-grouped).** C is chosen from {0.01, 0.1, 1} in the inner folds. The kill uses the **outer-fold** within-subject pair AUC.
- **Kill.** If the outer-fold AUC is < 0.58, H3 is not tested and the model is logged as negative. The final model is refitted on all discovery data with the C most often chosen.
- **Freeze.** The weights, scaler conventions and C go to `experiments/experience_benchmark/study3_model.json`, sealed before the confirmation labels are joined.
- **Test.** H3 is a separate single test, outside the Holm families: the within-subject pair AUC in the confirmation labs (N2), one-sided permutation p < 0.05 (5,000).
- **Its ΔAUC.** A model-0 baseline is fitted on discovery data and frozen with the Study 3 score as one extra column, the pair refitted on discovery only. ΔAUC is scored on the confirmation labs with no refitting.
- **Its gate.** The score is recomputed with surrogate-excess features from a second, independent surrogate draw, with the real features replaced by an FT or IAAFT surrogate of the awakening. The share-kept rule is as in §6.
- **Major only under the same marks as a single measure:** AUC ≥ 0.65, ΔAUC ≥ 0.03, gate PASS, ≥ 3 labs with the same sign.

## 11. Order of operations and exposure

1. Seal this file.
2. Write and seal the extraction script.
   - It reads only filenames and the EDF signal, and never the `Experience` column.
   - Its output, `features_confirmation.csv`, is keyed by DREAM `Key ID`, is hashed on completion and is not joined to labels.
3. Discovery extraction, the Study 3 fit, then seal `study3_model.json`.
4. Run PC1, PC2, P1 and P2 and record them; fix any measure faults by sealed amendment.
5. Write and seal the analysis script. Its first action checks the hashes of this file, the features file and the Study 3 model.
6. One unblinding run. The results are recorded whatever they are. Red-team, then atlas and ledger.

**Exposure declaration.**
- The analyst has read Siclari 2017, Wong 2025 and Aamodt 2023, and their reported effects.
- In task #31 the analyst computed delta, exponent and OFF-period features with labels on Tononi N2 (discovery lab).
- The analyst has read the per-awakening metadata of all labs, including class counts per subject (audit).
- No EEG sample of sets 9, 3, 16, 17 or 18 has been read. Only zip directories and the EDF headers of one file per set have been read.

## 12. Power

From `power_sim.json` (audit), N2, 397 awakenings / 47 subjects (that run keyed Aamodt by set; the realised P2 will use the final key):
- power at AUC 0.59 is 94% at α 0.05 and 59% at the Holm-worst α 0.05/28;
- with Holm over 8 the worst α is 0.00625, and power at AUC 0.60 is about 80%.

With a naive SE of about 0.03 the [0.40, 0.60] bound looks reachable. The within-lab subject bootstrap will likely be wider (§7 P2), so the dissociation outcome is less likely than the plan assumed. The realised power will be recomputed in P2 on the post-exclusion counts.

## Changes before sealing

An independent read-only review (a fresh agent, 2026-11-19) found these, and they were fixed before sealing:
- the Tononi metadata is triplicated;
- the Aamodt subject key was undefined;
- the meaning of a pooled AUC was ambiguous;
- the 1-30 Hz rule broke leave-one-lab-out;
- the Freedman-Lane null could not be computed as written;
- the major-negative rule contradicted itself;
- the P2 rule was incoherent;
- the window's end point was unchecked;
- total correlation could never pass the gate;
- missing-data, unit, seed and bootstrap-stratification rules were missing;
- the Study 3 cross-validation was not nested, and its gate and ΔAUC were undefined.

## Appendix A: channel maps (from EDF headers; no signal read)

| Lab | EEG channels | Posterior ROI | 10-20 subset |
|---|---|---|---|
| Rome (9) | 28: Fp1 F3 F7 FC1 Fp2 F4 F8 FC2 FC5 C3 T7 CP1 FC6 C4 T8 CP2 CP5 P3 P7 O1(`01`) CP6 P4 P8 O2 Fz Cz Pz Oz | P3 P4 Pz P7 P8 O1 O2 Oz | Fp1 Fp2 F7 F3 Fz F4 F8 T7 C3 Cz C4 T8 P7 P3 Pz P4 P8 O1 O2 |
| LODE (3) | 7 bipolar: Fp1-O1 Fp1-O2 Fp1-F7 F8-F7 F7-O1 F8-O2 Fp1-F8 | Fp1-O1 Fp1-O2 F7-O1 F8-O2 | all 7 derivations |
| DATA1 (16) | 25: Fp1 Fp2 F7 F8 F3 F4 T3 T4 C3 C4 TP7 TP8 T5 T6 P3 P4 O1 O2 Fpz Fz Cz Pz Oz PO7 PO8 (E1, E2 = EOG; SM-M2, M1-M2 dropped) | P3 P4 Pz T5(P7) T6(P8) PO7 PO8 O1 O2 Oz | Fp1 Fp2 F7 F3 Fz F4 F8 T3 C3 Cz C4 T4 T5 P3 Pz P4 T6 O1 O2 |
| Aamodt (17, 18) | the `EEG *-Ref` channels (about 64; the full list is written into the extraction script from the header) | P1-P8, Pz, PO3, PO4, POz, PO7, PO8, O1, O2, Oz, Iz present in the header | standard 10-20 labels present in the header |
| Tononi (13) | EGI 257 (`Chan 1`-`Chan 256`; the reference is dropped) | nearest electrodes to the 10-20 positions P3 P4 Pz P7 P8 O1 O2 Oz from `HydroCelGSN256v10.sfp` | nearest electrodes to the 19 10-20 positions |
| Zhang & Wamsley (1) | the `*-REF` EEG channels (LOC, ROC and EMG dropped) | parietal and occipital 10-10 labels present | the 19 10-20 labels present |

