# Pre-registration: how often would Sergent et al. 2021's comparison call "bifurcation" on graded observers like theirs? (threshold jitter k·τ from published summaries)

Agent: Open Mind thread   Date: 2026-11-25   Script: `experiments/sergent_jitter/jitter_recovery.py`   Source: Fable round 18, item 1 (coordinator ruling of 2026-11-25)

- **Data:** Sergent et al. 2021 source-data workbook (Nat Commun, doi:10.1038/s41467-021-21393-z, ESM 4, 11,262,796 bytes, sha256 a974ea4d…0014). It was read with our stdlib reader `xlsx_read.py` under `python -I` and dumped to CSV. The script asserts the CSV sha256 and layout. Local only, not redistributed.
- **Looked at before this prereg:** sheet names, header text, row and column layout, and NaN positions only. No subject value was printed or summarised. Sergent's public analysis code (`datasets/local/sergent2021_code/`) was read, not run, to copy their summary definitions.
- **Pre-seal review (Fable, 2026-11-25, two rounds)** found five blockers in round 1 and five smaller ones in round 2 (a bound flag that misfired for D, noise-alone access in placement, decoder noise still optimistic, a run-time fallback that could not run under seal, no seal check on `audit.py`). All were fixed before the seal. Round 1's blockers:
  - the published heard/not-heard means are raw, not baseline-subtracted;
  - decoder noise was too optimistic;
  - there was no validity envelope for real fits;
  - the rating model was rigid;
  - the k·τ map axis was not established at other slopes.
- **Cohen data:** not used (§6). The Cohen hold does not apply.

## 0. Fallbacks and fixed rules (written before any kill-test run or calibration)

There is no calibration stage. Two pre-run steps were done, and neither printed a recovery number or used real values:
- **Timing pilot:** 4 simulated subjects at fixed values, wall-clock time only. It took 6.5 s per subject for both fits on the loaded laptop.
- **Expectation check:** the analytic expectations were compared with a 400,000-trial simulation and agree to about 0.005. The θ integral was moved from 40-node Gauss-Hermite to a 321-point grid; the 40-node rule was off by up to 0.06 for the top-level not-heard mean.

