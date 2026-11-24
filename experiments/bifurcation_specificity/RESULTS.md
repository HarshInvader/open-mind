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
