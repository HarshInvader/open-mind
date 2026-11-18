# Surrogate gate on Sleep-EDF (task #8)

**Verdict: every measure that tells wake from N3 fails the gate. Lempel-Ziv complexity behaves like the spectrum. Phase-randomised surrogates of wake EEG keep their spectrum but lose all nonlinear structure, and LZ calls 86% of them "awake" (real wake: 89%). Its wake-vs-N3 AUC is 0.967 on surrogates against 0.982 on real data, so 97% of its separation survives when only the spectrum is kept. Phase-normalised LZ is the only measure that passes, and only because it carries no wake-vs-N3 information at all (AUC 0.51).** So on this dataset no complexity measure has yet shown information beyond the spectrum.

Pre-registration: `docs/prereg/2026-11-18_surrogate_gate_sleepedf.md` (sealed 2026-11-18T06:49Z, before any measure was computed on real EEG; two fetch amendments and one deviation, each sealed before outcomes; hashes in `docs/prereg/HASHES.txt`). Code: `gate.py`; measures in `experiments/lz_slope/features.py`.

## Data
Sleep-EDF Expanded (sleep-cassette, PhysioNet, DOI 10.13026/C2X676, ODC-BY). 59 of 78 subjects fetched (see Deviation). 45 met the inclusion rule (at least 10 clean epochs in each of W, N3 and REM). Used: 1800 W, 1670 N3 and 1779 REM real 30-s epochs, Fpz-Cz + Pz-Oz, 0.5-40 Hz. Ground truth: behaviour (R&K stage scoring). Surrogates: one multichannel Fourier phase-randomised surrogate per epoch. Median log10-PSD error between epoch and surrogate is 0.030.

## Planted check (passed first; `planted.json`)
Synthetic wake made of time-irreversible sawtooth alpha, and synthetic N3 that is linear with a steep spectrum. The spectral exponent failed the gate, as it must: surrogates called conscious 100%. Time-reversal asymmetry passed, as it must: surrogates called conscious 0.1%, real wake 99%. Surrogate PSD error was 0.029.

## Results (5-fold subject-held-out threshold on real W vs N3; 95% CIs from a 1000-resample subject bootstrap)

| Measure | Wake surrogates called "awake" | Real wake called "awake" | Real N3 called "awake" | AUC real (CI) | AUC on surrogates (CI) | Share of separation kept by surrogates | Gate |
|---|---|---|---|---|---|---|---|
| LZ | 0.857 [0.814, 0.897] | 0.894 [0.852, 0.930] | 0.029 | 0.982 [0.974, 0.989] | 0.967 [0.956, 0.977] | 0.97 | FAIL |
| Phase-normalised LZ | 0.191 [0.166, 0.217] | 0.392 [0.346, 0.441] | 0.454 | 0.514 [0.47, 0.56] | 0.495 | n/a (no signal) | PASS, but no information |
| Spectral exponent 1-40 Hz | 0.954 | 0.950 | 0.063 | 0.989 | 0.989 | 1.00 | FAIL (spectral by design) |
| Relative delta power | 0.846 | 0.841 | 0.016 | 0.974 | 0.974 | 1.00 | FAIL (spectral by design) |
| Permutation entropy | 0.912 | 0.908 | 0.083 | 0.971 | 0.958 | 0.97 | FAIL |

Mean values (real / surrogate): LZ is W 0.600 / 0.589 and N3 0.313 / 0.307. pnLZ is W 1.030, N3 1.019, REM 1.022, with surrogates at 1.000 in every stage.

## Reading
- The predictions sealed in advance held: the spectral measures fail by construction, and LZ fails. This matches the Maschke et al. claim (PMC12448740, as cited in the plan; I have not opened it, so treat it as unverified) that LZ's state signal is mostly spectral.
- pnLZ's pass is empty. Real epochs sit 2-3% above their own surrogates in every stage, so pnLZ does pick up some nonlinear structure, but that structure does not differ between wake and N3. A measure that passes the gate this way is not a candidate.
- What this does not show: that LZ adds nothing over the slope in a joint model. That is task #4.

## Not checked
- IAAFT (amplitude-matched) surrogates. FT surrogates make the signal Gaussian, which by itself can raise LZ.
- Only 2 bipolar channels, one lab, one family (sleep). Ages 25-101 are not controlled here (the comparison is within subject, and the threshold transfers across subjects).
- 19 subjects were not fetched. The compute lock was held by other projects for more than 4 hours. Selection was by file order only.
- Raw epochs were deleted after feature extraction. `experiments/lz_slope/features.jsonl` holds the features.

| Hypothesis | Prediction | Result |
|---|---|---|
| Slope and delta power fail the gate | fail | fail |
| LZ fails the gate | fail | fail (surrogates 0.86 vs real 0.89) |
| pnLZ | none | passes, but carries no W/N3 information |
| Permutation entropy | none | fail |
