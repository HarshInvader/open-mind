# DRAFT, NOT SEALED, DROPPED: are seen trials less variable than selection alone predicts? (Cohen et al. 2024, report block, SOA 50 ms)

Agent: Open Mind thread   Date: 2026-11-25   Script: `experiments/cohen_fixed_soa/variance_truncation.py`   Source: Fable round 15, item 4

> **Dropped before sealing (2026-11-25).** The Fable pre-seal review, on synthetic data only, found two problems. At the real effect sizes the truncation correction is about ±0.01, so the test reduces to Schurger 2015's raw variance comparison. Slow drift or state-dependent noise also gives false QUENCHED calls in 36–89% of simulated studies. The script was never run on real labels. See `docs/RESEARCH_STATE.md`.

- **Data:** `experiments/cohen_fixed_soa/out/prep.npz` (single-trial component amplitudes, already preprocessed and artefact-rejected by the sealed fixed-SOA study). Zero new bytes.
- **Subjects:** the 38 eligible subjects in `out/eligibility.csv` (14 pilot + 24 confirm). Median 109.5 trials per subject.
- **Not yet looked at:** no variance or other second-moment statistic split by seen/unseen has been computed on these data. Earlier studies used class means only.

## 0. Prior art and the question

- **Established:**
  - Seen trials are less variable than unseen trials in MEG pattern similarity at threshold (Schurger et al. 2015, *PNAS* 112:E2083). Of 113 citing works screened, none tests whether label selection alone could produce this.
  - Attention and task engagement quench trial-to-trial variability (Arazi et al. 2019, *J Neurosci*). Seen trials may be more attended.
- **The confound we test:** "seen" is a selection on a noisy graded variable. If amplitude correlates with that variable, selecting the top part of it changes each class's variance by itself.
  - The class in the tail (the smaller class) loses more variance. So a variance difference can appear with no change in how stable the brain state is.
- **Question:** after allowing for that selection, is the seen class still less variable?

## 1. Measure

- **Amplitude:** per trial, the mean over the component's ROI and window, exactly as stored in `prep.npz`.
  - **Primary:** VAN (PO9/PO10, 140–200 ms) and P3b (300–500 ms).
  - **Descriptive only:** P1 (100–140 ms) and N2 (250–290 ms).
- **Observed per subject:** log(var_seen / var_unseen), with ddof 1. It is corrected for the first-order small-sample bias of log sample variance: + 1/(n_seen − 1) − 1/(n_unseen − 1).
- **Graded-truncation null (no free parameter):**
  - z ~ N(0, 1) is graded visibility; "seen" iff z > c, with c set by the subject's own seen rate p.
  - Amplitude a = μ + b·z + e, with e independent of z.
  - Truncated-normal moments give the class means and class variances of z. The observed class-mean gap fixes b², and the pooled variance fixes var(e).
  - The predicted log(var_seen / var_unseen) follows. On large simulated bivariate-normal samples it matches the observed ratio to within ±0.012.
- **Excess** = bias-corrected observed − predicted. Below 0 means seen trials are less variable than selection alone predicts.
- **Group:** mean excess over 38 subjects. Two primary components, Bonferroni: 97.5% t-intervals.

## 2. Decision (per primary component)

| Verdict | Condition |
|---|---|
| QUENCHED | CI upper bound < 0 |
| WIDENED | CI lower bound > 0 |
| MATCHES NULL | CI inside ±0.15 (a variance ratio within about ×0.86 to ×1.16 of the prediction) |
| INCONCLUSIVE | otherwise |

- Each primary component gets its own verdict. There is no combined verdict.
- **Reported descriptively:** observed and predicted mean log ratios, the number of subjects with excess < 0, and the same statistics for P1 and N2 (no verdict).

## 3. Calibration (after sealing, before the real labels touch an amplitude; 300 runs, seed 20261131)

Fake labels only. The only real-label quantity used is each subject's seen count, which earlier studies already reported.

- **(a) Graded null on the real amplitudes:**
  - per subject and component, ρ ~ U(0.10, 0.50) and a random sign;
  - fake z = ±ρ·standardised(a) + √(1 − ρ²)·N(0, 1);
  - the top n_seen trials are "seen".
  - This keeps each subject's real amplitude distribution, including its skew and tails.
- **(b) Synthetic graded null with a skewed latent:**
  - z is a standardised gamma(4), skew 1;
  - a = SD_real·(ρz + √(1 − ρ²)·N(0, 1));
  - same counts.
  - This tests whether the Gaussian-latent formula is robust to a non-Gaussian visibility variable.
- **(c) Planted:** as (a), then the seen trials' deviations from the seen mean are shrunk so their variance is ×0.80 (log −0.22).
- **PASS:** false QUENCHED or WIDENED ≤ 5% in (a) and in (b), for each primary component, and QUENCHED ≥ 80% in (c) for each primary component.
- Mean excess per cell is reported as a bias check.

## 4. Calibration fallbacks (stated in advance)

- **F1, only if the main calibration fails:** replace the moment formula with a Monte Carlo prediction from the subject's own amplitudes.
  - 500 fake label sets from fake z = ±r·standardised(a) + √(1 − r²)·N(0, 1), top n_seen = seen.
  - r is set by bisection so the expected |gap| matches the observed gap.
  - Predicted = mean fake log ratio, which already contains the small-sample bias, so no separate correction.
  - Recalibrate once on the same three cells (same PASS rule), seed 20261138, and seal that calibration file.
  - Cell (a) is close to F1's own generator, so F1's real test is cell (b).
- **If F1 also fails:** the study stops at the gate. The real statistic is never computed.
- No other change to components, windows, subjects, bound, plant size, ρ range or interval after calibration. Any such change makes the study INVALID.

## 5. Limits

- **Attention:** a QUENCHED result cannot separate seen-specific stability from more attention on seen trials (Arazi 2019). Both are departures from a single graded variable with fixed noise.
- **Additive model:** the null assumes the amplitude noise e does not depend on z. A brain whose noise shrinks smoothly as visibility grows (graded, no state change) would also give QUENCHED. A QUENCHED result therefore rules out "selection alone", not "graded".
- **Scalar amplitude:** one number per trial per component. Schurger et al. used multivariate pattern similarity, so a null here does not contradict them directly.
- **Reaction and response:** report trials include a button press. Its motor activity may differ between answers, mostly after the VAN window.
