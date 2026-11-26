# Prior art: ds006171 VAN (seen vs unseen) and unseen vs catch

Checked 2026-11-26. "Opened" means the abstract and the relevant methods/results were read. Anything marked (unverified) was not opened.

## 1. The paper that published ds006171
**Melcón, Stern, Kessel, Arana, Poch, Campo & Capilla (2024), Psychophysiology 61:e14525, doi:10.1111/psyp.14525.** Opened through the open-access PDF at https://eprints.gla.ac.uk/316871/1/316871.pdf (the Wiley page returned 403). The DOI comes from https://s3.amazonaws.com/openneuro.org/ds006171/dataset_description.json, which lists only this paper.
- Design: Gabor (50 ms) in the left or right hemifield; contrast set trial by trial by a PEST-type staircase run per hemifield; 10% catch trials; a seen/unseen report on every trial, with orientation asked on 15% of trials. EEG was analysed for N=29 in the no-cue task.
- The analyses covered **pre-stimulus** alpha amplitude and phase only. Higher alpha preceded unseen trials in the no-cue and noninformative tasks; alpha phase did not predict seeing. There was **no post-stimulus ERP, VAN, contra-ipsi or unseen-vs-catch analysis.**

## 2. Existing reanalysis of ds006171 (important)
**GitHub repo itsxiatong/eeg-awareness-ds006171** (created 2026-10-24): https://github.com/itsxiatong/eeg-awareness-ds006171. Opened: README, `code/03`, `code/05`, `output/*.csv`, `output/AUDIT.md`, notebook outputs. It references a manuscript, but none is linked and I found no preprint.
- Covers the no-cue task, N=31. Hit rate 42.6%, FA 6.6%. Seen trials had 3.4% higher contrast than unseen (t(30)=7.69), so the staircase confound is real.
- "VAN" here is a **bilateral** ROI (PO7/PO8/P7/P8/O1/O2) at 180–280 ms, **not contra minus ipsi**: seen −1.26 vs unseen −0.57 µV, t(30)=−2.54, p=.017, dz=−0.46. With contrast-matched resampling: −0.72 µV, p=.014. Regression: β(seen)=−0.67, p=.022; β(contrast) not significant.
- P3b is large (dz=1.67). Decoding is above chance from 156 ms.
- Unseen vs catch was tested **only for P3b**: t=0.31, p=.76, BF10=0.2, which favours equality. Catch ERPs are computed, but there is no test for the VAN or a lateralised component. Seen/unseen are not split by hemifield.

## 3. Cohen et al. 2024 (the dataset we are replicating)
**Cerebral Cortex 34(11):bhae415, doi:10.1093/cercor/bhae415.** Opened at https://academic.oup.com/cercor/article/34/11/bhae415/7840405.
- Central faces, backward masking, 5 SOAs, with report and no-report conditions. The "N170/VAN" was **bilateral** (≈PO9/PO10, 140–200 ms), compared across SOAs rather than seen vs unseen, and was judged neither linear nor bifurcated. Only the fronto-central N2 (250–290 ms) tracked awareness.
- There was no ERP test of unseen vs absent. So a lateralised contra-ipsi seen/unseen test is a new kind of measurement relative to this paper, not a direct replication of it.

## 4. VAN reviews
- **Koivisto & Revonsuo 2010, Neurosci Biobehav Rev 34:922, doi:10.1016/j.neubiorev.2009.12.002.** Abstract opened via Europe PMC. VAN (~200 ms posterior negativity) is the most consistent correlate of awareness and depends on spatial attention. No unseen-vs-absent test.
- **Förster, Koivisto & Revonsuo 2020, Conscious Cogn 80:102917, doi:10.1016/j.concog.2020.102917.** Full PDF opened. VAN is stronger contralateral to the stimulus, and the graded vs dichotomous question is unresolved. It cites Wyart et al. 2012 (unverified) as showing an early correlate modulated by both report and physical presence/absence, i.e. graded.
- **Dembski, Koch & Pitts 2021, Trends Cogn Sci, doi:10.1016/j.tics.2021.05.009.** Full PDF opened via https://par.nsf.gov/servlets/purl/10290372. The awareness negativity is maximal contralaterally at 120–200 ms. Fig. 2 (from Boncompte & Cosmelli 2018, unverified) shows a seen-only contra-ipsi negativity at 200–300 ms for lateralised motion, which cancels when hemispheres are pooled. This argues that a contra-ipsi analysis matters.

## 5. Near-threshold Gabor VAN studies with absent trials
- **Koivisto & Grassini 2016, Neuropsychologia 84:235, doi:10.1016/j.neuropsychologia.2016.02.024.** Abstract opened via Europe PMC; the full text is paywalled. Liminal quadrant targets at matched accuracy: **contralateral** N200 at 180–280 ms is larger for seen than unseen. Unseen-correct trials show more contralateral N200 than unseen-incorrect, read as **graded/weak awareness**. Unseen was not compared with absent trials.
- **Eklund & Wiens 2018, Cogn Affect Behav Neurosci, doi:10.3758/s13415-018-0562-z.** Full text opened at https://pmc.ncbi.nlm.nih.gov/articles/PMC5823961. Unmasked, preregistered, 20% blank catch trials. The VAN at contralateral O1/O2 (180–280 ms, no ipsi subtraction) is −1.4 to −1.6 µV, BF10 79–111. Catch trials were used only for false alarms, so **unseen vs absent was not tested.**

