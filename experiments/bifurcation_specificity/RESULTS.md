# Can Sergent et al. (2021)'s bifurcation test tell two brain states from a graded brain?

**Verdict: NOT SPECIFIC.** The test is valid on its own two models. Yet it calls "bifurcation" in most simulated studies of three kinds of brain with no discrete states. The test was sealed and run once, with no fallbacks.

- **Prereg:** `docs/prereg/2026-11-24_bifurcation_specificity_audit.md`, sealed 2026-11-24T21:52:47Z (6aac4dc).
- **Script:** `audit.py`.
- **Outputs:** `out/*.json` and `out/summary.json`.
- **Data:** simulation only.
- **Code source:** the authors' OSF analysis code (315,806 bytes), read but never run, ported to Python.

## Result (300 simulated 20-subject studies per row; "call" = Model 3 protected exceedance > 0.95)

| Generator | Discrete states? | Bifurcation call rate | Mean subjects (of 20) best fit by Model 3 |
|---|---|---|---|
| Their Model 3 (two states) | yes | **1.00** (validity ≥ 0.80 ✓) | 18.3 |
| Their Model 2B (Gaussian graded) | no | **0.00** (validity ≤ 0.05 ✓) | 0.3 |
| Threshold jitter, SD 0.5 | no | 0.01 | 7.3 |
| Threshold jitter, SD 1.0 | no | **0.74** | 12.2 |
| Threshold jitter, SD 1.5 | no | **0.98** | 14.5 |
| Skewed noise (gamma) | no | 0.04 | 8.8 |
| Heavy-tailed noise (t, 4 df) | no | **0.67**\* | 12.5 |
| Threshold drift across blocks | no | 0.27 | 9.7 |

\*Three of the 300 studies hit a −inf test log-likelihood: a single heavy-tail outlier underflows the Gaussian density. Those studies count as no call, so 0.67 is a lower bound.

- **Decision rule:** a graded cell at ≥ 0.50 means NOT SPECIFIC. Three cells qualify.
- **Fit convergence:** fits hit the iteration cap, as MATLAB `fminsearch` would. The converged fraction is 0.72–0.84 across cells and does not track the call rate: the two-state cell converged most often (0.84).

## What it means

- **Their comparison asks a narrow question:** is the data closer to a two-Gaussian mixture or to one Gaussian whose SD grows linearly with the mean?
- **A graded brain can fail the second shape in two ways:**
  - The threshold moves a little from trial to trial. A random threshold makes each level's output a blend of "below threshold" and "above threshold" values.
  - The noise has heavier tails than a Gaussian.
- **When either happens, the mixture model wins, even with no discrete state behind the data.**
- **The jitter result is the important one.** Trial-to-trial variation in sensory threshold is ordinary: it is the standard account of a psychometric function, so it should be expected in any real brain.
- **What this does NOT show:**
  - It does not show that their data are graded. It shows that their Model 3 win cannot, on its own, separate discrete states from a graded signal with a jittery threshold or heavy tails.
  - Their extra evidence still stands: the report-free design and the link to subjective ratings.

## Limits

- **Scale:** one effect size (max-SNR mean 2 noise SDs) and one trial count. Their decoder outputs may be scaled differently, and a different signal-to-noise ratio could move the rates.
- **Windows:** we modelled one window. Their analysis spans many 30 ms windows with Simes correction, so our rates are per-window rates.
- **Deviation:** points with SD ≤ 0 return −inf in our port. MATLAB would return a complex value there.
- **A fairer test:** a stronger comparison would add a graded model with a jittered threshold or t noise to their model set. We did not test this.

---

# Follow-up: does a fairer model set make the test specific?

**Verdict: FIX WORKS.** Two graded models were added to the comparison: one with a trial-wise jittered threshold (J) and one with Student-t noise (T). With them in, the test called bifurcation in 91% of simulated two-state studies, and in at most 0.7% of studies from every graded generator, including two held out from the design of J and T. The test was sealed and run once, with no fallbacks.

