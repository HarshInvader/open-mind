# Item 2 (round 18): Sergent et al. 2021's own EEG under the 5-model set. DESIGN (not a prereg, not sealed)

Status 2026-11-25, about 17:30Z: design numbers pinned from the source data and code on disk; design gate specified; nothing streamed. The prereg (`docs/prereg/2026-11-25_sergent_eeg_five_models.md`) supersedes §4 and §7 where they differ.

## 1. Question

- Sergent et al. 2021 (Nat Commun 12:1149) report that, in late windows, single-trial decoder output is fit better by a two-state mixture (Model 3) than by graded models (0, 2B).
- Our sealed simulations show two things:
  - that comparison also calls two states for graded data with a jittered threshold or heavy tails (NOT SPECIFIC);
  - adding a jittered-threshold graded model (J) and a Student-t graded model (T) restores specificity (FIX WORKS).
- **Question:** on their own data, does Model 3 still win once J and T compete?

## 2. Design numbers (pinned; source in brackets)

| Quantity | Value | Source |
|---|---|---|
| Subjects | 20 (OSF files S1–S20; their list `01…25` with gaps) | `SoundConsciousEEG_MNE_GAT_SingleTrials.py` `subjects_list`; Dropbox listing (40 `S*_{Active,Passive}_data_ref.mat`) |
| Levels | 6: no sound, −13, −11, −9, −7, −5 dB (their snr codes 1–6) | same script, `snr_dB` and the comment on `y['snr']` |
| Trials per level, before EEG rejection | 168 for 18 subjects, 176 for 2 (all six levels) | inferred exactly: every identification percentage in Fig 1D is a multiple of 100/168 or 100/176 |
| Trials per level, after rejection | about 150 (the sealed audit's value, from the paper); exact counts are only in `data_ref.trialinfo` | audit.py `N_PER` |
| CV | 20 blocks, 5 folds of 4 blocks | `SoundConscEEG_SingleTrialPred_ModelFitting_Twind30ms_batch.m` |
| Signal | decoder decision values on the 500 Hz diagonal (not decimated; the decimated GAT is only for Fig 2), StandardScaler + LogisticRegression per time sample, trained on no sound vs −5 dB, 10-fold StratifiedKFold; intermediate levels scored by fold; then 10 Hz low-pass and 30 ms window means | GAT script (diagonal section), fitting script |
| Published max-level decoding | the diagonal of Fig 2B (no sound vs −5 dB, AUC per decimated sample, group mean) peaks at **0.731** (sample 69 of 176); 0.69–0.73 over its plateau | `source_data.xlsx`, sheet "Figure 2 Panel B" |
| Their 3-model result | Model 3 exceedance > 0.99 in a run of late windows | sheet "Figure 3 Panel E" (53 windows) |

## 3. Why the gate matters here (a pre-stream finding)

- The sealed generator reproduces AUC 0.731 at **DMAX = 0.89** noise SDs (`snr_timing.max_level_auc`: DMAX 0.875 → 0.728, 0.9 → 0.734).
- At 20 subjects and 150 trials per level, our sealed signal-strength follow-up (`out_snr/m5_*`) found, for true two-state data:
  - 5 models: Model 3 called (pxp > 0.95) in **0/100** studies at AUC 0.70 and at AUC 0.76, and in 1/100 at AUC 0.85. A call needs AUC of about 0.9.
  - 3 models (theirs): Model 3 called in 11/100 at AUC 0.70 and 28/100 at AUC 0.76.
- So at the published decoding strength, the 5-model comparison is expected to miss a true two-state brain almost always. The gate below will most likely FAIL on recall.
- **The puzzle this exposes:** their 3-model comparison returned pxp > 0.99 in late windows. In our simulation, true two-state data at the same AUC gives that in only 11–28% of studies. One of these must be true:
  1. The window signal they fit (10 Hz low-pass, 30 ms mean) is stronger than the per-sample AUC in Fig 2B.
  2. Subjects differ a lot, with a few strong subjects driving the random-effects BMS.
  3. The data have a feature our weak two-state generator lacks: rare but well-separated high states, heavy tails, or jitter.
- Only the real decoder outputs can tell these apart. Reading them is what streaming buys, even if the 5-model gate fails.

## 4. Design gate (synthetic only; before any EEG is streamed)

- **Machinery:** the sealed `audit.py` and `extended.py`, imported unchanged. The structure follows `gate_design.py`, with Sergent's design substituted.
- **Design:** 20 subjects; trial counts per level 168 (18 subjects) and 176 (2 subjects), scaled by a retention of 150/168 to the paper's post-rejection size; 100 studies per cell.
- **Cells:**
  - B_bifurcation (recall);
  - graded: G_jitter_mid, G_jitter_hi, G_heavy, H_jitter_t, H_gain;
  - if item 1 returns a τ estimate, a G_jitter cell at Sergent's fitted k·τ (see §6).
- **Signal sizes:**
  - **deciding:** DMAX 0.89 (the published AUC);
  - **sensitivity:** 1.0 (AUC 0.76) and 1.25;
  - **heterogeneity variant at 0.89:** per-subject DMAX_s = 0.89 · exp(N(0, 0.35²) − 0.35²/2).
- **Order and stop rule:** B_bifurcation runs first at 0.89. If recall < 0.80, the gate has FAILED on recall. The graded cells still run at 0.89, because specificity decides tier 2.
- **Rule, two tiers (a proposal for the coordinator):**
  - **Tier 1, the full gate (the sealed standard):** recall ≥ 0.80 on B and every graded cell ≤ 0.10. If it passes, both outcomes are interpretable.
  - **Tier 2, specificity only:** recall < 0.80 but every graded cell ≤ 0.10. Then streaming is allowed, but the decision is one-sided. A Model 3 call (5-model pxp > 0.95) reads "two-state survives fair rivals". Anything else is UNRESOLVED (low power) and is never read as evidence against two states.
  - **Tier 3:** any graded cell > 0.10. Do not stream for the 5-model question; the result is "not specific at this design".
- **After streaming:** as in the Cohen real-data prereg, the gate is re-run once at the measured signal size (per-window max-level DMAX in level-0 SD units, label-free) and the real counts. That run decides the tier.

## 5. Bytes and streaming

- **No decoder outputs are shared.** The Dropbox (OSF aw3t5, CC BY 4.0) has:
  - preprocessed `S*_Active_data_ref.mat`;
  - raw BrainVision files;
  - behavioural `.mat` files;
  - code.
- **Preprocessed files:**
  - MAT v5, one zlib-compressed element (type 15) per file, so they cannot be read per trial.
  - S1 is 533,608,099 bytes. All 20 active files together are about 11.4 GB (earlier HEAD sizes).
  - These hold their exact pipeline: ICA, visual rejection and interpolation. The raw files would need all of that redone by hand.
- **Plan:** stream one subject at a time.
  1. Download to a fresh scratch directory (about 0.55 GB).
  2. Load with `scipy.io.loadmat` under `python -I`.
  3. Compute the decoder outputs with their method: the diagonal only, every 500 Hz sample, float32.
  4. Keep the trialinfo columns (block, snr, audibility).
  5. Delete the `.mat` before the next subject.
- **Kept per subject:** about 1,000 trials × about 1,000 samples × 4 bytes ≈ 4 MB, plus the 53 window values. All 20: about 80 MB.
- **Disk:** peak extra use about 1.5 GB (one file plus the loaded arrays), far above the 10 GB guard at the current 19 GB free. Each subject starts only if free disk minus 1 GB is above 10 GB.
- **Network:** about 11.4 GB in total. This needs the coordinator's or owner's OK: it is above the 3 GB item-3 exception, though not a disk problem.
- **Range reads:** checked. OSF's Dropbox proxy answers Range with 206, so a resumable chunked download is possible.
- **Passive sessions:** not needed for the primary question. That would be another 12.4 GB, and it is out of scope.

## 6. Dependence on item 1 (fallbacks stated in advance)

| Item 1 outcome | Item 2 consequence |
|---|---|
| τ identifiable, fitted k·τ inside the validated range | Add a G_jitter cell at Sergent's fitted k·τ (median and the CI ends) to the gate, so that specificity is checked at the realistic jitter. |
| "τ not identifiable" | Item 2 proceeds on its own gate: the sealed graded cells (jitter mid/hi, heavy, jitter+t, gain) only. |
| OUTSIDE VALIDATED RANGE | Same as "not identifiable". |
| Placement says "CALL NOT DIAGNOSTIC" for the 3-model call | Strengthens item 2's motivation; no design change. |

## 7. Real-data analysis (to be fixed in the prereg)

- **Primary windows (pinned from Fig 3E):** their fitting script uses `TWOI = 101:15:901`, 30 ms windows from −300 ms (1-based window j covers −330 + 30j to −300 + 30j ms).
  - Their longest run with Model 3 exceedance > 0.95 is 1-based windows 23–28, i.e. **360–540 ms** (an earlier draft said 22–27, which counted from 0); pxp there is 0.990–0.999.
  - Isolated windows also pass: 1-based window 21 (300–330 ms, 0.99) and window 32 (630–660 ms, 0.97).
  - 2B exceeds 0.95 at 1-based windows 18, 33 and 37 (0.985–0.991): their "late unimodal" period begins at 660 ms.
  - **The prereg fixes the primary set as 1-based windows 23–28.** Candidate decision rule: a verdict needs the same outcome in at least 4 of the 6 windows. The prereg states it before streaming.
- **Verdicts:**
  - TWO-STATE SURVIVES: 5-model Model 3 pxp > 0.95.
  - GRADED RIVAL WINS: J or T > 0.95.
  - TWO-STATE LOST ITS EDGE: 3-model Model 3 > 0.95, but not under 5 models.
  - UNRESOLVED: otherwise.
  - Under tier 2, only the first verdict is read as evidence.
- **Replication check, before the 5-model fit:** our port must reproduce their 3-model pxp in the primary window (Model 3 > 0.95). If it does not, the result is "our pipeline does not reproduce theirs", the 5-model comparison is reported descriptively only, and no verdict is given.
- **Descriptive:**
  - the per-window max-level AUC and DMAX (answers §3 hypothesis 1);
  - the spread of AUC across subjects (hypothesis 2);
  - the level-0 and max-level distribution shapes (kurtosis), and J's fitted k·τ (hypothesis 3).

## 8. Compute

- **Measured cost:** the sealed `snr_timing` 5-model cells (100 studies, 20 subjects, 3 workers) took 1,050–1,100 s each, so about 14 min per cell on 4 workers. But a smoke test of this script used about 2 CPU-minutes per study while sharing the CPU with the kill test (likely on efficiency cores). If that holds, a cell takes up to about 50 min, and the 6 deciding cells 1.5–5 h.
- **Gate size:** 6 cells at 0.89, plus B at 1.0 and 1.25, plus the heterogeneity variant (6 cells) = 14 cells, about 3.3 h on 4 workers. The coordinator launches it after the kill test frees the workers (about 19:30Z).
- **Order:** the 6 cells at 0.89 first (about 1.4 h; they decide the tier), then the heterogeneity variant, then the B sensitivity points.
