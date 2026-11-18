# Pre-registration: entropic brain, signal entropy under propofol beyond the spectrum (task #16, test T-ENT)

Agent: mind-3   Task: #16   Date: 2026-11-18. Sealed before any EEG from this dataset was downloaded. Only `datainfo.mat` (file name, sedation level, propofol ng/ml, mean RT, hits/40) has been read.

## 1. Prediction, in the theory's own terms
The entropic brain hypothesis states that the richness of conscious states is indexed by the entropy (irregularity, information content) of spontaneous brain activity, with anaesthesia and deep sleep at the low end and psychedelic states at the high end (Carhart-Harris et al. 2014, doi:10.3389/fnhum.2014.00020; Carhart-Harris 2018, doi:10.1016/j.neuropharm.2018.03.010). The proponents' own measure family is Lempel-Ziv complexity. The rival account (project brief, Maschke 2025) is that LZ under drugs reflects the power spectrum. The riskiest form a proponent should accept is that the entropy drop survives control for the spectrum.

- H1: LZ complexity is lower at moderate propofol sedation than at baseline (within subject).
- H2 (riskiest, primary): phase-normalised LZ (pnLZ = LZ / mean LZ of 10 multichannel phase-randomised surrogates of the same epoch, preserving each channel's spectrum and the cross-spectrum) is lower at moderate sedation than at baseline.
- H3 (descriptive, held-out): subject-held-out AUC of exponent alone vs exponent + LZ for baseline vs moderate.
- H4 (secondary, behaviour): across subjects at moderate sedation, LZ change (moderate minus baseline) correlates positively with change in hits (Spearman, one-sided).

## 2. Data
Chennu et al. 2016 propofol resting EEG (Cambridge, doi:10.17863/CAM.68959; paper doi:10.1371/journal.pcbi.1004669), CC BY 2.0 UK. 20 subjects; level 1 (baseline, 0 ng/ml) and level 3 (moderate) files per `datainfo.mat`. Ground truth: behaviour (drug level; hits). Moderate sedation is not loss of consciousness for most subjects, so the contrast is "less vs more sedated", which is the gradient the theory addresses.
Only the first 120 s (12 x 10-s epochs) of each recording are fetched (partial deflate stream of the `.fdt` member by HTTP range request); channel labels from one `.set`. Exclusion: a recording with fewer than 6 clean epochs; then the subject is dropped from paired tests.

## 3. Preprocessing (`experiments/theory_tests/chennu_features.py`)
Average reference over all channels; low-pass 40 Hz and resample 250 -> 100 Hz (MNE resample); then `experiments/lz_slope/features.py::preprocess` (detrend + 40 Hz Butterworth). Epoch = 10 s. Drop an epoch if any channel peak-to-peak > 500 uV. All channels in the recording are used (91 per the dataset description).

## 4. Measures
From `experiments/lz_slope/features.py` (unchanged): `lz`, `pnlz` (k = 10 surrogates, rng seed 0), `spectral_exponent` (1-40 Hz), `perm_entropy` (descriptive). Per recording: median over clean epochs.

## 5. Statistics
- H1, H2: one-sided Wilcoxon signed-rank (moderate < baseline), n = included subjects; effect size = median paired difference and rank-biserial r; bootstrap 95% CI of the median difference (2000 resamples of subjects). Also an exact sign-flip permutation p (all 2^n or 10000).
- H3: logistic regression, 5-fold subject-held-out CV (`evidence.subject_folds`, `check_split` per fold), out-of-fold AUC; dAUC with subject-cluster bootstrap CI.
- Surrogate gate: LZ is also computed on one phase-randomised surrogate per epoch; we report whether the baseline vs moderate difference in LZ is reproduced by surrogates (if yes, LZ's effect is spectral; H2 is the formal test).
- Family for this prereg: {H1, H2}; H2 is primary, alpha 0.05 one-sided; H1 reported at alpha 0.05.

## 6. Pass marks
- PASSED this test: H2 p < 0.05 (one-sided) AND median pnLZ difference < 0.
- FAILED this test: H2 not met. Sub-verdicts: "LZ falls but only through the spectrum" (H1 passes, H2 fails); "no entropy drop" (H1 fails). If pnLZ rises significantly (two-sided p < 0.05 in the other direction), reported as opposite direction.

## 7. Planted checks (before real contrasts)
P1 (sensitivity to non-spectral structure): on the real baseline recordings only, compare each epoch with its own phase-randomised surrogate: pnLZ must differ (paired Wilcoxon p < 0.05) while the exponent difference is ~0 (|median| < 0.02). Shows pnLZ can see structure that the spectrum cannot.
P2 (null): baseline epochs 1-6 vs 7-12 of the same recording: H2 test must give p > 0.05.
If P1 fails, H2 cannot detect a non-spectral change and the test is reported as uninformative, not as a fail.

## 8. Power
Paired one-sided Wilcoxon, n = 20, alpha 0.05, power 0.8: smallest detectable standardised paired effect d_z about 0.58.
