# Pre-registration (DRAFT, not sealed): does a two-state win survive fair graded rivals on real EEG? (Cohen et al. 2024, report block)

Agent: Open Mind thread   Date: 2026-11-25   Builds on: `2026-11-24_bifurcation_specificity_audit.md` (NOT SPECIFIC) and `2026-11-25_bifurcation_extended_model_set.md` (simulation verdict pending)

> **Sealing gate.** This prereg is sealed only if the extended-model-set simulation returns **FIX WORKS**.
> - If it returns UNDECIDABLE, this file is closed with a note: the real-data test cannot decide between two states and a jittered graded threshold, so it is not run.
> - If it returns STILL NOT SPECIFIC or FAILS BOTH, it is closed the same way: the model set is not specific enough to read a real result.
>
> **Data gate.** It needs new bytes (section 5). Only SOA-50 epochs are on disk, and the method needs all six stimulus levels. The download budget is spent, so an owner decision is needed before any fetch.

## 0. Question

- Sergent et al. 2021 found that single-trial EEG at intermediate stimulus strengths is fit better by a two-state mixture (Model 3) than by graded models (0, 2B).
- Our simulations showed that this comparison also favours Model 3 when a graded brain has a jittery threshold or heavy-tailed noise.
- **Question:** on independent real data, does Model 3 still win once graded models that can express those features (J: jittered threshold; T: Student-t noise) are in the comparison?

## 1. Data and the mapping to Sergent's design

| Sergent 2021 (auditory, active session) | Here (Cohen et al. 2024, visual masking, report block) |
|---|---|
| 6 levels: no sound + 5 SNRs | 6 levels: mask only (code 150) + face at SOA 17 / 33 / 50 / 67 / 83 ms |
| Level 1 = no target: Model 3 has P(high) = 0 | Mask only = no target: same constraint |
| About 150 trials per level after rejection | Median 128–154 per level (min 115) in the 38 eligible subjects |
| 20 subjects | 38 subjects (eligible in `out/eligibility.csv`) |
| Blocks used for CV folds | Trials assigned to 20 pseudo-blocks in session order, 4 per fold (as in our port) |

- **Trials:** all report-block trials at each level, whatever the answer. Sergent modelled all trials, not only the reported ones. The existing SOA-50 epochs cover only trials with an answer (37 of 5,116 are missing); this is a stated deviation.
- **Preprocessing:** identical to the sealed fixed-SOA study (`cohen_killtest.py preprocess`): 30 Hz low-pass, linked mastoids, baseline −100 to 0 ms, the same artefact rejection and bad-channel rule.

## 2. Single-trial signal (their method, adapted)

- **Decoder, as in Sergent's `SoundConsciousEEG_MNE_GAT_SingleTrials.py` (read, not run):**
  - data decimated by 5 (500 → 100 Hz);
  - per time sample, StandardScaler then LogisticRegression (sklearn defaults) on the 59 scalp channels;
  - trained on level 0 (mask only) vs level 5 (SOA 83), with 10-fold StratifiedKFold;
  - y = `decision_function` at the same time sample as training (the diagonal of their generalisation matrix);
  - levels 0 and 5 are scored by the fold that held them out;
  - levels 1–4 are split into 10 parts by the same scheme, each scored by one fold's decoder, as in their code.
- **y** = decision value, averaged over a time window. Sergent used decimated, sliding 30 ms windows.
- **Primary window:** 300–500 ms after face onset. This is the P3b window used in all our Cohen studies, and it is the late "ignition" period where Sergent report bifurcation. It is a single window, matching the single-window simulation.
- **Secondary (descriptive):** consecutive 30 ms windows from 0 to 600 ms, with Model 3 pxp in the 3-model (theirs) and 5-model comparisons. There is no multi-window decision.
- **Second signal (descriptive):** the P3b ROI amplitude (channels 1/4/5/6/13/14/15, 300–500 ms) with no decoder, so that a result does not depend on decoder training.

## 3. Models and decision

