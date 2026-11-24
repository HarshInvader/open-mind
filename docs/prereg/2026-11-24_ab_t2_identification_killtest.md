# Pre-registration: attentional-blink T2 identification screen, held-out-subject kill test (ds001810)

Agent: Open Mind thread   Task: hypothesis generator, step 1   Date: 2026-11-24

Seal with `.venv/bin/python -I experiments/rules/evidence.py seal docs/prereg/2026-11-24_ab_t2_identification_killtest.md` before any real label is used. Analysis script: `experiments/hypothesis_generator/ab_killtest.py`. It refuses to read real labels unless this file is sealed.

## 0. What this is and is not

- **Outcome: T2 identification**, correct vs incorrect, on lag-3 trials with T1 correct. It is not seen vs unseen: "incorrect" includes trials where T2 was seen but named wrongly, and "correct" includes lucky guesses (the letter set is small). No claim about awareness is made from this study. A signature can be called an awareness candidate only if it later transfers to ds001785 (tactile hit vs miss).
- **Role:** the strongest cheap kill test for the hypothesis generator. Do theory-signed EEG signatures of T2 identification, picked on half the subjects, survive on the other half against a label-shuffled null? If nothing survives, the tactile confirmation (ds001785) is skipped entirely.
- **Novelty:** the ds001810 EEG has not been analysed for T2 outcome (Reteig 2022 is behaviour-only). The expected within-dataset effects (P3b, N2/VAN, no P1/N1) replicate Sergent 2005, Vogel 1998 and Alilović 2021. They are positive controls, not findings.

## 1. Hypotheses (direction: T2 correct minus T2 incorrect)

| ID | Candidate | Window (ms after T2) | Channels | Signed by | Predicted |
|---|---|---|---|---|---|
| C1 | P3b | 350–600 | CPz, Pz, CP1, CP2, P1, P2 | GNWT (ignition) | correct > incorrect (positive control) |
| C2 | N2 / VAN | 200–300 | PO7, PO8, P7, P8, O1, O2 | RPT / IIT (posterior recurrence) | correct more negative (positive control) |
| C3 | P1 | 80–130 | O1, Oz, O2, PO7, PO8 | none: early sensory | no difference (null control) |
| C4 | N1 | 150–200 | PO7, PO8, P7, P8 | none: early sensory | no difference (null control) |
| C5 | Frontal late positivity | 300–500 | Fz, FCz, Cz, AFz, F2, FC2 | GNWT (prefrontal ignition); IIT/RPT predict no frontal specificity | correct > incorrect |
| C6 | Global field power | 300–600 | all retained channels (SD across channels per sample, then mean) | GNWT (broad ignition) | correct > incorrect |
| C7 | Late sustained posterior | 600–800 | Pz, POz, PO3, PO4, Oz | HOT / report (late re-representation) | correct > incorrect |
| C8 | Pre-T2 posterior baseline-free mean | −200–0 (T1 period) | Pz, POz, PO3, PO4, Oz | unsigned (T1 processing depth; Alilović 2021) | two-sided |
| C9 | Multivariate decoder | 0–800, 16 bins of 50 ms | common retained channels | omnibus (no theory) | AUC > 0.5 |

C8 is measured before baseline correction, as the mean of the −200 to 0 ms window minus the mean of the whole epoch. All other candidates use baseline-corrected data.

## 2. Data

- **Dataset:** OpenNeuro ds001810 v1.1.0. Only the pre-tDCS blocks are used (`ses-anodalpre`, `ses-cathodalpre`), which are free of stimulation artefact.
- **Trials:** lag 3 with T1 correct. The label is T2 correct (event 61511) vs incorrect (61510). Lag-8 trials are not used.
- **Fetch:** T2-locked epochs −0.2 to 0.8 s were range-read by `fetch_ab_epochs.py`. Whole raw files were never downloaded.
- **Subjects:**
  - Eligibility: at least 20 correct and 20 incorrect trials after artefact rejection, pooled over the subject's pre blocks.
  - Excluded subjects are listed with reasons in the output.

## 3. Preprocessing (fixed; no tuning on real labels)

1. **Channels:**
   - Use the 64 scalp channels; drop EXG1–8 and Status.
   - Drop channels marked `bad` in each block's `_channels.tsv`. Many subjects have left-frontal slots blocked by the tDCS electrode.
   - Per block, also drop channels whose median peak-to-peak amplitude across trials exceeds 5× the median over channels.
2. **Re-reference** to the average of the retained scalp channels.
3. **Baseline:** subtract the −200 to 0 ms mean from each channel. T1 falls 275 ms before T2, so the baseline holds the T1 response. Both classes share T1-correct, and baseline correction is applied identically to both.
4. **Filter:** none beyond the 50 ms window averaging the measures use. The decoder uses 50 ms bin means.
5. **Artefact rule:** reject a trial if any retained channel's peak-to-peak amplitude exceeds 150 µV after re-referencing.
6. **Missing ROI channels:** a candidate's ROI uses whichever of its channels are retained. If none are retained, that subject is missing for that candidate.

