# Pre-registration: why did the 5-model bifurcation test lose specificity at 38 subjects? (simulation)

Agent: Open Mind thread   Date: 2026-11-25   Script: `experiments/bifurcation_specificity/gate_specificity.py`   Source: Fable round 17, study 3

- **Zero data.** Pure simulation with the sealed Sergent 2021 port (`audit.py`) and the sealed 5-model extension (`extended.py`), imported unchanged. Trial counts are Sergent's 150 per level, not the Cohen-derived counts used in Follow-up 3, so no Cohen data enters and the Cohen hold does not apply.

## 0. Calibration fallbacks and fixed rules (written before any check, pilot or calibration)

This study has no calibration stage. Two pre-run steps come before sealing, and neither shows a model-comparison outcome:

- **Equivalence check** (`check`). On one simulated `G_jitter_mid` subject, the STD arm must reproduce the sealed `extended.subject_lme5` log evidences exactly (tolerance 1e-9). It prints only True/False and the seconds taken.
- **Timing pilot** (`pilot`). One `G_jitter_hi` study at 20 subjects, all arms. Its output is discarded and it prints only the seconds taken.
  - **Projection** = pilot seconds ÷ 20 × (subject-fits in the run) ÷ 4 workers ÷ 3600.
  - The run has 100 × (38 + 38 + 20 + 76) = 17,200 subject-fits, or 9,600 without N = 76.
  - `B_bifurcation` subjects are counted at the `G_jitter_hi` cost, so the projection is slightly conservative.

| Situation | Pre-stated rule (applied in order, before sealing) |
|---|---|
| The equivalence check fails | Fix the STD arm until it passes, and change nothing else. The STD arm must be the sealed procedure. |
| The projection is above 8 h | Drop the secondary cell `G_jitter_hi` N = 76 (`DROP_76 = True`). |
| It is still above 8 h | STUDIES drops from 100 to 60 in every cell. |
| It is above 14 h at 60 studies without N = 76 | Not run; the study goes back to the coordinator. |
| A study's comparison has non-finite log evidence | That comparison counts as "no call". Its Δ is left out of the mean. Counts per cell and arm are reported. |
| A run crashes or is killed | Resume. Results are written in chunks of 20 studies, finished chunks are kept, and each chunk reruns from its fixed seeds. |

The run starts only after round 17 #2 has finished and released the Open Mind compute lock. Any other change after the seal makes the study INVALID.

## 1. The claim and prior art

- **The finding being explained** (`experiments/bifurcation_specificity/RESULTS.md`, Follow-up 3). Model 3 (bifurcation) pxp > 0.95 among 5 models was called on the graded `G_jitter_hi` generator in:
  - 0.007 of studies at 20 subjects × 150 trials per level (the sealed extended simulation);
  - 0.18 at 38 subjects with the real Cohen per-level counts (the design gate, which therefore failed). Those counts were close to 150: median 128–154 per level, minimum 115.
  - At 38 subjects × 64 trials per level (the "half" option) it was 0.06, so fewer trials lowered the rate.
  - So N = 38 at 150 per level is close to a direct replication of the 0.18.
- **Already visible in the sealed outputs** (back-solved from `out_ext/*.json` before this prereg; no new fitting).
  - The protected exceedance is pxp = (1 − BOR)·xp + BOR/5. Model 3 can therefore pass 0.95 only when BOR < 0.0625.
  - BOR was taken as 5 × pxp of the null model, which won no subject in any of the 150 studies per cell.
  - In `G_jitter_hi` at N = 20:
    - unprotected xp(M3) > 0.95 in **0.10** of studies;
    - BOR < 0.0625 in 0.073;
    - both, and so pxp > 0.95, in 0.007;
    - median BOR 0.16.
  - In `G_jitter_mid`: xp > 0.95 in 0.02, and BOR never < 0.0625 (median 0.33).
  - In `B_bifurcation`: xp > 0.95 in 0.94, and BOR < 0.0625 in 0.99.
  - So the 20-subject specificity largely came from the omnibus-risk protection, not from J out-predicting Model 3. More subjects shrink BOR.
  - The per-subject winners were nearly tied: mean subjects best per study at N = 20 were 2B 1.9, M3 7.6, J 8.5 and T 2.1, out of 20.
