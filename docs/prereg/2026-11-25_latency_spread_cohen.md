# Pre-registration: how much does the late seen-trial signal jitter in latency? (Cohen et al. 2024, SOA 50)

Agent: Open Mind thread   Date: 2026-11-25   Script: `experiments/latency_spread/latency_spread.py`   Requested by: coordinator (follow-up to TG-square)

- **Zero new bytes.** It uses the on-disk SOA-50 report-block epochs: 38 eligible subjects, the same as the sealed fixed-SOA study.
- **Why:** the TG-square simulation (`experiments/tg_square_specificity/RESULTS.md`) showed that a square becomes non-specific at a trial-to-trial latency SD of about 50 ms for a single brief code and 75 ms for a chain of brief codes. The real latency spread decides which reading of a square is open.

## 0. Prior art (read first; texts in `datasets/local/r16_priorart/latency/`)

- **Woody-type estimators fit noise.** On pure noise the lag spread approaches the window's uniform SD: about 58 ms for ±100 ms, right between our two cases.
  - Li & Principe 2009 (PMC3645474) fixed the true latency and still got Woody SDs of 60 ms at −20 dB and 15 ms at 12 dB.
  - Trongnetrpunya 2019 describes the "maximum correlation lag obtained with a signal component that is due to noise".
- **Published single-trial P3 latency SDs are 77–84 ms** (RIDE, flanker task, PMC11579232; HMP, oddball task, Weindel 2024). None is corrected for the noise floor, and none comes from masking.
- **So a raw SD cannot answer this.** Only an SD calibrated against the subject's own noise can, which is the design below. Woody 1967 and the RIDE methods papers had no open full text; their properties are taken from open secondary sources.

## 1. Estimator (fixed)

- **Data:** each subject's kept trials (same preprocessing and rejection as `cohen_killtest.preprocess`), good scalp channels; seen = answer 1, unseen = answer 2.
- **Per subject, 10-fold CV (stratified):**
  - **Spatial filter:** Ledoit-Wolf LDA on the 300–500 ms scalp mean, trained on the training trials, seen vs unseen.
  - **Template:** the training seen mean minus the training unseen mean of the filtered time course, 300–500 ms (mean-centred).
  - **Lag:** each held-out seen trial (filtered, minus the training unseen mean) is cross-correlated with the template at lags −100 to +100 ms in 2 ms steps, and the lag at the maximum is kept.
  - No trial contributes to the filter or template it is scored against. There is no iteration.
- **Subject statistic:** the SD of the seen-trial lags (the "apparent SD").
- **Descriptive extras from the same folds:** the lags of held-out unseen trials, and the held-out AUC of the window-mean LDA score. They do not change the seen-trial lags.

## 2. Calibration ladder and kill test (run before any real seen-trial lag)

- **Shape** (group, after sealing; reads seen-vs-unseen averages only):
  - the group seen-minus-unseen difference wave at the P3b ROI (channels 1/4/5/6/13/14/15), fitted over 200–600 ms by a Gaussian A·exp(−(t−μ)²/2σ_obs²);
  - the group 300–500 ms difference topography, scaled so the ROI mean is 1;
  - a per-subject amplitude scale: the subject's ROI 300–500 ms difference ÷ the group's, floored at 0.
  - The fit is OK if A > 0, 20 ≤ σ_obs ≤ 200 ms, 300 ≤ μ ≤ 500 ms, R² ≥ 0.70 over 200–600 ms, and the group window difference is > 0.
- **Synthetic data per subject (same seen and unseen counts as the real data):**
  - **Noise:** the subject's *unseen* residuals (unseen trial minus unseen mean), resampled with replacement to the total trial count, each with a random sign flip. Seen residuals are not used, because they carry the real seen signal's own latency and amplitude variability (pre-seal review, blocker 1).
  - Into each pseudo-seen trial goes topography × s_subj·A·(σ_obs/σ_w)·exp(−(t−μ−τ)²/2σ_w²) × a, with σ_w = √(σ_obs² − σ_j²) and τ ~ N(0, σ_j).
  - The planted average therefore matches the observed group difference wave, scaled per subject, at every jitter level.
- **Generators** (amplitude a per seen trial):

| Generator | Amplitude | Use |
|---|---|---|
| nominal | gamma, mean 1, CV 0.3 | the curve, and nominal pseudo-datasets |
| cv0 | 1 on every trial | nuisance |
| cv06 | gamma, CV 0.6 | nuisance |
| absent30 | 30% of seen trials carry no signal; the rest gamma CV 0.3, scaled by 1/0.7 | nuisance (guesses at threshold) |

- **Levels:** nominal at σ_j ∈ {0, 25, 50, 75, 100} ms with 100 replicates per subject; each nuisance generator at 50 and 75 ms with 50 replicates per subject.
  - A level is plantable only if σ_w ≥ 10 ms.
  - **Descriptive:** right-skewed latencies (gamma, k = 4) at 50 and 75 ms, nominal amplitudes, 33 replicates.
  - The level-0 point is the no-jitter floor; it is reported, not used for inversion.
