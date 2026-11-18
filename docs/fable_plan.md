> **Corrections after the citation audit (2026-11-18, experiments/research_sweep/RESULTS.md).** The plan below is kept as written; these override it.
> - The COGITATE paper's intracranial cohort is 34 patients, not 38.
> - OpenNeuro ds003059 is LSD fMRI only (no MEG).
> - The July 2026 reanalysis is Bandara, Rowe & Garrido (doi:10.64898/2026.07.16.738188).
> - The ketamine results in Sarasso 2015, Colombo 2019 and Maschke 2024 come from one cohort of 5 people, so they count as one result, not three.
> - Unverified: COGITATE experiment 2 n=139, the COGITATE download sizes, and the claim that higher-order, recurrent-processing and attention-schema collaborations are running.

**Bottom Line**

"Understand consciousness by 2027" is not reachable. A checkable, narrower goal is: a frozen, theory-derived measure that tracks reported experience across held-out datasets, including cases where behaviour and experience come apart, and beats both rival theories and dumb spectral baselines. I put that at roughly 3-5% by end of 2027.

The most valuable thing a laptop team can do is the Indus move: bench every published measure against proper nulls and confounds, and publish the negative atlas. Items marked "(memory)" I did not verify in this session.

**1. What "Cracked" Means By End Of 2027**

The root claim is about measurement, not the hard problem: we can tell from brain data whether and what someone is experiencing, better than any rival, on data we never touched. All of these must hold:

- **Frozen model:** one measure plus decision rule, derived from a named theory, with code and thresholds SHA-256 hashed before any held-out data is opened. No per-dataset threshold tuning.
- **State, zero-shot:** conscious vs unconscious on at least 4 held-out datasets across at least 3 families (sleep, anesthesia, disorders of consciousness), pooled AUC ≥ 0.90 and ≥ 0.80 in every dataset.
- **Dissociation cases:** correct where responsiveness misleads, namely ketamine (unresponsive, experience reported afterward), REM dreaming, and dream vs no-dream awakenings within the same sleep stage. This is the anchor outside our own data: ground truth is the delayed report, not behaviour or the EEG.
- **Beats baselines:** it outperforms spectral slope, band power, and an arousal classifier by a pre-registered margin. Otherwise it is a sleepiness detector.
- **Beats rivals:** at least two rival theories' measures, frozen under the same protocol, score worse on a pre-registered log score.
- **Prospective test:** at least one dataset published after the hash date, or run by an outside lab.
- **Red team:** an independent team fails to break it with surrogates, confound matching, or adversarial systems.

Our own bench can refute but not confirm alone; the prospective dataset and red team do the confirming.

**2. Claim Ladder**

- **L0 Signal:** the measure is reproducible and differs between states beyond permutation nulls.
- **L1 State:** it separates clearly conscious from clearly unconscious states, where behaviour agrees.
- **L2 Dissociation:** it tracks experience when behaviour or arousal disagree, and survives spectral confound control.
- **L3 Content:** it predicts what is experienced (seen vs unseen, which content) across subjects, with report and task confounds controlled.
- **L4 Theory:** one theory's pre-registered predictions beat rivals across L1-L3 and extend to untested systems (infants, animals, lesions, machines).

Where the field stands:

- **L1 is solid.** Many measures work at group level.
- **L2 is partial.** The perturbational complexity index (PCI) is the strongest candidate (Casarotto et al. 2016, Annals of Neurology; memory). Spontaneous-EEG measures are in doubt, see section 4.
- **L3 is contested.** COGITATE gave mixed results.
- **L4 is empty.** No theory has won an adversarial test.

**3. Theory Map**

- **IIT 4.0 (Albantakis et al. 2023, PLoS Comput Biol; memory).**
  - Riskiest predictions: content lives in a posterior "hot zone" with sustained synchrony for as long as the percept lasts; consciousness depends on physical causal structure, so feedforward systems and digital computers have none regardless of behaviour.
  - Status: strained. In COGITATE, the posterior cortex showed no sustained synchronization, which undercuts the claim that network connectivity specifies consciousness.
  - One prediction passed: face orientation could be decoded from posterior regions but not prefrontal ones.
  - Φ itself is not computable for brains, so only proxies are testable. In 2023 an open letter labelled IIT a pseudoscience.
