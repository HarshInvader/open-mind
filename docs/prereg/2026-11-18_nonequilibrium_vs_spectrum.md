# Pre-registration: does non-equilibrium (time-irreversible) EEG dynamics track conscious state beyond the spectrum?

Agent: mind-ne (Open Mind thread). Written 2026-11-18, before any NE measure was computed on real EEG. Code sealed with this file: `experiments/nonequilibrium/{ne_measures,planted,extract,ne_analyse,fetch_sleepedf}.py`.

## Why this test

Every complexity measure we have tested so far (LZ, permutation entropy) is carried by the spectrum. It adds nothing over the exponent plus band powers, and it fails the phase-surrogate gate (`experiments/lz_slope`, `experiments/surrogate_gate`, `experiments/theory_tests`). A recent line of work proposes that conscious states are further from thermodynamic equilibrium, and measures this as the irreversibility (the "arrow of time") of brain signals:
- Berjaga-Buisan et al. 2026, Cell Reports, doi:10.1016/j.celrep.2026.117782 (opened, full text via PMC13506674). Fluctuation-dissipation violations come from a linear Ornstein-Uhlenbeck model fitted to zero-lag and time-lagged covariance. They are higher in wake than under propofol or xenon, and track PCI.
- Camassa et al. 2024, Sci Rep, doi:10.1038/s41598-024-74649-1 (opened, PMC11484927). Rat LFP; irreversibility is the distance between forward and reversed time-shifted correlation matrices. It is lowest in slow-wave sleep and deep anaesthesia.
- Nartallo-Kaluarachchi et al. 2025, PNAS, doi:10.1073/pnas.2408791122 (abstract opened). Multilevel irreversibility in MEG.
- Yao 2024, Phys Rev E, doi:10.1103/physreve.109.054104 (abstract opened). Permutation time irreversibility of sleep EEG depends on sleep stage.

Our observation (the reason for two variants): the published measures in the first two papers use only second-order statistics, meaning lagged covariances. For a stationary signal those are fixed by the cross-spectrum, so multichannel phase-randomised surrogates keep them. That form of irreversibility is real (linear systems can be out of equilibrium), but it is a cross-spectral property. Only higher-order time asymmetry is zero for every Gaussian process, and so truly beyond the spectrum.

## Hypotheses

- **H-NE-HO (our variant).** Higher-order time-reversal asymmetry (`tra_x`) is larger in the conscious-side state than the other state. It adds at least 0.01 AUC over the spectral baseline on held-out subjects, and it passes the surrogate gate.
- **H-NE-2 (published form, replication).** Second-order lagged-correlation irreversibility (`ne2`) is larger in the conscious-side state, with single-measure held-out AUC ≥ 0.70. Prediction, stated in advance from the mathematics and confirmed on synthetic data (P1c): it fails the phase-surrogate gate (share kept > 0.5), because it is cross-spectral. The open question is whether it adds over the auto-spectral baseline (exponent + band powers), which does not contain cross-channel phase.

## Data and contrasts (ground truth: behaviour, grade B, for all)

| Contrast | Dataset | Conscious side vs other | Epochs |
|---|---|---|---|
| SE_W_vs_N3 | Sleep-EDF Expanded cassette (PhysioNet, doi:10.13026/C2X676), Fpz-Cz + Pz-Oz, 100 Hz | W vs N3 | 30 s; same seeded selection as task #4 (`fetch_sleepedf.py` is a copy of `lz_slope/fetch.py`), up to 40 per stage per subject |
| SE_REM_vs_N3 | same | REM vs N3 | same |
| CH_L1_vs_L3 | Chennu et al. 2016 propofol (doi:10.17863/CAM.68959), 91 ch, 250 to 100 Hz | baseline vs moderate sedation | first 120 s, 12 × 10 s |
| DS_awake_vs_sed2 | OpenNeuro ds005620 v1.0.0 (Oslo propofol), 65 ch, 5 kHz to 100 Hz | awake eyes closed (130-170 s) vs last 40 s of the first available `sed2` run (RASS -4) | 4 × 10 s each |

Labels are behaviour and drug state, not report. Moderate Chennu sedation leaves most subjects responsive. In ds005620, 24 of 29 informative awakenings from this sedation level reported experience (`docs/DATASETS.md`). So the propofol contrasts are "drug/arousal" contrasts. A measure that does not separate ds005620 sedation from wake is not thereby wrong about consciousness; this is reported, not scored.

Exposure: Sleep-EDF and Chennu were used before for LZ, slope and band powers, but no irreversibility measure has been computed on them. ds005620 has not been opened by any agent.

Preprocessing: linear detrend, then a 4th-order zero-phase Butterworth low-pass at 40 Hz (`features.preprocess`). Chennu and ds005620 are average-referenced and resampled to 100 Hz with an anti-aliased FFT resampler (MNE). An epoch is clean if every channel has peak-to-peak ≤ 500 µV and SD ≥ 0.5 µV. Inclusion: a subject enters a contrast with at least 10 (Sleep-EDF), 4 (Chennu) or 2 (ds005620) clean epochs in each class.

## Measures (`ne_measures.py`)

- `tra`: |E[Δ³]| / E[Δ²]^1.5 of increments Δ = x[t+τ] − x[t], at τ = 10, 20, 40 and 80 ms, averaged over lags and channels.
- `tra_x` (primary): `tra` minus its mean over 5 multichannel phase-randomised surrogates of the same epoch. This removes a finite-sample bias that depends on the spectrum.
- `ptir_x` (secondary): permutation time irreversibility (order 3), minus its surrogate mean.
- `tra_xi` (secondary): `tra` minus `tra` of one per-channel IAAFT surrogate.
- `ne2` (primary): mean over channel pairs of (C_ij(τ) − C_ji(τ))², averaged over the same lags. Sleep-EDF has only one pair.
- Reference measures: LZ, spectral exponent (1-40 Hz), permutation entropy and 6 relative band powers, all from `experiments/lz_slope/features.py`.

