# Pre-registration: attentional-blink T2 identification screen, held-out-subject kill test (ds001810)

Agent: Open Mind thread   Task: hypothesis generator, step 1   Date: 2026-11-24

- **Script:** `experiments/hypothesis_generator/ab_killtest.py`.
- **Sealed together, before any label–EEG statistic is computed on real labels:**
  - this file;
  - the script;
  - `ab_out/split.json` (split and frozen decoder channels);
  - `ab_out/eligibility.csv`;
  - `ab_out/prep_hashes.json` (sha256 of the two per-half data files).
- **Command:** `.venv/bin/python -I experiments/rules/evidence.py seal <files>`.
- **Before sealing:** the eligibility step reads label counts (behaviour only, already public in `ab_trial_counts.csv`). Calibration reads labels only to shuffle them. No real label–EEG association is computed.
- **Pre-seal review:** a Fable pre-seal review (2026-11-24) found that FAIL was impossible in the first draft, and that the null, baseline and sealing were weak. This version applies its must-fix list, as section 11 records.

## 0. What this is and is not

- **Outcome: T2 identification**, correct vs incorrect, on lag-3 trials with T1 correct. It is not seen vs unseen: "incorrect" includes T2 seen but named wrongly, and "correct" includes guesses. Every trial ends in a report. No claim about awareness is made from this study.
- **Transfer:** if a signature also separates tactile hit vs miss in ds001785, it may be called a modality-general correlate of reported detection, not an awareness marker. Both tasks involve report.
- **Role:** the strongest cheap kill test for the hypothesis generator.
  - **Question:** does any theory-tagged EEG signature beyond the known P3b/N2, picked on half the subjects, track T2 identification on the other half against a label-shuffled null?
  - **If not:** the tactile study (ds001785) is skipped.
- **Novelty:** we found no published analysis of the ds001810 EEG; Reteig 2022 is behaviour-only. The P3b and posterior N2 effects and the null P1/N1 replicate Sergent 2005, Vogel 1998 and Alilović 2021. They are positive controls, not findings.
- **Theory tags:** they say which theory family has usually pointed to a signature. They are not tests of those theories. Every trial here has a report, so no candidate separates experience from report.

## 1. Candidates (direction: T2 correct minus incorrect)

| ID | Candidate | Window (ms after T2) | Channels | Role | Predicted |
|---|---|---|---|---|---|
| C1 | P3b | 350–600 | CPz, Pz, CP1, CP2, P1, P2 | positive control and gate | correct > incorrect |
| C2 | posterior N2 | 200–300 | PO7, PO8, P7, P8, O1, O2 | positive control | correct more negative |
| C3 | P1 | 80–130 | O1, Oz, O2, PO7, PO8 | null control | none (two-sided) |
| C4 | N1 | 150–200 | PO7, PO8, P7, P8 | null control | none (two-sided) |
| C5 | frontal late positivity (tag: global workspace) | 300–500 | Fz, FCz, Cz, AFz, F2, FC2 | target | correct > incorrect |
| C6 | global field power (tag: global workspace, "broad ignition") | 300–600 | all retained | target | correct > incorrect |
| C7 | late posterior positivity (tag: late or post-perceptual processing) | 600–800 | Pz, POz, PO3, PO4, Oz | target | correct > incorrect |
| C8 | pre-T2 posterior (T1 period) | −200–0 | Pz, POz, PO3, PO4, Oz | descriptive only | two-sided |
| C9 | cross-subject decoder | 0–800, 16 × 50 ms bins | frozen common channels | omnibus, held-out only, descriptive | AUC > 0.5 |

- **C5 depends on C1.** Under the average reference, a posterior P3b also pushes frontal channels negative. A C5 effect is only counted if it survives residualisation on C1 and C2 (section 6).
- **C9 cannot earn a PASS.** A synthetic check showed that it keeps a pure-P3b effect even after residualising on the C1/C2 scalars, because its per-channel, per-bin weights capture the P3b better than an ROI mean does. It is reported in both halves. If the verdict is PASS, it is carried to ds001785 as an exploratory transfer decoder.

## 2. Data

- **Dataset:** OpenNeuro ds001810 v1.1.0, pre-tDCS blocks only (`ses-anodalpre`, `ses-cathodalpre`; one block = one visit, about a week apart).
- **Trials:** lag 3, T1 correct. The label is T2 correct (61511) vs incorrect (61510).
- **Epochs:** −0.2 to 0.8 s around T2 onset, range-read by `fetch_ab_epochs.py`. Whole raw files were never downloaded.
- **Block eligibility (after preprocessing):**
  - at least 50% of trials kept;
  - at least 15 correct and 15 incorrect.
- **Subject eligibility:** a subject with at least one eligible block. Counts are in `eligibility.csv`, filled at prep: eligible subjects 42 of 45 (21 discovery, 21 held-out); eligible blocks 76 of 84. The 8 ineligible blocks lack 15 trials of one class, and none fell under the 50% floor.

