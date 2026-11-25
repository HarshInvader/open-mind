# Pre-registration: Sergent et al. 2021's own EEG under the 5-model set (round 18, item 2)

Agent: Open Mind thread   Date: 2026-11-25   Status: to be sealed before the design gate runs and before any EEG byte is fetched. The item-1 k·τ values are not part of the seal; they are passed to the gate on the command line once and then fixed (§6).

- **Design notes:** `experiments/sergent_eeg/DESIGN.md`. This file fixes what that one proposed and adds the replication-first readout, the puzzle tests and the fallbacks.
- **Code:** `experiments/sergent_eeg/sergent_gate.py` (gate), `stream_decode.py` (fetch and decode), `analyse.py` (fits and readouts). Everything they import from `experiments/bifurcation_specificity/` (`audit.py`, `extended.py`) is already sealed and is used unchanged.
- **Data:** Sergent et al. 2021 preprocessed active-session EEG, OSF aw3t5 (Dropbox provider), CC BY 4.0, files `S1…S20_Active_data_ref.mat`, about 11.4 GB in total. The coordinator approved the bytes on 2026-11-25.

## 0. State at sealing

- No EEG byte from this dataset has been fetched or read. On disk: their code, their `source_data.xlsx` (published figure values) and the Dropbox file listing (`dropbox_listing.json`, paths and links only).
- Already known from the published figures, and used here: the 3-model pxp per window (Fig 3E; Model 3 > 0.95 at 1-based windows 21, 23–28 and 32, starting at 300, 360–510 and 630 ms) and the per-sample diagonal AUC (Fig 2B, peak 0.731).
- Also on disk and read before sealing: their per-subject window AUC (Fig 3F, 20 subjects × 53 windows; the sheet does not say which conditions are compared). The group mean is 0.752–0.767 in the primary windows, peaking at 0.767 in window 25. In our generator, AUC 0.76 is about DMAX 1.0, where the sealed 3-model call rate for true two-state data was 28/100. So H1 alone may not close the gap. This is reported next to (a) as a description and changes no rule.
- Already known from our sealed simulations: at that AUC, the 5-model comparison almost never calls Model 3 for true two-state data (0/100), and the 3-model comparison calls it in 11–28/100. That gap is the **puzzle** that §5 tests.

## 1. Questions

1. **Replication (first readout):** does our port of their pipeline, run on their preprocessed data, reproduce their 3-model result (Model 3 pxp > 0.95 at 360–540 ms)?
2. **Main:** with a jittered-threshold graded model (J) and a Student-t graded model (T) added, does Model 3 still win in those windows?
3. **Puzzle:** why did the 3-model comparison call Model 3 so firmly on data whose per-sample AUC is only 0.73? There are three candidate explanations: (H1) the window signal is stronger than the per-sample AUC; (H2) a few subjects carry the random-effects call; (H3) the data have heavy tails or well-separated high states that our generator lacks.

## 2. Pipeline (ported from their code, read but never run)

- **Input:** `data_ref.trial`, the first 63 channels (their `coi = range(63)`), every sample at 500 Hz. `trialinfo` columns: block (1–20), snr code (1–6), vowel, eval, respside, audibility.
- **Decoder (their `SoundConsciousEEG_MNE_GAT_SingleTrials.py`, diagonal):**
  - At each sample: StandardScaler, then LogisticRegression (C = 1, L2), trained on snr 1 (no sound) against snr 6 (−5 dB).
  - **Solver:** their `LogisticRegression()` default depends on their sklearn version, which is unknown (it is below 0.24, because they pass `random_state` without shuffle, which errors from 0.24). **Primary: liblinear** (the default before 0.22). lbfgs (the default from 0.22) is also decoded and fitted in the primary windows. It appears in R1 as one descriptive line and never changes any readout.
  - CV is StratifiedKFold(10) without shuffle on the training trials. Trials at snr 2–5 are split into 10 contiguous chunks by the same splitter on a dummy label, and each chunk is scored by one fold's decoder.
  - The output is `decision_function`.
- **Window values (their `…ModelFitting_Twind30ms_batch.m`):**
  - A 12th-order Butterworth low-pass with half power at 10 Hz (`butter(12, 0.04)` has |H|² = 0.5 at 10 Hz), applied zero-phase (`sosfiltfilt`, padlen 36; theirs is `designfilt` + `filtfilt`).
  - Then the mean over `TWOI(i):TWOI(i+1)`, with `TWOI = 101:15:901` (1-based samples, both ends inclusive). That gives 53 windows. **1-based window j covers −330 + 30j to −300 + 30j ms** (16 samples). The code places windows by time, which equals TWOI on the standard −500 ms axis (checked).
