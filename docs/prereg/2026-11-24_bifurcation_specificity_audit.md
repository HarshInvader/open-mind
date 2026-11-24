# Pre-registration: does Sergent et al. (2021)'s bifurcation model comparison pick "two states" when the brain is graded?

Agent: Open Mind thread   Date: 2026-11-24   Script: `experiments/bifurcation_specificity/audit.py`   Source: Fable round 15, study 1

- **Zero data.** Simulation only. We downloaded no EEG.
- **Paper.** Sergent, Corazzol, Labouret et al. 2021, *Nat Commun* 12:1149, "Bifurcation in brain dynamics reveals a signature of conscious processing independent of report".
  - They fit three models to single-trial decoder outputs at each SNR level: 0 (one Gaussian), 2B (a graded logistic mean with SD growing with the mean) and 3 (a two-state mixture whose high-state probability rises with SNR).
  - Model 3 won by random-effects BMS at late windows. They read that as a bifurcation, i.e. discrete "seen" and "unseen" brain states.
- **Code.** The authors' OSF scripts (osf.io/aw3t5, CC BY 4.0), 13 files, 315,806 bytes. We read them but never ran them. The sha256 of each file is in a local FETCH_LOG.json. The port follows their likelihoods, inits, block CV and `spm_BMS(lme,[],0,0,1)` call exactly.
- **Question.** Model 2B is one specific graded shape: Gaussian noise, with SD linear in the mean. Real graded signals can depart from that shape. A trial-wise threshold jitter, skewed noise, heavy tails or slow drift could each make the two-Gaussian mixture fit better without any discrete states. If so, a Model 3 win is not specific to bifurcation.
- **Prior art checked.** Doll et al. 2024 and Pereira et al. 2021 argue for graded accumulation. We found no published test of this comparison's specificity against non-Gaussian graded generators.

## 1. Port (fixed before any graded run)

- **Likelihoods:** `LLH_fun_null.m`, `LLH_fun_logisticB.m`, `LLH_fun_logisbimodalfixedsigma.m`. SNR is coded 0 (noise) to 5, and noise trials are included in every model.
  - Model 3 sets P(high) = 0 on noise trials.
  - Deviation: a point with SD ≤ 0 returns −inf. MATLAB would return a complex value there.
- **Inits:** taken from their batch script and computed on all trials in the window, as they do. Models 0, 2B and 3 each get one data-driven start.
- **Optimiser:** Nelder–Mead with MATLAB `fminsearch` defaults (TolX = TolFun = 1e-4, 200·n iterations and evaluations, 5% initial simplex). A fit that hits the iteration cap is kept, as in their code. The converged fraction is reported.
- **CV:** 20 blocks, 5 folds of 4 blocks. A subject's log-evidence per model is the mean over folds of the summed test log-likelihood.
- **Group:** random-effects VB BMS as in `spm_BMS`, with α0 = 1, exceedance from 200,000 Dirichlet samples, BOR from F1 vs F0, and pxp = (1−BOR)·xp + BOR/3.
- **Design per simulated subject:** 6 levels × 150 trials, spread evenly over the 20 blocks. Each study has 20 subjects, as in their study.
- **Smoke test (debug, not evidence).** Two studies each of the two validity cells, plus two BMS sanity cases:
  - Model 3 data: pxp3 = 1.0 and 1.0.
  - Model 2B data: pxp3 = 0.0 and 0.0.
  - Equal evidence: pxp about 1/3 each.
  - Strong Model 3 evidence: pxp3 about 1.

  No graded cell was fitted before sealing.

## 2. Generators (noise SD 1, noise mean 0, max-SNR mean 2, threshold 2.5, logistic slope 1.5)

| Cell | Role | Mechanism |
|---|---|---|
| B_bifurcation | validity: recall | Their Model 3: two discrete states, shared SD, P(high) logistic in SNR |
| M2_unimodal | validity: false alarm | Their Model 2B: Gaussian, logistic mean, SD = 1 + 0.25·mean |
| G_jitter_lo / mid / hi | graded | y = 2·logistic(1.5·(x − θ)) + N(0,1), with θ ~ N(2.5, τ²) per trial, τ = 0.5 / 1.0 / 1.5 (continuous latent) |
| G_skew | graded | logistic mean + shifted gamma(2) noise, SD 1 (right skew) |
| G_heavy | graded | logistic mean + Student-t(4) noise, SD 1 |
| G_drift | graded | θ drifts across blocks as a random walk, step SD 0.35, mean-centred; Gaussian noise |

- **Graded** means no discrete latent state, by construction.
- **KDE peak counts per level are descriptive only.** An outcome-free pre-check showed why. The true two-state generator reads as one peak (its states are about 1.3 SD apart), and the heavy-tailed cell shows a false 3 peaks. Density shape cannot define the cells.

## 3. Primary measure and decision

- **Measure:** per cell, 300 simulated studies. The rate is the fraction of studies where Model 3 pxp > 0.95, the paper's criterion at a single window.
- **Validity:** B_bifurcation rate ≥ 0.80 and M2_unimodal rate ≤ 0.05. Otherwise the result is VOID.
- **Verdict (if valid):**
  - NOT SPECIFIC: any graded cell has rate ≥ 0.50.
  - SPECIFIC: every graded cell has rate ≤ 0.10.
  - MIXED: otherwise.
- **Secondary (descriptive):**
  - mean pxp3;
  - mean number of subjects whose best model is Model 3;
  - converged fraction;
  - KDE peaks.

## 4. Calibration fallbacks (stated in advance)

- **None.** A validity failure gives VOID: no retuning of generators, effect size, optimiser or thresholds, and no re-run.
- Each cell runs once, with seed 20261128 and per-cell seed spawning.
- If the machine dies mid-run, finished cells are kept and only the missing cells are run, with the same seeds.
- Any other change after sealing makes the run INVALID.

## 5. Limits

- One effect size (max-SNR mean 2 noise SDs) and one trial count. Their decoder outputs may be on a different scale.
- Their pipeline has one window per 30 ms and Simes across windows. We model one window, which is the per-window false-alarm rate.
- A NOT SPECIFIC result says the method can call graded mechanisms "bifurcation". It does not say their data are graded.
- A SPECIFIC result covers only these four graded families.
