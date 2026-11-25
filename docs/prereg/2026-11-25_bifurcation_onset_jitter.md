# Pre-registration: does trial-to-trial onset jitter move the apparent onset of "bifurcation dynamics"? (Sergent et al. 2021, simulation)

Agent: Open Mind thread   Date: 2026-11-25   Script: `experiments/bifurcation_specificity/jitter_onset.py`   Source: Fable round 17, study 2

- **Zero data.** Pure simulation with the sealed Sergent 2021 port (`audit.py`) and the sealed 5-model extension (`extended.py`), both imported unchanged. No Cohen data, so the Cohen hold does not apply.

## 0. Calibration fallbacks and fixed rules (written before any pilot or calibration)

This study has no calibration stage. The only pre-run step is a **timing-only pilot**: one study (σ 80 ms, window +40 ms, seed 12345) whose only printed output is its wall-clock seconds. The pilot's model-comparison output is not printed, saved or looked at.

| Situation | Pre-stated rule |
|---|---|
| Pilot projects the full run (21 cells × 100 studies on 4 workers) above 6 h | STUDIES drops from 100 to 50. Nothing else changes. |
| Pilot projects above 12 h even at 50 studies | The study is not run; it goes back to the coordinator. |
| At σ = 0, the call rate at W = −40 is above 0.05, or at W = +40 below 0.80 (anchor check, per comparison) | That comparison's verdict is **INVALID**: the generator does not give a clean no-signal → signal rise, so a lag is not defined. No re-run with other windows or amplitudes. |
| At σ = 0 the fitted rate is already ≥ 0.5 at the first window, or never reaches it | **INVALID** for that comparison. |
| A jittered σ never reaches 0.5 inside its grid | Its crossing is right-censored at +200 ms (40 ms past the last window), which understates the lag; flagged. |
| A jittered σ is already ≥ 0.5 at its first window (−80 ms) | Its crossing is left-censored at −80 ms, which understates a lead; flagged. |
| A study has non-finite log model evidence | It counts as "no call" in the comparison whose models are non-finite (models 0–2 for the 3-model, all 5 for the 5-model); counts per cell are reported. |
| A cell's run crashes or is killed | Resume: finished cell files are kept, the cell is rerun from its own fixed seeds. |

Any other change after the seal makes the study INVALID.

## 1. The claim and prior art

- **Sergent, Corazzol, Labouret, Stockart, Wexler, King, Meyniel & Pressnitzer 2021** (Nat Commun, doi:10.1038/s41467-021-21393-z; full text in `datasets/local/r16_priorart/sergent2021.txt`).
  - **The model-comparison claim this study simulates:** "After 250 ms, there was a switch in favor of the bifurcation model, whose protected exceedance probability remained above 95% for most of the period between 250 and 700 ms."
  - Summary claim: "The data are so far consistent with qualitative predictions of the bifurcation model for latencies beyond 250–300 ms post-stimulus." (Their "around 300 ms" switch sentence comes from the earlier ERP-variability analysis, not the model comparison.)
  - Trial data were "temporally averaged over 30 ms time windows", contiguous, so that the signal "was more robust to small temporal fluctuations". Data were low-pass filtered at 10 Hz. They applied Simes correction across time points; here pxp > 0.95 in each window is used, a per-window simplification (as in our earlier follow-ups).
- **Klatzmann et al. 2025** (Cell Reports, doi:10.1016/j.celrep.2025.115372; library id `klatzmann-2025-cortex-bifurcation`, abstract only) model ignition as a dynamic bifurcation in associative cortex. It is a modelling paper and does not test single-trial timing.
- **Single-trial latency spread:** single-trial P3b latency SD is about 77–84 ms (Kim et al. 2024, Psychophysiology, doi:10.1111/psyp.14677, RIDE, not corrected for noise; library id `kim-2024-ride-p3b-latency-sd`). True spread is smaller, so 80 ms is an upper anchor and 40 ms a middle one.
- **Our sealed results with the same port** (`experiments/bifurcation_specificity/RESULTS.md`): the 3-model comparison is not specific (graded generators are also called bifurcation); the 5-model extension fixes that at 20 subjects; reduced SNR leaves a blind zone up to AUC 0.70.
- **The gap.** If ignition happens at a different time on each trial, a 30 ms window near the mean onset holds mostly a diluted two-state mixture (fewer high-state trials, at full amplitude) plus a minority of partly switched trials (about 30% of high trials at σ = 40, 15% at σ = 80). So the window where the bifurcation model is first called may move with latency spread. We found no test of this in the papers citing Sergent 2021 that we screened for round 17.

## 2. Generator