- **Fits:** the sealed `audit.subject_lme` (models 0, 2B, 3) and `extended.subject_lme5` (0, 2B, 3, J, T). Inputs:
  - x = snr − 1;
  - 5-fold CV where fold f tests blocks 4f…4f+3 (0-based, = their 1-based 4(f−1)+1…4f);
  - the per-subject LME is the mean held-out log-likelihood over folds, as in theirs.
- **Kept per trial:** the decoder fold that scored it (for §5c).
- **Group:** `audit.spm_bms` (random-effects BMS, protected exceedance probability), seed 20261205 + window index (0-based; 3-model) and + 100 + window index (5-model).
- **Known differences from their run:** sklearn and scipy versions; `sosfiltfilt` against MATLAB `filtfilt` edge handling (edges are far from the primary windows); our fminsearch port. These are what the replication check tests.

## 3. Design gate (synthetic; runs first, before any fetch)

- **Command:** `python -I sergent_gate.py run [KT…]`.
- **Design:** 20 subjects; per-level counts 150 (18 subjects) and 157 (2), i.e. 168/176 × 150/168; 100 studies per cell; 4 workers; seed 20261203.
- **Cells:**
  - B_bifurcation (recall);
  - graded: G_jitter_mid, G_jitter_hi, G_heavy, H_jitter_t, H_gain;
  - item-1 cells `G_jitter_kt{v}` if item 1 yields values (§6).
- **Signal sizes:** deciding DMAX 0.89 (the published AUC 0.731); heterogeneity variant at 0.89 (DMAX_s = 0.89·exp(N(0, 0.35²) − 0.35²/2)); sensitivity B at 1.0 and 1.25.
- **Tiers, on the 5-model Model 3 call rate (pxp > 0.95), computed for two tags only: `d0.89` (pre-stream) and `meas` (re-run). Every graded and item-1 cell must be present, or the tier is undefined:**
  - **Tier 1:** B ≥ 0.80 and every graded cell (including item-1 cells) ≤ 0.10.
  - **Tier 2:** B < 0.80 and every graded cell ≤ 0.10. The 5-model reading is one-sided (§4).
  - **Tier 3:** any graded cell > 0.10.
- **Also recorded per cell:** the 3-model call rate on the same studies (the first three LME columns are exactly the 3-model fits), and the median over subjects of the level-5 bimodality coefficient after standardising within 10 pseudo-folds (for §5c). For `meas` and `meas_het` B: the greedy flip count (§5b) of every study whose 3-model comparison calls Model 3.
- **Non-finite LMEs in the gate:** handled as F4 for the real data. Up to 2 subjects are dropped; with more, the study counts as no call.
- **Seal check:** `run`, `rerun`, `stream_decode run`, `measure`, `fit` and `readout` all refuse unless this prereg and their own file are sealed (`require_sealed`).
- **Streaming rule:**
  - Tier 1 or 2 at DMAX 0.89: stream. `stream_decode run` checks the tier itself.
  - Tier 3 at 0.89: stream only for the replication check and the puzzle tests, and only with the coordinator's OK (`stream_decode run tier3-ok`). No 5-model verdict is given unless the re-run (next bullet) reaches tier 1 or 2.
- **Re-run after streaming (decides the tier for the verdict):**
  - Command: `python -I sergent_gate.py rerun`. The k·τ cells are the ones fixed at the first `run` (`out_gate/kt.json`); `run` refuses a different list.
  - Signal size: the measured DMAX, i.e. the median over subjects of the mean over primary windows of (mean level 5 − mean level 0) / SD level 0, in window units. Counts are each subject's real per-level counts.
  - `measure` runs once, and only after every subject has an ok or skip record and at least 18 are usable. It writes `out_real/measured.json`, which is then frozen; `fit` refuses to run before it exists. Every `meas` file is stamped with the DMAX, log-SD and counts it used, and `rerun` refuses stale files.
  - The log-SD is taken over subjects with DMAX > 0; the number excluded is reported.
  - Tag `meas`: the same graded and item-1 cells. Tag `meas_het`: B with the measured across-subject SD of log DMAX.
  - The `meas` tier is final, whatever the pre-stream tier was.

## 4. Readouts, in order

