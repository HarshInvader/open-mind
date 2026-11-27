# Round 19 #3: is an unseen Gabor's bilateral VAN the same as target-absent? (design + kill test; not sealed)

Status: draft, 2026-11-26. The kill test runs first and is label-free (no EEG trial is paired with a seen/unseen answer).
Fable (pre-seal review of #2, 2026-11-26) ranked this third and expects it to fail: about 36 correct rejections per
subject, and the same R criterion already failed on Cohen (round 19 #1). If it fails, it is dropped: no re-cut.

## 1. Question
ds006171 no-cue task (Melcón et al. 2024, CC0). In the bilateral ROI (PO7/PO8, P7/P8, O1/O2 mean) at 180–280 ms:
R = (miss − CR) / (hit − CR). Miss = Gabor shown, reported unseen; hit = Gabor reported seen; CR = catch trial (no Gabor) reported unseen.
- R near 0: the unseen Gabor leaves no VAN-window trace (all-or-none at this stage).
- R well above 0: graded, or stimulus residue (not separable here: unseen orientation accuracy is at chance, and the window overlaps the sensory N1).
- Prior art: the GitHub reanalysis (itsxiatong/eeg-awareness-ds006171) tested unseen = catch for the P3b only. No VAN-window test exists (PRIORART.md).

## 2. Rivals and predictions (from van_allornone/DESIGN.md §2, same derivation)
| Rival | R |
|---|---|
| All-or-none with lapses λ ≤ 0.10 | 0.02–0.12 |
| Graded, report thresholds the VAN's own variable, σs 1–2 | 0.49–0.19 |
| Stimulus residue | > 0, any size |

## 3. Calls (as in round 19 #1; cut 0.20)
Group ratio of means over subjects, percentile bootstrap 95% CI (2,000 in the kill test, 10,000 in a real run).
- Upper bound < 0.20: ALL-OR-NONE-COMPATIBLE. Lower bound > 0.20: NOT ALL-OR-NONE AT THE VAN WINDOW. Else INCONCLUSIVE.

## 4. Kill test (label-free; criteria fixed before running)
- **Data:** `../ds006171_van/out/prep/<sub>.npz`, the label-blind prep of 2026-11-26 (`bil`, `keep`, `code`). All 35 subjects; no HEOG subject exclusion (a bilateral mean is not side-specific), but trial-level rejection as prepped. A subject is used if it keeps ≥ 20 pseudo-CR trials and ≥ 30 pseudo hits and ≥ 30 pseudo misses.
- **Counts (behaviour only):** per subject from events.tsv: hits = Gabor trials followed by 124, misses = Gabor followed by 125, CR = catch followed by 125. Scaled to kept trials.
- **Noise:** each subject's kept Gabor window means, centred, randomly split into pseudo hits/misses at the real proportion; kept catch window means, centred, subsampled to the CR count.
- **Plant:** hit − miss per subject hm_s ~ N(−0.69, sd_true) µV, where −0.69 µV is the reanalysis's bilateral seen − unseen difference (−1.26 vs −0.57 µV, dz −0.46, N 31). sd_true = sqrt(max(0, (0.69/0.46)² − v)), with v the mean sampling variance of the synthetic hit − miss difference, so the total between-subject SD matches the sourced dz. Means: CR 0, miss R·hm_s/(1 − R), hit hm_s/(1 − R).
- **Plants:** R = 0, 0.32 (graded σs 1.5), 0.40.
- **Pass (all required; same as round 19 #1):** median 95% half-width of R at R = 0 ≤ 0.12; correct calls ≥ 80% at R = 0 (ALL-OR-NONE-COMPATIBLE) and at R = 0.40 and 0.32 (NOT ALL-OR-NONE); wrong-direction calls ≤ 5% at every plant. 200 runs.
- **Fail:** drop. No change to window, ROI, cut, plant or criteria.

## 5. Kill test result: FAIL, DROPPED (2026-11-26)
`killtest.py`, 200 runs (`out/killtest.json`). 26 of 35 subjects met the trial minimums; median 34.5 pseudo-CR trials per subject; sd_true 1.34 µV (sampling SD of hit − miss 0.67 µV).

| Plant R | Correct | Wrong | Inconclusive | Median half-width |
|---|---|---|---|---|
| 0 | 0.24 | 0.00 | 0.76 | 0.46 |
| 0.32 | 0.195 | 0.005 | 0.80 | 0.28 |
| 0.40 | 0.51 | 0.00 | 0.49 | 0.21 |

Every criterion except wrong calls fails; the half-width at R = 0 is about 4× the 0.12 bar. The cause is a small denominator (hit − CR is near the sourced −0.69 µV) against about 35 CR trials. Dropped as pre-stated: no re-cut. Nothing original that is testable remains in ds006171's no-cue task at this power.