- **Global neuronal workspace (Dehaene, Changeux).**
  - Riskiest predictions: late all-or-none "ignition" with prefrontal broadcast at both onset and offset; content decodable from prefrontal cortex.
  - Status: strained. The Nature paper reports GNWT was partly challenged on its all-or-none threshold and prefrontal amplification, and press coverage notes workspace areas gave no sharp offset response when perception ended.
  - Caution: a July 2026 bioRxiv reanalysis using directed connectivity reports prefrontal ignition at both onset and offset, the latter missed in the original analyses. I did not get its authors; verify. Analytic flexibility on this dataset is large, which is why hashing matters.
- **Recurrent processing (Lamme).**
  - Riskiest prediction: local recurrence in sensory cortex is enough for experience, without report or frontal access.
  - Status: hard to refute, because it posits experience without access. I found no completed adversarial test.
- **Higher-order theories (Lau, Rosenthal, Brown).**
  - Riskiest prediction: prefrontal meta-representation is necessary, so prefrontal lesions or disruption should change experience itself, not only report.
  - Status: I found no published results. One secondary source says more collaborations are running, covering higher-order, recurrent processing and attention schema theories. Treat as unverified.
- **Predictive processing and active inference (Seth, Friston, Pennartz).**
  - Riskiest predictions: mostly none at the framework level, which is the problem. The INTREPID collaboration pits IIT against two versions: neurorepresentationalism (Pennartz) and active inference (Friston).
  - Status: no results yet that I could find. The 2026 consortium paper (Corcoran et al., Neurosci Biobehav Rev) plans the tests and reports no new findings.
- **Attention schema (Graziano).**
  - Riskiest prediction: awareness is a model of attention, so attention without awareness should show worse attentional control.
  - Status: few neural commitments; mostly useful as an AI test case.
- **Others worth a row:** dendritic integration (Aru, Suzuki, Larkum 2020, Trends Cogn Sci; memory), criticality and entropic-brain accounts, thalamocortical accounts. These yield cheap measures we can compute.

What COGITATE settles: n = 256 across fMRI, MEG and intracranial EEG, and the authors' verdict is that some predictions of each theory held while key tenets of both were substantially challenged. Nothing is refuted outright. A second experiment is in analysis: attention is manipulated through a video game, with 139 participants across fMRI and MEG.

**4. Bench The Published Claims**

The equivalent of "keys fitted to noise" is three questions for every published measure: does it beat a spectral baseline, does it survive phase-randomized surrogates, and does it transfer zero-shot?

- **Lempel-Ziv complexity (Schartner et al. 2015, PLoS One; memory).** The top target. A patient study found shuffle-normalized LZ correlated 0.86 with the 1-40 Hz spectral exponent, and its diagnostic value vanished once the measure was phase-normalized (Maschke et al., PMC12448740). Re-run on every open state dataset.
- **Spectral slope (Colombo et al. 2019, NeuroImage; memory).** It is both a candidate and the baseline to beat. Check whether it gets ketamine and REM right.
- **PCI and PCIst (Casali et al. 2013; Comolatti et al. 2019).** Can spontaneous EEG reproduce it? Maschke et al. 2024 (Communications Biology) claim that resting-EEG dynamics alone predict the TMS-derived index in healthy adults. Test that out of sample.
- **Φ proxies.** A rat study (Neuroscience of Consciousness 2024) found that spontaneous integrated-information estimates rose under propofol and sevoflurane and ran opposite to PCI. Bench all proxies with the planted controls in section 6.
- **Criticality measures.** Same three questions.
- **Neural-correlate claims (P3b, ignition, posterior hot zone).** Re-test on COGITATE with held-out subjects and task-relevance matched, plus the directed-connectivity reanalysis above.
- **Dream-report prediction (Siclari et al. 2017, Nature Neuroscience; memory).** Posterior low-frequency power predicting dream vs no dream within a sleep stage. This is the sharpest L2 test; I am unsure how well it has replicated.
- **Multivariate DoC classifiers (Sitt et al. 2014; Engemann et al. 2018, Brain; memory).** Check whether they transfer across sites and etiology.

**5. Open Datasets**

