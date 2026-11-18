# Pre-registration: surrogate gate on Sleep-EDF (task #8)

Agent: mind-2   Task: #8   Date: 2026-11-18. Sealed before any measure was computed on real EEG.

## 1. Question
Does each candidate measure call phase-randomised, spectrum-matched surrogates of wake EEG "conscious"? If it does, its wake-vs-N3 separation can be produced by the power spectrum alone (AGENT_BRIEF rule 4).

Measures gated: LZ (`lz`), phase-normalised LZ (`pnlz`), 1-40 Hz spectral exponent (`slope`), log relative delta power (`bp_delta`), permutation entropy (`perm_entropy`). Definitions: `experiments/lz_slope/features.py` (sealed with this file).

Predictions (stated before looking): slope and bp_delta FAIL by construction (they are spectral; they are the baselines, not candidates). LZ FAILS (expected from Maschke et al., PMC12448740, unverified for sleep). pnLZ: no prediction.

## 2. Data
Sleep-EDF Expanded v1.0.0, sleep-cassette, PhysioNet (open, ODC-By). First available night per subject; all subjects. Ground truth: behaviour (sleep stage scored by R&K; W = awake, N3 = R&K stages 3+4). Up to 40 random epochs per stage per subject (W restricted to 30 min before sleep onset to 30 min after last sleep epoch), seed = subject number (`fetch.py`). Channels Fpz-Cz and Pz-Oz, 100 Hz.

Exclusion: epoch dropped if, after preprocessing, any EEG channel has peak-to-peak > 500 uV or SD < 1 uV. Subject included if >= 10 clean epochs in each of W, N3 and REM (same inclusion as task #4).

## 3. Preprocessing
Per 30-s epoch: linear detrend, 4th-order zero-phase Butterworth low-pass at 40 Hz. Measures averaged over the two channels.

## 4. Surrogates
One multichannel Fourier phase-randomised surrogate per epoch (same random phases on both channels, preserving each power spectrum and the cross-spectrum), RNG seed fixed per subject. pnLZ is recomputed on each surrogate with its own 10 inner surrogates.
Quality check: median absolute difference of log10 Welch PSD (1-40 Hz) between epoch and surrogate, reported.

## 5. Split
5-fold subject-held-out folds from `experiments/rules/evidence.py::subject_folds` (seed 0), `check_split` on every fold.

## 6. Statistic
For each measure and fold: fit a one-feature logistic regression on REAL W vs N3 epochs of training subjects (balanced class weights). Apply it to test subjects:
- G1 (primary, the gate): fraction of test-subject W-surrogate epochs classified as W ("conscious"), pooled over folds. Compared with the fraction for real W epochs (sensitivity) and real N3 epochs (false-positive rate).
- G2 (diagnostic): AUC of the measure for W-surrogates vs N3-surrogates, against AUC for real W vs N3 (subject-cluster bootstrap 95% CI, 1000 resamples). Spectral share = (AUC_surr - 0.5)/(AUC_real - 0.5).

## 7. Pass marks
- PASS: G1 surrogate-conscious rate <= 0.50 AND its subject-bootstrap 95% CI upper bound < real-W rate's lower bound.
- FAIL: G1 > 0.50. A measure that fails may still enter task #4 but is labelled "spectrum-carried" there.
- A measure whose surrogate-conscious rate is <= 0.5 because surrogates move it past N3 (rate below the real N3 rate) is reported as "passes, surrogate-sensitive"; note it.

## 8. Planted check (must pass first)
Synthetic data, 20 subjects x 40 epochs per class: "wake" = Gaussian noise passed through a nonlinear asymmetric map giving sawtooth-like waves (time-irreversible), with a flatter spectrum; "N3" = linear Gaussian process with a steeper spectrum plus 1 Hz waves. Expected: the spectral exponent FAILS the gate; time-reversal asymmetry (`time_asymmetry`, non-spectral by construction) PASSES. The gate code is valid only if both come out as expected. Surrogate PSD error must be < 0.05 log10 units (median).

## 9. Power
With ~70 subjects x 40 W epochs, a binomial rate's 95% CI half-width is under 0.02 ignoring clustering; with subject clustering we report the bootstrap CI. The gate is a decision per measure, not a significance test.

## Not in scope
IAAFT (amplitude-adjusted) surrogates, which also preserve the amplitude distribution; reported as a follow-up if any measure passes.

## Amendment 1 (2026-11-18, before any measure was computed on real EEG)
The PhysioNet HTML index used by `fetch.py` listed only 52 of the 78 cassette subjects (PSG names ending F0, G0 etc. were also missed by the E0 pattern). `fetch.py` now reads the file list from RECORDS with any letter before the 0 and finds each hypnogram by probing its S3 key. Nothing else changes. The amended `fetch.py` is re-sealed with this file.

## Amendment 2 (2026-11-18, before any outcome was looked at)
Some cassette files store 60-s data records instead of 30-s ones. `fetch.py` now slices each 30-s epoch out of its record instead of stopping. Nothing else changes. Re-sealed with `fetch.py`.

## Deviation 1 (2026-11-18, before any outcome was looked at)
The shared compute lock was held by other projects for over 4 hours, so the fetch of the remaining subjects could not run. The analysis uses the 59 subjects fetched in file order before the 60-s-record file stopped the first run. Subject selection depends only on file order, not on any outcome. The 19 unfetched subjects are a follow-up.