- **Design and states:** exactly `audit.design` and the `B_bifurcation` shape: 6 SNR levels × 150 trials, 20 blocks, 20 subjects per study; P(high) = expit(1.5(x − 2.5)), 0 at x = 0; high-state amplitude (1 + 0.2(x − 2.5)) × 2.0/1.5; noise N(0, 1).
- **Onset jitter:** each high-state trial switches on as a step at its own onset oᵢ ~ N(0, σ) ms around the true mean onset (time 0).
- **Window value:** the mean over a 30 ms window centred at W ms: the high-state amplitude × the share of the window after oᵢ, plus N(0, 1) noise. Low-state trials have amplitude 0.
- **Grid (21 cells), σ-specific because at σ = 0 the whole rise lies inside W ∈ (−15, +15):**
  - σ = 0: W ∈ {−40, −10, −5, 0, +5, +10, +40} ms. W = +40 is exactly the sealed `B_bifurcation` cell; W = −40 is pure noise.
  - σ = 40 and 80: W ∈ {−80, −40, 0, 40, 80, 120, 160} ms.
- **Seeds:** `SeedSequence([20261727, σ, W + 1000])`, spawned per study.

## 3. Analysis

- **Per study:** each subject's 5-fold block-CV log model evidence from `extended.subject_lme5`; then `audit.spm_bms` on the first 3 models (Sergent's comparison, primary) and on all 5 (secondary).
- **Call:** protected exceedance probability of Model 3 (bifurcation) > 0.95.
- **Call rate** per cell = share of the 100 studies called.
- **Onset crossing** at each σ: the 7 call rates are first fitted non-decreasing in W (pool-adjacent-violators, equal weights), then the crossing is the first window where the fitted rate reaches 0.5, linearly interpolated between grid windows. Censoring as in §0.
- **Lag** at σ = crossing(σ) − crossing(0).
- **Uncertainty:** 2,000 bootstrap draws resampling studies within each cell, independently per cell (seed 20261736), refitting the isotonic curve in each draw. The one-sided 95% bounds are the 5th and 95th percentiles of the lag; ROBUST uses both together, which is a 90% two-sided interval (TOST logic).

| Verdict (primary: 3-model, σ = 80 ms; in order) | Condition |
|---|---|
| INVALID | σ = 0 anchor check fails, or the σ = 0 crossing is censored (§0) |
| APPARENT ONSET LAGS BY ≥ 40 MS | lag lower bound ≥ +40 ms |
| APPARENT ONSET LEADS BY ≥ 40 MS | lag upper bound ≤ −40 ms |
| ONSET TIMING ROBUST (\|lag\| < 40 ms) | upper bound < +40 and lower bound > −40 |
| LAG NOT RESOLVED AT THIS PRECISION | otherwise |

- **Secondary, same rules:** the 5-model comparison at σ = 80; both comparisons at σ = 40 (lag and bounds reported, no separate verdict).
- **Descriptive, reported in every case:**
  - the raw call rates for every cell and both comparisons, and a non-monotone flag (any raw drop > 0.10 between adjacent windows);
  - p* = Φ(crossing/σ), the share of high-state trials switched on at the crossing, for σ = 40 and 80. If dilution is the mechanism the two p* should be close;
  - the 3-model unimodal (Model 2B) call rates, the winning-model counts, non-finite counts and censoring flags.
- **The 40 ms bar** is about one and a half of their 30 ms windows: a lag smaller than that would not move "after 250 ms" by a window.

## 4. What a result would and would not mean

- **LAGS:** latency spread alone delays the apparent bifurcation onset by more than a window; the reported onset is later than the mean ignition time, and part of the "250–300 ms" may be jitter.
- **LEADS:** the test detects the early-igniting minority; the reported onset then precedes the mean ignition time.
- **ROBUST:** realistic jitter does not move the onset by a window, so the timing claim is not a latency artefact in this generator.
- **Limits:**
  - A sharp step onset. Their 10 Hz zero-phase low-pass turns each step into a ramp of roughly 35–50 ms; that is not simulated and would make the real σ = 0 reference softer, shrinking the lag slightly.
  - Jitter is Gaussian and independent of SNR; in real data latency often shortens with stimulus strength.
  - One amplitude scale (the sealed `B_bifurcation` one); the SNR study showed the call is SNR-sensitive, and the lag in ms scales with σ and power. p* is the more transferable number.
  - Per-window pxp > 0.95, not their Simes correction across time.
  - It says nothing about whether the brain's dynamics are bifurcating, only about what the windowed test reports when they are.

## 5. Compute and pre-seal record

- At most 4 workers, nice 20, run detached with a pid file and a log.
- **Pilot (done before sealing, timing only):** one study took 40.2 s on one core. Projection: 21 × 100 × 40.2 s ÷ 4 workers = 5.9 h, under the 6 h line, so STUDIES stays 100. The margin is small; an overrun is expected and changes nothing.
- **Pre-seal review (Fable, 2026-11-25), applied before sealing:** σ-specific grid and anchor checks replacing a near-vacuous sanity range; isotonic fit before the crossing; separate finite flags for the 3- and 5-model comparisons; summary checks cell metadata; left-censor flag; p*; LEADS meaning; corrected Sergent quote and Klatzmann venue. No model-comparison outcome of any cell was seen before these changes.
