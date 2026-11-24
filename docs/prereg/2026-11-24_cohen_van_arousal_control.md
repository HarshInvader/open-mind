# Pre-registration: does the seen/unseen VAN difference survive arousal and attention covariates? (Cohen et al. 2024, report block, SOA 50 ms)

Agent: Open Mind thread   Date: 2026-11-24   Script: `experiments/cohen_fixed_soa/arousal_control.py`

- **Builds on:** the sealed fixed-SOA kill test (`2026-11-24_cohen_fixed_soa_killtest.md`). The VAN (PO9/PO10, 140–200 ms) was −1.16 µV [−1.54, −0.80] more negative on seen trials in the 24 held-out subjects. P1 (100–140 ms) was flagged (AUC 0.525, p 0.03).
- **Data:** only data already on disk: the sealed `out/prep.npz` (same trials, rejection, bad channels and subjects), the raw epochs for prestimulus SD, and `trials.csv` for behaviour. No new bytes.
- **Scope:** one sealed run, time-boxed. This checks our own result for robustness. It is not a new claim.

## 1. Question

At a fixed stimulus, is the VAN difference between seen and unseen trials explained by fluctuations in arousal or attention that change both seeing and the ERP? The worry: on attentive or alert trials, faces are seen more often and early visual responses are larger, with no seeing-specific VAN.

## 2. Covariates (named before any adjusted statistic was computed)

| Name | What it indexes | Definition |
|---|---|---|
| local | attention state around the trial | mean of (seen − subject's seen rate at that SOA) over the 10 report face trials before and the 10 after, all SOAs, current trial excluded |
| prev | sequential state | the same residual for the previous report face trial |
| order | time on task / fatigue | rank of the trial in the session |
| p1 | early sensory gain | P1 amplitude, 100–140 ms, sealed P1 channels |
| prestd | prestimulus state (alpha) | SD over −100..0 ms, VAN + P1 channels (bad channels dropped), averaged over channels |

The epochs start at −100 ms, so a proper prestimulus alpha-power estimate is not possible; prestd is a crude stand-in. Response time is not used: it comes after the decision and depends on seeing.

## 3. Statistic

- Per subject, OLS: VAN = a + b·seen + Σ c_k·z(cov_k). b_adj is the seen effect adjusted for all five covariates. b_raw is the plain seen − unseen difference.
- Group: mean b_adj over the 24 eligible held-out (confirm) subjects, with a 95% t-interval over subjects. Retained fraction R = mean b_adj / mean b_raw, with a 95% percentile bootstrap CI over subjects (10,000 resamples, seed 20261125; numerator and denominator resampled together).
- Calibration note: the first calibration used a percentile bootstrap CI for b_adj, and null false calls came out at 5.7%. Before any real-label statistic was computed, b_adj's CI was switched to the t-interval (3.7%).

## 4. Decision rule

- **ROBUST:** b_adj CI upper < 0 and R CI lower ≥ 0.5.
- **REDUCED:** b_adj CI upper < 0, R CI lower < 0.5.
- **EXPLAINED:** b_adj CI upper ≥ 0 and R CI upper < 0.5.
- **INCONCLUSIVE:** otherwise.
- **No run** unless calibration passes (section 5).
- The pilot 14 subjects are reported as a secondary replication. Also reported, descriptively: each covariate's seen − unseen difference (z units), and b_adj with each covariate alone.

## 5. Planted checks (fake labels only, the 24 confirm subjects, 300 runs each)

- **Null:** seen labels shuffled within subject. False ROBUST or REDUCED must be ≤ 5%.
- **Planted confound:** labels generated from the covariates (logistic, weight 0.5 per z-scored covariate, the subject's real seen rate). The VAN is shifted by a covariate combination scaled so that seen − unseen ≈ −1.16 µV, with no direct effect of the label. False ROBUST must be ≤ 5%; EXPLAINED should dominate.
- **Planted direct effect, clean:** shuffled labels plus a direct −1.16 µV label effect on the VAN. Gives power for ROBUST.
- **Planted direct effect, coupled (descriptive):** labels from the covariates plus the direct −1.16 µV. The real VAN's own link to the covariates adds to the raw difference, so the true R is below 1 by construction.

### Calibration results (sealed with this file)

| World | ROBUST | REDUCED | EXPLAINED | INCONCLUSIVE |
|---|---|---|---|---|
| Null (shuffled) | 0.7% | 3.0% | 0 | 96.3% |
| Planted confound (raw −2.20 µV, direct 0) | 0 | 1.7% | 98.3% | 0 |
| Direct, clean | 100% | 0 | 0 | 0 |
| Direct, coupled (raw −2.20, adjusted −1.13 µV) | 4.7% | 95.3% | 0 | 0 |

- **Reading rule fixed now:** the coupled world shows REDUCED can occur with a full-size direct effect when seeing covaries strongly with the covariates. So a REDUCED verdict is read using the adjusted µV: if b_adj's CI includes −1.0 µV, the result is "compatible with a full direct effect"; if not, "smaller than the sealed effect".
- Results go in `out/arousal_calibration.json` and are sealed with this file and the script.

## 6. What it cannot say

- It removes only the confounds the five covariates measure. A state that changes seeing and the VAN but none of these measures is not controlled. The planted-confound check assumes the confound acts through the measured covariates, so it is optimistic.
- p1 and the VAN are adjacent in time and on overlapping posterior sites. Adjusting for p1 may remove some real seeing-related signal, so the check is conservative for ROBUST.
- Nothing here is report-free.
