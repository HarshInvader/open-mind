# Pre-registration: can an extended model set make the single-trial bifurcation test specific?

Agent: Open Mind thread   Date: 2026-11-25 (UTC)   Script: `experiments/bifurcation_specificity/extended.py`   Builds on: `2026-11-24_bifurcation_specificity_audit.md` (NOT SPECIFIC)

- **Zero data.** Simulation only.
- **What came before.** The sealed audit ported the comparison in Sergent et al. 2021: Model 0 (one Gaussian), Model 2B (graded: logistic mean, SD linear in the mean) and Model 3 (two-state mixture).
  - The comparison was valid on its own models.
  - It also called "bifurcation" in 74% of simulated studies with trial-wise threshold jitter (SD 1.0), 98% with jitter SD 1.5, and at least 67% with t(4) noise.
- **This study's question.** Does adding graded models that can express those features restore specificity, while keeping recall for real two-state data?

## 0. Prior art (checked 2026-11-25)

- **Screened:** all 122 works citing Sergent 2021 in Europe PMC (by title), the 9 closest by abstract, and a Europe PMC full-text search for critiques.
- **Found:** no published critique or fix of this model comparison.
- **Related:**
  - Boyer et al. 2026 (bioRxiv 10.64898/2026.06.17.732590) applies the same single-trial bifurcation modelling to fMRI.
  - Doll et al. 2024 and Stockart et al. 2025 report graded or accumulating signals but do not test the method.
  - Klatzmann et al. 2025 model ignition mechanistically.
  - The general point is known in statistics: misspecified, non-normal data produce spurious mixture classes (Bauer & Curran 2003, *Psychol Methods* 8:338). Its application to this test, and a fix for it, are not published.

## 1. Models (their three, unchanged, plus two)

- **J, jittered-threshold graded.** y = c + L·logistic(k·(x − θ)) + N(0, s²), with θ ~ N(x0, τ²) drawn per trial.
  - Six parameters [x0, k, L, c, τ, s].
  - Marginal likelihood by 40-node Gauss–Hermite quadrature over θ. Checked against a Monte Carlo integral: −340.68 vs −340.70.
  - Inits:
    - x0 and k as in their Model 2B;
    - L = mean(max) − mean(noise);
    - c = mean(noise);
    - τ = 1;
    - s = SD(noise).
- **T, heavy-tailed graded.** Model 2B's mean and scale, with Student-t noise and an estimated df (log ν, ν ∈ [0.5, 1000]).
  - Inits are Model 2B's, plus ν = 10. Checked against `scipy.stats.t` (identical).
- **Unchanged from the sealed audit and its code (`audit.py`, imported, not edited):** fitting (fminsearch defaults), inits for 0/2B/3, 5-fold block CV, the mean of summed test LLH, and spm_BMS (RFX VB, BOR, pxp).
- **Bifurcation call:** Model 3 pxp > 0.95 in the 5-model comparison.
- **J nests two states.** As k → ∞, J becomes a two-state mixture with P(high) = Φ((x − x0)/τ). On real two-state data, J may therefore match Model 3, which would cost recall. That is a possible outcome, named in advance as UNDECIDABLE (section 3).
- **Recorded per subject:** the median over folds of k·τ, J's step-likeness. It is descriptive only.

## 2. Generators (all 8 from the audit, same parameters, plus 2 held out)

| Cell | Two discrete states? | Contained in J or T? |
|---|---|---|
| B_bifurcation | yes | J (as a limit) |
| M2_unimodal | no | 2B, T |
| G_jitter_lo / mid / hi | no | J |
| G_skew | no | no |
| G_heavy | no | T |
| G_drift | no | approximately J |
| **H_jitter_t** (held out) | no | no: jitter SD 1.0 *and* t(4) noise |
| **H_gain** (held out) | no | no: trial-wise multiplicative gain, lognormal(0, 0.5), Gaussian noise |

The two held-out cells test whether any rescue extends beyond the models we added. J and T have a home advantage on the jitter and heavy-tail cells.

## 3. Kill test and verdict

Per cell: 150 simulated 20-subject studies (6 levels × 150 trials, 20 blocks). The rate is the fraction of studies with a call.

| Verdict | Condition |
|---|---|
| FIX WORKS | B_bifurcation ≥ 0.80 and every non-two-state cell (the 8 graded + M2_unimodal) ≤ 0.10 |
| UNDECIDABLE | B_bifurcation < 0.80 and every non-two-state cell ≤ 0.10. With these models, "two states" and "graded with a jittered threshold" cannot be told apart. |
| STILL NOT SPECIFIC | B_bifurcation ≥ 0.80 and some non-two-state cell > 0.10 |
| FAILS BOTH | otherwise |

**Secondary (descriptive):** winning-model counts per cell, mean subjects best fit per model, median k·τ, convergence, and non-finite studies.

## 4. Calibration fallbacks (stated in advance)

- **None for thresholds, generators, models, inits or optimiser.** The run is not calibrated: the verdict follows from the single run.
- **Non-finite studies:** a study with any non-finite subject log-evidence counts as no call, as in the audit.
- **Resume:** if the machine stops, finished cells are kept and only missing cells run, with the same seeds (seed 20261129, per-cell spawning).
- **Multi-window and Simes arm: not run.** It is not cheap to make faithful: it needs a model of how windows correlate. Misspecification bias repeats in each window, so pooling windows cannot remove it.
- Any other change after sealing makes the run INVALID.

## 5. Limits

- **Signal strength:** one effect size and one trial count, as in the audit.
- **Fairness:** FIX WORKS on the home-advantage cells alone would be weak. The held-out cells carry the generality claim.
- **Scope:** a pass means the extended set is specific against these ten generators, not against all graded mechanisms.
- **Neutrality:** results are stated as properties of the method under simulation, not as claims about the original data.
