# T4 predictions

**DRAFT. Not sealed.**

Written 2026-11-19 by the theory builder. No signal data were opened. Theory: `T4.md`. Primary data: Stockart et al. 2025 (OSF 8QE3A). Replication: MetaMosquito (OpenNeuro ds008959).

**Headline (P1).** In the no-report experiment, at one fixed stimulus intensity, single-trial late high-gamma in ventral visual cortex is a mixture of two states and not one graded distribution, while dorsolateral prefrontal and superior parietal cortex show no such mixture. Odds of a pass: about 20%.

## What the data allow (checked on OSF and in the paper)

| Fact | Consequence |
|---|---|
| **No-report trials carry no seen/unseen label.** In `task-noreport` files `sdt`, `resp` and `conf` are NaN or -1. The paper infers "seen" only from intensity: threshold vs 150% of threshold. | Every no-report prediction must be label-free (distribution shape, mixing fraction) or use a decoder trained on report trials. No prediction below treats intensity as a per-trial seen label. |
| No-report intensity is **exactly fixed** at two values per patient (G5: 0.0967 and 0.1450; 24 + 24 trials per block, 3 blocks in Grenoble, 2 in Brno). No catch trials. | "Same `intens`" holds exactly in no-report: about 72 trials per level per Grenoble patient. The no-stimulus reference must come from the stream before face onset or from delayed-report catch trials. |
| Delayed-report (`task-psycho`) intensity is staircased every threshold trial in 2-5% steps (G5, one block: 37 distinct values in 59 trials). 59 trials per block: 10 catch, 1 double-face, 24 threshold, 24 at 125%. | "Same `intens`" there means matched bins. I use bins of ±2.5% in log intensity within patient and block, plus intensity as a covariate. |
| Immediate report (`task-staircase`): 2 blocks of 52 (40 in Brno), about 20% catch, all targets at threshold, staircased. | Used only to define channels and decoders, so that tests on experiments 2 and 3 are independent. |
| Signal: high-gamma 70-150 Hz, divided by a 1 s pre-trial baseline, smoothed over 200 ms, resampled to 64 Hz, bipolar. No broadband. | Timing is blurred by about 200 ms. No phase measures. "Connectivity" can only be co-variation of high-gamma amplitude. |
| Single-trial structure of `data_by_condition_resampled.mat` is **unconfirmed** (mind-ne is checking). File sizes (131-187 MB per patient; `info_classif` files of 3-29 MB per region) fit single trials but prove nothing. | If only condition averages are shared, P1, P2 and P4 cannot run. P3 could run on trial-level regression inputs only if those exist. |
| Coverage: decoders exist for VVC in 18 patients, IFC 19, DLPFC 9, SPC 5. Both VVC and DLPFC in 4 patients (B1, G5, G10, G18); VVC and IFC in 8. | Region comparisons rest on few patients. The authors warn against direct comparisons between regions. |
| A face has 4 identities (`id_face`). Confidence is 3-point, mostly "very sure". 27 of 29 patients did the no-report experiment. | Identity decoding is possible in principle but I do not predict it; I expect it to be underpowered. |
| Reuse: the OSF node shows copyright CNRS 2024 and no licence name; the paper is CC BY-NC-ND. | Check reuse terms before publishing derived data. |

## What Stockart et al. already showed (limits on novelty)

