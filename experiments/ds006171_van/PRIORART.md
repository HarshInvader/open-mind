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