- **J is the true model family for `G_jitter_hi`.**
  - The generator is y = 2.0·expit(1.5(x − θ)) + N(0, 1), with θ ~ N(2.5, 1.5²) per trial.
  - Model J is exactly c + L·expit(k(x − θ)) + N(0, s²), with θ ~ N(x0, τ²).
  - With k·τ = 2.25 the latent expit(·) is bimodal at mid levels. So Model 3, a two-Gaussian mixture, can be a near-exact approximation there. That is a fair-comparison problem, not only a fitting one.
- **The fit budget.** `audit.fminsearch` copies MATLAB's default of 200·n evaluations. In the sealed `G_jitter_hi` cell only 69% of fits reported convergence (`out_ext/G_jitter_hi.json`, `mean_converged` 0.692). If J (6 parameters, quadrature likelihood) is under-fit, a better optimizer would help.
- **Rigoux, Stephan, Friston & Daunizeau 2014** (NeuroImage, doi:10.1016/j.neuroimage.2013.08.065; abstract only, not open access).
  - Random-effects BMS treats models as random effects with an unknown population distribution.
  - They introduce the Bayesian omnibus risk, "the chance likelihood of apparent differences in model frequencies", and protected exceedance probabilities.
  - Our reading: BOR's null is "all 5 models equally frequent". Once 3 of the 5 models win few subjects, that null is rejected and BOR offers no protection against a near-tie between the other two. Exceedance asks which model is most frequent in the population, not whether two models can be told apart within a subject.
- **Piray 2025** (Nat Hum Behav, doi:10.1038/s41562-025-02348-6; full text).
  - "While power increases with sample size, it decreases as more models are considered."
  - 41 of 52 reviewed studies had under 80% probability of identifying the true model.
  - Their framework uses xp (not pxp) and draws each subject's best model as given, with no fitting and no near-equivalent pair. False positives are controlled only under a uniform null.
  - We found no paper on wrong calls that become confident as N grows when two models are near-equivalent per subject, or on optimizer budgets in BMS.

## 2. Design

- **Generators:** `audit.gen`, unchanged. `G_jitter_hi` is primary and `B_bifurcation` is the recall check. The design is Sergent's: 6 levels × 150 trials, 20 blocks, 5-fold block CV.
- **Cells, in run order:**
  - `G_jitter_hi` at N = 38 (primary);
  - `B_bifurcation` at N = 38;
  - `G_jitter_hi` at N = 20;
  - `G_jitter_hi` at N = 76 (secondary; dropped first by the fallback).
  - Each cell has 100 studies, with seeds `SeedSequence([20261737, cell index, N])` spawned per study.
  - The BMS seed is the study seed + 1, with a fresh stream for each arm, so paired arms get identical draws.
- **Arms, fitted on the same simulated subjects:**
  - **STD:** the sealed procedure, one fminsearch run per model and fold from the sealed inits.
  - **RST:** each model and fold continues from the STD end point while fminsearch reports no convergence, up to 4 runs in total. The best training fit is used, and the same rule applies to all 5 models.
  - **ORC (`G_jitter_hi` only):** J is also fitted from its generating values (x0 2.5, k 1.5, L 2.0, c 0.001, τ 1.5, s 1.0), with the same restarts. The better *training* fit of RST-J and ORC-J is scored. Real data has no oracle; ORC only tests whether RST-J reached its optimum, and it is used in one verdict condition below.