- **COGITATE iEEG:** 38 patients under one standardized protocol; download needs a registered account on their portal. Tests L3 and both theories' predictions. Laptop: yes, subject by subject.
- **COGITATE MEG-EEG:** a four-participant sample bundle is about 28 GB and the full set about 700 GB. Laptop: sample yes, full no without an external disk and patience.
- **COGITATE experiment 2:** the data page lists a version 2.0 release that will add MEG and fMRI from experiment 2. I could not confirm it is out. If it lands after our hash date, it is the ideal prospective test.
- **OpenNeuro ds005620:** propofol sedation EEG with repeated awakenings, built to test whether complexity measures capture dreaming, and some sessions include TMS. The best single L2 dataset I found. Laptop: yes.
- **OpenNeuro ds003171:** fMRI at four propofol sedation levels, at rest and during an audio clip. Tests L1 in fMRI. Laptop: yes, slowly.
- **Cambridge propofol EEG (Chennu et al. 2016, PLoS Comput Biol; memory):** 20 subjects, graded sedation with drug levels. I believe it is on the Cambridge repository; verify.
- **Sleep:** Sleep-EDF on PhysioNet (memory) for stage-level L1. The DREAM database (Wong et al. 2025, Nature Communications; memory, verify) pools serial-awakening studies with dream reports and is the key L2 resource if access is open.
- **Psychedelics:** Imperial LSD and psilocybin MEG and fMRI (Carhart-Harris group; OpenNeuro ds003059 for LSD fMRI; memory, verify). Tests whether a measure rises when contents intensify but level does not obviously change.
- **Disorders of consciousness:** very little is fully open; most sits behind data agreements. I found no open patient TMS-EEG set. This is the largest gap.
- **Split-brain and blindsight:** I know of no usable open neural datasets. Treat as literature-only.

**6. Planted-Answer Controls**

- **Recover a known state:** inject a labelled effect of known size into real wake EEG (flatten the slope, add slow waves) at our sample size. The pipeline must recover it before any real output counts.
- **Surrogates that must fail:** phase-randomized and spectrum-matched surrogates of conscious data. If a measure calls them conscious, it is measuring the spectrum.
- **Known-Φ systems:** small networks where exact Φ is computable with PyPhi (memory). Each proxy must rank them correctly from simulated time series, with noise and subsampling like real EEG.
- **Simulated ignition:** a neural-mass or spiking model with ignition switched on or off. The detection pipeline must tell them apart at COGITATE-like signal-to-noise.
- **Stipulated negatives:** cerebellum-like feedforward simulations, a thermostat, shuffled-weights recurrent networks.
- **AI systems, as stress tests only:** score a transformer and a recurrent network against each theory's stated criteria using the indicator-properties rubric (Butlin, Long et al. 2023, arXiv; memory). Purpose: find where theories disagree or give absurd answers, such as a measure rating white noise as highly conscious. Not a verdict on AI.

**7. First Tasks**

**M1 Foundations**

- **T1 Rules of evidence.** Port the Indus hash-and-ledger tooling; define leakage rules (split by subject, never by epoch; same lab counts as near-copy). Decisive: a dry run catches a deliberately leaked split. Laptop: yes.
- **T2 Dataset audit.** Verify access, license, size and ground-truth type for everything in section 5. Decisive: at least 4 datasets across 3 families qualify, or the root goal is rescoped. Laptop: yes.
- **T3 Ground-truth schema.** Label every recording by responsiveness, delayed report, or neither. Decisive: we know how many true L2 cases exist. Laptop: yes.

**M2 Bench Published Measures**

- **T4 LZ vs slope.** Compute LZ, slope, and phase-normalized LZ on ds005620, Chennu and Sleep-EDF. Decisive: LZ adds AUC over slope under permutation null, or it goes in the negative atlas with the effect size we could have caught. Laptop: yes.
- **T5 Zero-shot transfer.** Train thresholds on one family, test on the others, for 8-10 measures. Decisive: any measure holding AUC ≥ 0.80 everywhere moves up; the rest are logged as state-specific. Laptop: yes.
- **T6 Dream vs no-dream.** Within-stage awakenings in ds005620 and DREAM. Decisive: above-chance held-out prediction, or a clear null with power stated. Laptop: yes.
- **T7 Ketamine and REM.** Does each measure call them conscious? Data: Chennu-type sets plus any open ketamine EEG (find in T2). Decisive either way. Laptop: yes.

