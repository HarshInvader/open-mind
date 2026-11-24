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