## Verdict
Our study would add the first contra-minus-ipsi (lateralised) VAN test in ds006171 at matched contrast, plus a VAN/lateralised (not P3b) unseen-vs-catch test with Bayes factors for all-or-none vs graded. The bilateral seen/unseen VAN, contrast matching and the P3b unseen=catch test have already been done in the GitHub reanalysis, so those parts would be replication, not novelty.

## Follow-up checks
Checked 2026-11-26.

### 1. Melcón et al. 2024: catch trials, side information, codes 31/32, fixation control
Sources: the open-access PDF at https://eprints.gla.ac.uk/316871/1/316871.pdf, plus the dataset's https://s3.amazonaws.com/openneuro.org/ds006171/sub-01/eeg/sub-01_task-nocue_events.json and `_events.tsv` for sub-01.
- **Display:** "each trial started with a fixation cross on a dark gray background and two boxes outlined in light gray, placed at the lower left and right sides of the fixation cross." Both boxes stay on screen on every trial. The paper describes no side-marking event in the no-cue task (Fig. 1a: "No cue preceded the Gabor stimulus"). The only cue is in the cue tasks: "one of the two boxes turning white for 200 ms".
- **Side is unpredictable:** "Gabor stimuli were equally likely to appear at either the left or the right location"; "no stimulus was presented in 10% of trials (catch trials)". There were 400 trials: 180 per hemifield and 40 catch. Contrast was calibrated "for each participant, task, and visual field". Catch trials were left out of the staircase, and the pre-task calibration had no catch trials.
- **Codes 31/32:** events.json says "31: Absent Gabor after a left cue", "32: Absent Gabor after a right cue". The same wording is used across tasks, and the no-cue task had no cue. In sub-01 no-cue there are 20 of each code, with `gabor_contrast` = NaN. My inference: 31/32 is a dummy left/right label for catch trials, not something the participant saw. Code 128 is the photodiode. Despite the JSON's "replace each 128 with the next trigger code", in sub-01 the 128 follows each stimulus code (including 31/32) by about 38 ms (range 38–56). So the photodiode also fires on catch trials, and what it detected there is unverified.
- **Fixation control:** no eye-tracking is mentioned. "Participants were asked to maintain their gaze on the fixation cross throughout the experiment". EOG came from "four external electrodes (placed below and above one eye, and lateral to both eyes)"; these are HEOG1/2 and VEOG1/2 in channels.tsv. Rejection: "we visually inspected the signal to discard trials contaminated by eye or cable movements … Participants with more than 45% of trials contaminated with ocular artifacts were not included (5 participants in the no-cue task)". ICA followed, then a common-average reference. No µV threshold or residual-HEOG criterion is given.

### 2. HEOG conventions for lateralised ERPs
- **Papaioannou & Luck 2020, Psychophysiology, doi:10.1111/psyp.13532.** Opened at https://pmc.ncbi.nlm.nih.gov/articles/PMC7160023/. Trials: a step-function on uncorrected bipolar HEOG/VEOG from −200 to 300 ms, "a modified version of the technique described in Woodman & Luck, 2003". The step µV value is not stated. Trials were also rejected for deflections >250 µV in any channel, and subjects with more than 25% of trials rejected were excluded. Residual: "The average deflection was less than 3.2 μV … which would correspond to an average eye movement of less than ±0.1° (on the basis of … Lins, Picton, Berg, & Scherg, 1993)". This is measured on the left-target minus right-target HEOG difference wave.
- **Constant et al. 2025, Cortex 190:304, doi:10.1016/j.cortex.2025.05.014** (multilab Eimer 1996 replication). Opened at https://researchonline.ljmu.ac.uk/id/eprint/26641/. Trials: "bipolar HEOG was larger than ±25 μV" or "VEOG … larger than ±60 μV" leads to rejection. Subjects: "if the maximal voltage of the HEOG difference wave … exceeded ±2 μV at any time point, the participant was rejected".
- **Woodman & Luck 2003, JEP:HPP 29:121, doi:10.1037/0096-1523.29.1.121** (unverified; the Vanderbilt PDF would not connect). Later papers describe its method as two steps: per-trial rejection plus subject exclusion based on averaged HEOG. Luck 2014, Eimer 1996 and Kiss, Van Velzen & Eimer 2008 are all unverified (not opened).
- **Note:** the common 3.2 µV criterion corresponds to ±0.1° when measured on a left-minus-right difference wave (Papaioannou & Luck), but some papers reportedly quote it as <0.2° (unverified, seen only in search snippets). State which waveform the criterion applies to.