| Situation | Pre-stated rule |
|---|---|
| Neither estimator meets the recovery bar (§3) | Result: **"τ not identifiable from Sergent's published summaries."** That is the finding. No real-data estimate is made. Item 2 (Sergent's EEG) proceeds on its own design gate. |
| Both estimators pass | P (heard/not-heard split) is used on real data. S is reported as a descriptive cross-check. |
| Only S passes | S is used on real data, labelled as the secondary estimator. |
| Real fits fall outside the validated envelope (§4) | Result: **"OUTSIDE VALIDATED RANGE: no placement."** The k·τ estimate is reported as descriptive only. |
| A fit returns no finite loss | That subject is dropped from the group median. Fewer than 16 fitted subjects counts as outside the envelope. |
| A kill-test cell crashes or is killed | Finished cell files are kept. The cell reruns from its own fixed seed. |
| Kill-test run time projects above 3 h on 4 workers | Rerun with the optional argument `100` (subjects per cell); the script accepts only 200 or 100, and the count is in every cell filename so the two never mix. Nothing else changes. |
| The recovery rate lands just under 0.90 | It fails. There is no "near miss" reading. Rates carry Monte Carlo error from 200 fits per cell, and the bar is applied as is. |

Any other change after the seal makes the study INVALID.

## 1. Question and why it matters

Our sealed audit (`experiments/bifurcation_specificity/RESULTS.md`) showed that Sergent's 3-model comparison calls "bifurcation" on purely graded data whose threshold jitters from trial to trial. With the sealed slope (0.75 per dB, i.e. 1.5 per 2 dB level), the rate was:

| Threshold SD τ | 1 dB | 2 dB | 3 dB |
|---|---|---|---|
| Bifurcation call rate | 1% | 74% | 98% |

Each rate comes from 300 studies (`out/G_jitter_*.json`).

That map varied τ at one slope, so it is not shown to be a function of k·τ alone. The open question is empirical: **what threshold spread and transfer slope do real observers have, and how often would Sergent's comparison call graded observers with those values "bifurcation"?**
- If graded observers like theirs are rarely called, their call is diagnostic.
- If they are usually called, Sergent's published comparison cannot separate graded-with-jitter from bifurcation for their listeners.

**Prior art:**
- Sergent & Dehaene 2004 (library `sergent-dehaene-2004-all-or-none-ab`) and Sergent 2021's own variability-peak analysis use rating or neural variability as a qualitative marker.
- We found no work that estimates the trial-to-trial threshold spread jointly with the neural transfer slope from published per-subject summaries.

## 2. Model and summaries

One latent drives both the decoder and the rating, per subject, with x in dB SNR:

- **Threshold:** θᵢ ~ N(x₀, τ²).
- **Access:** Aᵢ = expit(k(x − θᵢ)), with Aᵢ = 0 on noise-alone trials.
- **Decoder decision value (one window):** yᵢ = c + D·Aᵢ + N(0, σₙ²). The offset c is free, because logistic-regression decision values have an arbitrary per-subject intercept.
- **Audibility:** a continuous cursor scale (Sergent Methods), rᵢ = clip(G·Aᵢ + N(0, σₑ²), 0, 10), with free gain G ∈ [2, 10].
- **Heard:** rᵢ ≥ 3 (their `audthresh = 3`).

Summaries follow Sergent's own computation (`SoundConsciousEEG_MNE_SingleTrialPredict.m` lines 777–812; plotted and exported raw at lines 901–902 and 933):

- **Decoder means:** m_H(x) = mean(y | x, heard) and m_N(x) = mean(y | x, not heard), at −13, −11, −9, −7 and −5 dB.
  - These are **raw**, with no baseline subtraction. Only their SD columns are baseline-subtracted, and those are not used.
  - Empty categories are NaN and are ignored in the fit.
- **Audibility:** mean and SD (n − 1) at noise and at the five levels ("Supplementary Figure 1").
- **Subject order:** assumed identical across the two sheets (both say "lines are subjects").
- **Window (real data):** 300–600 ms, the mean of their three 100 ms window means (300–400, 400–500, 500–600). This lies inside the 250–700 ms span where they report the bifurcation call. The three windows separately are descriptive only.
- **Trial counts (simulation):** 150 per level including noise alone (their Methods: mean 150, range 127–160).

Expected summaries are analytic: the θ integral uses a 321-point grid over ±8 SD, and the rating moments are those of a censored normal.

## 3. Kill test (run first; decides whether any real-data estimate is made)

**Grid.**
- Planted k·τ ∈ {0.25, 0.5, 0.75, 1.0, 1.5, 2.25, 3.0} × τ ∈ {1, 2, 3} dB, which is 21 cells. k = k·τ/τ therefore varies separately from τ.
- 200 simulated subjects per cell. Each subject's k·τ and τ are the cell values × exp(N(0, 0.2)).

**Nuisances, fixed a priori** (not taken from Sergent's values):
- x₀ ~ U(−10.5, −7.5) dB.
- σₑ ~ U(1.0, 2.5).
- σₙ/D ~ U(1, 8), with D = 1: d′ at full access 0.125–1 (AUC about 0.53–0.76). Sergent's window-averaged single-trial d′ cannot be recovered from the summaries; their per-time-point heard AUCs (plot axis 0.48–0.6) suggest the lower part of this range. The guard is the envelope in §4.3, which includes the split residual relative to D.
- c ~ N(0, 0.5).
- G ~ U(6, 10).
- **Lapses (a misspecification the fit does not model):** on a share λ ~ U(0, 0.05) of all trials, including noise alone, the rating is uniform on [0, 10].

**Estimators** (Nelder-Mead from 6 starts; best loss kept):
- **P (primary, neural split):** fits m_H, m_N (≤ 10 values) and mean audibility (6 values) for x₀, τ, k·τ, σₑ, G, D and c.
  - Split block: weighted residuals with one profiled variance. The weights are model-predicted trial counts + 1, taken from a first-stage fit and then frozen for a second-stage refit.
  - Audibility means: fixed standard errors, the published SD/√150.
- **S (secondary, audibility variability):** fits the mean and SD of audibility (12 values) for x₀, τ, k·τ, σₑ and G, using fixed standard errors (SD/√150 and SD/√298).

**Study:** 2,000 resampled studies of 20 subjects, drawn without replacement from the cell's 200. The statistic is the group median.

**Recovery bar (per estimator; all three must hold):**
1. **Core:** in every cell with planted k·τ ∈ {0.5, 0.75, 1.0, 1.5, 2.25} and every τ, at least **90%** of studies have the median k·τ **and** the median τ each within **±25%** (|log ratio| ≤ log 1.25) of the cell value.
2. **Low end:** in every k·τ = 0.25 cell, at least 90% of studies have median k·τ < 0.75.
3. **High end:** in every k·τ = 3.0 cell, at least 90% of studies have median k·τ > 1.5.

**Also reported per cell:** the 5/50/95% quantiles of the study medians, failed fits, fits at a parameter bound, and non-converged fits.

**Seeds:** `SeedSequence([20261801, round(100·k·τ), round(10·τ)])` per cell; study resampling uses seed 20261802.

## 4. Real-data analysis (only if an estimator passes)

1. **Fit.** Fit the chosen estimator per subject (20 subjects) on the 300–600 ms window.
2. **Estimate.** Take the median k·τ across subjects, with a 95% percentile bootstrap CI over subjects (10,000 draws, seed 20261803).
3. **Validated envelope.** Over all core kill-test cells, take the 2.5–97.5% range of the estimates of x₀, τ, σₑ and G, plus, for P, the split residual RMS divided by D. The result is **OUTSIDE VALIDATED RANGE** if any of these holds:
   - any real median falls outside its range;
   - more than 4 subjects have an estimate at a parameter bound;
   - fewer than 16 subjects were fitted.
4. **Placement.** Use the sealed machinery itself (`bifurcation_specificity/audit.py`: `design`, `subject_lme` and `spm_bms`, unchanged), not the old map. Generate purely graded G_jitter-form data at the fitted values:
   - slope = median k̂ (converted to per level, ×2);
   - threshold = median x̂₀ (level = (x + 15)/2);
   - τ = k·τ/k̂ at each of the three points (CI lower bound, median, CI upper bound);
   - the sealed signal-to-noise (amplitude 2, noise SD 1), 20 subjects × 6 levels × 150 trials, 300 studies per point, seeds `SeedSequence([20261804, i])`;
   - noise-alone trials get zero access, as in the fitted model (the sealed G_jitter cells put noise at −15 dB on the logistic instead; that difference matters only at shallow slopes or wide τ).

   The call is Model 3 protected exceedance > 0.95. `place` checks that `audit.py` is still its sealed version. A study with non-finite model evidence makes the whole placement **INVALID** (no silent "no call").

| Result (in order) | Condition |
|---|---|
| CALL DIAGNOSTIC | call rate at the CI upper point ≤ 0.05 |
| CALL NOT DIAGNOSTIC | call rate at the CI lower point ≥ 0.50 |
| INTERMEDIATE | otherwise; all three rates reported |

**Descriptive only:**
- the S estimate when P is used;
- per-window medians;
- the sealed-map interpolation at the median k·τ.

## 5. How to read it, and limits stated now

- **What a high k·τ means.** A high k·τ is also what a true two-state system produces, because k·τ measures how step-like access is relative to the threshold spread. "Not diagnostic" therefore means Sergent's published comparison cannot tell graded-with-jitter from bifurcation for observers like theirs. It does not mean the observers are graded.
- **Signal-to-noise.** Placement uses the sealed map's signal-to-noise (amplitude 2 against noise SD 1), not Sergent's per-window value, which cannot be recovered from the summaries. Their late windows decode well (heard AUC up to about 0.6 per time point, higher after window averaging), and the sealed audit found the 3-model call is not specific for strong signals. Weaker signals would lower all call rates. That is stated as a limit, not adjusted.
- **One latent for both measures.** The model ties the rating and the decoder to one latent. If ratings carry an access-independent component beyond Gaussian noise and lapses, S is biased; P is less exposed because the split is neural.
- **Validity of the kill test.** It is valid only inside its envelope (§4.3). Real fits outside it give no placement.

## 6. Cohen et al. 2024 as a second map point: not placeable from on-disk data (stated now)

- **What the data allow.** Cohen's trial file has binary seen/unseen reports at 5 SOAs (about 200 trials per SOA per subject). Our on-disk EEG is SOA 50 ms only.
- **Why it is not placeable.** With one neural level and an unknown offset and gain, the split is c + D·f(k, τ), so k·τ is not identifiable by construction, and no simulation is needed to say so.
- **What would change that.** Cohen becomes a map point only if item 4 (the no-report block) or a later approved download adds neural data at other SOAs. That would need its own prereg.

## 7. Commands and outputs

All commands run from `experiments/sergent_jitter/`, with the venv Python under `-I` (`../../.venv/bin/python -I jitter_recovery.py …`):

| Step | Command | Run by | Output |
|---|---|---|---|
| Kill test | `killtest out/killtest` (fallback: `killtest out/killtest 100`, §0) | coordinator (long) | `out/killtest/` |
| Real data | `real ../../datasets/local/sergent2021_source/csv out` | me | `out/real/real_result.json` |
| Placement | `place out` | coordinator (long) | adds placement to `real_result.json` |

All three steps check the seal of this prereg and the script. Results go to `experiments/sergent_jitter/RESULTS.md`.