- **Hit > miss** high-gamma in all four regions with immediate and delayed report. Onsets with delayed report: VVC 0.33 s, IFC 0.31 s, SPC 0.46 s, DLPFC 0.67 s.
- **No-report:** threshold vs 150% intensity changes high-gamma in VVC (and lateral visual cortex, exploratory) from 0.25 to 0.61 s. Bayes factors favour no effect in SPC and DLPFC (both 0.27) and are inconclusive in IFC (0.6). So "posterior yes, DLPFC and SPC no, without report" is **already published at the level of means**, with intensity as the proxy.
- A decoder trained on immediate-report hit vs miss transfers to delayed report and, in VVC, to no-report intensity. The no-report transfer rests on **2 patients, 1 of whom passed** (AUROC 0.69).
- **Intensity raises high-gamma on hits and not on misses** (VVC and IFC). Confidence tracks high-gamma on hits in VVC, SPC and IFC, not in DLPFC (BF 0.44, inconclusive), and not on misses anywhere (BF 0.2-0.41).
- False alarms: the VVC latent variable crosses threshold more often than on correct rejections (p = 0.034, n = 4, uncorrected).
- A leaky accumulation model reproduces the mean traces.
- **Not reported:** any test of bimodality, mixture or trial-to-trial variability; misses vs correct rejections; a region-by-intensity interaction; amplitude coupling between regions. The paper does not mention bifurcation.

## Shared definitions

- **Channels.** "Responsive" channels are defined on experiment 1 only (hit > miss cluster), as in the paper. All tests use experiments 2 and 3.
- **Regions.** The paper's four (VVC, SPC, IFC, DLPFC) plus lateral visual cortex (LVC) and anterior insula as labelled in `electrodes.tsv`.
- **Score.** Per trial and region: the mean high-gamma of that region's responsive channels in the window, or the experiment-1 decoder's latent variable where a decoder exists. Both are reported; the channel mean is primary because it exists in every patient.
- **Windows** (from face onset): early 0-250 ms, late 400-900 ms. The gap allows for the 200 ms smoothing.
- **No-stimulus reference.** The same-length window ending before face onset in the same trial, and delayed-report correct rejections.
- **Inference.** Patient-held-out throughout: fit on all but one patient, score the held-out patient, and report the mean with a patient-level bootstrap interval. Channel-held-out within patient as a secondary check.
- **Planted checks.** Every prediction is run first on synthetic data built from the real trial counts, channel counts and noise: (a) the authors' published leaky accumulation model (their equations 1-2), which has no bifurcation; (b) Sergent 2021's bifurcation model with the hit-miss separation the paper reports (AUROC about 0.8 in the best patients, lower elsewhere). A prediction counts as **testable** only if the pipeline returns "pass" in at least 80% of (b) and in at most 5% of (a). If not, the outcome is "cannot decide", never "fails".

---

## P1 (primary). Two states without report, in VVC and not in DLPFC or SPC

- **Measure.** Held-out log-likelihood per trial of three models of the late-window score, fitted to no-report trials at both intensities:
  1. **Mixture (T4).** Each trial is in a low state or a high state. The low state is fixed to the no-stimulus reference. The high state's mean may differ between the two intensities. The mixing fraction β differs between intensities.
  2. **Graded.** One unimodal distribution per intensity (skew-normal, free mean, spread and skew).
  3. **Leaky accumulation.** The distribution of the peak of the authors' model, with its parameters fitted per patient.
- **Regions and windows.** VVC and LVC, late window. Controls: the same regions in the early window; DLPFC and SPC in the late window.
- **Conditions.** No-report threshold and 150% trials. Intensity is exactly fixed within each level, so matching is exact.
- **Pass mark.** All four:
  1. In VVC (late), the mixture beats both rivals: held-out log-likelihood difference above 0, 95% patient-bootstrap interval excluding 0, and p < 0.025 against the parametric null.
  2. β is higher at 150% than at threshold, and β at threshold is between 0.1 and 0.7.
  3. No mixture advantage in VVC early (interval includes 0, upper bound below half the late effect).
  4. No mixture advantage in DLPFC or SPC late, where the fitted β is not above the rate found by applying the same fit to no-stimulus windows.