## 3. Preprocessing (fixed; chosen from label-free data only)

1. **DC and filter:**
   - Remove each channel's mean per trial.
   - Apply a 30 Hz zero-phase 4th-order Butterworth low-pass (`filtfilt`). There is no high-pass, since that isn't possible on 1 s epochs.
2. **VEOG:** EXG1 − EXG2.
3. **Channels:**
   - Use the 64 scalp channels. Drop channels marked `bad` in the block's `_channels.tsv` (left-frontal slots blocked by the tDCS electrode in many blocks).
   - After a provisional average reference, drop channels whose median peak-to-peak across trials exceeds 5× the median over channels.
4. **Average reference** over the retained scalp channels.
5. **Measure basis: whole-epoch mean, no pre-T2 baseline.** Each channel's mean over −200 to 800 ms is subtracted.
   - **Why:** T1 is shown 275 ms before T2, so a −200 to 0 baseline would hold the T1 response. The T1 P3 is reported to be larger and longer on blinked trials. That would leak into every baseline-corrected measure with the sign C2 predicts.
   - **Cost:** a real late effect is partly subtracted from itself (by about the window's share of the epoch), and pre-T2 windows pick up the opposite sign. C8 is descriptive only for that reason.
6. **Trial rejection:**
   - Reject if any retained scalp channel's peak-to-peak exceeds 150 µV.
   - Reject if VEOG peak-to-peak in −200 to 300 ms exceeds 80 µV.
   - If a block's median VEOG peak-to-peak exceeds 80 µV, the VEOG rule is skipped for that block and reported.
   - **Label-free survey:** on the first 61 blocks, this rule rejects about 4% of trials (Fable estimate). Recomputed on all 84 blocks before sealing: 703 of 8,391 trials rejected (8.4%). No block was dropped, and the VEOG rule was usable in every block.
7. **Missing ROI channels:** an ROI uses whichever of its channels are retained. A block with none is missing for that candidate.

## 4. Measures

- **C1–C8:** the mean over the ROI channels and window. C6 is the standard deviation across retained channels at each sample, averaged over the window.
- **C9:**
  - Features are channel × 50 ms bin means over 0–800 ms on the frozen common channel list in `split.json` (43 channels), z-scored within block.
  - The model is L2 logistic regression (C = 0.01, class-balanced).
  - A single model is fit on all discovery subjects and applied to held-out subjects. There is no discovery statistic for C9: calibration showed that leave-one-subject-out scores are correlated across subjects, so the within-subject shuffle null was too narrow (11.5% of shuffled runs at p < 0.05).

## 5. Split and isolation

- **Split:** eligible subjects sorted by ID, shuffled with numpy seed 1810. The discovery half gets ⌈n/2⌉; the rest are held out. A subject's blocks stay in one half.
- **Files:** prep writes the halves to separate files (`prepped_discovery.npz`, `prepped_heldout.npz`) and seals their hashes.
- **`discover`:**
  - It refuses to run unless all sealed inputs match, and runs once.
  - It loads only the discovery file.
  - It writes `survivors.json` and seals it immediately.
- **`heldout`:**
  - It refuses to run unless `survivors.json` is sealed.
  - It re-runs discovery and stops if the result differs in any number.
  - Only then does it load the held-out file. It runs once and refuses if `result.json` exists.

## 6. Statistics

- **Within block:**
  - AUC of the scalar for correct (1) vs incorrect (0) per block.
  - Subject value: the trial-weighted mean of its block AUCs.
  - Group value: the mean over subjects.
- **Null:**
  - Shuffle labels within each block (5000 permutations; seed 2411 for discovery, 2412 for held-out) and recompute the group value.
  - For C9 (held-out only), the discovery-trained model is fixed, and only the held-out labels are shuffled. That model never saw them, and the held-out subjects are independent of each other.
- **p-values:** one-sided in the predicted direction for signed candidates; two-sided for C3, C4 and C8.
- **Discovery screen:** a target (C5, C6, C7) survives if p < 0.05.
- **Held-out, every survivor:**
  - the p-value, with Holm correction across the surviving targets;
  - a 95% bootstrap CI over subjects (B = 5000);
  - a residualised test: within each block, regress the target scalar on [1, C1, C2] and test the residual, one-sided, p < 0.05.
- **Held-out, always, outside the Holm family:** C1, C2, C3, C4, C8 and C9 are tested and reported.

## 7. Verdicts

- **INVALID:** C1 fails (held-out, one-sided p ≥ 0.05).
  - The pipeline is presumed faulty and nothing is interpreted.
  - The line stops. Any rerun needs a new prereg and cannot reuse this held-out half as untouched.
- **PASS:** C1 passes, and at least one target meets all three tests below. ds001785 is then licensed, with the passing targets, their signs and held-out effect sizes as its sealed candidate list. C9 goes along as an exploratory transfer decoder.
  - Holm p < 0.05.
  - Subject-level 95% CI on the predicted side of 0.5.
  - Residualised p < 0.05.
- **FAIL:** C1 passes but no target passes. ds001785 is skipped, and the hypothesis-generator line closes for this dataset pair.
  - A C1/C2/C9-only result is a FAIL. It replicates known effects and adds nothing to transfer.
- **Null-control flag:** if C3 or C4 has p < 0.05 on held-out, it is reported prominently next to the verdict. Early differences in an RSVP stream can come from T1 or distractor overlap. It does not change the verdict.
- **Reading a PASS:** it means "a signature beyond the P3b/N2 tracks T2 identification in held-out people in this sample". Theory credit would need the tactile transfer and, beyond that, a report-free contrast.

## 8. Calibration (must pass before sealing)

- **Shuffled labels:** 200 full runs (discovery → survivors → held-out, 500 permutations each) on the real epochs, with labels shuffled within block (seed 7).
  - Pass if any target meets the PASS criterion in at most 5% of runs.
  - Pass if every candidate's discovery p < 0.05 rate is at most 0.08.
- **Planted answer:**
  - Add +1.5 µV to the C1 ROI at 350–600 ms and −1.5 µV to the C2 ROI at 200–300 ms. The effect goes into the preprocessed epochs, which are then re-demeaned over the whole epoch exactly like real data, on a random half of the trials labelled "correct" in a shuffled copy. All features are then recomputed.
  - Pass if both C1 and C2 are recovered on held-out (p < 0.05) in at least 80% of 50 runs.
- **If a check fails:** fix the code, re-run the check, and record the change in section 11 before sealing.
- **Results (`ab_out/calibration.json`, 2026-11-24): all pass.**
  - Shuffled labels: any-target PASS in 0 of 200 runs.
  - Discovery p < 0.05 rates: 0.025–0.07 across C1–C8.
  - Held-out p < 0.05 rates: 0.04–0.075 (C9 0.055).
  - Plant: recovered in 50 of 50 runs.
- **Extra power check (not a gate):** +1.0 µV planted on the C5 ROI at 300–500 ms, on half the correct trials and re-referenced, gives a C5 PASS through residualisation in 18 of 20 runs; 1.5 µV gives 20 of 20.

## 9. Power

- **Expected size:** about 40 eligible subjects, so about 20 held out, with roughly 90 correct and 100 incorrect trials per subject.
- **Precision:** a per-block AUC from about 100 trials has an SE of about 0.06, so the subject value is about 0.04. The group SE over 20 subjects is about 0.01, plus between-subject variance.
- **Detectable effect:** a mean AUC of about 0.53 at 80% power. Published P3b effects for T2 seen vs unseen are far larger, so a C1 failure points to a fault.

## 10. Limits stated in advance

- **T1 overlap:** T1-locked activity still overlaps T2's 0–325 ms (the T1 P3). It is the same stimulus and the same T1 response class, but its size may differ by T2 outcome. Any effect may partly reflect how deeply T1 was processed. No pre-T1 samples were fetched.
- **Report:** T2 identification is not awareness. Seen-but-misnamed trials count as incorrect.
- **Fixed effects:** the permutation null tests "no effect in these subjects". The bootstrap CI over subjects is the population-level check.
- **One lab:** the generality is one lab, one task and one rig.

## 11. Deviations and changes before sealing

- **2026-11-24, after the Fable pre-seal review, before any real label–EEG statistic:**
  - **FAIL made possible:** C1 and C2 became controls, and PASS now needs a target (C5–C7) that passes Holm, the subject CI and residualisation.
  - **Within block:** AUC and shuffles are within block, eligibility is per block, and decoder z-scoring is per block.
  - **Measure basis:** the pre-T2 baseline was replaced by the whole-epoch mean.
  - **C8:** made descriptive.
  - **Sealing:** extended to the script, split, eligibility and data hashes. Survivors are sealed, and the held-out run happens once after an exact reproducibility check.
  - **Calibration and plant:** the calibration bar was tightened to 0.05 plus a per-candidate stage-1 check. The plant now goes into the epochs, at 1.5 µV.
  - **Trial rejection:** the 30 Hz low-pass, VEOG rule and block floor were added. The first rule would have rejected about 18% of trials, and all of one block.
  - **Wording:** "VAN" was renamed "posterior N2", the theory "predictions" were reworded as tags, and an awareness claim after transfer was ruled out.
  - **C9:** moved to omnibus after a synthetic check showed that it passes on a P3b-only effect even after residualisation.
  - **C9 discovery statistic removed** after calibration: 11.5% at p < 0.05 under shuffled labels, from leave-one-subject-out dependence. C9 is held-out only, with a calibrated rate of 0.055.
