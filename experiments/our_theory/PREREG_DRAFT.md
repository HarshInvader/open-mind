# Pre-registration DRAFT: T1-P1 (and T2-P1 as H4), slow-wave recency and spacing before dream reports

Agent: mind-theory-builder   Task: #27 (draft only)   Date: 2026-11-18

**DRAFT. Not sealed. Do not run.** Sealing happens in the task "Seal and run the open-data prediction of the best candidate", after the blind ledger scoring. Whoever seals it must:
1. copy this file to `docs/prereg/<date>_our_theory_T1_slowwave_recency.md`;
2. write `p1_features.py` and `p1_analysis.py` in `experiments/our_theory/`;
3. seal all three with `.venv/bin/python -I experiments/rules/evidence.py seal ...` before downloading any EEG.

No EEG from these awakenings had been downloaded or computed by me when I wrote this. I read only metadata: `dream_records.csv`, the DREAM set tables, and the LODE and Zhang experimental descriptions.

Known exposure: mind-3 (task #16) sealed and may have run posterior and frontal delta-power tests on Zhang & Wamsley and YoungAdults N2 awakenings. Those outcomes concern band power, which is a baseline here, not the tested measure. The sealer must state in the sealed file whether those results were seen.

## 1. Hypotheses

Theory T1 (settling window, `T1.md`): the report after an awakening describes what posterior cortex held just before it. Presence depends on the final stretch being free of OFF-periods, not on total slow-wave activity.

- **H1 (recency).** The time since the last posterior slow wave (L_post) is longer before "experience" than before "no experience", controlling for Model A (section 4). Direction: positive coefficient.
- **H2 (spacing at fixed count).** The longest OFF-free gap compared with random placement of the same waves (G_z) is larger before "experience", controlling for Model A plus L_post. Direction: positive.
- **H3 (beyond baselines, held-out labs).** Model B (A + log L_post + G_z) beats Model A on out-of-fold AUC with labs held out.
- **H4 (T1 vs T2).**
  - T1 predicts that frontal recency adds nothing beyond Model B.
  - T2 (`T2.md`) predicts a positive coefficient and a gain.

  One analysis decides between them.

## 2. Data

Ground truth: delayed report (L2). The files are DREAM awakenings with "Last sleep stage" = N2 and Experience ∈ {"Experience", "No experience"}, as labelled in `experiments/dataset_audit/dream_records.csv`. Excluded: "Without recall", "No experience or without recall" and "Unknown".

| Lab (fold) | DREAM set | N2 exp / no-exp (metadata) | fs, channels | Download |
|---|---|---|---|---|
| Furman (Zhang & Wamsley 2019) | 1, doi:10.6084/m9.figshare.22226692 | 68 / 37 | 400 Hz, 58 ch, filtered 0.3-35 Hz by the depositors, unreferenced | N2 members only, by HTTP range (about 0.36 GB) |
| Rome (DeGennaro YoungAdults) | 11, doi:10.6084/m9.figshare.14899506 | 20 / 15 | 128 Hz, 19 ch, mastoid reference | about 0.06 GB |
| DATA1 | 16, doi:10.6084/m9.figshare.24058740.v1 | 24 / 25 | 2000 Hz, 25 ch | N2 members only (about 0.3 GB) |

- **Total:** 112 experience / 77 no experience, 3 labs. Combined new download is about 0.7 GB. Check `du -sh data experiments` first; the project cap is 1.5 GB. Delete raw EDFs once per-awakening features are saved.
- **Not used:**
  - LODE: its derivations are frontal-occipital bipolar (Fp1-O1 and so on), so posterior and frontal cannot be separated.
  - Tononi Serial Awakenings: the discovery lab of the posterior effect, and too large for the budget. It is the designated replication set when budget allows (see section 10).
  - REM: few slow waves, so L is nearly always the full window.
- **Channel rule (fixed before data).**
  - Posterior ROI = all present channels from {P3, Pz, P4, O1, O2, Oz, POz}. At least 3 are required, or the dataset is excluded and reported.
  - Frontal ROI = all present channels from {F3, Fz, F4}. At least 2 are required.
  - If DATA1 fails either rule, it is dropped and the test runs on 2 labs. Two labs reduce power; this is reported, and the pass marks are unchanged.
- **Reference.** Mean of the mastoids (A1/A2 or M1/M2) if both are present. Otherwise the average of all scalp EEG channels. YoungAdults stays as deposited.
- **Exclusion.**
  - The file is shorter than 34 s.
  - Or a required ROI has fewer channels than the rule requires after bad-channel removal. A channel is bad if its SD in the window is < 0.5 µV or > 200 µV.
  - Or more than 30% of the window is artefact (any ROI channel with |x| > 300 µV after filtering, ±0.5 s padding).

## 3. Preprocessing

1. **Window.** [-32 s, -2 s] relative to the end of the file. The file end is the awakening in DREAM's format.
2. **Filters and resampling.** Resample to 128 Hz after an anti-alias low-pass at 40 Hz. Band-pass 0.5-4 Hz (zero-phase FIR, MNE defaults) for slow-wave detection. A separate 1-30 Hz copy is used for spectra.
3. **ROI signal.** The mean across ROI channels (posterior and frontal separately).
4. **Slow-wave detection** (after Siclari 2018, doi:10.1523/jneurosci.0855-18.2018, and the half-wave method it cites):
   - Candidates are negative half-waves between consecutive zero crossings of the 0.5-4 Hz ROI signal, lasting 0.25-1.0 s.
   - Amplitude threshold T_d for each dataset and ROI = the median negative-peak amplitude of all candidates in all included awakenings of that dataset. This is label-blind.
   - A slow wave is a candidate whose negative peak is ≤ -T_d.
   - Artefact segments are skipped.

## 4. Measures and models

- **N_post.** Count of posterior slow waves in the 30 s window.
- **L_post.** Seconds from the end (upward zero crossing) of the last posterior slow wave to the window end. It is 30 if there are none. Analysed as log(L_post + 0.25).
- **G_z.**
  - Gaps = OFF-free intervals between slow waves, including both window edges. S = the longest gap.
  - Null: place the same N_post waves, with their own durations, uniformly at random without overlap in the window (1,000 draws, seed 0). G_z = (S − mean_null) / sd_null.
  - If N_post < 2, G_z = 0 and a flag is set. Flagged cases are reported.
- **L_front.** As L_post, for the frontal ROI.
- **Baselines.** All are z-scored within each dataset, which uses no label information.
  - EXP: OLS slope of log10 PSD vs log10 f over 1-30 Hz, averaged over all scalp channels. Welch, 4-s Hann windows, 50% overlap, over the 30 s.
  - D_post: log10 posterior 1-4 Hz power.
  - D_front: the same for the frontal ROI.
  - AR: log10 posterior 8-30 Hz power in the last 10 s of the window. This is the arousal baseline.
- **Models** (logistic regression, L2, C = 1, class_weight balanced, a dataset indicator in every model):
  - A = EXP + D_post + N_post + AR;
  - B = A + log L_post + G_z;
  - B+F = B + log L_front + D_front + N_front.

## 5. Statistics and split

- **H1 and H2: coefficient tests on pooled data.**
  - Fit B on all cases. The statistic is the standardised coefficient of log L_post (H1) and of G_z (H2).
  - Null: 5,000 permutations of labels within each dataset, refitting each time. One-sided p.
  - The 95% CI comes from a subject-cluster bootstrap (2,000), stratified by dataset.
- **H3.** Leave one lab out. Train A and B on two labs and predict the third. Pool the out-of-fold predictions.
  - Statistic: AUC(B) − AUC(A), with a subject-cluster bootstrap 95% CI.
  - `evidence.check_split(train, test, mode="transfer")` runs on every fold.
  - Also reported, descriptive only: 5-fold subject-held-out CV within labs (`evidence.subject_folds`, mode "within", seed 0).
- **H4.** As H3, comparing B+F with B. Also the pooled permutation test of the log L_front coefficient in B+F (one-sided, positive, for T2).
- **Multiple tests.** The family is {H1, H2, H4-coefficient}, at α = 0.025 each (one-sided, Bonferroni over the main pair plus H4 reported at the same α). H3 is a gate, not a family member.

## 6. Pass marks

**T1:**
- **PASS:** H1 p < 0.025, AND the H3 ΔAUC 95% CI lower bound > 0, AND the surrogate control in section 7 passes.
- **STRONG PASS:** PASS and H2 p < 0.025.
- **REFUTED:** if the planted check in section 8 shows power ≥ 0.8 at ΔAUC = 0.05, then either:
  - the H1 coefficient's 95% CI lies wholly ≤ 0; or
  - the H3 ΔAUC 95% CI upper bound is < 0.05.
- **INCONCLUSIVE:** anything else, including power < 0.8. It is logged with the detectable effect size.
- **T1 on H4:** T1 expects the H4 ΔAUC CI to include 0. T1 is weakened, not refuted, if H4 passes for T2.

**T2 (H4):**
- **PASS:** the log L_front coefficient has p < 0.025, AND the H4 ΔAUC 95% CI lower bound > 0.
- **REFUTED:** with power ≥ 0.8 at ΔAUC = 0.05, either the H4 ΔAUC CI upper bound is < 0.03, or the coefficient's CI lies wholly < 0.

**Reporting.** Each AUC is reported with its CI and the n per lab. Results by lab are reported even when the pooled result passes. A pass driven by one lab is flagged.

## 7. Surrogate gate

L and G_z depend on timing, so phase randomisation should destroy their added value.
- For each awakening, make 1 multichannel phase-randomised surrogate of the 30 s window (the same random phases on all channels; seed = awakening index).
- Recompute every feature and rerun H3 with surrogate features (Model B_s vs Model A_s).
- **Gate passes if** the real ΔAUC exceeds the surrogate ΔAUC (paired bootstrap on out-of-fold predictions, 95% CI of the difference > 0).

If the surrogate gain is as large as the real one, the effect is spectral and T1-P1 is reported as failed on the gate.

## 8. Planted checks (must pass before real labels are used)

1. **Detector recovery.** Into 20 real awakenings, add synthetic slow waves: a negative half-sine of 0.5 s, amplitude 1.5 × T_d, at random known times, 10 per window. Pass: at least 80% of inserted waves are detected within ±100 ms of the true trough. On average, at most 1 extra detection per window is allowed beyond the waves found in the same window before insertion.
2. **Effect recovery.** Using the real feature matrix (from data) and synthetic labels drawn from a logistic model:
   - true log-odds = β × z(log L_post) + the fitted Model-A predictor;
   - β is chosen to give ΔAUC = 0 and to give ΔAUC = 0.05;
   - 200 repeats each, with the full H1 and H3 pipeline.

   Pass: false-positive rate at ΔAUC = 0 is ≤ 0.05 (+ binomial slack, ≤ 0.09), and the reported power at 0.05.
3. **Real-label shuffle.** Run the whole pipeline once with labels permuted within dataset. H3 ΔAUC must be within ±0.05 of 0.

## 9. Power (rough, before data)

With 112 vs 77 cases, the SE of one AUC is about 0.04 (normal approximation to the Mann-Whitney SE). Correlated predictors make the ΔAUC SE smaller. The planted check gives the real figure. Effects below ΔAUC ≈ 0.05 are unlikely to be detectable; a null below that is reported as such and is not a refutation.

## 10. Known risks, stated before data

- **Scalp dilution.** OFF-periods are often local (C44), and scalp slow waves see only the large ones. This biases toward a null.
- **Recall confound.** Lighter sleep just before awakening may help recall, not experience (C15 shows the two dissociate). AR (8-30 Hz power) and G_z (spacing at fixed count) are the guards. A recency effect with no G_z effect and a large AR coefficient is reported as "consistent with a recall account".
- **Sleep-onset N2.** Zhang's set includes sleep-onset N2 awakenings, which are close to N1. Stage labels are used as given.
- **YoungAdults reports.** These come from a morning diary, a weaker report.
- **Replication.** If PASS, replicate on 6-8 Tononi Serial Awakenings subjects (chosen at random, seed 0, before download) as a fourth, held-out lab, within budget, under a new seal.

## 11. Outputs

The runner writes these to `experiments/our_theory/`:
- `p1_features.csv`: one row per awakening;
- `p1_results.json`;
- `ledger_rows.csv`;
- a RESULTS section in `RESULTS.md` with the verdict first.
