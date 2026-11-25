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

---

# Follow-up 2: would weak two-state data look "unimodal"? (signal-strength grid)

**Verdict: BLIND ZONE REACHES AUC 0.70.** We simulated true two-state data and ran it through the authors' 3-model comparison. Until the strongest level is decoded at an AUC of about 0.85, the unimodal model often wins, and often wins confidently. The run was sealed (03:31:22Z, aaa6458) and run once. The validity check passed: at the strongest grid point Model 3 was top in 100/100 studies, matching the sealed audit.

- **Prereg:** `docs/prereg/2026-11-25_bifurcation_snr_timing.md`.
- **Script:** `snr_timing.py`, which imports the sealed `audit.py` unchanged.
- **Outputs:** `out_snr/m3_*.json` and `out_snr/summary.json`.
- **Setup:** 100 simulated 20-subject studies per row, 150 trials per level. AUC is the separation between the strongest level and no target in the simulated window values.

| Max-level AUC | Two-state data: Model 3 top | 2B top | Model 3 called (> 0.95) | **2B called (> 0.95)** | Graded data (Model 2B shape): 2B top |
|---|---|---|---|---|---|
| 0.57 | 12 | 87 | 0 | 0 | 95 (AUC 0.56) |
| 0.64 | 9 | 91 | 2 | **63** | 99 (0.62) |
| 0.70 | 45 | **55** | 11 | **37** | 99 (0.68) |
| 0.76 | 57 | 43 | 28 | 13 | 100 (0.72) |
| 0.85 | 99 | 1 | 96 | 0 | 100 (0.80) |
| 0.91 | 100 | 0 | 100 | 0 | 100 (0.86) |

Counts are per 100 studies. No study was non-finite.

- **Decision rule (sealed):** the result is BLIND ZONE if 2B is top in more than 50% of two-state studies at some grid point with AUC ≥ 0.69. At AUC 0.70, 55 of 100 meets the rule. That margin is within sampling noise of 50. The rest of the table does not depend on that one cell:
  - at AUC 0.64, 2B is top in 91/100 two-state studies and is *called* with pxp > 0.95 in 63/100;
  - Model 3 does not reliably win until AUC is about 0.85.

## What it means

- **Sergent et al. 2021 read the two weak-signal periods as findings.** The unimodal model "showed the highest probability" from 0 to 250 ms and from 700 to 900 ms. They described early processing as non-linear "but … the underlying dynamics were unimodal".
- **In this simulation, a genuine two-state signal whose strongest level decodes below about AUC 0.75–0.85 produces that same picture.** It often produces a confident unimodal call.
- **So a unimodal win at modest decoding strength cannot, on its own, show unimodal dynamics.** It is what the comparison returns for weak data of either kind.
- **What this does not show:**
  - It does not show that early processing is two-state.
  - It does not show that their early windows were weak enough to fall in the blind zone. Their window AUCs are in their Fig. 2 source data, which we have not fetched.
  - Their late-window Model 3 result is not affected, because strong signals are classified correctly.

## Limits

- **Separation-scaled weakness only.** Two states that are close together. A weak signal from rare but well-separated high-state trials would look more mixture-like.
- **AUC definition.** Ours is computed on window values. Theirs is per time sample after a 10 Hz low-pass, so the two are comparable but not identical.
- **One design.** 20 subjects and 150 trials per level, as in their study.
- **Pending.** The 5-model secondary (with J and T) is still running and will be added.

---

# Follow-up 3: design gate for the real-data test (Cohen report block). FAIL at the reference size; stopped early

The real-data prereg (`docs/prereg/2026-11-25_bifurcation_real_data_cohen.md`, sealed) requires a simulation gate at the real design before any byte is fetched. The design is 38 subjects with the real per-level trial counts ("full", 1.12 GB) or 64 per level ("half", 0.54 GB). The gate PASSES when B recall is ≥ 0.80 and every graded cell is ≤ 0.10, the same rule as the sealed simulation. Script: `gate_design.py`. Outputs: `out_gate/*.json` and `out_gate/summary.json`. 100 studies per cell.

**Results at DMAX 2 (the sealed simulation's signal size).** Call rate is Model 3 pxp > 0.95 in the 5-model comparison. Winner counts are [non-finite, M0, 2B, M3, J, T].

| Cell | Full: call rate | Full: winners | Half: call rate | Half: winners |
|---|---|---|---|---|
| B_bifurcation (recall) | **0.99** | [0,0,0,100,0,0] | **0.62** | [0,0,0,76,24,0] |
| G_jitter_mid | 0.02 | [0,0,1,12,87,0] | 0.01 | [0,0,1,13,86,0] |
| G_jitter_hi | **0.18** | [0,0,0,38,62,0] | 0.06 | [0,0,0,25,71,4] |
| G_heavy | 0 | [3,0,0,0,0,97] | 0 | [2,0,0,0,0,98] |
| H_jitter_t | 0 | [5,0,0,0,0,95] | 0 | [2,0,0,0,0,98] |
| H_gain | 0 | [0,0,0,0,0,100] | 0 | [0,0,0,0,0,100] |
| **Gate** | **FAIL** (specificity) | | **FAIL** (recall) | |

- **Stopped early by coordinator decision (2026-11-25).** Neither byte option passes at the reference signal size. That answers the byte question, so nothing is fetched.
- **Not run:** DMAX 1 and DMAX 3. A later DMAX 3 run on the full option alone is a possible follow-up. It would show whether a stronger real signal would pass.
- **Finding about the method:** with more subjects, the random-effects comparison loses specificity against large-jitter graded data.
  - At 20 subjects and 150 trials per level (sealed extended simulation), G_jitter_hi was called 0.007.
  - At 38 subjects with the real counts, it was called **0.18**.
  - The winner counts look alike: Model 3 had the top exceedance in 51/150 and 38/100 studies. More subjects make a narrow Model 3 edge more often pass 0.95.
  - So the FIX WORKS result holds for the 20-subject design. It does not carry over to larger samples without a design-matched check.
- **Half option:** it loses recall because J absorbs true two-state subjects when there are 64 trials per level.