## 4. Measures

- **C1–C8:** a scalar per trial. The within-subject effect is the AUC of the scalar for correct (1) vs incorrect (0) trials, with the sign flipped for C2 so that the prediction is AUC > 0.5. C3, C4 and C8 are tested two-sided.
- **C9:**
  - Features are channel × bin means, z-scored within subject.
  - The model is L2 logistic regression (C = 0.01, class-balanced), trained only on discovery subjects pooled.
  - Score: the held-out subject's per-trial decision value, then its within-subject AUC.
  - Channels: the intersection of channels retained in every eligible block. If fewer than 40 channels remain, C9 is not run, and this is reported.

## 5. Split

- **Rule:** eligible subjects are sorted by ID and split in half at random (numpy seed 1810).
  - The discovery half gets ⌈n/2⌉ subjects; the rest are held out.
  - A subject's two pre blocks always stay in the same half.
- **Timing:** the split is written to `split.json` before any label is read.
- **Isolation:** held-out subjects are not loaded until the survivor list from discovery has been written and hashed into `survivors.json`.

## 6. Statistics

- **Group statistic:** the mean of within-subject AUCs over subjects. For C9 on discovery subjects, use leave-one-subject-out within the discovery half.
- **Null:** shuffle labels within each subject (subject-level permutation of trial labels), recompute the full statistic, n = 5000, seed 2411.
  - For C9 the decision values are fixed (leave-one-subject-out models in discovery; the single discovery-trained model on held-out subjects) and only the test subject's labels are shuffled. The model never saw the test subject's labels, so this is a valid null for "these scores carry no information about this subject's outcome".
- **p-value:** one-sided in the predicted direction for signed candidates; two-sided (|AUC − 0.5|) for C3, C4 and C8.
- **Discovery screen:** a candidate survives if p < 0.05 (uncorrected; the screen is meant to be lenient).
- **Held-out test:** each survivor is tested once on held-out subjects, with Holm correction across survivors, α = 0.05. Effect size is reported as the mean AUC with a 95% bootstrap CI over subjects (B = 5000).

## 7. Pass marks

- **Pipeline gate (must hold, or the run is INVALID and nothing is interpreted):**
  - C1 (P3b) survives on held-out subjects in the predicted direction.
  - C3 (P1) does not reach Holm-significance on held-out subjects, if it survived discovery at all.
  - If the P1 does differ, the run is flagged rather than invalidated: early differences in an RSVP stream can come from T1/distractor overlap. It is reported prominently.
- **Kill test PASSES:**
  - The pipeline gate holds, and at least one candidate other than C3/C4 survives held-out Holm.
  - Then ds001785 is licensed. The survivors, with their sign and the held-out effect size, become the sealed candidate list for the tactile study.
  - **Licensed by default:** C1, C2, C5–C7, and C9 only as a decoder applied cross-modally. C8 (pre-T2) is not licensed, because touch has no T1.
- **Kill test FAILS:**
  - No candidate other than C3/C4 survives held-out Holm.
  - Then ds001785 is skipped, and the hypothesis generator line is closed for this pair of datasets.
- **Honest reading of a pass:** surviving here only means "reliably tracks T2 identification across people". Theory credit needs the transfer to touch and, beyond that, a report-free contrast. A C1/C2-only pass replicates known effects; its value is only as the input to the transfer test.

## 8. Planted-answer check and null calibration (must pass first, before real labels)

- **Shuffled-label run:** using the real epochs with labels shuffled within subject (seed 7), the full pipeline (discovery → survivors → held-out) is run 200 times with a reduced null (n = 500).
  - Requirement: the fraction of runs in which any non-control candidate passes held-out Holm is at most 0.10.
- **Planted run:**
  - Add +1.0 µV to the C1 ROI, 350–600 ms, on a random half of trials labelled "correct" in a shuffled-label copy.
  - Add −1.0 µV to the C2 ROI, 200–300 ms.
  - Requirement: both are recovered (held-out Holm p < 0.05) in at least 80% of 50 runs.
- **If either check fails:** fix the code, re-run the check, and record the change below before sealing.

## 9. Power

- **Expected size:** about 43 eligible subjects, so about 21 held out, with roughly 90 correct and 110 incorrect trials each.
- **Noise:** a within-subject AUC from about 200 trials has an SE of about 0.04. The group-mean SE over 21 subjects is about 0.04/√21 ≈ 0.009, plus between-subject variance.
- **Detectable effect:** a mean AUC of about 0.53 at 80% power. Published P3b effects for T2 seen vs unseen correspond to AUCs well above that, so a null on C1 indicates a pipeline fault, not low power.

## 10. Deviations

None yet.
