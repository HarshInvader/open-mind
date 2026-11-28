# Ideas from the library (2026-11-19)

Ranked ideas that came out of the 2026-11-19 library sweep. They are ideas only. None is a study. Anything that touches the experience benchmark (#42) needs a sealed amendment before any label is opened. Ids refer to `docs/library/library.json`.

## 1. Add Michalak's open N2 table as an extra spectral test lab for #42

- **Sources:** michalak-2026-immersive-n2-dreaming; selte-2026-nrem-experience-hdeeg; dream-eeg-mentation-database.
- **What is untested:** whether posterior delta, gamma and their ratio separate experience from no experience at N2 in a lab that is not in DREAM. Selte reports ROC-AUC 0.80, but from one lab with N2 and N3 pooled.
- **Open data:** Zenodo 10.5281/zenodo.15372992 (CC BY 4.0). It holds 1,024 N2 awakenings with channel-wise delta and gamma power per awakening. It is derived features only, about 180 MB.
- **Bears on a current study:** yes, #42. It can test only the spectral side, which is the part our "markers fail on experience" outcome depends on. The five report classes would need a mapping to experience vs no experience, sealed before any labels are read.

## 2. Report the spectral baseline's own experience AUC as a headline number in #42

- **Sources:** selte-2026-nrem-experience-hdeeg; rochas-2026-n2-dreaming-hdeeg; congyu-2026-neural-field-doc.
- **What is untested:** how well the frozen spectrum alone does at fixed stage, in held-out labs. If it is near 0.80, our "major negative" (every marker below 0.60) can only be about what markers add beyond the spectrum. It would then say nothing about whether EEG carries experience.
- **Open data:** the DREAM labs already in #42.
- **Bears on a current study:** yes, #42 reporting. This is not a new test: the baseline score is already computed. It only needs to be shown up front. Any change to the wording of the outcomes goes through an amendment.

## 3. Rerun high-AUC dream decoders with subjects held out, to measure leakage

- **Sources:** moctezuma-2025-hd-to-ld-dream-classification (AUROC 0.97, splits over awakenings); moctezuma-2025-dreams-dreamless-channels (fails on unseen subjects); dream-eeg-mentation-database (0.59 in NREM, held out).
- **What is untested:** how much of 0.97 is left when no person appears in both training and test.
- **Open data:** DREAM Tononi set (10.26180/23306054.v2) and Zhang & Wamsley set. Both are in our exposed tier, so this costs no confirmation data.
- **Bears on a current study:** supports #42 and #22 as a method note. It is quick, and it is a red-team result in its own right.

## 4. Stage-controlled check of the posterior gamma/alpha claim on exposed DREAM N2

- **Sources:** selte-2026-nrem-experience-hdeeg; bertoni-2026-pps-index-sleep-doc (no-experience reports: N3 50%, N2 21.9%); rochas-2026-n2-dreaming-hdeeg.
- **What is untested:** whether Selte's posterior pattern holds within N2 alone, or partly reflects the N2/N3 mix.
- **Open data:** DREAM Tononi set (exposed tier; same lab as Selte, so this is not independent).
- **Bears on a current study:** close to #42, so run it only on exposed data. It would explain a strong spectral baseline but cannot confirm one.

## 5. Use psilocybin EEG (ds006110) as the "more experience, same arousal" arm of Study 2

- **Sources:** stoliker-2026-psilocybin-context; dai-2026-integration-segregation-mirror; carhart-harris-2026-entropic-brain-today; nikolic-2026-psilocybin-eeg-timecourse.
- **What is untested:** whether complexity and integration measures that fall from wake to N3 and under propofol rise under psilocybin after the spectrum is nested. That is the entropic-brain claim of "breadth of experience, not arousal".
- **Open data:** OpenNeuro ds006110 (v1.2.0): 64-channel EEG, rest and naturalistic tasks, before and on psilocybin.
- **Bears on a current study:** Study 2 (state benchmark). Check the download size and the licence before planning.

## 6. Treat waveform asymmetry as an arousal marker when interpreting tra_x

- **Sources:** nunez-2026-waveform-morphology; berjaga-buisan-2026-fdt-nonequilibrium.
- **What is untested:** whether tra_x is explained by simple waveform-shape statistics (rise/decay asymmetry) on Sleep-EDF.
- **Open data:** Sleep-EDF Expanded (10.13026/C2X676), already local.
- **Bears on a current study:** it interprets the finished nonequilibrium result. This is a small exploratory check, labelled as such.

## 7. Add a "reach" line to the prereg template

- **Sources:** chis-ciure-2026-measure-centrality-index; overgaard-2026-theory-method-dependencies.
- **What is untested:** this one is process, not data. Each sealed outcome should say what it counts against and what we agree to change if it fails.
- **Bears on a current study:** future preregs only. Do not edit sealed preregs.

## 8. Correct the phi_proxy recovery test for phi's discontinuity

- **Sources:** wu-he-2026-certifying-phi; mayeux-2026-iit-xor-cycles; mayner-2018-pyphi.
- **What is untested:** how often near-identical small networks give very different exact phi in our test set. If that happens often, a proxy cannot be expected to recover phi, and a low recovery score says little.
- **Open data:** our own generated networks (PyPhi ground truth).
- **Bears on a current study:** phi_proxy. Report the result next to the recovery score.

## Lower priority

- **Serial dependence of reports across a night** (zheng-melloni-2026-long-timescale-awareness). Does the previous awakening's report predict the next one beyond the existing #42 covariates? Exploratory only.
- **Hutchinson VAN/P3b effect sizes as priors for any Stockart reanalysis** (hutchinson-2026-van-p3b-meta).
- **Simulated positive controls for spontaneous-EEG markers** (gaglioti-2026-structural-complexity). Plant known wiring in a model and check that each #42 marker can see it.

## Ideas from Thorat and Chopra (2026), added 2026-11-20

Source: arXiv:2609.33366 (doi:10.48550/arXiv.2609.33366, full text read). Their programme builds a "functional profile" of what awareness changes, using only contrasts where the information available about the content is matched. Their sweep code is public: https://github.com/Lossfunk/consciousness-sweep (opened). Ideas only; none is a study yet. Each needs the prior-art step before any compute.

### A. Sensitivity audit of the functional profile's nulls

- **What is untested:** their one "preserved without awareness" entry (Keizer et al. 2015, doi:10.3758/s13423-014-0706-2, not yet opened) rests on a non-significant masking-by-binding interaction (8.6 ms vs 5.8 ms binding cost; their summary). Nobody has said what effect that design could have detected, or whether the data support equivalence.
- **Method:** the same as the COGITATE null audit: smallest detectable effect and equivalence bounds from reported statistics, then from raw data if open.
- **Why it matters:** negative constraints are the hardest part of their profile to defend, and they say so themselves.

### B. A spectral-matching gate for neural evidence

- **What is untested:** whether the aware-vs-unaware neural differences their architectures must respect survive the neural version of their own matching rule (spectrum and signal strength matched). Our LZ result says at least one level marker does not.
- **Method:** extend the surrogate gate and spectral baseline from state contrasts to trial-level aware-vs-unaware contrasts on open no-report or masking EEG.

### C. Sealed, prospective AST predictions for COGITATE experiment 2

- **What is untested:** they ask for prospective predictions that separate candidate architectures. COGITATE experiment 2 manipulates attention, and results are not out. Attention Schema Theory, their worked example, should predict when an unattended stimulus is still reported as experienced.
- **Method:** write AST's predictions next to IIT's and GNWT's in the forecast registry and hash them before release. Ideally with the authors, so the predictions are ones AST's proponents accept.

## Added 2026-11-21 (paper watch)

### Alpha network shape versus alpha power under propofol (bears on #8, #21)

- **Source.** Zhou, Edlow et al. 2026, Cortex, doi:10.1016/j.cortex.2026.11.009 (abstract only). Alpha coherence network organisation classified DoC recovery at AUC .78 against .45-.53 for wPLI.
- **What is untested.** Whether the network measure carries anything beyond alpha power. Coherence comes from the cross-spectrum, which our multichannel phase-randomised surrogates keep, so it should count as spectral in the surrogate gate.
- **Open data.** Chennu propofol EEG (task #21).
- **Bears on a current study.** Yes, #8 (surrogate gate) as a classification note; a test would need a sealed prereg.

## Added 2026-11-28 (paper watch)

### Lattice versus paralattice cortex as a fixed split for posterior-versus-prefrontal tests (bears on the theory scorecard)

- **Source.** Boly, ... Sporns, Tononi 2026, bioRxiv, doi:10.64898/2026.11.24.768659 (abstract only). Strong short-range resting-state connections in 151 HCP 7T subjects split cortex into a dense, hierarchical posterior-central "lattice" and a distributed prefrontal "paralattice".
- **What is untested.** Whether conscious-content decoding sits in lattice vertices more than in size-matched paralattice vertices. This split comes from connectivity alone, so it is not chosen with the consciousness data in view, unlike the usual hand-drawn posterior and prefrontal ROIs.
- **Open data.** COGITATE fMRI (its data account is still an owner step; see docs/ACCOUNTS.md) and the HCP. It needs the lattice map, which the abstract does not say is released.
- **Bears on a current study.** Not yet. It would need a sealed prereg once the map is available.
