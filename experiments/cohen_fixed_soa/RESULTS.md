# Fixed-SOA seen vs unseen on Cohen et al. 2024: result (2026-11-24)

**Verdict (sealed, 24 held-out subjects): VAN PASS, N2 KILLED, P3b gate passed. The P1 control flag fired.**

The same masked face was shown at SOA 50 ms and only the report differed. On those trials:
- the posterior VAN (PO9/PO10, 140–200 ms) was more negative on seen trials in 22 of 24 subjects;
- the authors' fronto-central N2 window (250–290 ms) did not separate seen from unseen.

- **Prereg:** `docs/prereg/2026-11-24_cohen_fixed_soa_killtest.md`, sealed 2026-11-24T18:18:22Z (`docs/prereg/HASHES.txt`, commit 9bf289c), run once afterwards.
- **Data:** Cohen, Dembski, Ortego, Steinhibler & Pitts 2024, *Cerebral Cortex*, doi:10.1093/cercor/bhae415, raw EEG on OSF 6d5av.
  - The node states no licence. The data was analysed locally and is not redistributed. The corresponding author was asked about reuse terms on 2026-11-24.
- **Outputs:** `out/result.json`, `out/calibration.json`, `out/align.json`, `out/eligibility.csv`.

## Confirmatory set (24 subjects; the authors' 15 window-defining subjects excluded)

| Component | Role | Mean AUC (predicted direction) [95% CI] | Seen − unseen, µV [95% CI] | p (max of perm, sign-flip) | Subjects in predicted direction | Outcome |
|---|---|---|---|---|---|---|
| P3b 300–500 ms | gate | 0.606 [0.576, 0.636] | +3.28 [+2.37, +4.14] | 0.0001 | 22/24 | gate passed |
| VAN 140–200 ms, PO9/PO10 | target | 0.585 [0.560, 0.611] | −1.16 [−1.54, −0.80] | 0.0001 (Holm 0.0002) | 22/24 | **PASS** |
| N2 250–290 ms, authors' ROI | target | 0.498 [0.467, 0.529] | +0.15 [−0.94, +1.20] | 0.67 (Holm 0.67) | 10/24 | **KILLED** |
| N2 frontal (P3b electrodes removed) | secondary | 0.494 | +0.25 [−0.85, +1.30] | 0.78 | 9/24 | no effect |
| P1 100–140 ms | control | 0.525 (seen > unseen) | +0.32 [−0.13, +0.75] | perm 0.032, sign-flip 0.036 | – | **flag** |
| N2 electrodes 0–60 ms | control | 0.488 | −0.43 [−1.07, +0.12] | 0.29 | – | no flag |

**Sensitivity analyses** (reported, not part of the verdict):
- **Shuffles also stratified by face visibility tercile:** unchanged. VAN AUC 0.585 (p 0.0001); N2 0.498 (p 0.55).
- **Late answers only** (> 500 ms, 22 subjects, so the motor response falls outside the windows): VAN 0.584, −1.12 µV (p 0.0001); N2 0.500, +0.02 µV (p 0.67); P3b 0.600.

## Pilot set (14 subjects; secondary replication)

- **VAN PASS:** −2.04 µV [−3.12, −1.07], AUC 0.610, 13/14 subjects, Holm p 0.001.
- **N2 INCONCLUSIVE:** −1.24 µV [−3.17, +0.58], AUC 0.534. p_perm is 0.009 but p_signflip is 0.09, so it does not pass.
- **P3b gate passed** (+2.86 µV). No control flags.
- **Caveat:** the authors chose their windows on these subjects, though not using this contrast.

## How to read it

- **The VAN at a fixed stimulus.** With the stimulus held fixed, a posterior negativity at 140–200 ms tracks whether the face was reported seen.
  - The effect is about 1.2 µV and appears in 22 of 24 held-out subjects.
  - It survives controls for face identity and for motor responses.
  - This replicates Navajas et al. 2013 (larger N170 for seen faces at fixed noise) under backward masking, on independent data.
  - It is earlier than the roughly 270 ms divergence of Del Cul et al. 2007 and the "no divergence before about 270 ms" view (ledger C35).
- **Against Cohen et al.'s VAN conclusion (stated exactly).**
  - **What they tested:** only the shape of the SOA curve, using condition averages over 5 SOAs (25 subjects).
  - **What they found:** the N170/VAN followed "a pattern of amplitude increase that was neither linear nor bifurcated" in both conditions.
    - Report condition: it rose from 17 to 33 ms (behaviour barely changes there), was flat from 50 to 67 ms (behaviour goes from 51.9% to 86.8% seen), and dipped at 83 ms.
    - No-report condition: it grew up to SOA 50 and then plateaued.
    - They conclude it "may not be a candidate signature of perceptual awareness, though more research is called for".
  - **What they did not test:** seen vs unseen at a fixed SOA, or anything at the single-trial level.
  - **Our result** is a different test. Within SOA 50, the same window separates seen from unseen in 22 of 24 held-out subjects. A VAN whose average does not follow the sigmoid across SOAs can still track trial-to-trial seeing at a fixed stimulus. So their conclusion does not hold at the trial level in the report condition.
  - **What we do not claim:** that the VAN tracks awareness without report. They found it present in no-report too, but never tested it against awareness there. That is study 4, which is waiting on data.
