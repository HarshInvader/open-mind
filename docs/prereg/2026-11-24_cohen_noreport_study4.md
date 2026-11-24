# Pre-registration (DRAFT, not sealed): does the seen/unseen VAN difference need a report? (Cohen et al. 2024, no-report block, SOA 50 ms)

Agent: Open Mind thread   Date: 2026-11-24   Status: DRAFT. Parked until the owner approves a download exception. No no-report EEG is on disk; nothing below has touched it.

- **Builds on:** the sealed fixed-SOA study (`2026-11-24_cohen_fixed_soa_killtest.md`). In report trials at SOA 50 the VAN (PO9/PO10, 140–200 ms) was −1.16 µV more negative on seen trials, in 22 of 24 held-out subjects.
- **Design simulations (simulated data only):** `experiments/cohen_fixed_soa/study4_sim.py`, `study4_sim2.py`; outputs `out/study4_sim.json`, `out/study4_sim2.json`. Parameters come from the report trials (40 subjects: seen rate 0.53 ± 0.16, seen − unseen −1.42 µV, trial SD 4.45 µV, about 129 no-report SOA-50 trials each).

## 0. Question

- **What Cohen et al. tested:** in the no-report block the VAN average rose up to SOA 50 and then plateaued. They never tested it against awareness there, because there are no answers.
- **Our question:** on no-report SOA-50 trials, does the VAN look like a mix of seen-like and unseen-like trials, in the same proportion as in report trials? Or does every trial look unseen-like?
  - **AWARE-like:** the seen-like VAN shows up without report, so the report-block difference is not a product of reporting.
  - **REPORT-like:** the difference needs the report task.

## 1. What the simulations ruled out (why the 130 MB read alone is not enough)

- **Mixture share from the trial distribution (S1):** not identifiable. Single-trial d′ is about 0.3. The estimated share is 0.28 under AWARE and 0.25 under REPORT, with SD 0.05.
- **Position of the no-report mean on the report seen–unseen axis (S2):** right on average (0.53 under AWARE, −0.02 under REPORT). But a 1 µV block offset moves it by about 0.75 units, more than the whole AWARE–REPORT gap.
  - **Why an offset is likely:** the no-report block has a different task, a different attention state, and is recorded at a different time. Nothing in the no-report face trials alone can separate that from the effect.
- **Across-subject covariation with the report seen rate (S3):** fake-positive. It reaches p < .05 in 67–71% of REPORT runs, because both sides share the noise of the unseen-mean estimate.
- **Label-free covariation (S4):** has no power. The slope is attenuated to about −0.18 under REPORT, against an expected −1, with SE 0.34.
- **Conclusion:** the default ask (no-report SOA-50 face trials only, −100 to +300 ms, 129,628,800 bytes) cannot give a kill test that survives a block offset. A reference condition present in both blocks is needed.

## 2. Primary statistic: double difference with mask-only trials

- DD_s = (no-report face50 − no-report mask-only) − (report face50 − report mask-only), on the VAN window, per subject.
- Mask-only trials have no face, so seeing is near zero in both blocks. A block offset common to face and mask-only trials cancels.
- **Scaling:** DD_norm = mean(DD_s) / −mean(π_s · Δ̂_s), where Δ̂_s and π_s come from the sealed report trials.
  - AWARE predicts 0; REPORT predicts 1; a half-size effect predicts 0.5.
- **Inference:** a 95% bootstrap CI over subjects (10,000 resamples, numerator and denominator resampled together).

## 3. Decision rule

- **REPORT-like:** CI lower bound > 0.5.
- **AWARE-like:** CI upper bound < 0.5.
- **INCONCLUSIVE:** otherwise.
- **INVALID:** the alignment check of the sealed study fails on the no-report face trials (same frozen criterion, all 40 subjects, label-free), or fewer than 30 subjects have ≥ 40 clean trials in every cell.

## 4. Controls (kept from the sealed study)

- **P1 null control (100–140 ms, sealed electrodes):** the same DD_norm statistic, scaled by the VAN denominator. If its 95% CI excludes 0, every target result is flagged, as in the sealed rule.
- **P3b window (300–500 ms):** reported descriptively only. The no-report task has no response, so P3b differences are expected.

## 5. Simulated calibration (500 runs per cell, block offset ~ N(β, 1 µV), face/mask-only offset mismatch τ_int)

| World | Mask-only trials per block per subject | τ_int | DD_norm mean | SE | Called AWARE-like | Called REPORT-like |
|---|---|---|---|---|---|---|
| AWARE | 60 | 0.3 | −0.01 | 0.23 | 0.61 | 0.00 |
| AWARE | all (~154) | 0.3 | 0.00 | 0.19 | 0.79 | 0.00 |
| AWARE | all | 0.6 | −0.01 | 0.22 | 0.65 | 0.00 |
| HALF | all | 0.3 | 0.50 | 0.19 | 0.04 | 0.02 |
| REPORT | 60 | 0.3 | 1.01 | 0.23 | 0.00 | 0.58 |
| REPORT | all | 0.3 | 1.00 | 0.19 | 0.00 | 0.69 |
| REPORT | all | 0.6 | 1.00 | 0.22 | 0.00 | 0.59 |

- **Wrong calls:** 0 of 500 in every cell (AWARE never called REPORT-like, and the reverse). The block offset β (0 or 1 µV) does not change any row.
- **Power:** 0.6–0.8 for the correct call. A half-size effect is almost always INCONCLUSIVE, as it should be.
- **Before sealing, on the real data:** repeat this calibration with planted mixtures built from real no-report and mask-only trials (label-free), and shuffled-label runs.

## 6. Byte options (all −100 to +300 ms, 63 channels, 25,200 bytes per trial)

| Option | Trials | Bytes | Gives |
|---|---|---|---|
| A (current default ask) | no-report face SOA 50: 5,144 | 129,628,800 | S2 only, which a block offset confounds. Not a kill test. |
| **B (recommended)** | A + 60 mask-only per subject per block: 4,800 | 250,588,800 | DD, power about 0.6 |
| C | A + all mask-only: 12,344 | 440,697,600 | DD, power about 0.7–0.8 |

## 7. What it cannot say

- **No answers in the no-report block.** "AWARE-like" means the VAN mix matches the report-block seen rate. It does not prove those faces were seen.
- **Seeing may differ between blocks.** If the seen rate differs between blocks (task and attention differ), DD measures that as well as any report effect. Cohen et al. hold the stimuli fixed but cannot check this either.
- **An imperfect reference.** Mask-only trials are a reference only if the block offset is shared between face and mask-only trials. τ_int above models the part that is not.