- **Stored per study and arm:** pxp, xp, model frequencies, BOR, the per-subject log evidences, and per-model convergence and run counts.
- **Call:** Model 3 pxp > 0.95 among the 5 models (the gate's rule), from `audit.spm_bms`.

## 3. Questions and verdicts

All tests are one-sided at 95%. Wilson score bounds are used for rates.

**Q1, subject count (STD arm, `G_jitter_hi`).** The test is the lower bound of call rate(N = 38) − call rate(N = 20), from the Newcombe hybrid score interval. This interval is slightly liberal at very small counts.

| Verdict | Condition |
|---|---|
| STD CALL RATE RISES FROM 20 TO 38 SUBJECTS | lower bound > 0 |
| NO DETECTABLE RISE FROM 20 TO 38 SUBJECTS | otherwise |

The same bound for 76 vs 38 is reported, with no verdict.

**Q2, fit budget (primary: `G_jitter_hi` at N = 38; the same rules are reported at N = 76 as a secondary).** Conditions are checked in order:

| Verdict | Condition |
|---|---|
| NOT APPLICABLE: NO SPECIFICITY LOSS SHOWN AT THIS N | STD Wilson lower ≤ 0.10 |
| FIT-BUDGET ARTEFACT: RESTARTS RESTORE SPECIFICITY | RST Wilson upper ≤ 0.10, exact McNemar p < 0.05 (STD calls > RST calls, paired by study), and B recall under RST at N = 38 ≥ 0.80 (a point estimate) |
| FIT-BUDGET ARTEFACT, BUT RESTARTS COST RECALL | as above, but B recall under RST < 0.80 |
| PARTIAL: RESTARTS REDUCE BUT DO NOT REMOVE THE LOSS | RST Wilson lower > 0.10 and McNemar p < 0.05 |
| NOT A FIT-BUDGET ARTEFACT: SPECIFICITY STILL LOST WITH RESTARTS | RST Wilson lower > 0.10, McNemar p ≥ 0.05, ORC Wilson lower > 0.10, and RST convergence ≥ 0.95 for both Model 3 and J |
| UNRESOLVED: OPTIMUM NOT SHOWN | RST Wilson lower > 0.10 and McNemar p ≥ 0.05, but the ORC or convergence conditions fail |
| UNRESOLVED | otherwise |

- 0.10 and 0.80 are the sealed gate's specificity and recall bars.
- At 100 studies, "≤ 0.10" (Wilson upper) needs at most 5 calls and "> 0.10" (Wilson lower) needs at least 15.
- **Descriptive, in every case, per cell and arm:**
  - the call rate and Wilson bounds;
  - the rates of xp(M3) > 0.95, of BOR < 0.0625, and of both; median BOR;
  - the mean per-subject Δ = lme(M3) − lme(J) in nats, with a t-interval over studies (> 0 means Model 3 predicts held-out trials better);
  - the paired STD-only and RST-only call counts;
  - convergence share, runs and held-out gain from restarting (RST − STD), all per model;
  - best-model counts per subject;
  - for `G_jitter_hi`, J's held-out gain from the oracle start.
- **Mechanism reading, stated in advance:** if the STD call rate rises from 20 to 38 while the xp > 0.95 rate stays near its N = 20 level and the BOR < 0.0625 rate rises, the rise is described as protection fading with N. This is a description, not a verdict.

## 4. What a result would and would not mean

- **FIT-BUDGET ARTEFACT:** restarting the fits changes the outcome and restores specificity at this N. Any reuse of Sergent's code should restart unconverged fits. The per-model held-out gains show whether J's improvement or Model 3's change drives it. A gate re-run with restarts would be the natural next step, but is not part of this study.
- **NOT A FIT-BUDGET ARTEFACT:** with fits at their optimum (convergence ≥ 0.95, and the oracle start agrees), the true graded model still loses to Model 3 often enough at this N. The cause is then in the comparison itself. Model 3 approximates a bimodal-looking graded latent, and once the omnibus risk is small, random-effects BMS turns a near-tie into a confident call. More subjects would make the test less specific, not more.
- **Limits:**
  - One graded family (threshold jitter) at one signal size (DMAX 2), with Sergent's trial counts. The Cohen per-level counts are not used.
  - Restarts are one optimizer repair. Converged local optima are not revisited, except J via ORC.
  - ORC uses knowledge that real data never gives.
  - No arm separates "Model 3 is a near-exact approximation of the bimodal latent" from fit quality at the parameter level.
  - pxp is computed per window, with no Simes correction over time.

## 5. Compute

- At most 4 workers, nice 20, detached with a pid file and a log, under the Open Mind compute lock, after #2 finishes.
