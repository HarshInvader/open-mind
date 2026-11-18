# Pre-registration: does LZ add anything over the spectral exponent? Sleep-EDF (task #4, first dataset)

Agent: mind-2   Task: #4   Date: 2026-11-18. Sealed before any measure was computed on real EEG. Same data, preprocessing, exclusions and measure code as `docs/prereg/2026-11-18_surrogate_gate_sleepedf.md` (sections 2-3); `experiments/lz_slope/features.py` is sealed with it.

## 1. Hypotheses
Claim under test (Schartner et al. 2015 and later): LZ complexity tracks conscious state. Rival (Maschke et al., PMC12448740): LZ is largely the spectral exponent in disguise.

- H1: LZ adds out-of-subject AUC over the spectral exponent alone.
- H2: phase-normalised LZ (pnLZ) adds AUC over the spectral exponent alone.
- H3: LZ adds AUC over the full spectral baseline (exponent + 6 log relative band powers: delta 1-4, theta 4-8, alpha 8-12, sigma 12-15, beta 15-30, low gamma 30-40 Hz).
- H4: pnLZ adds AUC over the full spectral baseline.

Each in two contrasts: C1 W vs N3 (primary, behaviour agrees), C2 REM vs N3 (REM = unresponsive but usually dreaming; "conscious" side is REM). 8 tests, one family, Holm correction.

Descriptive (no test): single-measure AUCs for every measure in every contrast incl. C3 W vs REM; within-subject Spearman correlation of LZ and pnLZ with the exponent (median over subjects); an arousal classifier (log mean submental EMG envelope + log EOG variance) AUC.

## 2. Model and split
Logistic regression (L2, C=1, balanced classes), features standardised with training-fold mean/SD only; no per-subject normalisation. 5-fold subject-held-out CV (`experiments/rules/evidence.py::subject_folds`, seed 0, `check_split` per fold). Statistic: pooled out-of-fold AUC. Delta AUC = AUC(baseline + added) - AUC(baseline).

## 3. Null
Freedman-Lane within subject: regress the added measure on the baseline features within each subject, permute the residuals across that subject's epochs (all stages in the contrast), add back the fitted values, refit the CV. 1000 permutations. One-sided p = (1 + #{null dDelta >= observed}) / 1001.
CI: subject-cluster bootstrap (1000) of the out-of-fold predictions for AUC and delta AUC.

## 4. Pass marks
- "LZ adds" (positive) for a hypothesis/contrast: Holm-adjusted p < 0.05 AND delta AUC >= 0.01.
- Otherwise negative for that cell; reported with the smallest delta AUC detectable at 80% power (from the planted check) and goes in the negative atlas if all four hypotheses fail in C1.
- Surrogate gate results (task #8) are reported alongside: a measure that adds AUC but failed the gate is labelled "adds, but spectrum-carried".

## 5. Planted checks (must pass first; otherwise real results do not count)
P1 State recovery: on real W epochs of the included subjects, plant a "deep sleep" copy by adding 0.5-2 Hz band-limited noise with RMS = k x the epoch's own RMS (k = 0, 0.5, 1, 2). The exponent must separate planted from original copies with subject-held-out AUC rising monotonically with k, near 0.5 at k = 0 (|AUC-0.5| < 0.05) and > 0.8 at k = 2.
P2 Calibration and power of the delta-AUC test, on the real C1 data: add a synthetic feature Z = d x (label - 0.5) x 2 + e, e ~ N(0,1) independent of everything, for d in {0, 0.1, 0.2, 0.3, 0.5}; 20 repeats each, 200 permutations each. Pass: false-positive rate at d = 0 <= 0.15 (3/20) at alpha 0.05. Report the mean delta AUC at the smallest d with power >= 0.8 as the detectable effect.

## 6. What would change the conclusion
Different datasets (propofol: ds005620, Chennu) may differ; this is one family (sleep), one lab, two frontal/parietal bipolar channels. Not a transfer test.

## Amendment 1 (2026-11-18, before any measure was computed on real EEG)
Same as Amendment 1 of the surrogate-gate pre-registration: all 78 cassette subjects are fetched (the HTML index listed only 52).

## Deviation 1 (2026-11-18, before any outcome was looked at)
Same as Deviation 1 of the surrogate-gate pre-registration: 59 of 78 subjects fetched, selection by file order only.

## Amendment 2 (2026-11-18, after P1 failed, before any H1-H4 outcome was computed)
P1 failed its pass mark. The exponent's subject-held-out AUC for planted vs original wake epochs was 0.500, 0.561, 0.644 and 0.759 at k = 0, 0.5, 1 and 2: monotonic, but under 0.8 at k = 2. Diagnosis: a 0.5-2 Hz plant changes only the 1-2 Hz bins, 3 of the 79 points in the 1-40 Hz fit, so it is a weak test of an exponent fit. The failure stays on record in `planted1.json`.
P1b replaces it and uses the plan's own wording ("flatten the slope"). It plants a spectral tilt of known size into the same real wake epochs: amplitude x f^(-beta/2), RMS kept, beta in {0, 0.25, 0.5, 1} (beta = 1 is two-thirds of the observed W-to-N3 exponent gap of about 1.5). Pass mark, unchanged in form: |AUC - 0.5| < 0.05 at beta = 0, monotonic, and AUC > 0.8 at beta = 1. LZ AUCs are reported too. P1b streams the epochs again from S3 and stores nothing raw (`planted1b.py`). The main analysis now requires `planted1b.json` and `planted2.json` to pass.

## Note 3 (2026-11-18, after H1-H4 were computed)
`analyse.py main` finished all 8 sealed tests (1000 permutations each, logged in `main.log`). It then crashed in the descriptive block: the submental EMG feature is NaN in 152 epochs (negative mean envelope). `finish.py` reads the logged deltas and p-values, recomputes every observed delta (they matched to 1e-9) and adds the bootstrap CIs, Holm correction and descriptives. Epochs with NaN EMG are dropped from the arousal-classifier descriptive only. No test, pass mark or sample changed.
