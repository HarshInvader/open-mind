# COGITATE null audit: prior-art check (2026-11-20)

**Verdict: the audit is alive.** No one, the consortium included, has measured how large an effect either headline COGITATE null could have detected.

The idea: a planted-effect audit of two nulls in Cogitate Consortium 2025, Nature ([PMC12137136](https://pmc.ncbi.nlm.nih.gov/articles/PMC12137136/)).
- **(a) No sustained inter-areal synchrony.** BF01 1.15-4.9.
- **(b) No PFC offset ignition.** None of 655 PFC electrodes fit the predicted profile (BF01 > 3 for each).

## What was opened and what it says about detectability

- **Cogitate 2025: main text, Supplementary Information and Peer Review File** (Nature ESM files `41586_2025_8888_MOESM1_ESM.pdf` and `MOESM3`). There is no sensitivity analysis, power analysis, simulation or planted effect for either null.
  - **Synchrony null:** a single JZS prior (Cauchy r = 0.707), with no check of how the result depends on the prior. Power was addressed only by pooling task-relevant and task-irrelevant trials (SI 7.1.1).
  - **Offset null:** detectability is argued from positive controls (offset responses elsewhere, strong PFC onsets), not tested.
  - **Peer review:** a referee asked for power. The authors gave a textbook paired t-test figure (90% power at d = 0.33 / 0.31 for MEG / fMRI), said iEEG group sensitivity analyses "are not informative", and declined simulation as "computationally expensive and less meaningful". That figure is not in the published paper.
- **Moioli 2026 thesis appendix** ([github.com/enricomoioli/thesis-cogitate-appendix](https://github.com/enricomoioli/thesis-cogitate-appendix)).
  - Reproduces prediction 3 (iEEG dynamic functional connectivity) on an 8 GB laptop. The log shows 33 of 38 patients preprocessed and 2 failed.
  - Filed five consortium code issues (#53-#57):
    - amplitude normalisation always takes the interruption branch;
    - bad-channel attributes are not initialised;
    - `n/a` demographic fields stop preprocessing;
    - the selectivity permutation test has no seed;
    - synchrony configs point at folders that are never created.

    It also notes that the FreeSurfer reconstructions are missing.
  - No sensitivity or planted test.
- **Chis-Ciure 2026** ([arXiv 2611.06925](https://arxiv.org/abs/2611.06925)): philosophy of science. It puts detection and powering explicitly out of scope.
- **Bandara, Rowe & Garrido 2026** ([bioRxiv 10.64898/2026.07.16.738188](https://doi.org/10.64898/2026.07.16.738188); abstract only, full text rate-limited). A DCM reanalysis of the MEG data (N = 100) that reports PFC ignition at both onset and offset, contradicting the offset null by another method. It is not a sensitivity test.
- **Aperture Neuro commentary** ([link](https://apertureneuro.org/article/158354-human-consciousness-and-cognition-go-hand-in-hand-but-require-different-types-of-explanations)). Calls the synchrony BFs "inconclusive" because of coverage (12 early-visual electrodes against 472 in PFC). No simulation.
- **Searches for other sensitivity or planted reanalyses** (bioRxiv, arXiv, PsyArXiv, general web): none found.

## What remains open (the audit's question)

What effect size could the pooled-pair synchrony analysis (PPC/DFC/gPPI, BF01 1.15-4.9) and the 655-electrode onset+offset model comparison have detected, given the real electrode coverage and trial counts?

## Access

- **Licence:** CC BY 4.0.
- **Where:** [arc-cogitate.com/data-bundles](https://www.arc-cogitate.com/data-bundles) or XNAT (cogitate-data.ae.mpg.de).
- **Registration:** a free Cogitate data-user account is needed. The owner is creating it; no account is used yet.
- **Sizes:**
  - iEEG: 13 GB for the sample bundle, 77 GB for the full set.
  - MEG: 29 GB sample, 740 GB full.

## COGITATE experiment 2 (inattention): results status

No results preprint or paper was found (web and OpenAlex searches, 2026-11-20).
- **Design:** the 2022/2023 PLOS ONE protocol ([doi:10.1371/journal.pone.0268577](https://doi.org/10.1371/journal.pone.0268577)).
- **Latest public material:**
  - an ASSC 2025 poster (Hirschhorn, Melloni, Pitts, Mudrik): behaviour and method only, N = 139 (76 fMRI, 63 MEG);
  - a University of Birmingham news item saying the analysis is underway.

So sealed forecasts are still possible.
