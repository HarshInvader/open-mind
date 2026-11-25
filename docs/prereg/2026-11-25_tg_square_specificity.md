# Pre-registration: is a temporal-generalisation "square" specific to a sustained code? (simulation)

Agent: Open Mind thread   Date: 2026-11-25   Script: `experiments/tg_square_specificity/tg_square.py`   Source: Fable round 16, item 2

- **Zero data.** Simulation only.
- **Why now:** a 2026 preprint uses the TG square as a no-report marker of conscious access, and dismisses the main alternative without a test.

## 0. The claim and prior art (read first; library entries added 2026-11-25)

- **Hutchinson, Dehaene, Slagter & Pitts 2026** (bioRxiv, doi:10.64898/2026.01.30.702733) reanalysed four no-report EEG datasets.
  - **Finding:** seen stimuli gave a TG "square" at about 200–400 ms without a P3b.
  - **Their reading:** "A 'square' pattern of temporal generalization thus indicates that a single neural code is sustained and stabilised over time".
  - **Jitter:** they raise the alternative that "temporal generalization here reflects variability in the latency of evoked responses", then answer "We ultimately find this interpretation unlikely". There is no simulation or number behind that answer.
  - **Square criterion:** none. Square versus diagonal is judged by eye, and they ask for "a quantitative metric".
  - **Pipeline:** online 0.1 Hz high-pass (three datasets), baseline −100 to 0 ms, 250 Hz.
- **Already established, so not re-tested here:**
  - Onset jitter smooths the TG matrix (King & Dehaene 2014, TICS).
  - Growing onset variability across a chain of distinct codes looks like growing persistence (Vidaurre et al. 2019, Cereb Cortex). Their simulation is generic.
  - Volume conduction (Sandhaeger & Siegel 2023) and high-pass filtering with baseline correction (van Driel et al. 2021) create spurious cross-time generalisation.
- **The gap:** no one has tested whether non-sustained dynamics reproduce *this* footprint, at EEG scale, through *this* pipeline, under a square criterion fixed in advance. No one has proposed a test that tells the two apart in data that already exist.

## 1. Design

- **Simulated EEG:**
  - 64 channels mixing 24 latent sources (volume conduction), pink background noise plus white sensor noise.
  - 20 subjects per study, each with its own mixing; 150 seen and 150 unseen trials.
  - Signal is added to seen trials only.
  - Trial-to-trial amplitude variability (gamma, CV 0.5) is the same in every generator.
- **Generators (cells):**

| Cell | Ground truth | Role |
|---|---|---|
| SUS | One code, sustained 200–400 ms (20 ms ramps, onset SD 20 ms). This is the reading Hutchinson et al. give. | validity |
| SUS_j60 | The same, with onset SD 60 ms | CPL control: a sustained code with large jitter |
| NULL | No signal | false-positive rate of the square criterion |
| CH4_s{0,25,50,75} | A chain of four distinct brief codes (latent-orthogonal, 50 ms FWHM each, centred 215/265/315/365 ms) with a common latency jitter SD 0/25/50/75 ms. No code is sustained. | **primary** |
| J1_s{0,25,50,75} | One brief code (50 ms FWHM, centred 300 ms) with latency jitter SD 0/25/50/75 ms. This is their stated alternative. | descriptive |

- **Why J1 is descriptive only:**
  - A single jittered pattern gives a rank-1 TG matrix, so its SQ follows arithmetically from its envelope width.
  - The pre-seal reviewer's throwaway checks (see section 4) also showed J1's SQ values at guessed amplitudes.
  - CH4, where no code lasts longer than 50 ms, is the real test of "a single code sustained over time".
- **Pipeline, as theirs:**
  - causal first-order 0.1 Hz high-pass on a 5 s padded epoch;
  - baseline −100 to 0 ms;
  - 250 Hz, decimated to 125 Hz for TG;
  - per-time LDA with Ledoit-Wolf shrinkage, 5-fold stratified CV;
  - AUC on decision values.
- **Calibration:**
  - For each cell except NULL, the signal amplitude is set by bisection on log amplitude in [0.05, 100], up to 16 steps, with the same 4 calibration seeds at every step. The seeds are separate from the run.
  - Target: the group-mean **mean diagonal AUC over 200–400 ms** is 0.58 ± 0.004. The closest step is kept.
  - Cells are compared at equal decodability in the block, so a square cannot come from a stronger signal.
  - A mean over a fixed window is used instead of a peak, because a peak inflates more on a flat plateau.
- **Studies:** 40 per cell. Seed 20261203.

## 2. Measures (per study)

| Measure | Definition |
|---|---|
| SQ (square index) | mean(AUC − 0.5) over the 200–400 × 200–400 ms block ÷ mean(AUC − 0.5) on its diagonal. A perfect square gives 1; a pure diagonal of orthogonal codes gives about 0. NaN if the diagonal mean ≤ 0. |
| SPAN | Contiguous test-time span (ms) around the **300 ms** training time (the block centre) where the group one-sided t > t_crit (p < .05, df 19). It is 0 if the training time itself is not significant. |
| CPL (coupling, new) | For the decoder trained at 250 ms, the across-trial correlation between its decision values averaged over 230–270 ms and over 330–370 ms, Fisher z, seen minus unseen; group mean and t. A sustained code predicts CPL > 0: a trial strong early is strong late. A brief jittered code predicts CPL < 0: a trial with the code early lacks it late. CH4_s0 predicts CPL ≈ 0, because without jitter the 250 ms code never reaches 350 ms. |

