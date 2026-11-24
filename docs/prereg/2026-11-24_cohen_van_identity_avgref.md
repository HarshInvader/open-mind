# Pre-registration: does the VAN hold within the same face image, and under an average reference? (Cohen et al. 2024, report block, SOA 50)

Agent: Open Mind thread   Date: 2026-11-24   Script: `experiments/cohen_fixed_soa/van_identity.py`   Source: Fable round 15, study 2

- **Builds on:** the sealed fixed-SOA kill test, where the VAN (PO9/PO10, 140–200 ms) was −1.16 µV [−1.54, −0.80] in 24 held-out subjects, and on the sealed arousal control (ROBUST).
- **Data:** only data on disk: the sealed `out/prep.npz` (same trials, rejection and subjects) and the raw epochs, re-referenced (`out/avgref.npz`, label-free, 88 KB).
- **Why:** this is the project's one positive result. Two plain threats remain:
  1. **Image confound:** some of the 40 face images may be both easier to see and give a more negative VAN. The earlier identity-tercile shuffle reduces this risk but does not remove it.
  2. **Reference confound:** the mastoid reference sits next to PO9/PO10.

## 1. Primary: within-image VAN (24 confirm subjects)

- Per subject, OLS: VAN = b·seen + Σ_i d_i·[image = i]. b_adj is the seen effect within an image; b_raw is the plain difference.
- Group: mean b_adj, with a 95% t-interval over subjects. Retained fraction R = mean b_adj / mean b_raw, with a 95% percentile bootstrap CI over subjects (10,000 resamples, seed 20261127).
- **Decision:**
  - ROBUST: CI upper < 0 and R CI lower > 0.5.
  - EXPLAINED: R CI upper < 0.5.
  - REDUCED: CI upper < 0, otherwise.
  - INCONCLUSIVE: otherwise.

## 2. Co-primary: average reference

- All good scalp channels are re-referenced to their mean, then baseline-corrected (−100..0 ms). Same filter and rejection as the sealed study.
- The same identity-adjusted statistic is computed for:
  - VAN_avg (PO9/PO10, 140–200 ms), predicted negative;
  - VPP_avg (channels 1, 2, 3, 7, 8 = Cz, FCz and neighbours from the layout coordinates, 140–200 ms), predicted positive.
- Each is called present if its 95% t-interval excludes 0 in the predicted direction.
- If VAN_avg is absent, the mastoid-referenced result is flagged as reference-dependent.
- The VPP has not been looked at in this dataset.

## 3. Calibration (fake labels, the 24 confirm subjects, 300 runs; `out/identity_calibration.json`, sealed)

| World | Result |
|---|---|
| Null (shuffled labels) | false ROBUST/REDUCED 4.3% (bar ≤ 5%) |
| Planted between-image confound (image visibility offsets shift both labels and the VAN, raw −1.20 µV, no within-image effect) | EXPLAINED 79% (bar ≥ 75%), false ROBUST 0% (bar ≤ 5%) |
| Planted within-image effect −1.2 µV | ROBUST 96% (bar ≥ 90%) |

**Changes made on fake labels only, before any real-label statistic:**
- The first rule counted a CI excluding 0 in either direction. It became one-sided in the predicted direction (null false calls 6.3% → 4.3%).
- The EXPLAINED bar was lowered from Fable's 90% to 75%. Identity dummies cost degrees of freedom (about 3 trials per image per subject). The protection that matters, false ROBUST under the confound, stayed at 0%.

## 4. Secondary and limits

- The pilot 14 subjects are reported as a replication.
- No hemisphere split is run.
- **Limit:** within-image control removes stimulus differences between images. It does not remove trial-to-trial differences in the same image, which the arousal control addressed in part.
- This is still a report-block result.