- **Primary windows:** 1-based 23–28 (360–540 ms), their longest Fig 3E run with Model 3 pxp > 0.95 (0.990–0.999). A window "calls" a model if that model's pxp > 0.95.

**R1. Replication (first).**
- PASS if the 3-model Model 3 pxp > 0.95 in at least 4 of the 6 primary windows.
- If it FAILS: the finding is "our port of their pipeline does not reproduce their 3-model result on their data". The 5-model pxp is reported descriptively, with no verdict, and the puzzle tests are still reported.
- The full 53-window 3-model pxp curve is reported next to their Fig 3E values.

**R2. 5-model verdict** (only if R1 passed and the `meas` tier is 1 or 2; at least 4 of 6 windows needed):

| Verdict | Rule |
|---|---|
| TWO-STATE SURVIVES fair graded rivals | Model 3 called in ≥ 4 primary windows |
| GRADED RIVAL WINS (tier 1 only) | J or T called in ≥ 4 primary windows (the two graded rivals are pooled: J in some windows and T in others counts) |
| TWO-STATE LOST ITS EDGE (tier 1 only) | Model 3 called in ≤ 2 primary windows, no graded-rival verdict |
| UNRESOLVED | anything else; under tier 2, everything except the first row |

- Under tier 2, UNRESOLVED is reported as "low power at this design". It is never read as evidence against two states.
- If the `meas` tier is undefined (files missing or incomplete) or 3, no 5-model verdict is given; each case has its own result string.
- **Usable subjects:** at least 60 trials at every level and no empty CV fold (F3). With fewer than 18 usable subjects the result is INVALID.

## 5. Puzzle tests (reported in every tier and whatever R1 says)

- **(a) Window signal against per-sample signal (H1).**
  - Per subject, compute:
    - the mean AUC (snr 6 against snr 1) over the unfiltered diagonal samples in 360–540 ms;
    - the mean AUC over the six primary-window values;
    - the measured DMAX (§3).
  - **H1 explains the puzzle if** the `meas` gate's B_bifurcation 3-model call rate is ≥ 0.80. That is, at the window-level signal size actually present, our generator makes their 3-model call routinely. This is a plausibility check: the gate rate is per window, while their run spans 6 correlated windows.
  - If that rate stays below 0.30, H1 does not explain it.
  - Between 0.30 and 0.80, it explains it in part.
- **(b) Few strong subjects (H2), per primary window on the 3-model LMEs:**
  - Leave-one-subject-out pxp (minimum, and how many single drops bring Model 3 to ≤ 0.95).
  - A greedy flip count: repeatedly drop the subject with the largest log-evidence advantage for Model 3 until Model 3 pxp ≤ 0.95. Both run only in primary windows where the 3-model call was made.
  - **Calibration:** a raw flip count mostly measures how marginal the call is. In the pre-seal review's simulation, 12 of 19 calls from a homogeneous population flipped within 3 drops. The reference is therefore the flip-count distribution of the `meas` B studies that make the 3-model call (a homogeneous population at the measured size and counts).
  - **H2 is supported if** the real flip count is below that distribution's 5th percentile in at least 4 called primary windows. It is not assessable if fewer than 20 gate studies call, if fewer than 4 primary windows are called, or if that 5th percentile is ≤ 1 (a called window always needs at least one drop, so the test would have no room). Non-finite subjects are dropped first, as in F4.
  - Also reported: the `meas_het` B 3-model call rate against `meas`, and the across-subject spread of measured DMAX and window AUC.
- **(c) Distribution shape (H3), per subject, per primary window, then the median over windows and then over subjects.** Values are first standardised within decoder fold, because fold-specific decoders make each level a mixture of slightly different means and scales, which inflates kurtosis on its own.
  - Level-0 excess kurtosis, against a Gaussian null: 1,000 simulations with each subject's real level-0 fold sizes, standardised the same way, seed 20261205. Level 0 is Gaussian in every generator. The null draws one window per subject, which spreads wider than a median over six correlated windows, so it is conservative.
    - **Heavy tails** if the real median exceeds the null's 95th percentile **and** exceeds 0.5 (an effect-size bar, about a t distribution with 16 df).
  - The level-5 bimodality coefficient (Sarle), against the `meas` gate's B_bifurcation studies (standardised within pseudo-folds).
    - **Well-separated high states** if the real median exceeds the 95th percentile of the generator's per-study medians.
  - Also reported: the median of J's fitted k·τ in the primary windows.