- **The N2 window.** The authors' N2 window does not carry a seen/unseen difference in report trials: the CI excludes a predicted effect of 1 µV or more.
  - **This is not news.** The authors already report that the N2 did not appear in the report condition, and blame P3b overlap. Removing the electrodes shared with the P3b changes nothing (+0.25 µV).
  - It says nothing against their no-report claim. Every trial here has a report.
- **The P1 flag.** Seen trials are slightly more positive at 100–140 ms (AUC 0.525, under a third of the VAN's distance from 0.5; the µV CI includes zero).
  - Under the sealed rule, this flags every target result: part of what separates seen from unseen may start before the VAN, for example in attention or pre-stimulus state.
  - The P1 shift is positive and the VAN effect is negative, so the VAN effect cannot be the P1 difference carried forward. That is a descriptive observation, not a sealed test.
  - The flag stands. The pilot set shows no P1 difference (AUC 0.501).
- **What it cannot say:**
  - Every trial has a report, so nothing here shows the VAN is report-free.
  - "Seen" includes guesses and criterion effects. Confidence was not recorded.

## Original vs revised alignment check (required by the coordinator)

- **The original label-free criterion failed on the first 11 subjects:** an occipital N1 below baseline at 140–200 ms.
  - The timing was right: the response starts at about 92 ms, peaks at about 142 ms and dips at about 182 ms.
  - But the response to the first mask (onset 50 ms) overlaps the face N1 and keeps the window positive. On all 40 subjects that window is +4.07 µV.
- **The revised criterion was set before sealing, on pooled trials only:** onset 60–120 ms, peak 100–160 ms, 100–160 ms mean above baseline.
  - It passed on all 40: onset 92 ms, peak 142 ms, +4.21 µV, t = 11.5, p = 5e-14.

## Data read

- **This study:** 5,079 epochs, exactly 223,983,900 bytes.
  - One partial subject was lost in a server restart and re-read. That adds at most about 5.9 MB, uncounted (the largest subject is 133 trials × 44,100 bytes).
- **Headers and markers:** 9,812,193 bytes.
- **Project total with ds001810:** 1,488,284,157 bytes counted, at most about 1.494 GB with the lost partial. This is within the 1.5 GB budget.

## Robustness: arousal and attention covariates (sealed 2026-11-24T20:07:59Z, commit ec0a8f7; run once)

Prereg `docs/prereg/2026-11-24_cohen_van_arousal_control.md`; script `arousal_control.py`; output `out/arousal_result.json`.

- **Question:** is the seen/unseen VAN difference a by-product of trial-to-trial arousal or attention, which could change both seeing and the early visual response?
- **Covariates, named before the run:**
  - local seen rate over neighbouring trials, adjusted for SOA;
  - previous-trial seen;
  - time on task;
  - P1 amplitude;
  - prestimulus posterior SD.
- **Model:** per-subject OLS of the VAN on seen plus all five covariates.
- **Verdict: ROBUST.**
  - Confirm, n = 24: adjusted −1.20 µV [−1.63, −0.77], against −1.16 µV unadjusted.
  - Retained fraction 1.03 [0.90, 1.17]; 21 of 24 subjects negative.
  - Pilot, n = 14: ROBUST, −1.69 µV, retained 0.83 [0.62, 1.05].
- **The covariates did carry state information.**
  - Seen trials sat in stretches with a higher local seen rate (+0.35 z) and followed seen trials more often (+0.21 z).
  - They also came earlier in the session (−0.20 z).
  - Even so, adjusting for them left the VAN effect unchanged.
  - P1 differed little between seen and unseen (+0.07 z). Adjusting for P1 alone made the effect slightly larger (−1.37 µV).
- **Calibration** (fake labels):
  - Null: false ROBUST/REDUCED 3.7%.
  - Planted covariate confound: EXPLAINED 98%, false ROBUST 0%.
  - Planted direct effect: ROBUST 100%.
- **Limits:**
  - Only the measured covariates are controlled. The prestimulus measure is crude, because the epochs start at −100 ms.
  - This is still a report-block result.

## Graded vs arousal vs two-state VAN (report × RT-speed): stopped at the power gate (2026-11-24; never run on real RT)

- **Design:** `rt_gradient.py`, Fable plan item 2.
  - Within each class at SOA 50, split trials at the median response time into fast and slow.
  - Graded evidence predicts a crossover: fast seen trials more negative than slow seen, and fast unseen less negative than slow unseen.
  - Arousal predicts fast trials more negative in both classes. A two-state signal predicts no gradient within either class.
- **Gate 0 (behaviour, other SOAs, pooled medians):** passed informally. Response times show the folded-X pattern:
  - seen responses speed up with SOA, 632 → 552 ms;
  - unseen responses slow down with SOA, 546 → 602 ms.
- **Power gate:** RT shuffled within class keeps the real VAN noise; 0.4 µV within-class gradients were then planted on top, 500 runs.

| Sample | SE of crossover | Crossover detected | Arousal detected | False GRADED / AROUSAL | FLAT reachable |
|---|---|---|---|---|---|
| 24 confirm | 0.35 µV | 0.56 | 0.53 | 0.022 / 0.030 | 0% |
| 38 confirm + pilot | 0.30 µV | 0.71 | 0.73 | 0.016 / 0.026 | 0.8% |

- **Decision:** the bar was 0.8 power for both patterns, so the study stops. With this many trials the test cannot separate graded, arousal and two-state accounts at realistic effect sizes, and it cannot call a flat result.
- **Real RT was never used against the VAN.** The arousal-covariate result above already argues against the arousal account in a different way.
- **Files:** `out/rt_power_confirm24.json`, `out/rt_power.json` (38 subjects).

## Robustness: within the same face image, and under an average reference (sealed 2026-11-24T21:41:49Z, commit 5257fa6; run once)

Prereg: `docs/prereg/2026-11-24_cohen_van_identity_avgref.md`. Script: `van_identity.py`. Output: `out/identity_result.json`.

| Test (24 confirm subjects) | Unadjusted | Identity-adjusted [95% CI] | Retained [95% CI] | Verdict |
|---|---|---|---|---|
| VAN within image (primary) | −1.16 µV | −0.95 [−1.54, −0.36] | 0.82 [0.47, 1.10] | **REDUCED** |
| VAN, average reference | −2.60 | −2.15 [−2.99, −1.30] | 0.83 [0.60, 1.03] | present (ROBUST) |
| Fronto-central VPP, average reference | +0.85 | +0.63 [−0.03, +1.29] | 0.74 [0.07, 1.19] | not present |

- **Pilot replication (14 subjects):**
  - within image: ROBUST, −1.86 µV, retained 0.91;
  - average-reference VAN: ROBUST, −3.68;
  - VPP: present, +1.11 [0.39, 1.82].
- **Reading:**
  - The seen/unseen VAN difference survives within the same face image: its CI excludes 0. The lower bound on the retained fraction (0.47) sits just under the 0.5 bar. So differences between images may account for up to about half of the effect, though the point estimate keeps 82%.
  - The effect is not a mastoid-reference artefact. Under an average reference it is larger (−2.15 µV), as expected, because the mastoid partly picks up the posterior negativity.
  - The fronto-central positive counterpart is not clear in the confirm set (CI touches 0) but is clear in the pilot. That is consistent with one generator seen from both ends, but not shown here.
- **Calibration** (fake labels): null 4.3% false calls; between-image confound EXPLAINED 79% with 0% false ROBUST; within-image effect ROBUST 96%.
- **Limits:**
  - The within-image control removes stimulus differences between images, not trial-to-trial state (the arousal control covers part of that).
  - This is still a report-block result.

## Do stronger earlier showings of a face make it easier to see later? Stopped at the calibration gate (2026-11-25; real statistic never computed)

- **Prereg:** `docs/prereg/2026-11-25_cohen_prior_showings.md`, sealed 2026-11-25T01:41:25Z (a4a6c42). Behaviour only, from `trials.csv`.
- **Question:** at SOA 50, is a face seen more often when more of its earlier showings were strong (SOA 67/83) rather than weak (17/33), with the number of earlier showings held fixed?
- **Calibration** (`out/prior_calibration.json`, 300 runs):

| Check | Result | Bar |
|---|---|---|
| Randomisation null on real responses (per-face strong↔weak swap) | false calls **7.7%** | ≤ 5% ✗ |
| Fake-response null (drift, image offsets, streaks, item practice) | false calls 4.3% | ≤ 5% ✓ |
| Planted 1.5 points per net strong showing | EFFECT+ 92% | ≥ 80% ✓ |

- **Verdict:** the gate failed. The prereg stated no fallback, so the real slope was not computed and will not be.
- **Possible causes:** 23 of 300 runs is about 2 SE above 5%, so it may be chance. It may also be heavy-tailed per-subject slopes making a 40-subject t-interval slightly anti-conservative. We did not investigate further, to avoid tuning on a failed gate.
- **Process note:** the Fable pre-seal review rejected two earlier nulls before calibration. A free permutation doubled the spread of D. A within-quarter permutation left D almost unchanged, which would have leaked the answer.