- **Prereg:** `docs/prereg/2026-11-25_bifurcation_extended_model_set.md`, sealed 2026-11-25T23:26:07Z (40d99e9).
- **Script:** `extended.py`, which imports the sealed `audit.py` unchanged.
- **Outputs:** `out_ext/*.json` and `out_ext/summary.json`.
- **Run:** 150 simulated 20-subject studies per row; "call" = Model 3 protected exceedance > 0.95 among the five models. The run stopped at a shell time limit after 5 of 10 cells. The other 5 ran under the prereg's resume rule (same seeds, finished cells kept).

| Generator | Discrete states? | Call rate, 3 models (audit) | Call rate, 5 models | Studies won by each model (0 / 2B / 3 / J / T) | Mean subjects (of 20) best fit by Model 3 / J / T |
|---|---|---|---|---|---|
| Their Model 3 (two states) | yes | 1.00 | **0.91** (≥ 0.80 ✓) | 0 / 0 / 149 / 1 / 0 | 13.7 / 5.1 / 0.7 |
| Their Model 2B | no | 0.00 | 0.00 | 0 / 147 / 0 / 0 / 3 | 0.3 / 0.1 / 5.9 |
| Threshold jitter, SD 0.5 | no | 0.01 | 0.00 | 0 / 5 / 1 / 141 / 3 | 3.5 / 9.2 / 3.2 |
| Threshold jitter, SD 1.0 | no | 0.74 | **0.00** | 0 / 1 / 21 / 128 / 0 | 5.7 / 9.0 / 2.7 |
| Threshold jitter, SD 1.5 | no | 0.98 | **0.007** | 0 / 0 / 51 / 99 / 0 | 7.6 / 8.5 / 2.1 |
| Skewed noise (gamma) | no | 0.04 | 0.00 | 0 / 0 / 0 / 0 / 150 | 0 / 0 / 20 |
| Heavy-tailed noise (t, 4 df) | no | 0.67 | **0.00**\* | 0 / 0 / 0 / 0 / 148 | 0 / 0 / 20 |
| Threshold drift across blocks | no | 0.27 | 0.00 | 0 / 0 / 3 / 145 / 2 | 4.8 / 9.2 / 3.2 |
| Held out: jitter SD 1.0 + t(4) noise | no | not run | 0.00 | 0 / 0 / 0 / 0 / 150 | 0 / 0 / 20 |
| Held out: trial-wise gain (lognormal) | no | not run | 0.00 | 0 / 0 / 0 / 0 / 150 | 0 / 2.1 / 13.0 |

\*Two studies had a non-finite log-likelihood and count as no call. "Studies won" counts the model with the highest protected exceedance, whether or not it passed 0.95.

## What it means

- **The audit's false positives go away once graded models that can express jitter or heavy tails are allowed to compete.** The fix holds on the two held-out generators, which neither J nor T was built for. That matters most for the claim that the fix generalises.
- **Real two-state data still come out as two states, at a modest cost.** Recall fell from 1.00 to 0.91, because J can mimic two states (it nests them as a limit). On two-state data J was the best fit for about 5 of 20 subjects per study.
- **The margin is thinnest at large jitter.** At jitter SD 1.5, Model 3 had the highest exceedance in 51 of 150 studies, yet passed 0.95 in only one. At the subject level, Model 3 and J were close (7.6 vs 8.5 subjects).
- **A practical rule follows from this simulation:** a single-trial bifurcation claim should include at least a jittered-threshold graded model and a heavy-tailed graded model in the comparison.

## Limits

- One signal size (max-level mean 2 noise SDs), 150 trials per level and 20 subjects, all as in the audit. The rates may differ at other designs; a design-matched gate is part of the real-data prereg.
- One time window. Their analysis spans many windows.
- A pass is relative to these ten generators. It does not cover every graded mechanism.
- This is a property of the method under simulation. It says nothing about whether the original data are two-state.