- **The three hypotheses are not exclusive.** All three readings are reported. None of them changes the R2 verdict.

## 6. Dependence on item 1 (fallbacks stated in advance)

| Item 1 outcome | Here |
|---|---|
| τ identifiable, fitted k·τ in the validated range | `G_jitter_kt{v}` cells at Sergent's fitted k·τ (median and both CI ends) join the graded cells in both the gate and the re-run. They count toward the tier. |
| τ not identifiable, or OUTSIDE VALIDATED RANGE | The gate runs without k·τ cells. |
| Placement step says the 3-model call is not diagnostic | No design change; noted next to R1. |

- These k·τ values are the only input allowed after the seal, and only from the sealed item-1 outputs (`experiments/sergent_jitter/out/…`).

## 7. Fallbacks (stated before calibration; any other change after the gate makes the result INVALID)

| Event | Fallback |
|---|---|
| F1: a subject's download fails after 5 attempts, its file is larger than 1.5 GB, it cannot be loaded (any load error), or it has fewer than 63 channels | That subject is skipped; the run continues. ≥ 18 decoded subjects are needed for any verdict. With fewer, the result is INVALID, and only descriptives and puzzle tests are reported. |
| F2: the time axis does not start at −500 ms, or fsample ≠ 500 | fsample ≠ 500 means the subject is skipped (F1). Windows are always placed by time (1-based window j = samples in [−330 + 30j, −300 + 30j] ms), so an on-grid shift of t0 needs no change (an off-grid axis falls under F10); t0 is recorded. |
| F3: `trialinfo` block outside 1–20 or snr outside 1–6; fewer than 60 trials at any level (checked before decoding); a CV fold with no trials | The subject is excluded (counted under F1). |
| F4: non-finite LME for a subject in a window | That subject is dropped from that window's BMS. If more than 2 subjects are dropped, that window has no outcome (it counts against the 4-of-6 rule). |
| F5: R1 fails | No 5-model verdict (§4). The failure itself is reported as a finding. No pipeline change and no re-fit. |
| F6: pre-stream tier 3 | Stream for R1 and §5 only, with the coordinator's OK. The re-run tier decides whether R2 is given. |
| F7: the `meas` tier differs from the pre-stream tier | The `meas` tier decides. |
| F8: sklearn convergence warnings in the decoder | Ignored, as in theirs (sklearn defaults). |
| F9: disk free − 2.5 GB < 10 GB before a subject | Streaming stops. It resumes per subject later with no change (subjects with an ok or skip record are not redone; a leftover partial file is deleted first). |
| F10: a window does not have exactly 16 samples on a subject's time axis (e.g. an off-grid t0) | That window is NaN for that subject. A subject with any NaN primary window is excluded before `measure` (counted under F1). NaN non-primary windows are handled by F4. So F2's placement by time covers only on-grid shifts of t0. |

## 8. Commands (coordinator launches anything longer than a few minutes)

| Step | Command (in `experiments/sergent_eeg/`) | When |
|---|---|---|
| Gate | `nice -n 20 ../../.venv/bin/python -I sergent_gate.py run [KT…]`, then `summary` (the k·τ list is fixed by the first call) | after the kill test exits |
| Stream | `nice -n 20 ../../.venv/bin/python -I stream_decode.py run` | after the gate's tier is known (§3 streaming rule) |
| Measure | `python -I analyse.py measure` | after streaming |
| Re-run gate | `python -I sergent_gate.py rerun`, then `summary` | after measure |
| Fit | `python -I analyse.py fit` | after measure, and after the re-run finishes (each uses 4 workers) |
| Readout | `python -I analyse.py readout` (it recomputes `summary` itself) | after the re-run and the fit |

## 9. What it cannot say

- **The decoder output is one projection of the EEG.** A graded or two-state verdict is about that projection in these windows, not about the brain as a whole.
- **Tier 2 is one-sided.** Failing to call Model 3 at this power is not evidence for graded processing.
- **J and T are two graded rivals, not all of them.** "Survives" means it survives these rivals.
- **H1 and the measured size are not label-free.** They use the snr labels, though not the audibility answers. The SD at level 0 includes the decoder's fold-to-fold variance. Generator B puts about 98% of level-5 trials in the high state; if fewer real trials are "heard", B understates separation, and "not H1" can shade into H3.
- **The puzzle readings rest on our generator family.** An effect that none of the generators has can show up only as "not H1, not H2", not by name.