**M3 Theory Tests On COGITATE**

- **T8 Reproduce.** Re-run the consortium's public decoding analysis on the iEEG release. Decisive: we match the published numbers or document why not. Laptop: yes.
- **T9 Pre-registered multiverse.** Hash a set of reasonable analysis variants for ignition-at-offset and posterior synchrony, then run them all. Decisive: the fraction of variants supporting each theory, reported whole. Laptop: yes on iEEG, partial on MEG.

**M4 Planted Controls**

- **T10 Φ-proxy recovery.** Section 6 known-Φ networks. Decisive: proxies that fail to rank correctly are barred from brain data. Laptop: yes.
- **T11 Surrogate gate.** Every measure in T4-T7 runs on surrogates first. Decisive: pass or fail per measure. Laptop: yes.

**M5 Latest Research Sweep**

- **T12 Standing sweep.** Monthly pass over bioRxiv, arXiv, Neuroscience of Consciousness, plus COGITATE experiment 2, INTREPID and the other collaborations. Decisive: each new result is added to the scoreboard or noted as irrelevant. Laptop: yes.
- **T13 Verify my "(memory)" items.** Decisive: each is confirmed with a DOI or struck. Laptop: yes.

**M6 Red Team**

- **T14 Break every positive.** A separate agent with no access to the producing notes tries confound matching (age, drug dose, muscle artefact, eyes closed), alternative preprocessing, and site effects. Decisive: the result survives or is downgraded one ladder level. Laptop: yes.
- **T15 Theory-proponent check.** Draft, for the human lead to send by hand, each prediction as we encoded it, asking proponents whether it is fair. Decisive: sign-off or documented dispute. Laptop: yes.

**8. Honest Odds**

- **Full root goal by end of 2027:** about 3-5%. The binding constraints are too few open datasets with report-based ground truth, and no open patient TMS-EEG.
- **A red-teamed L2 benchmark** showing which measures survive the spectral confound and which do not: about 50-60%. That is a real, publishable contribution and where I would aim.
- **A clear theory winner at L4:** under 1%.

What would raise the odds most:

- An open TMS-EEG dataset across sleep, anesthesia and patients, so PCI can be benched directly.
- Open access to pooled serial-awakening dream data at scale.
- COGITATE experiment 2 or INTREPID data released after our hash date, giving a clean prospective test.

**9. Site Pages That Differ From Indus**

- **Theory scoreboard:** theory by prediction grid; each cell shows passed, failed or untested, with source and whether the test was adversarial.
- **Measure leaderboard:** each measure by dataset, with AUC, baseline delta, surrogate result and zero-shot result.
- **Dissociation cases:** one page per hard case (ketamine, REM, dream awakenings, covert awareness) showing which measures get it right.
- **Prediction registry:** hashed predictions with open, resolved and failed status.
- **Confound ledger:** every known confound and which results have been checked against it.
- **What we do not claim:** the hard problem, AI sentience, clinical use.
- **Machines:** the AI stress tests, framed as tests of theories.

**10. Blind Spots And Traps**

- **The hard problem.** Nothing here explains why experience exists. Say so on the home page, or critics will say it for us.
- **Report is the only ground truth.** No-report paradigms infer experience from prior report. Every label is inferential; grade label quality.
- **Unresponsive is not unconscious.** Most anesthesia and patient labels are behavioural. This is why L2 is the real test.
- **Level vs content.** A single "level" number may be the wrong shape for the problem (Bayne, Hohwy, Owen 2016, Trends Cogn Sci; memory).
- **Theories that do not compete.** IIT is about intrinsic structure, GNWT about access. A test can strain both without separating them.
- **Analytic flexibility.** The same COGITATE data already supports opposite conclusions on offset ignition.
- **Ordinary confounds.** Drug-specific EEG effects, age, muscle artefact, eyes closed, site and amplifier.
- **Small samples.** Most open state datasets have 10-30 subjects; state the detectable effect size every time.
- **AI hype.** Language models produce reports without any agreed ground truth. Never score a model's self-report as evidence.
- **Clinical overreach.** A measure that looks good here is not a diagnostic. Say that on the patient pages.
- **Our own bias.** A team that benches measures will be tempted to crown the survivor. A survivor is not a theory.