## Tests (`ne_analyse.py main`)

Per contrast: logistic regression with 5-fold subject-held-out CV (`check_split` on every fold). ΔAUC = AUC(spectral baseline + measure) − AUC(spectral baseline), where the baseline is the exponent plus 6 band powers. Null: 1000 within-subject Freedman-Lane permutations. CI: 1000-resample subject bootstrap. Holm correction over the 8 primary tests (`tra_x`, `ne2` × 4 contrasts). Secondary measures are reported uncorrected.

Gate: the single-measure classifier is fit on real epochs and applied to one phase surrogate per epoch. "Share kept" = (AUC on surrogates − 0.5) / (AUC real − 0.5). PASS if ≤ 0.5.

A cell counts for H-NE-HO if all three hold: Holm p < 0.05 with ΔAUC ≥ 0.01; the conscious-side class has the higher mean; and the gate passes.

**Decision rule for H-NE-HO:**
- SUPPORTED if at least 3 of 4 contrasts count, including at least one sleep and one propofol contrast.
- NOT SUPPORTED if none count.
- PARTIAL otherwise.

**H-NE-2:** "replicates" per contrast if CV AUC ≥ 0.70 in the predicted direction. "Adds beyond spectrum" per contrast if Holm p < 0.05 with ΔAUC ≥ 0.01. The gate result is reported against the stated prediction (fail).

Secondary for Sleep-EDF: `tra_x` over the spectral baseline plus arousal (log EMG, log EOG variance).

## Planted checks (must pass before real results count)

- **P1 (synthetic, `planted.py`).** Pass marks were set after one synthetic pilot, before any real data. The pilot showed that raw |skew| statistics have a spectrum-dependent bias of 0.03 to 0.07, and that a strictly periodic sawtooth gives non-Gaussian phase surrogates. So the primary measures became excess over surrogates, and the plant uses a sawtooth with a wandering frequency. The marks:
  - **P1a:** Gaussian alpha AR(2), |tra_x| and |ptir_x| < 0.01.
  - **P1b:** planted asymmetric alpha at k = 0, 0.25, 0.5 and 1. `tra_x` rises monotonically, is below 0.01 in magnitude at k = 0 and above 0.05 at k = 1, and the phase surrogate of the k = 1 signal has |tra_x| < 0.01.
  - **P1c:** one-way lagged Gaussian VAR. `ne2` is at least 5× the symmetric value, the surrogate keeps `ne2` within 25%, and |tra_x| < 0.01.
  - The pilot after the revision passed (`planted.json`).
- **P2 (`ne_analyse.py power`, run on real labels and the spectral baseline only, never on the NE measures).** A synthetic feature with effect d ∈ {0, 0.2, 0.4} is added in each contrast: 10 repeats, 200 permutations. It must give a false-positive rate ≤ 0.2 at d = 0. It reports the ΔAUC detectable at 80% power. The NE results count only if P2 passes.

## What would change the plan

- If ds005620 files are unreadable for a subject, that subject is skipped and listed.
- If fewer than 5 subjects qualify in a contrast, the contrast is dropped and reported.
- Any further change is written as a dated amendment and hashed before the affected outcomes are computed.

## Known weaknesses, stated in advance

- Time asymmetry at the scalp also reflects waveform shape: arc-shaped mu and alpha, spindles, K-complexes, sawtooth slow waves, eye movements and muscle. A positive `tra_x` result means "non-Gaussian, time-asymmetric structure beyond the spectrum separates the states", which is a necessary signature of non-equilibrium dynamics, not proof of it.
- Sleep-EDF has two bipolar channels, so `ne2` there is a single pair.
- Ground truth is behavioural.

## Amendment 1 (2026-11-18, before any ds005620 or Chennu outcome was analysed)

Sleep-EDF features were extracted; ds005620 extraction stopped at sub-1024 `sed2`, whose header lists 64 channels instead of 65. `extract.py` now reads the channel count from each header, and average-references over the channels present. Any file that still fails the format checks is skipped and listed, as the plan already said. No analysis (`ne_analyse.py`) had been run on any dataset. Nothing else changed.

## Amendment 2 (2026-11-19, after a crash part-way through `ne_analyse.py main`)

Extraction finished: ds005620 gave 20 subjects (160 clean real epochs); Chennu gave 480 clean real epochs. P2 passed its false-positive check (`planted2.json`), but it showed the propofol contrasts have low power: a planted effect of d = 0.4 reached 10% power in Chennu and 0% in ds005620, against ≥ 80% in both sleep contrasts. This was recorded before any NE outcome was seen.

`main` then crashed in the gate for the secondary measure `tra_xi`. `extract.py` writes `tra_xi` only on real rows, so surrogate rows held NaN. Before the crash, the log printed SE_W_vs_N3 results for `tra_x`, `ne2` and `ptir_x`. Disclosed here: I saw those three lines before writing this fix. The fix only makes `gate()` drop surrogate rows where the measure is missing. If none are left, it reports "not computed" for that measure (here, `tra_xi`). No measure, test, threshold, contrast or decision rule changed. Seeds are unchanged, so the rerun reproduces the printed lines exactly.