- **T4 fails if** the planted check says the test is decisive and either the graded or the accumulation model matches or beats the mixture in VVC late, or the mixture advantage is as large in DLPFC as in VVC.
- **Secondary (label-light).** A decoder trained on experiment-1 hit vs miss, applied to no-report trials, gives a "high" fraction at threshold no greater than the patient's experiment-2 hit rate plus 10 points, and a higher fraction at 150%. If the record of who noticed the inverted faces in the control block can be had from the authors (not found on OSF), patients who noticed have a higher β than those who did not.
- **What others predict.**
  - *Plain GNWT:* a mixture, strongest in PFC, and present there whenever it is present in VVC. Sergent's 2021 revision of GNWT predicts what T4 predicts; P1 cannot separate them.
  - *Leaky accumulation (the dataset's authors):* model 3 wins; no mixture.
  - *RPT:* graded recurrent activity in visual cortex; no commitment to two states; no frontal signal.
  - *IIT:* no prediction about trial-to-trial distributions; posterior location only.
- **Planted check.** As in "Shared definitions". In addition, plant a mixture in DLPFC synthetic data to show that mark 4 can detect one there at DLPFC's channel and patient counts.
- **Controls.**
  - *Matched intensity:* exact, by design.
  - *Held-out:* leave one patient out; leave one channel out within patient.
  - *Permutation null:* parametric bootstrap from the fitted graded model (1,000 draws, same trial counts); plus shuffling the intensity label within patient for mark 2.
  - *Confidence:* not available without report. The experiment-2 version of the test (P2) carries this control.
  - *False alarms and catch trials:* there are none without report. The low state is anchored to pre-onset windows; the fit is repeated with experiment-2 correct rejections as the anchor, and both must agree.
  - *Slow drifts:* block and trial index are regressed out first, since attention may fall over a passive block and fake a mixture. A two-state result must survive this.
  - *Evoked-response removal:* not applicable (no connectivity measure).
- **Odds.** Pass about 20%. Cannot decide about 40% (72 trials per level, few patients near the fusiform face area, class separation near d' = 1). Fail about 40%.
- **Novelty limit.** Sergent 2021 showed the same signature in scalp EEG for sounds. A pass here would be the first intracranial, regional, visual version, and the first head-to-head with accumulation.

## P2. With delayed report: unseen equals nothing shown, and state predicts report at matched intensity

- **Measure.** (a) The difference in late-window VVC score between misses and correct rejections, in SD units of the correct rejections. (b) AUROC for hit vs miss from the mixture's posterior probability of the high state, with the mixture fitted **without labels**.
- **Regions and windows.** VVC and LVC; late window for the claims, early window as contrast. Experiment 2.
- **Conditions.** Threshold and 125% trials, hits and misses compared only within the same ±2.5% log-intensity bin, patient and block; catch trials for correct rejections and false alarms.
- **Pass mark.** All three:
  1. Misses equal correct rejections in the late window: the 90% interval lies inside ±0.2 SD.
  2. Label-free state assignment predicts report: AUROC of at least 0.65, patient-held-out, p < 0.01 by permutation.
  3. False alarms have a higher high-state probability than correct rejections somewhere in the trial (the paper's n = 4 result, re-run in all VVC patients with correction for the number of windows searched).
- **T4 fails if** misses exceed correct rejections by more than 0.2 SD in the late window with the interval excluding 0.2, or the label-free AUROC interval lies below 0.6 when the labelled hit vs miss AUROC is above 0.7.
- **What others predict.**
  - *Plain GNWT:* subliminal stimuli still activate high-level visual cortex, so misses above correct rejections in VVC; equality only in PFC.
  - *RPT:* misses above correct rejections early (feedforward sweep), smaller late.
  - *Leaky accumulation:* misses carry sub-threshold evidence, so misses above correct rejections, growing with intensity.
  - *IIT:* silent.
- **Planted check.** Plant a miss-minus-rejection difference of 0.3 SD and show the equivalence test rejects it in at least 80% of runs; plant a mixture and a truncated unimodal distribution and show mark 2 separates them.
- **Controls.**
  - *Matched intensity:* bins as above; a second run with intensity as a covariate.
  - *Held-out:* patient-held-out fit of the mixture; channels defined on experiment 1.
  - *Permutation null:* shuffle hit/miss within patient, block and intensity bin, 5,000 times.
  - *Confidence:* added as a covariate to mark 2 (state must predict report beyond confidence), and marks 1-2 repeated on high-confidence trials only.
  - *False alarms and catch trials:* mark 1 and mark 3 are built on them. Trials with "more than one face" are excluded, as in the paper.
  - *Evoked-response removal:* not applicable.
- **Odds.** Pass about 30%. Mark 1 is the risky one.

## P3. PFC is a pointer: seen-related signal without grading

- **Measure.** Within hits of experiment 2, the slope of late-window high-gamma on (i) intensity level (threshold vs 125%) and (ii) confidence (high vs low), per responsive channel, in a hierarchical model with channels nested in patients and a **region-by-slope interaction**.
- **Regions.** VVC vs DLPFC (primary); IFC and anterior insula reported separately.
- **Pass mark.** All three:
  1. DLPFC shows hit > miss (replicating the paper).
  2. Both slopes in DLPFC lie inside an equivalence bound of ±one third of the VVC slope (90% interval).
  3. The region-by-slope interaction (VVC > DLPFC) is above 0, p < 0.025, for intensity and for confidence.
- **T4 fails if** either DLPFC slope is reliably above one third of the VVC slope, or if mark 1 fails (then DLPFC carries nothing and "pointer" is empty).
- **What others predict.**
  - *Plain GNWT:* the broadcast amplifies and sustains the representation, so PFC should scale with stimulus strength once ignited; van Vugt 2018 describes strong sustained frontal activity for reported stimuli.
  - *Higher-order theories:* PFC should track confidence at least as well as VVC. This is the sharpest contrast.
  - *IIT and RPT:* no PFC role; both are satisfied by mark 2 but not by mark 1.
- **Planted check.** Plant a DLPFC slope equal to the VVC slope at DLPFC's real channel and patient counts and show mark 2 rejects equivalence in at least 80% of runs. With 9 DLPFC patients this may fail; then P3 is "cannot decide".
- **Controls.**
  - *Matched intensity:* the confidence slope is estimated within intensity level and bin; the intensity slope within confidence level.
  - *Held-out:* leave-one-patient-out stability of the interaction; channels from experiment 1.
  - *Permutation null:* shuffle region labels across channels within patient where a patient has both regions (4 patients), and shuffle intensity or confidence labels within patient elsewhere.
  - *Confidence:* is a variable of interest here, and a covariate for the intensity slope.
  - *False alarms and catch trials:* DLPFC's false alarm vs correct rejection difference is reported; a pointer should fire on false alarms too.
  - *Evoked-response removal:* not applicable.
- **Odds.** Pass about 25%. **Novelty limit:** the per-region pattern (DLPFC intensity p = 0.053, confidence BF 0.44) is in the paper, so the direction is a retrodiction. Only the equivalence and the interaction are new, and IFC's graded response was known before I assigned it to the report loop.

## P4. The loop: amplitude coupling rises in the high state, posterior-posterior without report

- **Measure.** Trial-by-trial correlation of late-window high-gamma between region pairs within a patient, computed on **residuals** after subtracting the mean response of each condition cell (intensity level by report), then compared between hits and misses (experiment 2) and between trials assigned high vs low by the P1 mixture (experiment 3).
- **Pairs.** VVC-LVC (the claimed loop), VVC-IFC and VVC-DLPFC (the optional pointer).
- **Pass mark.** Both:
  1. VVC-LVC residual correlation is higher on hits than on misses at matched intensity (difference above 0, patient-bootstrap 95% interval), and higher in high-state than low-state no-report trials.
  2. VVC-DLPFC shows the hit vs miss increase with report and **no** increase without report (interval includes 0 and its upper bound is below the VVC-LVC effect).
- **T4 fails if** VVC-LVC coupling does not differ between hits and misses, or if VVC-DLPFC coupling rises without report as much as with it.
- **What others predict.**
  - *Plain GNWT:* long-distance coupling with PFC on every seen trial, with or without report.
  - *IIT:* posterior coupling in both states of report, no PFC coupling; does not require a hit vs miss difference tied to a late window.
  - *RPT:* posterior coupling on seen trials; agrees with T4 here. P4 cannot separate T4 from RPT.
- **Planted check.** Synthetic pairs with shared evoked responses and zero residual coupling must give no effect (this is the test that evoked-response removal works). Planted residual coupling of r = 0.2 on high-state trials must be recovered in at least 80% of runs.
- **Controls.**
  - *Evoked-response removal:* condition-mean subtraction as above, repeated with a per-trial regression on the evoked template; an effect must survive both. Because splitting by report selects on the outcome and can induce correlations, the same split is applied to the accumulation-model simulation, and the real effect must exceed it.
  - *Matched intensity:* bins as in P2.
  - *Held-out:* patient-level bootstrap; pairs sharing a bipolar contact or lying within 10 mm are dropped.
  - *Permutation null:* shuffle trial order of one region within condition cell.
  - *Confidence:* covariate in the hit-only correlation.
  - *False alarms and catch trials:* coupling on correct rejections is the floor.
- **Odds.** Pass about 15%. Few patients have both regions of a pair, and amplitude coupling at 64 Hz after 200 ms smoothing is a blunt measure.

## P5. Replication on MetaMosquito: the same two rules in hearing and vision

- **Data.** 8 sEEG patients, near-threshold auditory, visual and audiovisual detection with present/absent report, confidence and catch trials; high-gamma epochs at 512 Hz. **Every trial has a report. There is no no-report condition**, so P1 cannot be replicated there. Events files and per-trial intensity were not read (direct S3 access was denied on 2026-11-19); whether intensity is fixed or staircased is unverified.
- **Measures.** P2 marks 1 and 2 and P3, run per modality, with all thresholds and windows frozen from Stockart before the files are opened.
- **Pass mark.**
  1. In the modality's own high-level sensory cortex (ventral visual for vision, superior temporal for hearing), misses equal correct rejections late (±0.2 SD) and the label-free mixture predicts report (AUROC at least 0.65).
  2. The mixture is modality-specific in sensory cortex: the visual site shows none for sounds, and the reverse.
  3. Any prefrontal site with hit > miss in both modalities has intensity and confidence slopes inside the P3 equivalence bound.
- **T4 fails if** mark 1 fails in both modalities with a decisive planted check, or if supramodal prefrontal sites are graded by confidence as strongly as sensory sites.
- **What others predict.** Plain GNWT expects a supramodal, graded frontal ignition; higher-order theories expect supramodal frontal confidence coding; accumulation expects graded misses in sensory cortex.
- **Planted check and controls.** As in P2 and P3. Intensity matching follows whatever the events files allow; if intensity varies trial by trial, matched bins; if it is fixed per modality, exact. The 512 Hz sampling permits a narrower early window (0-200 ms) than Stockart.
- **Odds.** Pass about 20%, given 8 patients.

---

## Summary

| | Claim | Needs single trials | Separates T4 from | Pass odds |
|---|---|---|---|---|
| **P1** | Two states without report in VVC, none in DLPFC/SPC | yes | accumulation, graded encoding, PFC-centred GNWT | 20% |
| P2 | Misses equal no stimulus; state predicts report | yes | accumulation, GNWT's subliminal activation, RPT's early sweep | 30% |
| P3 | PFC signal not graded | trial-level values | higher-order theories, plain GNWT | 25% |
| P4 | Loop coupling, posterior without report | yes | plain GNWT | 15% |
| P5 | P2 and P3 in a second dataset and modality | yes | as P2, P3 | 20% |

**Before sealing.**
1. Confirm single-trial structure in the Stockart `.mat` files (mind-ne).
2. Run the planted checks on synthetic data only, and drop any prediction that cannot reach the 80% / 5% gate.
3. Read the MetaMosquito events files and fix the intensity-matching rule.
4. Ask the authors for the inverted-face noticing record and the reuse terms.
5. Freeze windows, bounds and model code by hash, then open the signals.

**What no prediction here can do.** Separate T4 from Sergent's 2021 "global playground" (they agree on P1, P2 and P4), test postdiction, or test dreams, ketamine and covert awareness.
