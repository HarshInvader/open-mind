# Pre-registration: IIT posterior hot zone, dream vs no-dream within N2 (task #16, test T-IIT)

Agent: mind-3   Task: #16   Date: 2026-11-18. Sealed before any EEG signal from these awakenings was downloaded or computed. Only metadata (Records.csv, ExperimentalDescription.txt, one EDF header per set for channel labels) has been read. Shared pipeline with `2026-11-18_theory_gnwt_frontal_dream.md` (same data, same preprocessing; the two tests form one family of 2).

## 1. Prediction, in the theory's own terms
IIT locates the physical substrate of experience in a posterior cortical "hot zone" (Koch, Massimini, Boly & Tononi 2016, doi:10.1038/nrn.2016.22; IIT 4.0, Albantakis et al. 2023, doi:10.1371/journal.pcbi.1011465). The IIT group's own dream study (Siclari et al. 2017, doi:10.1038/nn.4545) reported that, within NREM sleep, awakenings with experience are preceded by LOWER low-frequency (1-4 Hz) power over posterior cortex than awakenings with no experience, and argued the posterior effect does not need prefrontal involvement.

Riskiest form a proponent should accept, tested on two labs that are NOT the Wisconsin lab where the effect was found:
- H1: in the 20 s before awakening from N2, posterior delta (1-4 Hz) power is lower before experience than before no experience.
- H2 (specificity, the part that separates IIT from frontal theories): the posterior effect is larger than the frontal effect.
- H3 (beyond spectrum): posterior delta adds subject-held-out discrimination over the global spectral exponent.

## 2. Data
- DREAM Zhang & Wamsley 2019 (Figshare 10.6084/m9.figshare.22226692, CC BY 4.0; Furman University lab). 58 EEG ch, 400 Hz, data filtered 0.3-35 Hz by the depositors. All awakenings with Last sleep stage = N2 (code 2) and Experience in {0, 2}. Metadata counts: 68 experience, 37 no experience, 28 subjects. Includes sleep-onset N2 awakenings; the stage label is used as given.
- DREAM DeGennaro_YoungAdults (Figshare 10.6084/m9.figshare.14899506, CC BY 4.0; Rome lab). 19 ch 10-20, 128 Hz, low-passed 30 Hz, mastoid-referenced. N2 awakenings only (20 experience, 15 no experience; one awakening per subject). Report = morning diary feeling of having dreamt; weaker than an immediate report; stated as a limitation.
- Ground truth: delayed report (R). Not used: LODE (no posterior-only derivation), Tononi serial awakenings (discovery lab), REM (35 Hz / 30 Hz filters remove the high-frequency REM effect; REM posterior delta reported as descriptive only).
- Exclusion: an awakening is dropped if fewer than 3 clean 4-s segments remain (section 3) or a required ROI channel is missing.

## 3. Preprocessing (`experiments/theory_tests/dream_features.py`)
1. Window: the 20 s ending 2 s before the end of the file ([-22 s, -2 s]); the file end is the awakening per DREAM's format.
2. Reference: Zhang re-referenced to the mean of A1 and A2; YoungAdults kept as deposited (averaged mastoids).
3. Low-pass 30 Hz (zero-phase FIR, MNE default), resample to 100 Hz, linear detrend per channel.
4. Split into five 4-s segments; drop a segment if any used channel has peak-to-peak > 500 uV or SD < 0.5 uV.
5. PSD: Welch, 2-s Hann windows, 50% overlap, per segment, averaged over clean segments.

## 4. Measures
- ROIs (channels present in both sets): posterior = P3, Pz, P4, O1, O2; frontal = F3, Fz, F4.
- Delta power D_roi = mean over ROI channels of log10(sum of PSD 1-4 Hz). z-scored within dataset (removes amplifier scale; no label information used).
- Spectral exponent baseline: OLS slope of log10 PSD vs log10 f over 1-30 Hz (not 1-40 Hz: both sets are low-passed at 30-35 Hz), averaged over all 17 shared scalp channels (Fp1, Fp2, F7, F3, Fz, F4, F8, C3, Cz, C4, P3, Pz, P4, O1, O2, T7/T3, T8/T4), z-scored within dataset.
- Score for H1: s = -D_post (higher = predicted experience).

## 5. Statistics and split
- H1: pooled AUC of s for experience (1) vs no experience (0), both datasets together. Null: 5000 label permutations within dataset; one-sided p. CI: subject-cluster bootstrap (2000), stratified by dataset.
- H2: dAUC = AUC(-D_post) - AUC(-D_front); subject-cluster bootstrap 95% CI.
- H3: logistic regression (L2, C=1, class_weight balanced), 5-fold subject-held-out CV built with `evidence.subject_folds` (mode within, seed 0) and `check_split` on every fold. Model A: exponent. Model B: exponent + D_post. Statistic: out-of-fold AUC(B) - AUC(A), subject-cluster bootstrap 95% CI. Also lab transfer (descriptive): train on one dataset, test on the other, `check_split(mode="transfer")`.
- Surrogate control: delta power is fully determined by the power spectrum, so phase-randomised surrogates give identical values by construction; this is reported, and H3 (exponent control) is the beyond-spectrum test for this measure.
- Multiple tests: family = {T-IIT H1, T-GNWT H1}; alpha 0.025 each (Bonferroni).

## 6. Pass marks
- PASSED this test: H1 p < 0.025 AND H2 95% CI lower bound > 0 AND H3 95% CI lower bound > 0.
- FAILED this test: anything else. Sub-verdicts are reported: "no posterior effect" (H1 fails), "posterior effect but not posterior-specific" (H1 holds, H2 fails), "not beyond spectral exponent" (H1, H2 hold, H3 fails). If the H1 AUC 95% CI lies wholly below 0.5, it is reported as an effect in the opposite direction.

## 7. Planted check (must pass before the real labels are used)
On the real downloaded N2 awakenings with labels replaced by random labels (same counts per dataset), multiply the 1-4 Hz band of the posterior ROI channels of the "experience" cases by amplitude factor a (a = 1.0, 0.85, 0.75; FFT-domain scaling before PSD), 200 repeats each, 1000 permutations. Pass: false-positive rate at a = 1.0 <= 0.05 (+ binomial slack, <= 0.09), and power >= 0.8 at a = 0.75. Report the power at each a and the AUC it corresponds to.

## 8. Power
With about 88 experience and 52 no experience awakenings, one-sided alpha 0.025, power 0.8: smallest detectable AUC is about 0.64 (normal approximation to the Mann-Whitney SE, 0.051). The planted check gives the empirical figure. Any negative is reported with this number.

## 9. Known risks
- Zhang & Wamsley 2019 (doi:10.1111/psyp.13368) analysed these same recordings. I have not read its results before sealing; I will report how our result relates afterwards.
- Sleep-onset N2 awakenings are close to N1; YoungAdults reports are morning diary reports. Both bias toward a null.