- **Models:** 0, 2B and 3 (their code, ported in `audit.py`), plus J and T (`extended.py`). Fitting, inits, 5-fold block CV, the mean of summed test LLH and spm_BMS are unchanged from the sealed simulation code. Nothing is re-tuned.
- **Design-matched gate (before the real fit):** re-run the extended simulation at this design.
  - Design: 38 subjects, the real per-level trial counts, 100 studies per cell.
  - Cells: B_bifurcation, G_jitter_mid, G_jitter_hi, G_heavy, H_jitter_t, H_gain.
  - Signal size: the real max-level signal, in units of level-0 SD (median over subjects of (mean y at SOA 83 − mean y at mask only) / SD at mask only). This depends only on the stimulus, not on any report. It is the only real-data quantity read before the gate.
  - **Gate PASS:** recall ≥ 0.80 on B and every graded cell ≤ 0.10, the same rule as the sealed simulation. If the gate fails, the real fit is not run and the result is "the test is not specific at this design".
- **Verdict on the real data (primary window, decoder y):**

| Verdict | Condition |
|---|---|
| TWO-STATE SURVIVES | Model 3 pxp > 0.95 in the 5-model comparison |
| GRADED RIVAL WINS | J or T pxp > 0.95 |
| TWO-STATE LOST ITS EDGE | Model 3 pxp > 0.95 in their 3-model comparison but not in the 5-model comparison |
| UNRESOLVED | otherwise |

- **Reported descriptively:** subjects best fit per model, the median k·τ of J (step-likeness), and the 3-model result (a replication of their analysis on new data).

## 4. Calibration fallbacks (stated in advance)

- **None for the models, fitting, CV, windows or decision rule.** The gate in section 3 is the only check, and its outcome is final.
- **If the decoder fails** (cross-validated AUC for mask only vs SOA 83 below 0.60 in the primary window, median over subjects), the primary signal becomes the P3b ROI amplitude. This rule applies only to that case and is stated here in advance.
- Any other change after sealing makes the study INVALID.

## 5. Bytes (owner decision needed)

- **On disk:** SOA-50 report epochs (5,079 trials, 223,983,900 bytes, already counted in the spent 1.5 GB budget).
- **Needed for this study** (same range-read method as `fetch_epochs.py`: −0.1 to 0.6 s, 63 channels, 44,100 bytes per trial):

| Option | Content | Trials | Bytes |
|---|---|---|---|
| Full (recommended) | all report-block mask-only and SOA 17/33/67/83 trials, 38 eligible subjects | 25,425 | **1,121,242,500 (1.12 GB)** |
| Half | a random, label-free 64 per level per subject (and 64 of the on-disk SOA-50 trials) | 12,160 | 536,256,000 (0.54 GB) |

- The half option moves the design away from the simulated regime (150 per level). The design-matched gate in section 3 would cover it.

### Sergent's own data, as a later second dataset (for an owner decision)

- **Where:** the same OSF project (osf.io/aw3t5), stored on a linked Dropbox (CC BY 4.0).
- **Preprocessed:** 40 `.mat` files, 20 subjects × active/passive, **23,783,330,981 bytes (23.8 GB)** in total. Sizes were read with HEAD requests only; no data bytes were read.
- **By part (HEAD requests only):**

| Part | Bytes |
|---|---|
| Preprocessed, active sessions | 11,429,457,072 (11.4 GB) |
| Preprocessed, passive sessions | 12,353,872,126 |
| Raw BrainVision `.eeg`, active | 24,253,094,880 |
| Raw BrainVision `.eeg`, passive | 24,779,114,640 |
| Behaviour (active) | 1,701,514 |

- **Cheapest route:** range-read trial epochs from the raw active `.eeg` files, as we did for Cohen. That needs the small `.vhdr`/`.vmrk` headers first (well under 1 MB) to count the bytes exactly, and it would also need their preprocessing to be redone.
- **Simplest route:** the preprocessed `.mat` files cannot be range-read per trial, so the active sessions alone would be 11.4 GB.
- A run on Sergent's data would replicate their 3-model result exactly and then add J and T. It is the most direct test, and the most expensive one.

## 6. Limits

- **Modality:** visual masking with faces is not auditory detection in noise. Sergent's claim is general, so it should transfer, but a different result here would not refute their auditory finding directly.
- **Signal:** decision values from a mask vs SOA-83 decoder. At SOA 83 the second mask still arrives, so the "max" level is not unmasked.
- **Scope:** a pass means the two-state win survives these five models on one window. It does not prove discrete states.
- **Neutrality:** results are stated as properties of the data under these models, not as claims about Sergent's data.