- **Group curve:** the mean over subjects of each subject's mean nominal apparent SD, per level. It is read from 25 ms upward.
- **Inversion:** linear interpolation on the curve from 25 ms to the top plantable level. A value below the 25 ms point gives 25 with flag LOW (an upper bound); above the top gives the top level with flag HIGH (a lower bound). A curve that is not strictly increasing from 25 ms gives NaN.
- **Kill test (GATE):** a pseudo-dataset takes replicate k of every subject at true 50 (or 75) ms.
  - Nominal pseudo-datasets are inverted on the curve built without replicate k. Nuisance pseudo-datasets are inverted on the full **nominal** curve, so the gate tests misspecified amplitude distributions, not only precision (pre-seal review, blocker 3).
  - **GATE PASS** needs: the nominal curve strictly increasing from 25 ms, and **for every generator**: estimated < 62.5 ms in ≥ 90% of pseudo-datasets at true 50, ≥ 62.5 ms in ≥ 90% at true 75, and |median bias| ≤ 15 ms at both.
  - Otherwise the verdict is **METHOD BLIND**: the real data are not analysed, and the method is reported as unable to answer the question at our SNR and trial counts under plausible amplitude distributions.
  - If 50 or 75 ms cannot be planted, the verdict is **GATE NOT RUNNABLE**. Only the width bound is then reported, with its assumptions.

## 3. Real data (only after GATE PASS)

- **Group apparent SD:** the mean over subjects of the real apparent SD, inverted on the nominal curve. 95% CI from 2,000 bootstrap resamples of subjects; the curve is recomputed on the same resample (shape parameters held fixed).
- **Verdict from the CI.** The TG simulation found a square for a single brief code at 50 ms but not 25, and for a chain at 75 but not 50; each threshold lies somewhere inside those intervals, and those simulated codes were 50 ms wide while here σ_w changes with level.

| Verdict | CI | Reading for the TG square |
|---|---|---|
| JITTER BELOW 50 MS | upper < 50 | chain alternative excluded (its threshold is above 50); single-code alternative not decided (threshold between 25 and 50) |
| JITTER AT LEAST 50 MS | 50 ≤ lower < 75 | single-code alternative open; chain not decided |
| JITTER AT OR ABOVE 75 MS | lower ≥ 75 | both alternatives open |
| UNRESOLVED | otherwise, or > 5% of bootstrap inversions NaN | — |

- **Flags carried with the verdict:**
  - **OUT OF RANGE:** the point estimate's LOW or HIGH flag, and the share of flagged bootstrap draws.
  - **RESPONSE-LOCKED:** if the within-subject Spearman correlation between seen-trial lag and RT has a group t > 3, the verdict is reported as possibly reflecting motor timing.
- **Reported in every case:**
  - per-subject apparent SDs and the curve;
  - the apparent SD using only seen trials with RT > 600 ms or no response, beside the full SD for the same subjects;
  - the apparent SD of held-out unseen trials scored the same way (an in-data noise floor);
  - the held-out 300–500 ms LDA AUC, real versus the nominal ladder at each level (a check on the synthetic SNR);
  - the gamma-latency curve and the nuisance-generator curves at 50 and 75;
  - the width bound: the moment SD of the positive difference wave over 200–600 ms, and σ_obs. This bound holds only for a single non-negative component whose latency is independent of its amplitude and which lies inside the window; truncation at the epoch end can make it too small. It is not model-free.

## 4. Fallbacks (stated before calibration)

- **Shape fit fails** (section 2 criteria): INVALID. There is no refit.
- **A level cannot be planted:** it is dropped. If that is 50 or 75, the verdict is GATE NOT RUNNABLE (section 2).
- **The gate fails:** METHOD BLIND. There is no change to the window, lag range, iteration, estimator or generators.
- **Compute:** at most 4 workers, nice 20 (results do not depend on the worker count; seeds are fixed per job).
- **Pre-seal disclosures:**
  - The author's pilot timed one estimator call on one subject with permuted labels and printed only the runtime and lag counts.
  - The pre-seal reviewer ran throwaway simulations on purely synthetic data (24 synthetic subjects, one SNR) and a label-free count of response times (median RT 560 ms; 62% inside the epoch). They saw: a nominal-curve gap of about 6 ms between 50 and 75; replicate SD of the group mean about 0.9 ms; amplitude CV 0.6 or 30% absent trials moving the apparent SD by 4–6 ms; seen-residual noise biasing estimates downward. These findings caused the unseen-only noise, the nuisance generators in the gate, per-subject amplitude scaling, inversion from 25 ms with flags, the narrower shape criteria, the revised reading table and the RT checks.
  - The author's smoke test ran the ladder and gate code on 3 real subjects with **permuted** labels and a **guessed** shape (A 3 µV, μ 400 ms, σ_obs 90 ms, flat topography), 4 nominal and 3 nuisance replicates. It printed a non-monotone curve (about 55–60 ms at every level) and METHOD BLIND. It used no real seen/unseen contrast. It found and fixed a key-type bug (channel keys read back from JSON as strings).
- Any other change after sealing makes the study INVALID.

## 5. Limits

- **Report block, not no-report.** Hutchinson et al.'s squares come from no-report data, and the motor response and report may add late variance here; the RT checks in section 3 are the guard.
- **Single-code model.** The ladder plants one Gaussian code; a chain or a sustained signal would give a different lag distribution. The verdict is read as "the latency spread of the dominant seen-vs-unseen component".
- **Lag SD mixes jitter and amplitude.** The nuisance generators cover CV 0 to 0.6 and 30% absent trials; distributions outside that range are not covered.
- **Shape held fixed:** the group σ_obs includes between-subject latency spread, so σ_w is slightly underestimated at each level; the bootstrap does not refit the shape.
- **Neutrality:** a statement about these data under this estimator, not about Hutchinson et al.'s datasets.