- **"Square" for a study:** SQ ≥ 0.80 **and** SPAN ≥ 150 ms. Both thresholds are fixed. 150 ms is below the 200 ms code length because significance at the ramps is lost.

## 3. Decision

| Verdict | Condition (checked in this order) |
|---|---|
| INVALID | SUS, SUS_j60 or NULL not usable (uncalibrated, missing, or run-median level more than 0.01 off target); SUS "square" in < 80% of studies, or median SQ in SUS < 0.80; NULL "square" in > 10%; no usable CH4 cell with SD ≤ 50; or any run's median level more than 0.01 off target. |
| SQUARE NOT SPECIFIC (jitter ≤ 50 ms) | Some usable CH4 cell with SD ≤ 50 ms is "square" in ≥ 50% of studies. |
| SQUARE NOT SPECIFIC ONLY AT LARGE JITTER (75 ms) | Only CH4_s75 meets that bar. |
| SQUARE SPECIFIC IN THIS MODEL | Otherwise. A chain of brief codes does not produce their square under their pipeline, and this idea is dead for the chain alternative. |

- **Secondary (only if some CH4 or J1 cell is "square" in ≥ 50% of studies):**
  - **Power gate first:** if SUS or SUS_j60 has CPL t > t_crit in < 80% of studies, the result is **CPL UNINFORMATIVE**.
  - **COUPLING SEPARATES:** every "square" cell has CPL t < −t_crit in ≥ 80% of studies. This means a test exists that can be run on existing epochs.
  - **COUPLING DOES NOT SEPARATE:** otherwise.
- **Reported in every case:**
  - per cell: median SQ, SPAN and CPL, the shares, calibrated amplitudes, and run-median levels;
  - the descriptive J1 rows;
  - per-study values (kept in the output files).

## 4. Calibration fallbacks and disclosures (stated in advance)

- **UNCALIBRATED:** a cell whose calibration misses ± 0.004 is marked UNCALIBRATED and not run. If that cell is SUS, SUS_j60, or every CH4 cell with SD ≤ 50, the result is INVALID (section 3). Otherwise it is reported and excluded. There is no re-tuning.
- **Resume:** finished cells and calibrations are kept, with the same seeds.
- **The author's pilot** printed runtime and finiteness only, with 2 subjects.
- **Disclosure:** the pre-seal reviewer ran throwaway checks at guessed amplitudes on the first draft (seeds 901, 911–915; peak-AUC matching, 200 ms SPAN anchor, single-time CPL). They saw:
  - SUS SQ 0.94–0.96, with SPAN 0 at the 200 ms anchor;
  - J1_s50 SQ 0.82 and J1_s75 SQ 0.90–0.97;
  - SUS single-time CPL t of −0.1 to 1.3;
  - J1_s50/75 CPL t about −5, and CH4_s75 CPL t about −2.
  - No CH4 SQ or SPAN was observed.
  - The changes made after review are: J1 moved to descriptive, the SPAN anchor moved to 300 ms, window-averaged CPL with a power gate, mean-diagonal calibration, and the SUS_j60 and NULL cells. Fixed thresholds (SQ 0.80, SPAN 150 ms) replace the SUS-percentile rule. They were chosen to fix the reviewer's blockers, not by looking at CH4.
- Any other change after sealing makes the run INVALID.

## 5. What a result would and would not mean

- **SQUARE NOT SPECIFIC:**
  - **Means:** the square alone cannot separate a sustained code from latency-jittered brief codes under their pipeline.
  - **Does not mean:** that their data come from jitter.
  - **Next step:** CPL on real seen and unseen epochs. Our on-disk Cohen SOA-50 report epochs are a zero-byte candidate, which would need its own prereg.
- **SQUARE SPECIFIC IN THIS MODEL:**
  - **Means:** at matched decodability, their dismissal survives the alternatives they named.

## 6. Limits

- **No real head model:** volume conduction comes from a random mixing matrix, not a lead field, because fsaverage would be a new download. Codes are orthogonal in latent space and correlated at the sensors.
- **Jitter realism:** the jitter grid is not tied to a published single-trial latency distribution for these datasets. The verdict names the SD at which a square appears, so readers can judge.
- **Signal model:** seen vs unseen as signal vs no signal. Real unseen trials can carry weaker versions of the same codes.
- **CPL depends on amplitude variability:** with CV 0 a sustained code gives no positive coupling. The CV is fixed at 0.5 for every cell, and the power gate catches the case where it is too weak.
- **One target decodability** (mean diagonal AUC 0.58 over 200–400 ms). Their per-dataset AUCs are not tabulated in the text we read.
- **Orthogonal codes are the hardest case for a square:** LDA whitening largely undoes the random mixing, so CH4's codes are near-orthogonal to the decoder. Codes that share part of their pattern would add a genuinely stable component, so they are not modelled.
- **Not run here:** the filter and baseline ablation (van Driel 2021) and a no-low-pass check.
- **Neutrality:** results are properties of the method under simulation, not claims about their data.
