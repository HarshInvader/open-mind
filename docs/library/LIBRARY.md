# Open Mind library

Generated from `library.json` on 2026-11-25. Do not edit by hand.

237 entries: 49 read in full, 188 from the abstract only. Every DOI was opened and its title and authors checked.

Relevance: **core** bears on a current study; **useful** may shape one; **context** is background.

## Theories tested (72)

### A data-driven approach to identifying and evaluating connectivity-based neural correlates of conscious visual perception

Bryant AG, Whyte CJ (2026). *Neuroscience of Consciousness 2026(1), niag029*. [doi:10.1093/nc/niag029](https://doi.org/10.1093/nc/niag029). Paper, abstract only, **core**.

- **Question:** Testing 246 ways of measuring brain connectivity on the COGITATE data gives tentative support to the workspace theory.
- **Data and method:** COGITATE MEG, 94 of 100 downloaded participants with anatomy for source localisation. 246 functional connectivity measures between IIT- and GNWT-predicted regions; barycenter-based measures decoded stimuli best and generalised across regions. Neural mass models: GNWT with delayed ignition, IIT with synchronous sensory dynamics; both captured the observed patterns. Conclusion: tentative support for GNWT, because ignition appeared regardless of task demands. A correction was issued (niag071).
- **Results:** Rather than pick one connectivity measure, the authors tried 246 of them on the same public recordings, found the family that best tells pictures apart, and then built small brain models of each theory to see which reproduced it. Both models fit; the authors lean slightly towards the workspace theory.
- **For us:** A second independent reanalysis of the same data, from a different angle. Its 246-measure sweep is a template for our pre-registered multiverse; we would hash the measure list first.
- **Touches:** news

### A late meta-stable code of conscious access in the absence of report

Hutchinson BT, Dehaene S, Slagter HA, Pitts MA (2026). *bioRxiv*. [doi:10.64898/2026.01.30.702733](https://doi.org/10.64898/2026.01.30.702733). Preprint, full text, **core**.

- **Question:** Without report (and without a P3b), is there still a late, sustained neural code for seen stimuli?
- **Idea tested:** Reanalysis of four no-report EEG datasets with temporal-generalisation (TG) decoding of seen vs unseen.
- **Data and method:** Four EEG datasets; per-timepoint decoders, TG matrices, cluster statistics; 0.1 Hz online high-pass in three datasets, baseline -100 to 0 ms, 250 Hz.
- **Results:** Seen stimuli gave a TG 'square' at about 200-400 ms without report or P3b; read as a single code sustained over time (GNW ignition). For faces, a decoder trained at 200 ms generalised from about 180 to 400 ms.
- **Limits:** Latency jitter is raised and rejected in words, not by simulation. Square vs diagonal is judged by eye; the authors call for a quantitative metric. The pipeline's high-pass and baseline are known to create cross-time generalisation (van Driel 2021).
- **For us:** Source of round 16 item 2: does jitter across non-stable transient codes reproduce their square under their pipeline?
- **Touches:** tg_square_specificity

### Integrated information and predictive processing theories of consciousness: an adversarial collaborative review (INTREPID)

Corcoran AW, Haun AM, Dorman R, Tononi G, Friston KJ, Pennartz CMA, TWCF INTREPID Consortium (2026). *Neuroscience & Biobehavioral Reviews 187, 106742*. [doi:10.1016/j.neubiorev.2026.106742](https://doi.org/10.1016/j.neubiorev.2026.106742). Paper, abstract only, **core**.

- **Question:** The second big adversarial collaboration has published its plan: IIT against two predictive-brain theories. No results yet.
- **Data and method:** Compares IIT, neurorepresentationalism (Pennartz) and active inference (Friston): target phenomena, explanatory styles, methods. Lists key hypotheses for multi-site experiments and what would support or challenge each theory, and proposes formally combining results across experiments and replications into a quantitative measure of evidential support per theory. Preprint arXiv:2509.00555 (v1 Aug 2025, v3 May 2026). Online 14 May 2026, issue Aug 2026.
- **Results:** Three teams with rival theories wrote down, together, which experiments would tell their ideas apart and what each result would mean. The experiments run across several labs. This paper is the agreed plan and a comparison of the theories, not the results.
- **For us:** If its data appears after we seal our predictions, it is a clean prospective test. Its evidence-pooling idea is a model for our own log-score comparison of theories.
- **Touches:** news

### Testing the spatiotemporal predictions of global neuronal workspace theory and integrated information theory

Bandara KH, Rowe EG, Garrido MI (2026). *bioRxiv*. [doi:10.64898/2026.07.16.738188](https://doi.org/10.64898/2026.07.16.738188). Preprint, full text, **core**.

- **Question:** Do GNWT's phasic prefrontal ignition (onset and offset) and IIT's sustained posterior feedback show up in directed connectivity of the COGITATE MEG data?
- **Idea tested:** Dynamic causal models with and without each theory's key connections, compared by Bayesian model reduction in expanding time windows.
- **Data and method:** COGITATE MEG, task-irrelevant faces (100 recruited, 98 analysed), discovery (N = 48) and validation (N = 52) batches; DCM of prefrontal, fusiform and V1 nodes in expanding windows after onset and offset; post-hoc face-vs-object specificity check. Not peer reviewed.
- **Results:** Dynamic causal modelling of the MEG data (100 recruited, 98 analysed) split into a discovery batch (N = 48) and a validation batch (N = 52), with expanding time windows. Removing prefrontal-to-fusiform feedback was strongly penalised (posterior probability > 0.95) in the 300-500 ms window after onset and, at offset, from the 400 ms window, in both batches. Fusiform-to-V1 feedback was needed (pp > 0.95) in only 2 of 8 non-successive windows in discovery and was not sustained in validation; intrinsic fusiform gain was needed in every window in validation but dipped at 600 ms in discovery (ending at pp about 0.78). A face-versus-object network check did not reach strong evidence for face selectivity in any window. Unlike the original COGITATE analysis, this finds prefrontal feedback at offset as well as onset.
- **Limits:** One reanalysis with many modelling choices on data whose original analysis found no offset ignition; the failed content-specificity check means the network may not be face-specific, which weakens the posterior (sustained) tests most. Not peer reviewed.
- **For us:** This is the 'July 2026 reanalysis' the plan could not name. It goes into our multiverse on COGITATE (task #11) as one of the analysis paths, and shows why we hash the analysis set first. Used as a post-cutoff item in the theory-ledger leak probe and manipulation check (experiments/theory_leak).
- **Touches:** news, ledger

### The neural correlates of consciousness: a systematic review and meta-analysis of the visual awareness negativity and P3b

Hutchinson BT, Pustejovsky JE, Bandara K, McGovern H, Cox J, Voce A, Pitts M, Slagter HA (2026). *Psychological Bulletin*. [doi:10.1037/bul0000521](https://doi.org/10.1037/bul0000521). Review, abstract only, **core**.

- **Question:** Are the VAN and P3b necessary and sufficient markers of visual awareness?
- **Idea tested:** A registered-report meta-analysis of seen and unseen effects with quality and bias moderators.
- **Data and method:** 117 studies, 547 seen effect sizes (322 VAN, 225 P3b) and 89 unseen effect sizes.
- **Results:** VAN standardized mean difference 0.37 (95% CI 0.32-0.43); P3b 0.49 (0.41-0.57). P3b was not reliably present when stimuli were task-irrelevant (-0.12, -0.47 to 0.23), so it is not necessary; the VAN appeared even without awareness, so it is not sufficient. (abstract only)
- **Limits:** Abstract only; moderator results not read.
- **For us:** Settles two ledger rows: P3b as a report/task marker (C28 line) and VAN as not sufficient. Our GNWT extension (T4) and any Stockart reanalysis should use these effect sizes as priors.
- **Touches:** constraint_ledger, theory_gnwt_frontal_dream, T4

### Towards full-stack functionalist theories of consciousness: Identifying the functional profile

Thorat S, Chopra P (2026). *arXiv (Lossfunk)*. [doi:10.48550/arXiv.2609.33366](https://arxiv.org/abs/2609.33366). Preprint, full text, **core**.

- **Question:** If consciousness is something a system does, what does being aware of a thing change about how the system can use it?
- **Idea tested:** They searched the literature for experiments that compare using the same information with and without awareness, and kept only those where the unaware version did not simply carry weaker information (for example, by matching how well people could discriminate the stimulus).
- **Data and method:** Literature review with strict inclusion rules: awareness measured or validated, information strength matched or ruled out by design (a reversal), and an outcome that says how the information is used. Sweep code: github.com/Lossfunk/consciousness-sweep.
- **Results:** Only a few studies pass. Awareness goes with control over attention (Tsushima 2006: faint, invisible motion distracted people more than stronger, visible motion, as if visible distractors can be suppressed) and with knowing when you're right (Persaud 2011: blindsight patient GY was equally accurate in both visual fields, but his bets tracked his accuracy far better in the seeing field, r = .52 vs .30). Simple binding of a feature to a location worked without awareness (Keizer 2015). They then argue a full theory must also explain what experience is like and why people find it mysterious, and use Attention Schema Theory as the worked example of going from one such finding to a buildable architecture.
- **Limits:** The profile is thin: metacognition rests mainly on one patient, binding on one paradigm. The binding 'no difference' is a non-significant interaction (8.6 vs 5.8 ms), not shown equivalence, as the authors say. Neural signatures are excluded unless their computation is known.
- **For us:** This is the basis of our 'Can AI be conscious?' sub-project: the self-model agents study tries their agenda item 4 (build agents that model their own attention, ablate the model, check the profile). Also: audit the power of the binding null (as in the COGITATE null audit), and seal AST predictions for COGITATE experiment 2.
- **Touches:** Self-model agents, Can AI be conscious?, COGITATE forecasts

### Adversarial testing of global neuronal workspace and integrated information theories of consciousness

Cogitate Consortium (Ferrante, Gorska-Klimowska, Henin, Hirschhorn, Khalaf, Lepauvre, Liu, Richter, Vidal and others) (2025). *Nature 642, 133-142*. [doi:10.1038/s41586-025-08888-1](https://doi.org/10.1038/s41586-025-08888-1). Paper, full text, **core**.

- **Question:** The first big head-to-head test of two theories of consciousness found that each got some predictions right and each got key claims wrong.
- **Data and method:** n = 256 (fMRI 120, MEG 102, iEEG 34), suprathreshold faces, objects, letters and false fonts shown for 0.5, 1.0 or 1.5 s, task-relevant and task-irrelevant. Content information found in visual, ventrotemporal and inferior frontal cortex; sustained responses in occipital and lateral temporal cortex tracked duration; content-specific synchronisation between frontal and early visual areas. IIT challenged by no sustained posterior synchronisation; GNWT challenged by general lack of offset ignition and limited prefrontal representation of some conscious dimensions. Preregistration: osf.io/92tbg. Data CC BY 4.0, account needed for download.
- **Results:** Two rival theories agreed in advance what results would count against them. Then 256 people looked at pictures while their brains were scanned in three different ways. Neither theory won. One theory said the back of the brain should stay in sync for as long as a picture is seen; it did not. The other said the front of the brain should flare up when a picture disappears; mostly it did not.
- **For us:** The data is public (Experiment 1: MEG, fMRI, iEEG), so it is the first place we test whether the published conclusions survive other reasonable analyses. Note the paper's iEEG n is 34; the plan said 38.
- **Touches:** news

### GNW theoretical framework and the "adversarial testing of global neuronal workspace and integrated information theories of consciousness"

Naccache L, Sergent C, Dehaene S, Wang XJ, Farisco M, Changeux JP (2025). *Neuroscience of Consciousness*. [doi:10.1093/nc/niaf037](https://doi.org/10.1093/nc/niaf037). Article, full text, **core**.

- **Question:** How do GNW's proponents read the COGITATE experiment 1 results?
- **Idea tested:** A reply by GNW proponents to the COGITATE 2025 results.
- **Data and method:** Commentary on published data; no new data.
- **Results:** They say several core GNW predictions were confirmed (onset ignition, frontal content decoding, frontal-visual synchrony); offset ignition is not a core prediction; and COGITATE experiment 1 could not test GNW's central claim, conscious vs unconscious processing, because every stimulus was clearly visible.
- **Limits:** Written by the theory's proponents. The offset-ignition prediction was signed off before the results.
- **For us:** Shows why experiment 2 (seen vs unseen) is the test GNW proponents call decisive. Our forecasts take that test as the target.
- **Touches:** COGITATE forecasts

### An adversarial collaboration protocol for testing contrasting predictions of global neuronal workspace and integrated information theory

Melloni L, Mudrik L, Pitts MA, Bendtz K, Ferrante O, Górska U, Hirschhorn R, Khalaf AF, and others (2023). *PLOS ONE*. [doi:10.1371/journal.pone.0268577](https://doi.org/10.1371/journal.pone.0268577). Article, full text, **core**.

- **Question:** How can GNW and IIT be tested against each other with predictions both sides agree on in advance?
- **Idea tested:** The COGITATE protocol: two experiments with predictions signed off by GNW and IIT proponents. Experiment 1 shows clearly visible stimuli with task relevance varied; experiment 2 hides faces and objects in the background of a demanding video game, so some are missed (inattentional blindness), then replays the same displays with a detection task.
- **Data and method:** fMRI, M-EEG and iEEG at several sites. Experiment 2 contrasts seen vs unseen under distraction, and tests whether brain patterns generalise between distracted and attended viewing.
- **Results:** Protocol only. In experiment 2, GNW predicts conscious content decodable from prefrontal cortex at 300-500 ms, prefrontal-to-category-area synchrony for seen stimuli, no seen/unseen difference before 250 ms, and higher prefrontal pre-stimulus activity before missed stimuli. IIT predicts posterior patterns that stay the same across tasks for seen stimuli and posterior (category area to V1/V2) synchrony.
- **Limits:** Frequent awareness probes make the 'unattended' stimuli partly task-relevant, which blurs the inattention manipulation. Experiment 2 results were not public as of 2026-11-21.
- **For us:** Basis for our sealed forecasts of experiment 2 (docs/prereg/2026-11-21_cogitate_exp2_forecasts.md, 17 items, scored against each theory as a forecaster).
- **Touches:** COGITATE forecasts, COGITATE audit

### Bifurcation in brain dynamics reveals a signature of conscious processing independent of report

Sergent C, Corazzol M, Labouret G, Stockart F, Wexler M, King JR, Meyniel F, Pressnitzer D (2021). *Nature Communications*. [doi:10.1038/s41467-021-21393-z](https://doi.org/10.1038/s41467-021-21393-z). Paper, full text, **core**.

- **Question:** Does single-trial EEG at threshold show a bifurcation into two states (conscious access), and does this hold without report?
- **Idea tested:** Auditory vowel detection in noise at 6 SNRs, active (report) and passive (mind-wandering probes) sessions; MVPA projections modelled trial by trial.
- **Data and method:** 20 subjects, EEG. Decoder trained on no-sound vs max SNR, generalised to intermediate SNRs; per 30 ms window, Model 0 (null), Model 2 (unimodal, logistic mean) and Model 3 (two-state mixture) fitted with 5-fold block CV; random-effects BMS with protected exceedance.
- **Results:** Model 3 protected exceedance above 0.95 from about 250 to 700 ms; the unimodal model had the highest probability from 0 to 250 ms and again from 700 to 900 ms. The bifurcation fit predicted reports (AUC > 0.75) and mind-wandering probe content without report.
- **Limits:** The model set has no graded rival with a jittered threshold or heavy tails: our simulation found the comparison calls bifurcation on such graded data (74-98% of studies), fixed once those rivals are added. The early-unimodal period coincides with weak decoding.
- **For us:** Source of our bifurcation audit (NOT SPECIFIC), the extended-model fix (FIX WORKS), the SNR-timing study and the real-data Cohen prereg. Data and code on OSF aw3t5 (Dropbox-linked; 11.4 GB preprocessed active).
- **Touches:** bifurcation_specificity

### Decoding across sensory modalities reveals common supramodal signatures of conscious perception

Sanchez G, Hartmann T, Fuscà M, Demarchi G, Weisz N (2020). *PNAS*. [doi:10.1073/pnas.1912584117](https://doi.org/10.1073/pnas.1912584117). Paper, abstract only, **core**.

- **Question:** Is there a signature of conscious detection that is shared by vision, hearing and touch?
- **Idea tested:** Train a detected-vs-undetected decoder in one sense and test it in another.
- **Data and method:** MEG, near-threshold visual, auditory and tactile stimuli in the same participants; two samples (n = 16 and 14).
- **Results:** Detected vs undetected decoded across modalities, peaking around 400 ms after the stimulus, and this replicated in the second sample.
- **Limits:** MEG, small samples; the shared signal is late and widespread, which a commentary reads as a content-free late modulation rather than a specific mechanism.
- **For us:** The closest prior art to a cross-sense transfer screen. Late cross-modal transfer is established in MEG, so that alone would not be new; nobody has done it in open EEG into touch.
- **Touches:** hypothesis-generator

### PyPhi: a toolbox for integrated information theory

Mayner WGP, Marshall W, Albantakis L, Findlay G, Marchman R, Tononi G (2018). *PLoS Computational Biology 14:e1006343*. [doi:10.1371/journal.pcbi.1006343](https://doi.org/10.1371/journal.pcbi.1006343). Paper, full text, **core**.

- **Question:** How can phi be computed exactly?
- **Idea tested:** An open Python implementation of IIT 3.0.
- **Data and method:** Software paper.
- **Results:** Exact phi takes exponential time; practical up to about 10-12 nodes.
- **Limits:** Exact only for tiny networks.
- **For us:** The ground truth in our phi_proxy recovery test.
- **Touches:** phi_proxy

### On the independence of visual awareness and metacognition: a signal detection theoretic analysis

Jachs B, Blanco MJ, Grantham-Hill S, Soto D (2015). *J Exp Psychol Hum Percept Perform*. [doi:10.1037/xhp0000026](https://doi.org/10.1037/xhp0000026). Article, abstract only, **core**.

- **Question:** Does knowing whether you are right (metacognition) depend on being aware of the stimulus?
- **Idea tested:** People judged the tilt of a masked, near-threshold grating, then reported awareness and confidence on every trial.
- **Data and method:** Three experiments; type-1 (perceptual) and type-2 (metacognitive) sensitivity by awareness level. Data are in the Confidence Database.
- **Results:** Awareness strongly raised perceptual sensitivity but changed metacognitive sensitivity much less.
- **Limits:** Small samples; binary awareness; no stimulus manipulation; abstract only read here (paywalled).
- **For us:** The single-study version of our planned metacognition test, so its data cannot be reused as new evidence. Our test needs a simulated signal-detection null because rating-defined 'unseen' trials are biased.
- **Touches:** Metacognition and awareness, Can AI be conscious?

### Characterizing the dynamics of mental representations: the temporal generalization method

King JR, Dehaene S (2014). *Trends in Cognitive Sciences*. [doi:10.1016/j.tics.2014.01.002](https://doi.org/10.1016/j.tics.2014.01.002). Review, full text, **core**.

- **Question:** How can decoding across train and test times reveal the dynamics of a mental representation?
- **Idea tested:** Simulations of different neural dynamics and the TG matrices they produce.
- **Data and method:** Taxonomy of TG patterns (diagonal, square, chains, reactivation) from simulated sources.
- **Results:** Sustained codes give a square; a chain of transient codes gives a diagonal. Onset jitter smooths the matrix horizontally and vertically.
- **Limits:** Asks, but leaves open, which factors make operations appear diagonal or square.
- **For us:** Baseline taxonomy for the TG-square specificity simulation.
- **Touches:** tg_square_specificity

### Have grand theories of consciousness earned their keep?

Owen AM, Goodale MA (2026). *Neuron*. [doi:10.1016/j.neuron.2026.08.020](https://doi.org/10.1016/j.neuron.2026.08.020). Paper, abstract only, **useful**.

- **Question:** Have overarching theories driven the field's real advances?
- **Idea tested:** The biggest advances came from rigorous empirical work, not grand theory.
- **Data and method:** Perspective.
- **Results:** Argues future progress may depend on returning to empirical tradition. (abstract only)
- **Limits:** Opinion.
- **For us:** Supports our results-first, theory-light ordering; useful framing for the #42 write-up if it is a benchmark rather than a theory test.
- **Touches:** #42, #17

### Integrated information and predictive processing theories of consciousness: An adversarial collaborative review

Corcoran AW, Haun AM, Dorman R, Tononi G, Friston KJ, Pennartz CMA, INTREPID Consortium (2026). *Neuroscience and Biobehavioral Reviews 187, 106742*. [doi:10.1016/j.neubiorev.2026.106742](https://doi.org/10.1016/j.neubiorev.2026.106742). Paper, abstract only, **useful**.

- **Question:** How do IIT, neurorepresentationalism and active inference differ, and what will INTREPID test?
- **Idea tested:** Review comparing the three theories and setting out the hypotheses for the multi-site INTREPID experiments.
- **Data and method:** Review, no new data.
- **Results:** States the planned hypotheses and an evidence-integration scheme; no experimental results yet.
- **Limits:** No results, so nothing yet to score forecasts against.
- **For us:** Source of pending-outcome items for the ledger when INTREPID reports.
- **Touches:** theory-ledger

### Long-timescale dynamics shape visual conscious awareness

Zheng Z, Trübutschek D, Cai Y, Melloni L (2026). *bioRxiv (8 Sep 2026)*. [doi:10.64898/2026.09.03.748970](https://doi.org/10.64898/2026.09.03.748970). Preprint, full text, **useful**.

- **Question:** How does conscious awareness fluctuate over time across trials?
- **Idea tested:** Subjective reports should carry long autocorrelation not explained by response bias.
- **Data and method:** Reanalysis of 20 existing visual awareness datasets (N = 335) of visibility/confidence and accuracy; one reanalysed single-pulse TMS dataset (right DLPFC vs vertex, 0-500 ms).
- **Results:** Reanalysis of 20 existing datasets (N = 335). Subjective measures fit an exponential decay; in the 14 datasets with known trial durations the characteristic timescales generally exceeded 5 s, with autocorrelation reaching asymptote over about 30-100 s; accuracy fit a slow linear decay. In a reanalysed TMS dataset (right DLPFC vs vertex, single pulses at 0-500 ms), DLPFC stimulation reduced the amplitude of confidence autocorrelation (beta = -0.129, SE = 0.050, P = 0.010) without changing its decay constant (P = 0.323), and had no detectable effect on objective performance (P = 0.735 intercept, P = 0.589 slope).
- **Limits:** All data are reanalysed from earlier studies; the TMS evidence is one dataset with a between-subjects site factor. Long autocorrelation in reports may still partly reflect criterion drift, which the authors argue against but cannot rule out.
- **For us:** Serial-awakening reports may also be autocorrelated within a night. #42 already has awakening index and time of night as covariates; the previous report could be checked as a nuisance in an exploratory analysis. Used as a post-cutoff item in the theory-ledger leak probe and manipulation check (experiments/theory_leak).
- **Touches:** #42, ledger

### No support beyond reach: the Measure Centrality Index 2.0 and adversarial comparisons of consciousness theories

Chis-Ciure R (2026). *arXiv 2611.06925*. [doi:10.48550/arXiv.2611.06925](https://doi.org/10.48550/arXiv.2611.06925). Preprint, abstract only, **useful**.

- **Question:** How can preregistered adversarial tests stop passes being claimed for a theory's core while failures are pinned on auxiliaries?
- **Idea tested:** The Reach Principle: a pass counts only as deep as the matching failure would have cut; fix attribution before the result.
- **Data and method:** Conceptual framework applied to COGITATE's third prediction.
- **Results:** On COGITATE prediction 3, the target was the posterior-connectivity implementation; the core of both theories stood outside the test, so a pass could have been claimed at any depth. (abstract only)
- **Limits:** Conceptual.
- **For us:** Add a 'reach' line to our prereg template: for each outcome, what it counts against and what we agree to change. Cheap and it hardens every sealed test.
- **Touches:** docs/prereg/TEMPLATE.md, #11, #28

### QNodes: A Scalable Algorithm for Efficient Minimum Information Partitioning in Integrated Information Theory

Guerrero Mendieta L, Bustamante-Mora A, Arango-López J, Díaz-Arancibia J, Ossa L (2026). *Applied Sciences 16(22):11532*. [doi:10.3390/app162211532](https://doi.org/10.3390/app162211532). Paper, abstract only, **useful**.

- **Question:** Can the minimum information partition, the costly core step in computing IIT's phi, be found fast and exactly for larger systems?
- **Idea tested:** A Queyranne-style pendant-pair search over partitions with the Earth Mover's Distance loss, plus an N-cube representation of conditional distributions, for the effect-side MIP of a mechanism-purview pair.
- **Data and method:** Proofs (the loss is symmetric, has a closed form on node-factorizable repertoires, is not submodular in general; exactness holds under a node-by-node checkable condition). Benchmark on 470 subsystems of synthetic and real networks against PyPhi.
- **Results:** Matched PyPhi's minimum loss in all 317 cases PyPhi completed; 153 times faster at 10 elements; completed every subsystem up to 22 elements. Outside the sufficient condition it is a heuristic, and the paper reports its failure rate and loss gaps against exhaustive search. (abstract only)
- **Limits:** Abstract only: the MDPI page and PDF returned HTTP 403. Covers only the effect-side MIP of one mechanism-purview pair, not full system Phi (cause side, purview search, system partition). Exactness is guaranteed only when the condition holds. Modest venue; not yet used by IIT groups.
- **For us:** For #9 (phi_proxy): our known-Phi networks are capped by PyPhi's cost. If the code is open, QNodes could extend the ground truth to larger networks for the effect-side quantity only, and its exactness check tells us which networks are safe. Check whether that partial quantity is close enough to system Phi before using it.
- **Touches:** #9, phi_proxy

### Rapid alternation of conscious and suppressed stimulus representations in the primate brain

Hesse JK, Lanfranchi FF, McGrory C, Shi Y, Engel TA, Tsao DY (2026). *bioRxiv (16 Oct 2026)*. [doi:10.64898/2026.10.15.759299](https://doi.org/10.64898/2026.10.15.759299). Preprint, abstract only, **useful**.

- **Question:** Is there a pure neural signal of conscious perception in face patches?
- **Idea tested:** Binocular flash suppression with Neuropixels across face patches and prefrontal cortex.
- **Data and method:** Macaque Neuropixels recordings in IT face patches and PFC.
- **Results:** During a constant percept the brain alternated about 15 times per second between conscious and suppressed micro-epochs; each epoch allowed reconstruction of the respective image; tuning was amplified in conscious epochs; PFC was qualitatively similar. (abstract only)
- **Limits:** Monkeys; report paradigm details not in abstract.
- **For us:** A strong content-NCC result for the ledger and the theory scorecard; not directly testable on our open data.
- **Touches:** constraint_ledger, theory_scorecard

### Systematic theory-method dependencies in consciousness research

Overgaard M, Dietz M, Waade PT (2026). *PsyArXiv (16 Aug 2026)*. [doi:10.31234/osf.io/3rqbk_v2](https://doi.org/10.31234/osf.io/3rqbk_v2). Preprint, abstract only, **useful**.

- **Question:** Does the experimental method predict which theory a study supports?
- **Idea tested:** If theories share an empirical space, method should not predict support.
- **Data and method:** Updated ConTraSt database of 518 experiments; Bayesian regression of theory support on methodological features.
- **Results:** Decisive evidence that methodology predicts whether a study supports, challenges or ignores a theory; theories occupy partly separate methodological niches. (abstract only)
- **Limits:** Correlational; database coding.
- **For us:** Direct input for the theory disagreement map (#17) and scorecard (#25): weight evidence by method niche, or a theory's 'wins' partly measure which paradigms its proponents run.
- **Touches:** #17, theory_scorecard, #29

### Testing the prevalent consistency assumption of (un)conscious processing through massive feature extraction of inattentional blindness EEG

Leung A, Kawashima Y, Tsuchiya N (2026). *PsyArXiv (9 Sep 2026)*. [doi:10.31234/osf.io/qjm48_v1](https://doi.org/10.31234/osf.io/qjm48_v1). Preprint, abstract only, **useful**.

- **Question:** Do EEG features that detect invisible stimuli keep doing so when the stimuli become visible?
- **Idea tested:** A registered report testing the consistency assumption behind contrastive NCC analysis.
- **Data and method:** Over 7,000 time-series features (hctsa-style toolbox) on inattentional blindness EEG; Bayesian tests.
- **Results:** Pilot results suggest the assumption is likely invalid across many features. (abstract only)
- **Limits:** Registered report; final results pending.
- **For us:** Massive feature extraction is our Study 3 route. Their toolbox is the parent of catch22, which is in #42's measure list; worth reading their feature-family handling and multiple-comparison control before sealing Study 3 variants.
- **Touches:** #42, Study 3

### A dynamic bifurcation mechanism explains cortex-wide neural correlates of conscious access

Klatzmann U, Froudist-Walsh S, Bliss DP, Theodoni P, Mejías JF, Niu M, Rapan L, Palomero-Gallagher N, Sergent C, Dehaene S, Wang XJ (2025). *Cell Reports*. [doi:10.1016/j.celrep.2025.115372](https://doi.org/10.1016/j.celrep.2025.115372). Article, abstract only, **useful**.

- **Question:** What network mechanism produces all-or-none ignition across cortex?
- **Idea tested:** Simulation of a detection task in a connectome-based model of macaque cortex.
- **Data and method:** Computational model; receptor predictions checked against in vitro autoradiography.
- **Results:** A dynamic bifurcation in associative regions produces ignition; an NMDA/AMPA gradient shapes it, with higher NMDA:AMPA ratios predicted in sensory than association areas.
- **Limits:** Model only, no human EEG test of single-trial bimodality.
- **For us:** The 'cortex-wide bifurcation' paper the coordinator asked about (not by Garnier-Allain). Gives the theory behind the bifurcation kill test; does not pre-empt it.
- **Touches:** bifurcation

### Integrated information theory (IIT) 4.0: formulating the properties of phenomenal existence in physical terms

Albantakis L, Barbosa L, Findlay G, Grasso M, Haun AM and others; senior author Tononi G (2023). *PLOS Computational Biology 19, e1011465*. [doi:10.1371/journal.pcbi.1011465](https://doi.org/10.1371/journal.pcbi.1011465). Paper, abstract only, **useful**.

- **Question:** The current formal version of integrated information theory.
- **Data and method:** Axioms to postulates to mathematical expressions; a unique measure of intrinsic information consistent with the postulates; explicit treatment of causal relations; a system's unfolded cause-effect structure accounts for the quality of experience.
- **Results:** IIT starts from what experience is like and works out what a physical system must be like to have it, then puts that in mathematics. In principle the maths says whether any system is conscious and how. In practice it cannot be computed for a brain, so only rough stand-ins can be tested.
- **For us:** The reference for the IIT row on our scoreboard and for which toy networks have exactly computable Phi in our planted-answer tests.
- **Touches:** news

### The integrated information theory of consciousness as pseudoscience

IIT-Concerned, Fleming SM, Frith CD and others (2023). *PsyArXiv (open letter); follow-up in Nature Neuroscience 28, 689-693 (2025)*. [doi:10.31234/osf.io/zsr78](https://doi.org/10.31234/osf.io/zsr78). Paper, abstract only, **useful**.

- **Question:** A group of researchers called IIT pseudoscience, which set off a public dispute over what counts as a test of a theory of consciousness.
- **Data and method:** Letter posted 16 Sep 2023 on PsyArXiv. Follow-up: IIT-Concerned et al., 'What makes a theory of consciousness unscientific?', Nature Neuroscience 28, 689-693, doi:10.1038/s41593-025-01881-x (104 author entries in Crossref, including the collective name). We did not verify the number of signatories on the 2023 letter.
- **Results:** After press coverage called IIT a leading, tested theory, researchers wrote an open letter objecting. In 2025 a follow-up in Nature Neuroscience argued the theory's core claims cannot be tested even in principle. The row is about what a fair test of a theory of consciousness looks like.
- **For us:** It is why we judge every theory only by predictions sealed in advance.
- **Touches:** news

### Neural correlates of consciousness in an attentional blink paradigm with uncertain target relevance

Dellert T, Krebs S, Bruchmann M, Schindler S, Peters A, Straube T (2022). *NeuroImage*. [doi:10.1016/j.neuroimage.2022.119679](https://doi.org/10.1016/j.neuroimage.2022.119679). Paper, abstract only, **useful**.

- **Question:** Which attentional-blink ERPs track awareness when T2 is not task-relevant?
- **Idea tested:** Make T2 relevance uncertain to separate awareness from task demands.
- **Data and method:** EEG, attentional blink with uncertain target relevance.
- **Results:** The awareness negativity survived when T2 was task-irrelevant; the P3b did not (via our prior-art read).
- **Limits:** Abstract or secondary summary only.
- **For us:** In ds001810 T2 is always task-relevant, so a P3b effect there cannot separate awareness from report.
- **Touches:** hypothesis-generator

### The ConTraSt database for analysing and comparing empirical studies of consciousness theories

Yaron I, Melloni L, Pitts M, Mudrik L (2022). *Nature Human Behaviour*. [doi:10.1038/s41562-021-01284-5](https://doi.org/10.1038/s41562-021-01284-5). Article, abstract only, **useful**.

- **Question:** Does the evidence for each consciousness theory depend on how studies were designed?
- **Idea tested:** They coded 412 experiments interpreted in light of four leading theories.
- **Data and method:** Database and meta-research analysis.
- **Results:** Which theory a study supports can be predicted from its method choices alone, and most studies interpret findings after the fact rather than testing predictions set in advance.
- **Limits:** Abstract only read here.
- **For us:** The core argument for sealing definitions and scoring rules before data, as any tournament must.
- **Touches:** Hypothesis tournament, COGITATE forecasts

### Dissociating perceptual awareness and postperceptual processing: the P300 is not a reliable marker of somatosensory target detection

Schröder P, Nierhaus T, Blankenburg F (2021). *Journal of Neuroscience*. [doi:10.1523/JNEUROSCI.2950-20.2021](https://doi.org/10.1523/JNEUROSCI.2950-20.2021). Paper, abstract only, **useful**.

- **Question:** Does the P300 mark tactile awareness, or the report that follows it?
- **Idea tested:** Decouple report from detection in the task.
- **Data and method:** EEG, near-threshold somatosensory detection with two task versions that decouple report.
- **Results:** The N140 tracked detection in both versions; the P300 difference vanished when report was decoupled.
- **Limits:** Abstract only.
- **For us:** Supports the early-negativity side in touch. A component screen on ds001785 should expect N140 to survive and the P3 to depend on report demands.
- **Touches:** hypothesis-generator

### Perceptual awareness negativity: a physiological correlate of sensory consciousness

Dembski C, Koch C, Pitts M (2021). *Trends in Cognitive Sciences*. [doi:10.1016/j.tics.2021.05.009](https://doi.org/10.1016/j.tics.2021.05.009). Review, abstract only, **useful**.

- **Question:** Is there one early ERP correlate of awareness across vision, hearing and touch?
- **Idea tested:** Pool evidence on the visual, auditory and tactile awareness negativities.
- **Data and method:** Review.
- **Results:** Argues for a general 'perceptual awareness negativity' across senses and against the P3b as a correlate of awareness itself.
- **Limits:** A review argument; it does not test whether the same pattern transfers across senses, and the negativities differ in topography by sense.
- **For us:** The early-negativity prediction a theory-signed screen would test. Sensor-space transfer of the visual or auditory negativity into touch is expected to fail on anatomy alone.
- **Touches:** hypothesis-generator

### Neural correlates of consciousness: progress and problems

Koch C, Massimini M, Boly M, Tononi G (2016). *Nature Reviews Neuroscience 17:307-321*. [doi:10.1038/nrn.2016.22](https://doi.org/10.1038/nrn.2016.22). Review, abstract only, **useful**.

- **Question:** What counts as a neural correlate of consciousness, and where is it?
- **Idea tested:** Define the NCC as the minimal mechanisms sufficient for a percept and separate it from prerequisites and consequences.
- **Data and method:** Review.
- **Results:** Proposes a posterior cortical 'hot zone' as the best candidate for content-specific NCCs.
- **Limits:** Review; the hot-zone claim is contested by GNWT proponents.
- **For us:** The posterior hot-zone prediction behind Siclari 2017 and the spatial priors in #42.
- **Touches:** #42, theory_scorecard

### Distilling the neural correlates of consciousness

Aru J, Bachmann T, Singer W, Melloni L (2012). *Neurosci Biobehav Rev*. [doi:10.1016/j.neubiorev.2011.12.003](https://doi.org/10.1016/j.neubiorev.2011.12.003). Article, abstract only, **useful**.

- **Question:** Does comparing 'seen' with 'unseen' isolate the brain activity of experience itself?
- **Idea tested:** A conceptual analysis of the contrastive method.
- **Data and method:** Review.
- **Results:** The seen-minus-unseen contrast mixes the NCC proper with its prerequisites (what must happen first) and its consequences (what follows, like report).
- **Limits:** Conceptual; abstract only read here.
- **For us:** Any marker tournament must say whether a marker is a prerequisite, the NCC or a consequence; state markers (sleep, anaesthesia) mostly index prerequisites.
- **Touches:** Hypothesis tournament

### Equal numbers of neuronal and nonneuronal cells make the human brain an isometrically scaled‐up primate brain

Azevedo et al. (2009). *Journal of Comparative Neurology 513:532-541*. [doi:10.1002/cne.21974](https://doi.org/10.1002/cne.21974). Paper, full text, **useful**.

- **Question:** Primary source for ledger constraint C05 (lesion).
- **Results:** The cerebellum holds most of the brain's neurons, yet losing it impairs movement and not, as far as anyone reports, consciousness.
- **Limits:** Azevedo 2009: 86.1 billion neurons, only 19% in cerebral cortex; Tononi & Koch 2015 put the cerebellum at 69 of 86 billion. Grade rests on clinical consensus and case reports (e.g. Yu 2014, cerebellar agenesis); there are few formal studies of experience after cerebellar loss.
- **For us:** Evidence grade A in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C05

### Forty-five years of split-brain research and still going strong

Gazzaniga (2005). *Nature Reviews Neuroscience 6:653-659*. [doi:10.1038/nrn1723](https://doi.org/10.1038/nrn1723). Paper, abstract only, **useful**.

- **Question:** Primary source for ledger constraint C03 (lesion).
- **Results:** Cutting the corpus callosum stops the two hemispheres comparing or jointly reporting stimuli from the two visual half-fields.
- **Limits:** Pinto 2017 replicated the failure to compare across half-fields in two patients.
- **For us:** Evidence grade A in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C03

### Timing of the brain events underlying access to consciousness during the attentional blink

Sergent et al. (2005). *Nature Neuroscience 8:1391-1400*. [doi:10.1038/nn1549](https://doi.org/10.1038/nn1549). Paper, abstract only, **useful**.

- **Question:** Primary source for ledger constraint C35 (timing).
- **Results:** Seen and unseen stimuli first diverge about 150-300 ms after onset; prior expectation moves this earlier (about 300 ms to about 200 ms) and lowers the threshold.
- **Limits:** Melloni 2011 gives ~300 ms without and ~200 ms with expectation. Exact onset depends on paradigm (VAN earlier than P3b).
- **For us:** Evidence grade A in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C35

### Neuroanatomical correlates of brainstem coma

Parvizi (2003). *Brain 126:1524-1536*. [doi:10.1093/brain/awg166](https://doi.org/10.1093/brain/awg166). Paper, abstract only, **useful**.

- **Question:** Primary source for ledger constraint C47 (subcortical).
- **Results:** Small lesions in the rostral dorsal pontine tegmentum cause coma.
- **Limits:** Fischer 2016: 12 coma-causing vs 24 control brainstem lesions. Brainstem is necessary as an enabling condition; whether it holds content is C55.
- **For us:** Evidence grade A in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C47

### Visual capacity in the hemianopic field following a restricted occipital ablation

Weiskrantz et al. (1974). *Brain 97:709-728*. [doi:10.1093/brain/97.1.709](https://doi.org/10.1093/brain/97.1.709). Paper, abstract only, **useful**.

- **Question:** Primary source for ledger constraint C01 (lesion).
- **Results:** After V1 damage, people can locate and discriminate stimuli in the blind field well above chance while saying they see nothing (blindsight).
- **Limits:** Macaque work shows the residual vision runs through LGN to extrastriate cortex (Schmid 2010: LGN inactivation abolished it). Caveat: some patients report vague 'feelings' in the blind field (Overgaard 2011), so 'no experience at all' is contested; 'degraded and unreportable as seeing' is robust.
- **For us:** Evidence grade A in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C01

### A Rosetta Stone hypothesis for neurophenomenology: mathematical predictions from predictive processing

Da Costa L, Seth AK, Friston K, Ramstead MJD, Sandved-Smith L (2026). *Neuroscience of Consciousness*. [doi:10.1093/nc/niag026](https://doi.org/10.1093/nc/niag026). Paper, abstract only, **context**.

- **Question:** Can predictive processing link phenomenology, behaviour and neural dynamics mathematically?
- **Idea tested:** If phenomenology is a function of beliefs, specific predictions follow.
- **Data and method:** Theory.
- **Results:** Derives predictions for similarity judgements, metabolic cost, effort and time perception. (abstract only)
- **Limits:** Conditional on a strong assumption.
- **For us:** Context for INTREPID-related theory work.
- **Touches:** theory_scorecard

### Brainstem theory of consciousness

Devor M, Baron M (2026). *The Neuroscientist*. [doi:10.1177/10738584261470362](https://doi.org/10.1177/10738584261470362). Review, abstract only, **context**.

- **Question:** Does raw experience come from the brainstem rather than cortex?
- **Idea tested:** Pain, which needs no cortex, shows sentience is brainstem-based.
- **Data and method:** Review argument.
- **Results:** Argues cortical lesions remove 'consciousness of' contents while brainstem lesions abolish sentience. (abstract only)
- **Limits:** Contested; argument from lesions and pain.
- **For us:** Context for ledger subcortical rows.
- **Touches:** constraint_ledger

### Distinct electrophysiological correlates of low- and high-level visual consciousness with minimized post-perceptual processing

Hense A, Peters A, Dellert T, Bruchmann M, Straube T (2026). *iScience*. [doi:10.1016/j.isci.2026.117853](https://doi.org/10.1016/j.isci.2026.117853). Paper, abstract only, **context**.

- **Question:** Do ERP correlates of awareness differ for low- and high-level content when task demands are removed?
- **Idea tested:** Inattentional blindness with three awareness levels for one stimulus.
- **Data and method:** 85 participants, inattentional blindness, task-irrelevant stimuli.
- **Results:** Line awareness enhanced an early occipital negativity; face awareness added a right occipitotemporal negativity and later medial posterior positivities. (abstract only)
- **Limits:** Single paradigm.
- **For us:** Context; fits the VAN meta-analysis.
- **Touches:** constraint_ledger

### Existence of an infinite family of substrates satisfying all the postulates of integrated information theory, exclusion included, with arbitrarily large integrated information

Mayeux A (2026). *arXiv 2610.02219*. [doi:10.48550/arXiv.2610.02219](https://doi.org/10.48550/arXiv.2610.02219). Preprint, abstract only, **context**.

- **Question:** Can simple substrates have arbitrarily large integrated information?
- **Idea tested:** A constructive proof.
- **Data and method:** Cycles of XOR units.
- **Results:** Exhibits cycles that are complexes in every state with phi growing as two to a power quadratic in the number of units. (abstract only)
- **Limits:** Mathematical.
- **For us:** An 'unfolding'-style challenge to IIT for the scorecard; also a stress case for phi_proxy.
- **Touches:** phi_proxy, theory_scorecard

### Integrated information theory (IIT) and the testability of the silent neuron predictions

Ponce de Leon S, Yoshimi J (2026). *Neuroscience of Consciousness*. [doi:10.1093/nc/niag037](https://doi.org/10.1093/nc/niag037). Paper, abstract only, **context**.

- **Question:** Are IIT's silent-brain and disabled-neuron predictions testable?
- **Idea tested:** A mechanism outside the main complex could report while the complex stays silent.
- **Data and method:** Conceptual analysis.
- **Results:** Argues both predictions can in principle be tested, against Bartlett 2022. (abstract only)
- **Limits:** Conceptual.
- **For us:** Context for the theory scorecard's IIT row.
- **Touches:** theory_scorecard

### Is it possible to make unconscious inferences? The limits of the influence of unconsciously perceived stimuli on conscious decisions

Remiszewski M, Łacny J, Cwalina F, Masłowska K, Cleeremans A, Binder M (2026). *Neuroscience of Consciousness*. [doi:10.1093/nc/niag068](https://doi.org/10.1093/nc/niag068). Paper, abstract only, **context**.

- **Question:** How complex a decision can masked stimuli drive?
- **Idea tested:** Unconscious influence should fade as decisions need integration and inference.
- **Data and method:** Sandwich masking at three decision complexities.
- **Results:** Accuracy 58% for simple decisions, 54% for intermediate, not reliably above chance for complex inference. (abstract only)
- **Limits:** One paradigm.
- **For us:** Context for ledger psychophysics rows.
- **Touches:** constraint_ledger

### Low-intensity focused ultrasound pulsation along the anterior-posterior thalamic axis differentially modulates the latency of reporting conscious visual experience

Jang H, Liu J, Hudetz AG, Huang Z (2026). *bioRxiv (25 Aug 2026)*. [doi:10.64898/2026.08.21.746115](https://doi.org/10.64898/2026.08.21.746115). Preprint, abstract only, **context**.

- **Question:** Does thalamic focused ultrasound change visual categorisation or the report that follows?
- **Idea tested:** Target and duty cycle should affect report latency specifically.
- **Data and method:** 60 adults randomised to two duty cycles, four left thalamic targets, acoustic simulations.
- **Results:** Target-by-duty-cycle interaction for report latency, not categorisation; at the ventroposterior target report latency was 55.9 ms longer under the higher duty cycle. (abstract only)
- **Limits:** Latency, not awareness itself.
- **For us:** Context.

### Overcoming essentialism: evaluation of theories of consciousness by the lawful regularities they predict

Bassler M, Pennartz CMA (2026). *Neuroscience of Consciousness*. [doi:10.1093/nc/niag069](https://doi.org/10.1093/nc/niag069). Paper, abstract only, **context**.

- **Question:** Should theories be judged by their definition of consciousness?
- **Idea tested:** Judge theories by the testable regularities they propose, not their essence claims.
- **Data and method:** Conceptual (Popper).
- **Results:** No consensus definition is needed for progress. (abstract only)
- **Limits:** Conceptual.
- **For us:** Context; matches our ledger-and-scorecard approach.
- **Touches:** theory_scorecard

### Pluralism within limits: how to make the idea of multiple NCC kinds useful

Kob L, Marvan T (2026). *Neuroscience of Consciousness*. [doi:10.1093/nc/niag060](https://doi.org/10.1093/nc/niag060). Paper, abstract only, **context**.

- **Question:** Can several kinds of NCC all be valid?
- **Idea tested:** A two-factor framework with a finite, ordered set of NCC kinds.
- **Data and method:** Conceptual.
- **Results:** Pluralism is viable only with general factors separated from content encoding. (abstract only)
- **Limits:** Conceptual.
- **For us:** Context.
- **Touches:** #17

### Simultaneous recordings link intracranial and scalp correlates of somatosensory awareness in humans

Mikulan E, Zauli FM, Russo S, Mannini F, Del Vecchio M, Albertini D, d'Orio P, Nobili L, Sartori I, Massimini M, Avanzini P, Pigorini A (2026). *bioRxiv (11 Oct 2026)*. [doi:10.64898/2026.10.03.756393](https://doi.org/10.64898/2026.10.03.756393). Preprint, abstract only, **context**.

- **Question:** What is the neural source of the scalp N140, the putative somatosensory awareness negativity?
- **Idea tested:** Simultaneous scalp and intracranial recordings should link N140/SAN to insulo-opercular activity.
- **Data and method:** Simultaneous high-density scalp EEG and intracranial EEG during median nerve stimulation.
- **Results:** The N140/SAN is the scalp expression of the insulo-opercular field potential that follows the tonic broadband high-frequency response. (abstract only)
- **Limits:** Abstract only.
- **For us:** Context: links a scalp awareness marker to a cortical source.
- **Touches:** constraint_ledger

### System-level nonequivalence between integrated information and expected free energy in noisy permutation networks

Tanabe K (2026). *Neuroscience*. [doi:10.1016/j.neuroscience.2026.11.021](https://doi.org/10.1016/j.neuroscience.2026.11.021). Paper, abstract only, **context**.

- **Question:** Does a network's predictive free energy determine its integrated information?
- **Idea tested:** Build networks with identical predictions but different causal wiring.
- **Data and method:** Noisy binary permutation networks; exact IIT calculations.
- **Results:** Architectures with identical one-step predictions and expected free energy had zero (multicycle) or positive (single cycle) system phi; maximum phi approaches one ibit for large n. (abstract only)
- **Limits:** Formal.
- **For us:** Context for INTREPID-related scorecard rows.
- **Touches:** theory_scorecard

### Why testing structural theories requires the unconscious condition

Zheng Z, Rodrigues JPP, Kob L, Matić K (2026). *PsyArXiv (7 Oct 2026)*. [doi:10.31234/osf.io/a9uph_v1](https://doi.org/10.31234/osf.io/a9uph_v1). Preprint, abstract only, **context**.

- **Question:** Can structure-matching between qualia and neural structure identify the substrate of experience?
- **Idea tested:** Structure-matching assumes the matching structure is conscious-specific; that must be tested with unseen stimuli.
- **Data and method:** Review and proposed design.
- **Results:** Existing evidence suggests relational structure survives absence of awareness, though no study settles it. (abstract only)
- **Limits:** Argument.
- **For us:** Context for our theory track; the same logic as our spectral-baseline nesting: a correlate must fail when experience is absent.
- **Touches:** #17, #35

### Neural correlates of perceptual consciousness from within: a narrative review of human intracranial research

(see arXiv) (2025). *arXiv*. [doi:10.48550/arXiv.2510.08736](https://arxiv.org/abs/2510.08736). Preprint, abstract only, **context**.

- **Question:** What can intracranial recordings tell us about the NCC that scalp methods cannot?
- **Idea tested:** A narrative review of single-neuron and population recordings in humans.
- **Data and method:** Review.
- **Results:** Intracranial data can help separate proper NCCs from other processes, but the problem is not solved; they lay out limits and future paradigms.
- **Limits:** Abstract only read here; authors not recorded.
- **For us:** Background on the prerequisite/NCC/consequence problem; relevant once COGITATE iEEG access arrives.
- **Touches:** Hypothesis tournament, COGITATE forecasts

### What makes a theory of consciousness unscientific?

IIT-Concerned et al. (2025). *Nature Neuroscience 28:689-693*. [doi:10.1038/s41593-025-01881-x](https://doi.org/10.1038/s41593-025-01881-x). Paper, abstract only, **context**.

- **Question:** Is IIT testable science?
- **Idea tested:** Follow-up to the 2023 open letter calling IIT pseudoscience.
- **Data and method:** Commentary.
- **Results:** Argues IIT's core claims are untestable and its public framing overstates evidence.
- **Limits:** Commentary; contested by IIT proponents.
- **For us:** Context for the IIT row of the scorecard and the testability notes.
- **Touches:** theory_scorecard

### Decoding perceptual awareness across the brain with a no-report fMRI masking paradigm

Hatamimajoumerd et al. (2022). *Current Biology 32:4139-4149.e4*. [doi:10.1016/j.cub.2022.07.068](https://doi.org/10.1016/j.cub.2022.07.068). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C30 (no-report).
- **Results:** In a no-report masking design, frontal univariate responses vanish but whether a stimulus was seen can still be decoded from frontal and posterior patterns.
- **Limits:** Hatamimajoumerd 2022, one fMRI study.
- **For us:** Evidence grade C in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C30

### The No-Report Paradigm: A Revolution in Consciousness Research?

Duman I, Ehmann IS, Gonsalves AR, Gültekin Z, et al. (2022). *Frontiers in Human Neuroscience*. [doi:10.3389/fnhum.2022.861517](https://doi.org/10.3389/fnhum.2022.861517). Article, abstract only, **context**.

- **Question:** Do no-report paradigms actually deliver report-free NCCs?
- **Idea tested:** They examined published comparisons of report and no-report conditions.
- **Data and method:** Critical review.
- **Results:** Every example they examined allows alternative readings or has method problems; removing the report does not stop people reflecting on what they saw.
- **Limits:** Abstract only read here.
- **For us:** Caution for any 'controls for report' claim in our studies.
- **Touches:** Hypothesis tournament

### Theories of consciousness

Seth AK, Bayne T (2022). *Nature Reviews Neuroscience 23:439-452*. [doi:10.1038/s41583-022-00587-4](https://doi.org/10.1038/s41583-022-00587-4). Review, abstract only, **context**.

- **Question:** How do the main theories of consciousness compare?
- **Idea tested:** Group theories into four families and lay out what each explains.
- **Data and method:** Review.
- **Results:** Higher-order, global workspace, re-entry/predictive processing and IIT families differ in what they aim to explain and in their tests.
- **Limits:** Review.
- **For us:** Framing for the level vs content split on our findings page.
- **Touches:** theory_scorecard, #17

### Bifurcation in brain dynamics reveals a signature of conscious processing independent of report

Sergent et al. (2021). *Nature Communications 12:1149*. [doi:10.1038/s41467-021-21393-z](https://doi.org/10.1038/s41467-021-21393-z). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C29 (no-report).
- **Results:** Without any task, the same sound gives late sustained activity on some trials and not others from about 250-300 ms, and this predicts later content reports.
- **Limits:** Sergent 2021, one study; frontal executive components were absent without a task.
- **For us:** Evidence grade C in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C29

### Electrophysiological chronometry of graded consciousness during the attentional blink

Eiserbeck A, Enge A, Rabovsky M, Abdel Rahman R (2021). *Cerebral Cortex*. [doi:10.1093/cercor/bhab289](https://doi.org/10.1093/cercor/bhab289). Paper, abstract only, **context**.

- **Question:** Is awareness in the attentional blink all-or-none or graded in the ERPs?
- **Idea tested:** Relate graded visibility to the N170, the visual awareness negativity and the P3b.
- **Data and method:** EEG, attentional blink with graded visibility.
- **Results:** The N170, VAN and P3b all scaled with graded visibility (via our prior-art read).
- **Limits:** Abstract or secondary summary only.
- **For us:** Counter-evidence to all-or-none ignition; a binary T2 identification label cannot test grading.
- **Touches:** hypothesis-generator

### Thalamus Modulates Consciousness via Layer-Specific Control of Cortex

Redinbaugh et al. (2020). *Neuron 106:66-75.e12*. [doi:10.1016/j.neuron.2020.01.005](https://doi.org/10.1016/j.neuron.2020.01.005). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C49 (subcortical).
- **Results:** Stimulating central lateral thalamus wakes anaesthetised macaques and restores wake-like cortical activity, with location and frequency specificity.
- **Limits:** Two labs (Redinbaugh 2020; Bastos 2021). Human central-thalamus DBS in MCS is one patient (Schiff 2007, doi:10.1038/nature06041), grade C.
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C49

### Intrinsic Functional Connectivity of the Brain in Adults with a Single Cerebral Hemisphere

Kliemann et al. (2019). *Cell Reports 29:2398-2407.e4*. [doi:10.1016/j.celrep.2019.10.067](https://doi.org/10.1016/j.celrep.2019.10.067). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C06 (lesion).
- **Results:** Adults who had one cerebral hemisphere surgically removed are conscious and hold normal within-hemisphere networks.
- **Limits:** Kliemann 2019: 6 hemispherectomy adults vs controls and n = 1,482 norms; between-network connectivity was increased. Consciousness is clinical observation, not measured.
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C06

### Differential Role of Prefrontal and Parietal Cortices in Controlling Level of Consciousness

Pal et al. (2018). *Current Biology 28:2145-2152.e5*. [doi:10.1016/j.cub.2018.05.025](https://doi.org/10.1016/j.cub.2018.05.025). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C51 (subcortical).
- **Results:** Cholinergic stimulation of rat prefrontal cortex, but not of two parietal sites, reversed sevoflurane anaesthesia while the drug continued.
- **Limits:** Pal 2018; rodents; righting reflex as the measure of consciousness.
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C51

### Are the Neural Correlates of Consciousness in the Front or in the Back of the Cerebral Cortex? Clinical and Neuroimaging Evidence

Boly et al. (2017). *The Journal of Neuroscience 37:9603-9613*. [doi:10.1523/JNEUROSCI.3218-16.2017](https://doi.org/10.1523/JNEUROSCI.3218-16.2017). Paper, full text, **context**.

- **Question:** Primary source for ledger constraint C08 (lesion).
- **Results:** Large prefrontal lesions do not abolish consciousness.
- **Limits:** Not contested that patients stay conscious; contested whether conscious perception is subtly altered (Odegaard, Knight & Lau 2017 vs Boly et al. 2017). Mashour et al. 2020 (GNWT) agree focal lesions should not cause full loss.
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C08

### Split brain: divided perception but undivided consciousness

Pinto et al. (2017). *Brain:aww358*. [doi:10.1093/brain/aww358](https://doi.org/10.1093/brain/aww358). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C04 (lesion).
- **Results:** Whether a split brain holds one or two subjects is unresolved: two patients detected and localised stimuli across the whole field with either hand or speech.
- **Limits:** Pinto 2017 (n = 2, confidence ratings) argue for undivided consciousness with split perception; this conflicts with the classic two-agent reading. Small n; contested.
- **For us:** Evidence grade C in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C04

### No-Report Paradigms: Extracting the True Neural Correlates of Consciousness

Tsuchiya N, Wilke M, Frässle S, Lamme VAF (2015). *Trends in Cognitive Sciences*. [doi:10.1016/j.tics.2015.10.002](https://doi.org/10.1016/j.tics.2015.10.002). Article, abstract only, **context**.

- **Question:** Does asking people to report what they saw contaminate the search for the brain basis of experience?
- **Idea tested:** A review of report-based and no-report designs.
- **Data and method:** Review.
- **Results:** Report requirements have biased NCC research; no-report paradigms try to remove that bias, with their own trade-offs.
- **Limits:** Abstract only read here.
- **For us:** Background for our closed no-report bifurcation test and for the report confound in any tournament.
- **Touches:** Hypothesis tournament

### Binocular Rivalry: Frontal Activity Relates to Introspection and Action But Not to Perception

Frässle et al. (2014). *The Journal of Neuroscience 34:1738-1747*. [doi:10.1523/JNEUROSCI.4403-13.2014](https://doi.org/10.1523/JNEUROSCI.4403-13.2014). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C31 (no-report).
- **Results:** In binocular rivalry, frontal fMRI activity relates to reporting switches, not to the switches themselves.
- **Limits:** Frässle 2014 used optokinetic nystagmus and pupil size as no-report read-outs.
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C31

### Electrical stimulation of a small brain area reversibly disrupts consciousness

Koubeissi et al. (2014). *Epilepsy &amp; Behavior 37:32-35*. [doi:10.1016/j.yebeh.2014.05.027](https://doi.org/10.1016/j.yebeh.2014.05.027). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C50 (subcortical).
- **Results:** Claustrum: stimulation near the left claustrum stopped behaviour and responsiveness in one patient; claustrum lesions in 171 veterans related to how long, not how often, consciousness was lost.
- **Limits:** Weak. Koubeissi 2014 is n = 1 with the electrode between claustrum and insula; Chau 2015 is correlational in penetrating injury. Crick & Koch 2005 is a hypothesis, not evidence. Treat as unestablished.
- **For us:** Evidence grade C in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C50

### Isolating neural correlates of conscious perception from neural correlates of reporting one's perception

Pitts et al. (2014). *Frontiers in Psychology 5*. [doi:10.3389/fpsyg.2014.01078](https://doi.org/10.3389/fpsyg.2014.01078). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C28 (no-report).
- **Results:** The P3b disappears when people see a stimulus but do not have to report it; it tracks report and task relevance, not awareness.
- **Limits:** Cohen 2020: robust P3b with report, none without. Mostly one research line (Pitts, Cohen). Earlier ~200-240 ms visual awareness negativity survives.
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C28

### Neuronal Discharges and Gamma Oscillations Explicitly Reflect Visual Consciousness in the Lateral Prefrontal Cortex

Panagiotaropoulos et al. (2012). *Neuron 74:924-935*. [doi:10.1016/j.neuron.2012.04.013](https://doi.org/10.1016/j.neuron.2012.04.013). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C32 (no-report).
- **Results:** Prefrontal neurons in macaques track the content of rivalry switches with no report, enough to decode contents single-trial.
- **Limits:** One lab (Panagiotaropoulos, Logothetis). Monkey percept is inferred from eye movements; C31 and C32 point opposite ways and are the core of the front-vs-back dispute.
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C32

### Causal role of prefrontal cortex in the threshold for access to consciousness

Del Cul et al. (2009). *Brain 132:2531-2540*. [doi:10.1093/brain/awp111](https://doi.org/10.1093/brain/awp111). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C09 (lesion).
- **Results:** Left anterior prefrontal lesions raise the masking threshold for subjective visibility more than for objective performance.
- **Limits:** One study (Del Cul et al. 2009). Not independently replicated in what we found.
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C09

### Neural signature of the conscious processing of auditory regularities

Bekinschtein et al. (2009). *Proceedings of the National Academy of Sciences 106:1672-1677*. [doi:10.1073/pnas.0809667106](https://doi.org/10.1073/pnas.0809667106). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C38 (no-report).
- **Results:** A late global response to violations of a sequence rule needs awareness of the rule, while the early local mismatch response persists in sleep, inattention and coma.
- **Limits:** Bekinschtein 2009 (incl. 8 DoC patients); Strauss 2015 (global response vanished in sleep; local response kept but lost a prediction-error peak). Global effect can be absent in conscious people who miss the rule.
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C38

### Consciousness without a cerebral cortex: A challenge for neuroscience and medicine

Merker (2007). *Behavioral and Brain Sciences 30:63-81*. [doi:10.1017/S0140525X07000891](https://doi.org/10.1017/S0140525X07000891). Paper, full text, **context**.

- **Question:** Primary source for ledger constraint C55 (subcortical).
- **Results:** Children born without most of the cerebral cortex (hydranencephaly) show emotional and orienting responses that some clinicians read as conscious.
- **Limits:** Merker 2007; Solms 2019 cites four children assessed by Shewmon. Behavioural inference only; how much cortex remains varies by case (not checked here). Strongly contested.
- **For us:** Evidence grade C in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C55

### Relative blindsight in normal observers and the neural correlate of visual consciousness

Lau et al. (2006). *Proceedings of the National Academy of Sciences 103:18763-18768*. [doi:10.1073/pnas.0607716103](https://doi.org/10.1073/pnas.0607716103). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C27 (metacognition).
- **Results:** Subjective visibility and objective performance can dissociate in healthy people (equal accuracy, different visibility).
- **Limits:** Lau & Passingham 2006 (relative blindsight). The follow-up claim that prefrontal TMS impairs metacognition (Rounis 2010) failed to replicate (Bor 2017, two experiments). So the dissociation is B; its prefrontal cause is C.
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C27

### An information integration theory of consciousness

Tononi G (2004). *BMC Neuroscience 5:42*. [doi:10.1186/1471-2202-5-42](https://doi.org/10.1186/1471-2202-5-42). Paper, abstract only, **context**.

- **Question:** What makes a system conscious?
- **Idea tested:** Consciousness corresponds to the capacity to integrate information (phi).
- **Data and method:** Theory.
- **Results:** Defines phi and argues it accounts for features of conscious experience.
- **Limits:** Theory.
- **For us:** Background for the IIT row of the scorecard.
- **Touches:** theory_scorecard

### Unconscious activation of visual cortex in the damaged right hemisphere of a parietal patient with extinction

Rees (2000). *Brain 123:1624-1633*. [doi:10.1093/brain/123.8.1624](https://doi.org/10.1093/brain/123.8.1624). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C52 (lesion).
- **Results:** In extinction after parietal damage, unseen stimuli in the affected field still activate early visual cortex.
- **Limits:** Rees 2000, one patient with right inferior parietal damage (event-related fMRI).
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C52

### Rubber hands ‘feel’ touch that eyes see

Botvinick et al. (1998). *Nature 391:756-756*. [doi:10.1038/35784](https://doi.org/10.1038/35784). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C53 (self).
- **Results:** Synchronised visual and touch signals can make people feel a rubber hand or a virtual body as their own and shift where they feel located.
- **Limits:** Lush 2020 (n = 156, 404, 353): illusion strength tracks trait suggestibility, so demand effects inflate reports.
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C53

## Measuring consciousness (110)

### Bifurcation dynamics in a shared network beyond sensory areas characterize conscious auditory perception independently of report

Boyer J, Beraud N, Béranger B, Hardy T, Türker B, Gouyette H, Lopez-Persem A, Sergent C (2026). *bioRxiv*. [doi:10.64898/2026.06.17.732590](https://doi.org/10.64898/2026.06.17.732590). Preprint, abstract only, **core**.

- **Question:** Which brain networks produce all-or-none bifurcation dynamics in conscious perception, with and without a task?
- **Idea tested:** fMRI with near-threshold sounds in task and no-task contexts; single-trial modelling of bifurcation.
- **Data and method:** fMRI; sample size not in the abstract.
- **Results:** Intensity modulated broad networks including PFC in both contexts; single-trial models found bifurcation beyond primary sensory cortex and predicted perception trial by trial in both contexts.
- **Limits:** Originating lab (Sergent); abstract only; no planted or recovery check stated. Licence CC BY-NC-ND.
- **For us:** Narrows the novelty of the bifurcation kill test: the originating lab has now shown no-task bifurcation in EEG (2021) and fMRI. What stays open is an outside, sealed, planted-bounded test across Cohen and Sergent EEG.
- **Touches:** bifurcation

### Critical dynamics in spontaneous EEG predict perturbational complexity in disorders of consciousness with measurable evoked responses

Newman D, Maschke C, O'Byrne J, Colombo MA, Comanducci A, Casarotto S, Citerio G, Rosanova M, Massimini M, Jerbi K, Blain-Moraes S (2026). *medRxiv/bioRxiv*. [doi:10.64898/2026.06.04.730221](https://doi.org/10.64898/2026.06.04.730221). Preprint, abstract only, **core**.

- **Question:** Resting brain signals could stand in for the stimulation-based consciousness index in some brain-injured patients, but not across all of them.
- **Data and method:** 26 patients (vascular, traumatic, anoxic). Multivariate criticality features did not generalise PCImax prediction across the full cohort; they did when restricted to non-anoxic patients and to patients with non-zero PCImax. Extends Maschke et al. 2024 (anaesthesia) to brain injury. Not peer reviewed.
- **Results:** The best-tested consciousness index needs a magnetic pulse to the head. This team asked whether ordinary resting EEG can predict it in 26 brain-injured patients. It could not across the whole group, only in patients whose injury was not from lack of oxygen and in those with a measurable response.
- **For us:** Tempers the 2024 claim that resting EEG can replace PCI. Our out-of-sample test of that claim should report results by aetiology.
- **Touches:** news

### Individualised electrophysiological neural field models for the assessment of thalamocortical function in disorders of consciousness: a multicentre study

Cóngyǔ L, Tewarie PKB, Alnagger NLN, Mindlin I, Van der Lande GJM, Belloli L, Laureys S, Naccache L, Rohaut B, Thibaut A, Annen J, Gosseries O, Núñez P, Sitt JD (2026). *PLoS Computational Biology*. [doi:10.1371/journal.pcbi.1014905](https://doi.org/10.1371/journal.pcbi.1014905). Paper, full text, **core**.

- **Question:** Can a fitted corticothalamic model explain EEG differences between MCS and UWS?
- **Idea tested:** Per-patient corticothalamic neural field fits should reveal reduced thalamocortical integrity (mesocircuit hypothesis).
- **Data and method:** High-density EEG from two independent datasets: 203 UWS, 270 MCS, 74 controls; Robinson model fitted to spectra; simulated EEG compared on complexity metrics.
- **Results:** The model captured spectral features across states and showed reduced corticothalamic integrity, worse in UWS than MCS. Simulated EEG reproduced empirical complexity; permutation entropy distinguished MCS from UWS in real and simulated data. Code and replication data on GitHub (braintrak, nftsim, predictivecat/DoC_tcmodel).
- **Limits:** A model fitted to the spectrum reproduces complexity, which means complexity here is largely spectral.
- **For us:** Strong support for our spectral-confound line: if a spectrum-fitted model reproduces permutation entropy, PE carries little beyond the spectrum. Check whether the DoC_tcmodel repository holds per-patient fitted parameters or spectra; if so, it is the first open DoC-derived data for Study 2.
- **Touches:** Study 2, lz_slope, surrogate_gate

### Thermodynamics of consciousness: non-equilibrium brain dynamics track conscious states

Berjaga-Buisan T, Monti JM, Cortada M, Colombo MA, Geli SM, Gaglioti G, Sarasso S, Kringelbach ML, Corbetta M, Sanchez-Vives MV, Massimini M, Perl YS, Deco G (2026). *Cell Reports 38:117782*. [doi:10.1016/j.celrep.2026.117782](https://doi.org/10.1016/j.celrep.2026.117782). Paper, full text, **core**.

- **Question:** Does non-equilibrium in spontaneous brain activity track consciousness the way PCI does?
- **Idea tested:** Violations of the fluctuation-dissipation theorem (FDT), estimated from whole-brain models fitted to spontaneous signals, should fall with loss of consciousness.
- **Data and method:** Generative whole-brain models in humans (wake, anaesthesia, DoC) and mice (graded anaesthesia, LFP).
- **Results:** In mice PCI tracked anaesthesia depth (Spearman 0.71), FDT violations tracked it more tightly (0.885), and FDT correlated with PCI (0.68). FDT violations fell in unresponsive DoC and anaesthesia. Mouse LFP data are open on EBRAINS (10.25493/WKA8-Q4T).
- **Limits:** Model-based, not compared against a spectral baseline. Anaesthesia and DoC confound arousal with consciousness.
- **For us:** We already tested its scalp second-order irreversibility form (ne2) and it did not replicate (AUC 0.43-0.56); our higher-order variant tracked arousal only. The model-based FDT estimator is still untested by us and would need the spectral baseline and an arousal-free contrast such as #42's.
- **Touches:** nonequilibrium, #41, #42

### Waveform morphology links local circuit kinetics to cortical interactions

Núñez P, Kumar G, Gotti C, Wang P, Martineau L, Bonaventure PL, Hoyer R, Mišić B, Albouy P, Laureys S, Tewarie PKB (2026). *bioRxiv (16 Nov 2026)*. [doi:10.64898/2026.11.13.766469](https://doi.org/10.64898/2026.11.13.766469). Preprint, abstract only, **core**.

- **Question:** How does local synaptic kinetics shape waveform shape and measures of inter-areal interaction?
- **Idea tested:** Synaptic rise and decay times set waveform asymmetry, which then biases irreversibility and coherence measures.
- **Data and method:** Modified Wilson-Cowan model; stereo-EEG from 23 patients; macaque ECoG.
- **Results:** Waveform asymmetry was most strongly associated with local irreversibility in sEEG; alpha frequency related more to inter-regional measures. Phase-locked perturbations changed imaginary coherency and irreversibility with coupling fixed. Macaque ECoG reproduced the frequency links but not the waveform link. (abstract only)
- **Limits:** Abstract only; preprint.
- **For us:** A mechanism for our own result: our waveform-asymmetry marker tra_x separated wake from N3 but not REM from N3. If asymmetry indexes local kinetics, it should track arousal-linked synaptic changes, not experience. Cite it in the nonequilibrium write-up.
- **Touches:** nonequilibrium, #41

### The role of etiology in the identification of clinical markers of consciousness: comparing EEG alpha power, complexity, and spectral exponent

Maschke C, Belloli L, Manasova D, Sitt JD, Blain-Moraes S (2025). *Cerebral Cortex 35(9), bhaf254*. [doi:10.1093/cercor/bhaf254](https://doi.org/10.1093/cercor/bhaf254). Paper, abstract only, **core**.

- **Question:** In 303 unresponsive patients, a popular complexity measure mostly repeated what the slope of the EEG spectrum already showed; once corrected for that, its diagnostic value vanished.
- **Data and method:** 303 unresponsive patients. Shuffle-normalised LZC correlated with the 1-40 Hz spectral exponent at r(197) = 0.86; phase-normalising (surrogates with matched spectrum) reduced this to r(197) = 0.24, and all LZC diagnostic effects vanished; partialling out the exponent did the same. Alpha power had more diagnostic value in anoxic patients; spectral slope only in non-anoxic patients. Code: github.com/BIAPT/Markers.
- **Results:** A brain 'complexity' score is often used as a sign of consciousness. Here it moved almost in lockstep with a much simpler property of the signal, how fast power falls off with frequency. When the authors compared each recording with scrambled copies that keep that property, the complexity score stopped telling patients apart. Which marker worked also depended on the cause of brain injury.
- **For us:** The direct source for our surrogate gate (task #8) and the LZ vs slope test (task #4). It is the PMC12448740 paper the plan cites. We also stratify by aetiology wherever patient data allow.
- **Touches:** news

### Neural signatures of visual awareness independent of postperceptual processing

Cohen MA, Dembski C, Ortego K, Steinhibler C, Pitts MA (2024). *Cerebral Cortex*. [doi:10.1093/cercor/bhae415](https://doi.org/10.1093/cercor/bhae415). Article, full text, **core**.

- **Question:** Which EEG signals track visual awareness when report is removed?
- **Idea tested:** Visual masking with 5 linear SOAs (17-83 ms), separate report and no-report conditions, ERP analysis.
- **Data and method:** EEG, 40 participants; seen rates about 58% at 50 ms and 89% at 67 ms in the report condition. Data on OSF 6d5av (no licence stated).
- **Results:** Only a fronto-central N2 (about 250-300 ms) follows awareness nonlinearly in both conditions; the VAN does not survive removal of report; earlier ERPs follow the linear SOA manipulation.
- **Limits:** Condition-averaged ERPs: no single-trial or fixed-SOA seen vs unseen test. OSF data has no licence stated; analysed locally with derived statistics only (coordinator decision 2026-11-24), and the corresponding author was asked about reuse terms.
- **For us:** Primary dataset for the fixed-SOA seen vs unseen kill test (experiments/cohen_fixed_soa) and the no-report bifurcation test (experiments/bifurcation).
- **Touches:** bifurcation, cohen-fixed-soa

### Spectral Slope and Lempel-Ziv Complexity as Robust Markers of Brain States during Sleep and Wakefulness

Höhn C, Hahn MA, Lendner JD, Hoedlmoser K (2024). *eNeuro*. [doi:10.1523/ENEURO.0259-23.2024](https://doi.org/10.1523/ENEURO.0259-23.2024). Article, full text, **core**.

- **Question:** How do the EEG spectral slope and Lempel-Ziv complexity behave across sleep stages and waking tasks, and does the frequency range matter?
- **Idea tested:** They recorded 28 young men over two weeks (three nights and days each) and computed slope and LZ in a broad (1-45 Hz) and a narrow (30-45 Hz) range.
- **Data and method:** Within-subject EEG across wake tasks (rest, attention, memory) and sleep stages; FOOOF and robust fits for the slope; LZ after Comsa 2019.
- **Results:** From wake to N3 the broadband slope steepened and LZ fell. REM was best told apart by the narrowband slope. They write that LZ 'is still strongly influenced by oscillatory activity', and conclude the slope carries more information than LZ.
- **Limits:** No test of whether LZ adds anything over a full spectral baseline, and no phase-randomised surrogates. Only men aged 18-25.
- **For us:** Prior art for our LZ result. Our finding that LZ is mostly the spectrum in sleep confirms theirs; what we add is the sealed incremental-AUC test and the surrogate gate.
- **Touches:** LZ vs spectrum

### Perceptual Awareness Occurs Along a Graded Continuum: No Evidence of All-or-None Failures in Continuous Reproduction Tasks

Cohen MA, Keefe JM, Brady TF (2023). *Psychological Science*. [doi:10.1177/09567976231186798](https://bradylab.ucsd.edu/pdfs/CohenKeefeBrady2023.pdf). Paper, full text, **core**.

- **Question:** Do failures of awareness in blink, masking, Sperling and retro-cue tasks need an all-or-none 'guess' state?
- **Idea tested:** Compared one continuous signal-detection model against mixture models across several awareness tasks, including Asplund's data.
- **Data and method:** Model comparison (BIC) on continuous-report data from several paradigms.
- **Results:** The single continuous model beat the mixture models across tasks. On Asplund's data it was preferred in 27 of 28 people.
- **Limits:** Continuous colour report is not a visibility rating; the conclusion depends on the signal-detection model family.
- **For us:** This closes most of the behavioural all-or-none question, so our item 4 would have added a method, not a new answer. We judged it a no-go.
- **Touches:** Fable#13 item 4, all-or-none vs graded

### Effects of tDCS on the attentional blink revisited: a statistical evaluation of a replication attempt

Reteig LC, Newman LA, Ridderinkhof KR, Slagter HA (2022). *PLOS ONE*. [doi:10.1371/journal.pone.0262718](https://doi.org/10.1371/journal.pone.0262718). Paper, full text, **core**.

- **Question:** Does tDCS over left DLPFC change the attentional blink, as an earlier study suggested?
- **Idea tested:** Replicate the earlier tDCS effect with anodal and cathodal sessions and EEG recorded throughout.
- **Data and method:** N = 40, two visits (anodal, cathodal), pre/during/post blocks; letter RSVP with T1 red and T2 green at lag 3 or 8; Biosemi 64-channel EEG. Data: OpenNeuro ds001810.
- **Results:** No tDCS effect on the blink. The authors did not analyse the EEG 'given the absence of a behavioral effect'. Lags 3 and 8 were chosen to give about equal numbers of seen and missed T2 for EEG.
- **Limits:** Behavioural paper only; the EEG is unpublished.
- **For us:** Our discovery set for the hypothesis generator: the pre-tDCS blocks give about 45 T2-correct and 55 T2-incorrect lag-3 trials per block, and the T2-correct vs incorrect EEG contrast has never been published on this dataset. Outcome is T2 identification, not seen vs unseen.
- **Touches:** hypothesis-generator, rhythm_blink

### Neural complexity is a common denominator of human consciousness across diverse regimes of cortical dynamics

Frohlich J, Chiang JN, Mediano PAM, Nespeca M, Saravanapandian V, et al. (2022). *Communications Biology*. [doi:10.1038/s42003-022-04331-7](https://doi.org/10.1038/s42003-022-04331-7). Article, abstract only, **core**.

- **Question:** When brain rhythms and conscious state come apart, which EEG markers still track consciousness?
- **Idea tested:** They used two rare genetic conditions as a testbed: children with Angelman syndrome look sleep-like while awake, and children with Dup15q look wake-like in NREM sleep.
- **Data and method:** Regularised logistic classifiers trained on wake vs NREM in Angelman children, using entropy (complexity) or spectral features, then tested on typical children and on Dup15q.
- **Results:** Entropy-based markers were not capped by spectral ones and beat them.
- **Limits:** Children with rare syndromes; abstract only read here.
- **For us:** The strongest counter-evidence to our 'complexity is just the spectrum' result. Our result holds for typical sleep EEG; a dissociation testbed like theirs is the right confound control for any marker tournament.
- **Touches:** LZ vs spectrum, Hypothesis tournament

### Evidence accumulation relates to perceptual consciousness and monitoring

Pereira M, Megevand P, Tan MX, Chang W, Wang S, Rezai A, Seeck M, Corniola M, et al. (2021). *Nature Communications*. [doi:10.1038/s41467-021-23540-y](https://doi.org/10.1038/s41467-021-23540-y). Paper, full text, **core**.

- **Question:** Does the neural evidence accumulation behind detecting a near-threshold touch also drive confidence and awareness?
- **Idea tested:** Awareness and confidence both read out an accumulated evidence signal, not a separate all-or-none event.
- **Data and method:** EEG, 62 channels at 1024 Hz, near-threshold vibrotactile detection with confidence, 500 trials per subject, 20% catch trials, staircase; also intracranial and single-neuron data. EEG data open as OpenNeuro ds001785 (18 subjects; about 140-215 hits and 184-259 misses each).
- **Results:** A hit-vs-miss decoder defines an evidence-accumulation proxy that a leaky accumulator fits and that also tracks confidence. A per-electrode mixed model on the 0.5-1.5 s mean amplitude gives a detection x confidence interaction. Effects are late (>200 ms).
- **Limits:** Named components (P50, N80, N140, P3), time-resolved mass-univariate maps and spectral contrasts are not in the main text.
- **For us:** The strongest open trial-level seen/unseen EEG set we have. A preregistered, theory-tagged component screen on it is not in the paper.
- **Touches:** hypothesis-generator

### All-or-none face categorization in the human brain

Retter TL, Jiang F, Webster MA, Rossion B (2020). *NeuroImage*. [doi:10.1016/j.neuroimage.2020.116685](https://doi.org/10.1016/j.neuroimage.2020.116685). Paper, full text, **core**.

- **Question:** Is face categorization in the brain all-or-none across stimulus strength?
- **Idea tested:** Frequency-tagged EEG with faces at graded visibility; single-trial classification of responses.
- **Data and method:** Scalp EEG, fast periodic visual stimulation.
- **Results:** The graded average response reflects the proportion of absent and full responses: a mixture of all-or-none trials, not a graded single-trial response.
- **Limits:** Faces and frequency tagging, not masking SOA curves.
- **For us:** States the mixture identity that makes 'tracks the seen rate' follow from any seen/unseen difference, the core of the psychometric-criterion audit.
- **Touches:** psychometric_criterion

### An electrophysiological marker of arousal level in humans

Lendner JD et al. (2020). *eLife*. [doi:10.7554/eLife.55092](https://doi.org/10.7554/eLife.55092). Journal article, abstract only, **core**.

- **Question:** Is the aperiodic slope a marker of arousal across sleep and anaesthesia?
- **Idea tested:** Spectral slope in scalp and intracranial data across wake, NREM, REM and propofol.
- **Data and method:** Spectral slope in scalp and intracranial data across wake, NREM, REM and propofol.
- **Results:** Per-contrast LDA: wake vs propofol 76.6%, wake vs REM 76.3%, wake vs N3 73.1%.
- **Limits:** Separate classifier per contrast; no shared threshold or transfer.
- **For us:** Our REM-placement test uses frozen cutoffs, which Lendner did not.
- **Touches:** Task #5 transfer

### Temporally unconstrained decoding reveals consistent but time-varying stages of stimulus processing

Vidaurre D, Myers NE, Stokes M, Nobre AC, Woolrich MW (2019). *Cerebral Cortex*. [doi:10.1093/cercor/bhy290](https://doi.org/10.1093/cercor/bhy290). Paper, full text, **core**.

- **Question:** Does standard TG decoding mistake growing trial-to-trial timing variability for persistent coding?
- **Idea tested:** Simulated a chain of five states with equal durations and increasing onset variability; proposed an HMM-based temporally unconstrained decoder.
- **Data and method:** Simulation plus MEG data; standard TG vs a decoder that lets stage timing vary per trial.
- **Results:** Standard TG suggests an artificial increase in persistence as the trial goes on: apparently stable patterns can come from increasing onset variability of the same code.
- **Limits:** Generic simulation, not EEG-scale and not matched to any consciousness study's pipeline.
- **For us:** Closest prior art for TG-square specificity; our gap is a pipeline-matched test of Hutchinson 2026's footprint.
- **Touches:** tg_square_specificity

### Visibility Is Not Equivalent to Confidence in a Low Contrast Orientation Discrimination Task

Rausch M, Zehetleitner M (2016). *Frontiers in Psychology*. [doi:10.3389/fpsyg.2016.00591](https://doi.org/10.3389/fpsyg.2016.00591). Article, full text, **core**.

- **Question:** Are 'how clearly did you see it' and 'how sure are you' the same report?
- **Idea tested:** Twenty people judged grating orientation at six contrasts and gave both visibility and confidence on continuous scales every trial, in counterbalanced order.
- **Data and method:** meta-d_a for each scale by contrast, metacognitive bias, conditional report rates at a 25% cut, Bayesian mixed models. Data are in the Confidence Database (Rausch_2016).
- **Results:** Confidence tracked accuracy better than visibility (meta-d_a 1.2 vs 0.5). People were often confident without seeing, but hardly ever saw without being confident.
- **Limits:** One lab, n=20. It compares the two scales; it does not test whether confidence works better on high-visibility trials.
- **For us:** The only open dataset that can test the Persaud-style claim in healthy people with continuous scales. Our power gate decides whether n=20 is enough.
- **Touches:** Metacognition and awareness

### Cortical activity is more stable when sensory stimuli are consciously perceived

Schurger A, Sarigiannidis I, Naccache L, et al. (2015). *PNAS*. [doi:10.1073/pnas.1418730112](https://doi.org/10.1073/pnas.1418730112). Paper, abstract only, **core**.

- **Question:** Is cortical activity less variable across and within trials when a threshold stimulus is seen?
- **Idea tested:** Conscious perception goes with a stable activity pattern, as in attractor states.
- **Data and method:** Simultaneous MEG and EEG, threshold-level visual stimuli; pattern-similarity on MEG gradiometers; EEG metric also applied to disorders-of-consciousness patients.
- **Results:** Variability drops after stimulus onset, then diverges by report: seen trials are less variable, coinciding with within-trial stability; stability alone classifies single trials seen/unseen.
- **Limits:** Read at abstract level only.
- **For us:** Direct prior art for round 15 item 4. Their measure is pattern-based MEG; an amplitude-based healthy-EEG version at a fixed stimulus, with a selection-matched null, is not in the abstract.
- **Touches:** round15-priorart, stability_specificity

### Large scale screening of neural signatures of consciousness in patients in a vegetative or minimally conscious state

Sitt JD, King JR, El Karoui I, Rohaut B, Faugeras F, Gramfort A, Cohen L, Sigman M, Dehaene S, Naccache L (2014). *Brain 137:2258-2270*. [doi:10.1093/brain/awu141](https://doi.org/10.1093/brain/awu141). Paper, abstract only, **core**.

- **Question:** Which EEG measures separate vegetative from minimally conscious patients?
- **Idea tested:** Screen many spectral, complexity and connectivity measures at once.
- **Data and method:** 181 high-density EEG recordings from DoC patients and controls.
- **Results:** Theta/alpha power, complexity and wSMI in theta/alpha separated VS from MCS; combined in a classifier they did best.
- **Limits:** Single centre at the time; spectral and complexity features were not nested.
- **For us:** The source of wSMI and the 'many markers' design that #42 inherits; our nesting rule asks what each adds beyond spectrum.
- **Touches:** #42, Study 2

### Alpha entrainment is responsible for the attentional blink phenomenon

Zauner A, Fellinger R, Gross J, Hanslmayr S, Shapiro K, Gruber W, Müller S, Klimesch W (2012). *NeuroImage*. [doi:10.1016/j.neuroimage.2012.06.075](https://doi.org/10.1016/j.neuroimage.2012.06.075). Paper, full text, **core**.

- **Question:** Is entrainment of alpha to the ~10 Hz RSVP stream the cause of the attentional blink?
- **Idea tested:** EEG during a 10 Hz RSVP blink task (fixed and jittered SOA); phase-locking index (7-cycle Morlet, 8-12 Hz) within +/-50 ms of T2, AB vs NoAB vs control trials.
- **Data and method:** Human EEG, 14 analysed subjects, lag about 300 ms.
- **Results:** Alpha phase-locking and evoked alpha larger for AB (T2 missed) than NoAB trials at T2; no whole-power difference; concludes entrainment 'may be considered the critical factor'.
- **Limits:** 14 subjects; ROI electrodes chosen from the data; the control comparison was not count-matched although PLI depends on trial count.
- **For us:** Claim tested by the rhythm_blink study on ds001810 (42 subjects, count-matched).
- **Touches:** rhythm_blink

### A Spatiotemporal Filtering Methodology for Single-Trial ERP Component Estimation

Li R, Principe JC, et al. (2009). *IEEE Transactions on Biomedical Engineering*. [doi:10.1109/TBME.2008.2002153](https://doi.org/10.1109/TBME.2008.2002153). Paper, full text, **core**.

- **Question:** How well do Woody-type and spatiotemporal methods recover single-trial ERP latency at low SNR?
- **Idea tested:** Simulations with known latency at a range of SNRs; compares Woody filtering to a spatiotemporal filter.
- **Data and method:** Simulated ERPs plus real EEG.
- **Results:** With the true latency fixed, Woody estimates still spread by about 60 ms SD at -20 dB and 15 ms at 12 dB: at low SNR the estimator reports noise as jitter.
- **Limits:** Simulation SNRs are not ours; single component.
- **For us:** Why the latency-spread study calibrates against each subject's own noise instead of reading a raw lag SD.
- **Touches:** latency_spread

### Is Consciousness a Gradual Phenomenon? Evidence for an All-or-None Bifurcation During the Attentional Blink

Sergent C, Dehaene S (2004). *Psychological Science 15(11)*. [doi:10.1111/j.0956-7976.2004.00748.x](https://www.unicog.org/publications/SergentDehaene_PsychScience04.pdf). Paper, full text, **core**.

- **Question:** Is seeing a target during the attentional blink graded, or all or none?
- **Idea tested:** People rated target visibility on a 21-point scale during the attentional blink, and in a masking task where the target's duration varied.
- **Data and method:** Behaviour, about 10 people per experiment. Group rating histograms were fitted by regression as mixtures of the 'absent' and 'seen' histograms.
- **Results:** In the blink, ratings looked like a mix of two states: unseen and fully seen, with few in between. When masking duration was varied the ratings were one bump that shifted gradually, and in Exp 3 the 'seen' peak itself moved with duration.
- **Limits:** Small samples; tested on group histograms, which can hide individual patterns; a bounded rating scale can produce two peaks from a graded signal.
- **For us:** The founding behavioural case for all-or-none access. It also shows graded visibility under masking, so a graded result on masking data would not count against the global workspace theory.
- **Touches:** Fable#13 item 4, all-or-none vs graded

### Distributional assumptions of growth mixture models: implications for overextraction of latent trajectory classes

Bauer DJ, Curran PJ (2003). *Psychological Methods*. [doi:10.1037/1082-989x.8.3.338](https://doi.org/10.1037/1082-989x.8.3.338). Paper, abstract only, **core**.

- **Question:** Can mixture models find latent classes when only one group exists?
- **Idea tested:** Non-normal data alone can make multi-class mixtures look optimal.
- **Data and method:** Statistical theory of finite normal mixtures plus simulation.
- **Results:** Multiple trajectory classes are estimated and appear optimal for non-normal single-population data; within-class estimates are largely uninterpretable.
- **Limits:** Read at abstract level only; growth-mixture setting, not EEG.
- **For us:** The general statistical principle behind our finding that the Sergent 2021 two-state model wins on heavy-tailed or threshold-jittered graded data.
- **Touches:** bifurcation-audit

### "The self" as shifting coalitions of brain systems in a continuous configuration space

Skipper JI, Blackburne G, Cooper G, Jaglinska M, Jedlovszky K, Kuc J, McAlpine R, Timmermann C (2026). *bioRxiv*. [doi:10.64898/2026.11.12.766263](https://doi.org/10.64898/2026.11.12.766263). Preprint, abstract only, **useful**.

- **Question:** Is there a core brain region or network for the self?
- **Idea tested:** Meta-analysis of 912 neuroimaging papers; titles and abstracts clustered into ten forms of self; brain maps per form; held-out prediction of reported regions.
- **Data and method:** 912 publications, ten self-related maps (e.g. autobiographical memory, body ownership, interoception).
- **Results:** No location significant in all ten maps; maps related selectively to aspects of consciousness; graded mixtures of maps predicted held-out papers' regions better than single maps or on/off combinations.
- **Limits:** Abstract only. 'No core' rests partly on a failed conjunction across ten maps, an absence-of-evidence inference whose sensitivity is not stated in the abstract. Licence CC BY-NC-ND (no figure reuse).
- **For us:** Self and ego are related to consciousness, not the same. Relevant to ego dissolution (psychedelics; Timmermann is an author) and to any self-consciousness study. A planted check of the conjunction null (could a real shared core have been detected?) would fit our null-audit style.

### Alpha coherence is a network signature of cognitive recovery from disorders of consciousness

Zhou DW, Conte MM, Curley WH, Spencer-Salmon CA, Chatelle C, Rosenthal ES, Bodien YG, Victor JD, Schiff ND, Brown EN, Edlow BL (2026). *Cortex*. [doi:10.1016/j.cortex.2026.11.009](https://doi.org/10.1016/j.cortex.2026.11.009). Paper, abstract only, **useful**.

- **Question:** Does the network organisation of posterior alpha coherence in clinical EEG track recovery of higher cognition after severe brain injury better than standard connectivity measures?
- **Idea tested:** Alpha that stays in step across posterior cortex, summarised as a network, indexes the thalamocortical integrity needed for higher cognition.
- **Data and method:** 95 clinical EEG recordings from two centres: 28 healthy controls and 33 patients with acute or chronic disorders of consciousness, 25 with follow-up. Global coherence analysis; network organisation from the principal eigenvector of the 8-12 Hz cross-spectral matrix. Recovery = CRS-R total 22 or above.
- **Results:** Classifying recovery: AUC .78 for the alpha network measure against .45-.53 for weighted phase lag index connectivity (abstract only).
- **Limits:** Small sample pooled from two studies; behavioural threshold outcome; published text closed, abstract only; an earlier medRxiv version gives slightly different comparison AUCs.
- **For us:** Coherence comes from the cross-spectrum, which our multichannel phase-randomised surrogates keep, so it counts as spectral in the surrogate gate (#8). Test whether alpha network shape adds anything over alpha power on the Chennu propofol EEG (#21) under a sealed prereg.
- **Touches:** #8, #21

### Atlas of intracranial EEG complexity across cortical regions and global states of consciousness

Jeantin L et al. (2026). *PNAS Nexus*. [doi:10.1093/pnasnexus/pgag048](https://doi.org/10.1093/pnasnexus/pgag048). Journal article, abstract only, **useful**.

- **Question:** How does iEEG complexity vary across regions and states?
- **Idea tested:** Kolmogorov complexity, permutation and spectral entropy in 106 iEEG participants; propofol in 5.
- **Data and method:** Kolmogorov complexity, permutation and spectral entropy in 106 iEEG participants; propofol in 5.
- **Results:** Random forest on sleep stages micro-AUC 0.90; complexity lowest under propofol (descriptive).
- **Limits:** Propofol n=5, not classified.
- **For us:** Complexity measures in sleep and propofol, intracranial only.
- **Touches:** Task #5 transfer

### Electrophysiological markers of surprise-induced failures of visual and auditory awareness

Leong EL, Chua YD, Obana T, Asplund CL (2026). *Consciousness and Cognition 145:104118*. [doi:10.1016/j.concog.2026.104118](https://doi.org/10.1016/j.concog.2026.104118). Paper, abstract only, **useful**.

- **Question:** Which EEG responses go with surprise-induced blindness and deafness, where a rare task-irrelevant surprise makes people miss a probe 300-400 ms later?
- **Idea tested:** Surprise drives a novelty response that steals the resources needed to become aware of the probe.
- **Data and method:** 33 adults, visual (SiB) and auditory (SiD) tasks in counterbalanced order; 16-channel OpenBCI EEG at 125 Hz, left-earlobe reference (stored values are microvolts/24). Data and code are open: OpenNeuro ds006394.
- **Results:** A late parietal novelty positivity locked to the surprise shrank across trials along with the behavioural deficit; early and probe-evoked components differed by modality and did not habituate (abstract only). Their scripts contrast surprise vs standard and probe present vs absent; they do not contrast aware vs unaware probes.
- **Limits:** Abstract only (paywalled). Low-density consumer EEG. Few unaware trials: our count from the behaviour files is a median of 3 surprise-induced misses per subject (visual) and 1 (auditory).
- **For us:** We planned ds006394 as the discovery set for the hypothesis generator. Our trial counts killed that: too few unaware trials, and the misses are confounded with surprise and trial number (experiments/hypothesis_generator).
- **Touches:** hypothesis-generator

### Identifying neural correlates of auditory perceptual awareness and deviance using a no-report inattentional deafness paradigm

Ellinghorst A, Dellert T, Zhu Y, Straube T, Dykstra AR, Schloßmacher I (2026). *bioRxiv*. [doi:10.64898/2026.10.05.755932](https://doi.org/10.64898/2026.10.05.755932). Preprint, abstract only, **useful**.

- **Question:** Can awareness, deviance and task relevance be separated in auditory ERPs?
- **Idea tested:** Multitone masking; three phases with identical tone pairs: naive (unaware), informed (aware), task-relevant.
- **Data and method:** EEG ERPs; physically identical target-tone pairs in multitone masks across three fixed-order phases (naive, informed, task-relevant gap judgement); sample size not in the abstract.
- **Results:** Physically identical target-tone pairs in multitone masks across three phases differing only in instructions: naive (unaware), informed (aware, task-irrelevant), and task-relevant (gap judgement). Awareness gave an auditory awareness negativity and an increased positivity in the P3 window, both larger when task-relevant. Deviants gave a mismatch negativity in all phases (largest when task-relevant), while a significant deviant P3 appeared only in the task-relevant phase. (abstract only)
- **Limits:** Abstract only; sample size and effect sizes not in the abstract. Awareness is manipulated between fixed-order phases, so time on task and expectation are confounded with awareness; condition-averaged ERPs.
- **For us:** Not a single-trial bifurcation test, so no threat to that study's novelty. Shows AAN and P3 can be dissociated from report in audition. Used as a post-cutoff item in the theory-ledger leak probe and manipulation check (experiments/theory_leak).
- **Touches:** bifurcation, ledger

### Inferring brain structural complexity from dynamical measures

Gaglioti G, Cattani A, Nieus T, Momi D, Comolatti R, Dalla Porta L, Sarasso S, Massimini M (2026). *bioRxiv (22 Oct 2026)*. [doi:10.64898/2026.10.21.760743](https://doi.org/10.64898/2026.10.21.760743). Preprint, abstract only, **useful**.

- **Question:** Which complexity measures actually reflect the integration-differentiation balance of the underlying network?
- **Idea tested:** Simulate networks with known structure and see which observational and perturbational measures follow it.
- **Data and method:** Wilson-Cowan mean-field simulations over systematically rewired networks; observational (spontaneous) and perturbational metrics.
- **Results:** Observational measures behaved heterogeneously: some tracked integration, some differentiation, some barely moved. Perturbational measures peaked at intermediate rewiring, scaled with small-worldness, resisted common-driver confounds and were highest near a wake-like regime. (abstract only)
- **Limits:** Simulation only; abstract only.
- **For us:** A model-based reason why the spontaneous-EEG markers in #42 may fail: they do not track structure reliably. Use it to frame a negative #42 result, and as a design idea: plant structure in simulation as a positive control for each marker.
- **Touches:** #42, #5, Study 2

### Spontaneous slow waves index multiple dimensions of recovery in disorders of consciousness

Ruyant Belabbas A, Boullet A, Manasova D, Le Coz A, Valente M, Lejeune F, Sitt JD, Naccache L, Rohaut B, Andrillon T (2026). *bioRxiv (8 Oct 2026)*. [doi:10.64898/2026.09.30.755786](https://doi.org/10.64898/2026.09.30.755786). Preprint, abstract only, **useful**.

- **Question:** Do local slow waves in DoC patients index damage, residual awareness, or recovery potential?
- **Idea tested:** Sleep-like slow waves in awake patients may carry information about cortical state beyond EEG slowing.
- **Data and method:** 256-channel EEG during the Local-Global paradigm in 236 DoC patients (123 UWS, 62 MCS-, 29 MCS+); slow-wave density, amplitude and slopes, related to CRS-R, Local-Global responses, one-year GOS-E and MRI.
- **Results:** Associations with concurrent and follow-up measures are reported; the abstract text available to us was cut before the numerical results. (abstract only)
- **Limits:** Abstract only; data availability unknown; no open DoC EEG.
- **For us:** Slow-wave density and slope belong on our arousal axis. If the Paris DoC EEG ever opens, Study 2's DoC arm could test whether complexity markers add anything over slow-wave features.
- **Touches:** Study 2, #5

### Subjective Visibility Enhances Early Posterior Electroencephalography Decoding of Stimulus Location across Report and No-report Tasks

Gnodde S, Aslanov V, Hogan A, Francken JC, Olcese U, Stein T (2026). *Journal of Cognitive Neuroscience*. [doi:10.1162/jocn.a.2691](https://doi.org/10.1162/jocn.a.2691). Article, abstract only, **useful**.

- **Question:** Does subjective visibility change what EEG can decode about a stimulus, with and without report?
- **Idea tested:** Near-threshold gratings; stimulus-location decoding in report and no-report tasks, split by visibility.
- **Data and method:** EEG; gratings, not faces. Preprint: doi:10.64898/2026.04.20.719596 ('Posterior but not frontal neural signatures of subjective visibility in report-independent EEG decoding').
- **Results:** Visibility enhances early posterior location decoding (about 130-170 ms) in both tasks; no frontal visibility effect.
- **Limits:** Location decoding, not an awareness contrast at a fixed ERP window; different stimuli and data.
- **For us:** Supports testing the posterior VAN window at fixed SOA in Cohen 2024; not a pre-emption of that test.
- **Touches:** cohen-fixed-soa

### Trial-wise awareness ratings do not capture the dynamics of masked priming

Berger A, Rohr M, Wentura D, Kiefer M (2026). *Neuroscience of Consciousness*. [doi:10.1093/nc/niag034](https://doi.org/10.1093/nc/niag034). Paper, abstract only, **useful**.

- **Question:** Do trial-wise PAS changes track changes in masked priming?
- **Idea tested:** Awareness ratings drift with practice independently of priming.
- **Data and method:** Reanalysis of three masked priming experiments, with and without trial-wise PAS.
- **Results:** PAS ratings rose with practice, even on catch trials, without matching changes in priming; ratings also altered priming dynamics.
- **Limits:** Read at abstract level only.
- **For us:** For item 3: practice raises reported visibility in general, so prior-showing effects must be item-specific and control trial rank.
- **Touches:** round15-priorart

### White-matter disconnection shapes distributed cortical spectral dynamics after stroke

Mazzonetto I, Celli M, Pini L, et al. (2026). *bioRxiv (24 Aug 2026)*. [doi:10.64898/2026.08.20.745699](https://doi.org/10.64898/2026.08.20.745699). Preprint, abstract only, **useful**.

- **Question:** Does post-stroke slow-wave activity spread to disconnected but intact cortex?
- **Idea tested:** Slow waves follow structural disconnection (connectional diaschisis).
- **Data and method:** 128-channel source EEG with disconnection mapping in 49 acute stroke patients and 20 controls.
- **Results:** Disconnected regions showed perilesional-like changes: more delta/theta and steeper aperiodic slopes, correlated with severity. (abstract only)
- **Limits:** Awake, conscious patients.
- **For us:** The aperiodic exponent steepens with disconnection in conscious people, one more reason the exponent is a confound to control, not a consciousness marker. Ledger: large activity changes with consciousness intact (C42-type).
- **Touches:** constraint_ledger, lz_slope

### Cortical evidence accumulation for visual perception occurs irrespective of reports

Stockart F, Msheik R, Robin A, et al. (2025). *Nature Communications*. [doi:10.1038/s41467-025-63255-y](https://doi.org/10.1038/s41467-025-63255-y). Paper, abstract only, **useful**.

- **Question:** Does evidence accumulation in cortex explain perception without report?
- **Idea tested:** A leaky accumulator explains both detection and confidence, with or without reports.
- **Data and method:** sEEG, 29 participants, three preregistered experiments (immediate response, delayed detection, passive viewing).
- **Results:** High-gamma build-up slope in visual, inferior frontal and insular cortex tracks RT; the ventral visual signal separates seen/unseen, high/low intensity, and confidence levels.
- **Limits:** Read at abstract level only.
- **For us:** Same group as Sergent 2021, with a graded-accumulation account; relevant to whether single-trial bifurcation and accumulation can be told apart.
- **Touches:** bifurcation-audit

### Perceptual and attentional impairments of conscious access involve distinct neural mechanisms despite equal task performance

Noorman S, Stein T, Fahrenfort JJ, van Gaal S (2025). *eLife*. [doi:10.7554/eLife.97900](https://doi.org/10.7554/eLife.97900). Paper, abstract only, **useful**.

- **Question:** Do masking and the attentional blink block conscious access in the same way?
- **Idea tested:** Equate performance and compare neural signatures.
- **Data and method:** EEG, masking vs attentional blink at matched performance.
- **Results:** The two impair access by distinct neural mechanisms despite equal task performance (title and our prior-art read).
- **Limits:** Abstract only.
- **For us:** A caution for transfer: an attentional-blink signature need not carry to near-threshold tactile detection.
- **Touches:** hypothesis-generator

### Adiposity influences intraindividual variability in behavioral and neuroelectric indices of attentional inhibition

Kim J, et al. (2024). *Psychophysiology*. [doi:10.1111/psyp.14677](https://doi.org/10.1111/psyp.14677). Paper, full text, **useful**.

- **Question:** Is intraindividual variability in P3b latency linked to adiposity?
- **Idea tested:** RIDE-based single-trial P3b latency in a flanker task; SDs of single-trial latencies.
- **Data and method:** Flanker EEG in adults.
- **Results:** Single-trial P3b latency SDs of about 77-84 ms, not corrected for the estimator's noise floor.
- **Limits:** Flanker task, not masking; raw SDs include estimation noise.
- **For us:** A published range for raw P3b latency SD, which brackets our 50 and 75 ms cases.
- **Touches:** latency_spread

### Critical dynamics in spontaneous EEG predict anesthetic-induced loss of consciousness and perturbational complexity

Maschke C, O'Byrne J, Colombo MA, Boly M, Gosseries O, Laureys S, Rosanova M, Jerbi K, Blain-Moraes S (2024). *Communications Biology 7, 946*. [doi:10.1038/s42003-024-06613-8](https://doi.org/10.1038/s42003-024-06613-8). Paper, abstract only, **useful**.

- **Question:** In 15 healthy adults under three anaesthetics, resting EEG predicted the stimulation-based consciousness index closely.
- **Data and method:** 15 healthy adults (propofol 5, xenon 5, ketamine 5), data from earlier studies. Avalanche criticality, chaoticity and related metrics; unconsciousness moved away from criticality and the edge of chaos. Ridge regression on 16 features predicted PCImax; leave-one-subject-out (15 folds) mean absolute error 0.065 (+/- 0.042); a 0.35 threshold separated conscious and unconscious states for true and predicted PCImax.
- **Results:** Volunteers were put under with propofol, xenon or ketamine; all stopped responding, but only the ketamine group reported vivid dreams afterwards. Measures of how close the resting brain sits to a 'critical' tipping point separated the dreaming group from the others, and predicted each person's score on the magnetic-pulse test.
- **For us:** If true, the best-validated measure could be tested on many more open datasets. Caution: 15 subjects, 5 per drug, and the same cohort as Colombo 2019 and Sarasso 2015, so these are not independent replications. We test it out of sample.
- **Touches:** news

### Exploring effects of anesthesia on complexity, differentiation, and integrated information in rat EEG

Nilsen AS, Arena A, Storm JF (2024). *Neuroscience of Consciousness 2024(1), niae021*. [doi:10.1093/nc/niae021](https://doi.org/10.1093/nc/niae021). Paper, abstract only, **useful**.

- **Question:** In rats, integrated-information estimates from spontaneous EEG went up under anaesthesia, opposite to the stimulation-based index.
- **Data and method:** Rats under propofol, sevoflurane and ketamine. PCI (electrical stimulation), LZ and geometric integrated information (PhiG) best separated wake from propofol and sevoflurane. PCI was anti-correlated with spontaneous integrated-information measures, which generally increased under propofol and sevoflurane. Authors suggest perturbation-based and spontaneous measures may be complementary.
- **Results:** The researchers compared a stimulation-based complexity score with several scores computed from ordinary EEG in rats under three anaesthetics. Some scores worked well. But the estimates of 'integrated information', the quantity at the heart of one major theory, generally rose under propofol and sevoflurane, the reverse of what that theory expects.
- **For us:** A warning that Phi proxies may not track what IIT says Phi tracks. Our known-Phi network test checks this before any proxy touches brain data.
- **Touches:** news

### How well do neural signatures of resting-state EEG detect consciousness? A large-scale clinical study

Ma X, Qi Y, Xu C, et al. (2024). *Human Brain Mapping*. [doi:10.1002/hbm.26586](https://doi.org/10.1002/hbm.26586). Article, abstract only, **useful**.

- **Question:** Which of the many proposed EEG signatures of consciousness actually work in a large patient sample?
- **Idea tested:** They computed 380 resting-EEG metrics in 296 people (99 UWS, 129 MCS, 36 emerged from MCS, 32 healthy) and evaluated each with bootstrap resampling.
- **Data and method:** Spectral, nonlinear, connectivity and graph measures; bootstrap evaluation.
- **Results:** Relative alpha and delta power were the most dependable markers of consciousness.
- **Limits:** One clinical cohort; DoC only; abstract only read here.
- **For us:** A many-marker screen already exists for DoC, and simple spectral power won. Supports our habit of requiring every marker to beat the spectrum.
- **Touches:** Hypothesis tournament

### Perceptual awareness of near-threshold tones scales gradually with auditory cortex activity and pupil dilation

Doll L, Dykstra AR, Gutschalk A (2024). *iScience*. [doi:10.1016/j.isci.2024.110530](https://doi.org/10.1016/j.isci.2024.110530). Paper, abstract only, **useful**.

- **Question:** Does the auditory awareness negativity need a non-linear threshold, or does it scale with perception?
- **Idea tested:** Awareness tracks a graded signal, in line with signal detection theory.
- **Data and method:** MEG, EEG and pupillometry; near-threshold tones, task-relevant vs irrelevant; six-point perception ratings.
- **Results:** Task-irrelevant tones gave no awareness negativity or pupil dilation. Task-relevant tones gave both, stronger for hits but present for misses, and responses fell gradually with lower ratings.
- **Limits:** Read at abstract level only.
- **For us:** Graded counterpart to Sergent 2021 in the same modality; motivates graded generators in our bifurcation audit.
- **Touches:** bifurcation-audit

### Trial-by-trial detection of cognitive events in neural time-series

Weindel G, et al. (2024). *Imaging Neuroscience*. [doi:10.1162/imag_a_00400](https://doi.org/10.1162/imag_a_00400). Paper, full text, **useful**.

- **Question:** Can the trial-by-trial timing of cognitive events be recovered from EEG?
- **Idea tested:** Hidden multivariate pattern (HMP) model fitting event onsets per trial.
- **Data and method:** Simulations and oddball-type EEG.
- **Results:** Condition-averaged ERPs are distorted by between-trial time jitter; later components inherit the jitter of earlier ones; HMP recovers by-trial event times.
- **Limits:** Assumes a fixed sequence of events; not masking.
- **For us:** An alternative to Woody estimation if our gate says the method is blind.
- **Touches:** latency_spread

### Testing the generalization of neural representations

Sandhaeger F, Siegel M (2023). *NeuroImage*. [doi:10.1016/j.neuroimage.2023.120258](https://doi.org/10.1016/j.neuroimage.2023.120258). Paper, full text, **useful**.

- **Question:** Can significant cross-condition or cross-time generalisation arise when the underlying codes are orthogonal?
- **Idea tested:** Simulations of signal mixing in EEG/MEG-like data; a test comparing observed generalisation with what identical codes would give.
- **Data and method:** Simulation and analytic arguments; proposed identity-expected generalisation benchmark.
- **Results:** Signal mixing and dependencies can drive significant generalisation between orthogonal representations; spurious generalisation is markedly lower than expected under identical codes. High-pass filtering can give below-chance TG.
- **Limits:** Does not model latency jitter.
- **For us:** Their observed-vs-identity-expected ratio is a candidate pre-set square metric.
- **Touches:** tg_square_specificity

### Low frequency oscillations drive EEG's complexity changes during wakefulness and sleep

González J, Mateos D, Cavelli M, Mondino A, Pascovich C, Torterolo P, Rubido N (2022). *Neuroscience*. [doi:10.1016/j.neuroscience.2022.04.025](https://doi.org/10.1016/j.neuroscience.2022.04.025). Article, abstract only, **useful**.

- **Question:** Why does EEG complexity drop in slow-wave sleep: is it the oscillations?
- **Idea tested:** They tested how the frequency content of brain signals in freely moving rats shapes complexity estimates across sleep and wake.
- **Data and method:** Rat recordings at micro, meso and macro scales across the sleep-wake cycle.
- **Results:** The low-frequency spectrum (delta, theta, sigma) drives the complexity changes between sleep and wake.
- **Limits:** Rats; abstract only read here.
- **For us:** Earliest prior art we found for 'complexity in sleep is spectral'. Cite it beside Höhn 2024 whenever we state our LZ result.
- **Touches:** LZ vs spectrum

### Quantifying arousal and awareness in altered states of consciousness using interpretable deep learning

Lee M, Sanz LRD, Barra A, Wolff A, Nieminen JO, Boly M, et al. (2022). *Nature Communications*. [doi:10.1038/s41467-022-28451-0](https://doi.org/10.1038/s41467-022-28451-0). Article, abstract only, **useful**.

- **Question:** Can one EEG index separate arousal (being awake) from awareness (having experience)?
- **Idea tested:** They trained an explainable deep network on EEG responses to TMS across sleep, anaesthesia and brain injury, and also tested resting EEG.
- **Data and method:** TMS-EEG in sleep (n=6), general anaesthesia (n=16) and severe brain injury (n=34); resting EEG under anaesthesia (n=15) and brain injury (n=34).
- **Results:** The index tracked both components across physiological, drug and injury states; ketamine anaesthesia and REM sleep came out as low arousal with high awareness.
- **Limits:** Small groups per state; abstract only read here.
- **For us:** Closest existing cross-state 'one marker everywhere' attempt. Any tournament must beat or explain this, and must report sample sizes per state honestly.
- **Touches:** Hypothesis tournament

### Evidence accumulation relates to perceptual consciousness and monitoring

Pereira M, Megevand P, Tan MX, et al., Faivre N (2021). *Nature Communications 12, 3261*. [doi:10.1038/s41467-021-23540-y](https://doi.org/10.1038/s41467-021-23540-y). Paper, abstract only, **useful**.

- **Question:** Do perceptual consciousness and confidence involve evidence accumulation?
- **Idea tested:** Single-neuron recording in posterior parietal cortex (one participant) and EEG in healthy volunteers during near-threshold vibrotactile detection with confidence ratings; accumulation-to-bound model.
- **Data and method:** Intracranial microelectrode and EEG, own data.
- **Results:** Detected stimuli evoked accumulation-like responses, irrespective of motor confounds or task demands; a model with detection = evidence reaching a bound and confidence = distance from the bound reproduced behaviour and neural data.
- **Limits:** Tactile, near-threshold detection; one intracranial participant.
- **For us:** Covers the seen-vs-unseen response-locked P3b/CPP question at a fixed stimulus, so our item 3 (P3b response-locking on Cohen data) was skipped as established.
- **Touches:** cohen-fixed-soa

### High-pass filtering artifacts in multivariate classification of neural time series data

van Driel J, Olivers CNL, Fahrenfort JJ (2021). *Journal of Neuroscience Methods*. [doi:10.1016/j.jneumeth.2021.109080](https://doi.org/10.1016/j.jneumeth.2021.109080). Paper, abstract only, **useful**.

- **Question:** Do high-pass filtering and baseline correction distort decoding time courses?
- **Idea tested:** Simulations and EEG data with varied high-pass cut-offs and baselines.
- **Data and method:** Decoding and TG under filtering settings.
- **Results:** High-pass filtering and baseline correction displace multivariate patterns into activity-silent periods, most visibly in TG, even at 0.05 Hz.
- **Limits:** Read at abstract level only (bioRxiv rate limit).
- **For us:** Secondary arm of TG-square study: filter/baseline ablation.
- **Touches:** tg_square_specificity

### Modelling visibility judgments using models of decision confidence

Rausch M, Hellmann S, Zehetleitner M (2021). *Attention, Perception, & Psychophysics*. [doi:10.3758/s13414-021-02284-3](https://doi.org/10.3758/s13414-021-02284-3). Paper, abstract only, **useful**.

- **Question:** Which models of decision confidence also describe visibility ratings?
- **Idea tested:** Fitted several graded confidence models to continuous visibility ratings in masked orientation tasks with 5 masking intervals (SOAs).
- **Data and method:** Behaviour; model comparison; data on OSF gfkta (no licence set).
- **Results:** Graded models fit the visibility ratings; no discrete-state model was tested.
- **Limits:** No all-or-none model in the comparison. Depth of reading not recorded by the planning agent, so treated as abstract.
- **For us:** A 5-level masking dataset that could carry a conditional-independence test, but masking is where graded visibility is already conceded.
- **Touches:** Fable#13 item 4, all-or-none vs graded

### Representational dynamics preceding conscious access

Alilović J, van Moorselaar D, Graetz M, van Gaal S, Slagter HA (2021). *NeuroImage*. [doi:10.1016/j.neuroimage.2021.117789](https://doi.org/10.1016/j.neuroimage.2021.117789). Paper, abstract only, **useful**.

- **Question:** What in the EEG predicts whether T2 is seen in the attentional blink, and how early?
- **Idea tested:** Multivariate decoding of seen vs unseen T2 and of T1 identity.
- **Data and method:** EEG, Biosemi 64 channels, N = 32, attentional blink (same lab as ds001810).
- **Results:** The T2 P3 is larger for seen T2 while the T1 P3 does not differ; seen vs unseen decodes for more than 900 ms after T2 and above chance before T1; T1 identity decodes more strongly on T2-seen trials (via our prior-art read).
- **Limits:** Abstract and secondary summary only.
- **For us:** The closest design to our ds001810 screen; its effects are our within-dataset positive controls, not findings.
- **Touches:** hypothesis-generator

### Characterizing the brain's dynamical response from scalp-level neural electrical signals: a review of methodology development

Ouyang G, et al. (2020). *Cognitive Neurodynamics*. [doi:10.1007/s11571-020-09631-4](https://doi.org/10.1007/s11571-020-09631-4). Paper, full text, **useful**.

- **Question:** What methods separate single-trial latency variability from ERP averages?
- **Idea tested:** Review of Woody, RIDE and related decomposition methods.
- **Data and method:** Review.
- **Results:** Latency variability smears averaged components; RIDE decomposes stimulus-locked, response-locked and latency-variable parts.
- **Limits:** Review; method author's perspective.
- **For us:** Our report-block data have response-locked activity, which the single-code ladder does not model (stated as a limit).
- **Touches:** latency_spread

### Neural Variability Is Quenched by Attention

Arazi A, Yeshurun Y, Dinstein I (2019). *Journal of Neuroscience*. [doi:10.1523/jneurosci.0355-19.2019](https://doi.org/10.1523/jneurosci.0355-19.2019). Paper, abstract only, **useful**.

- **Question:** Do alertness and spatial attention reduce trial-by-trial EEG variability?
- **Idea tested:** Attention raises signal-to-noise partly by quenching variability.
- **Data and method:** EEG with alerting and spatial cues.
- **Results:** Cues reduced trial-by-trial variability, specific to visual cortex and larger contralateral to the attended field; larger quenching went with larger behavioural benefit.
- **Limits:** Read at abstract level only.
- **For us:** Main confound for item 4: seen trials may be more attended, so lower variance on seen trials need not be about consciousness.
- **Touches:** round15-priorart, stability_specificity

### Single-Trial Mechanisms Underlying Changes in Averaged P300 ERP Amplitude and Latency in Military Service Members After Combat Deployment

Trongnetrpunya A, Rapp P, Wang C, et al. (2019). *Frontiers in Human Neuroscience*. [doi:10.3389/fnhum.2019.00377](https://doi.org/10.3389/fnhum.2019.00377). Paper, full text, **useful**.

- **Question:** Do averaged P300 changes come from single-trial amplitude or latency changes?
- **Idea tested:** Single-trial P300 latency and amplitude estimation before and after deployment.
- **Data and method:** Oddball EEG in service members.
- **Results:** Separates amplitude from latency effects in averages; warns that the maximum-correlation lag can come from a signal component that is due to noise.
- **Limits:** Clinical sample; not masking.
- **For us:** Noise-driven lag bias, the same issue our calibration ladder handles.
- **Touches:** latency_spread

### The EEG signature of sensory evidence accumulation during decision formation closely tracks subjective perceptual experience

Tagliabue CF, Veniero D, Benwell CSY, Cecere R, Savazzi S, Thut G (2019). *Scientific Reports 9, 4949*. [doi:10.1038/s41598-019-41024-4](https://doi.org/10.1038/s41598-019-41024-4). Paper, abstract only, **useful**.

- **Question:** Does the centro-parietal positivity track physical or subjective evidence?
- **Idea tested:** Varied physical stimulus strength and collected ratings of experienced strength.
- **Data and method:** EEG, own data.
- **Results:** The link between physical strength and CPP amplitude is mediated by the subjective rating.
- **Limits:** Stimulus strength varies; not a fixed-stimulus seen/unseen test.
- **For us:** A P3b/CPP seen-unseen difference may be a decision signal; response-locking is the test.
- **Touches:** cohen-fixed-soa

### The spectral exponent of the resting EEG indexes the presence of consciousness during unresponsiveness induced by propofol, xenon, and ketamine

Colombo MA, Napolitani M, Boly M, Gosseries O, Casarotto S, Rosanova M, Brichant JF, Boveroux P, Rex S, Laureys S, Massimini M, Chieregato A, Sarasso S (2019). *NeuroImage 189:631-644*. [doi:10.1016/j.neuroimage.2019.01.024](https://doi.org/10.1016/j.neuroimage.2019.01.024). Paper, abstract only, **useful**.

- **Question:** Does the 1/f exponent of resting EEG track consciousness across anaesthetics?
- **Idea tested:** Use ketamine (dreaming) against propofol and xenon (no report) to split responsiveness from experience.
- **Data and method:** Resting EEG, n = 5 per drug (Milan cohort).
- **Results:** The exponent became steeper under propofol and xenon, not ketamine, and correlated with PCI.
- **Limits:** Five people per drug; same cohort as Sarasso 2015.
- **For us:** The origin of our spectral-slope baseline feature and of the ketamine gap noted in the negative atlas.
- **Touches:** lz_slope, #7, Study 2

### Robust EEG-based cross-site and cross-protocol classification of states of consciousness

Engemann DA, Raimondo F, King JR, Rohaut B, Louppe G, Faugeras F, Annen J, Cassol H, Gosseries O, Fernandez-Slezak D, Laureys S, Naccache L, Dehaene S, Sitt JD (2018). *Brain 141:3179-3192*. [doi:10.1093/brain/awy251](https://doi.org/10.1093/brain/awy251). Paper, abstract only, **useful**.

- **Question:** Do EEG classifiers of DoC states transfer across sites and protocols?
- **Idea tested:** Random forest on Sitt-style markers, trained in Paris, tested in Liège.
- **Data and method:** 327 DoC recordings plus 66 controls; cross-site test.
- **Results:** Cross-site AUC 0.73-0.78.
- **Limits:** Spectral markers carried much of the performance.
- **For us:** A benchmark for what held-out DoC classification achieves; the bar Study 2's DoC arm would need to meet.
- **Touches:** Study 2, #14

### Individual differences in dual-target RSVP task performance relate to entrainment but not to individual alpha frequency

Kranczioch C (2017). *PLOS ONE*. [doi:10.1371/journal.pone.0178934](https://doi.org/10.1371/journal.pone.0178934). Paper, full text, **useful**.

- **Question:** Do people whose visual cortex entrains more to the RSVP stream show a larger blink?
- **Idea tested:** Between-subject correlations of inter-trial coherence and power with dual-target performance; individual alpha frequency vs stream rate.
- **Data and method:** Human EEG, 51 participants.
- **Results:** Contrary to prediction, ITC correlated positively with performance (for targets not preceded by targets); no mediation by individual alpha frequency.
- **Limits:** Between-subject only; no trial-level blink vs no-blink comparison.
- **For us:** Opposite-signed evidence to Zauner; its between-subject design is our pre-declared secondary.
- **Touches:** rhythm_blink

### Initial-state-dependent, robust, transient neural dynamics encode conscious visual perception

Baria AT, Maniscalco B, He BJ (2017). *PLOS Computational Biology*. [doi:10.1371/journal.pcbi.1005806](https://doi.org/10.1371/journal.pcbi.1005806). Paper, abstract only, **useful**.

- **Question:** What dynamics of slow cortical activity distinguish seen from unseen threshold stimuli?
- **Idea tested:** Dynamic-pattern (state-space) analysis of whole-brain slow (<5 Hz) MEG during a threshold visual task; across-trial variability split into norm and angle.
- **Data and method:** Human MEG, threshold-level visual detection.
- **Results:** Pre-stimulus patterns predict later seen reports; seen and unseen trials follow separated trajectories; stimulus-induced across-trial variability reduction is mainly in pattern angle, matching Schurger 2015; 5-15 Hz trajectories slow down only in seen trials.
- **Limits:** Partly replicates Schurger's across-trial effect; no amplitude- or SNR-matched control of the angle measure.
- **For us:** Their 'angle, not norm' result has the same SNR blind spot as Schurger's norm control; the injection test applies to it too.
- **Touches:** stability_specificity

### Are there levels of consciousness?

Bayne T, Hohwy J, Owen AM (2016). *Trends in Cognitive Sciences 20:405-413*. [doi:10.1016/j.tics.2016.03.009](https://doi.org/10.1016/j.tics.2016.03.009). Review, abstract only, **useful**.

- **Question:** Is 'level of consciousness' one dimension?
- **Idea tested:** Argue for a multidimensional view of global states.
- **Data and method:** Conceptual.
- **Results:** Global states differ along several dimensions; a single 'level' misleads.
- **Limits:** Conceptual.
- **For us:** Why our benchmark separates arousal from experience instead of one 'level' score.
- **Touches:** #42, Study 2

### Early Local Activity in Temporal Areas Reflects Graded Content of Visual Perception

Tagliabue CF, Mazzi C, Bagattini C, Savazzi S (2016). *Frontiers in Psychology 7, 572*. [doi:10.3389/fpsyg.2016.00572](https://doi.org/10.3389/fpsyg.2016.00572). Paper, abstract only, **useful**.

- **Question:** Is the VAN graded with rated clarity (PAS) or all-or-none?
- **Idea tested:** ERPs to reduced-contrast stimuli rated on the four-point Perceptual Awareness Scale.
- **Data and method:** EEG, own data.
- **Results:** A VAN (left centro-parietal, 280-320 ms here) and a late positivity both grew gradually with PAS rating.
- **Limits:** Contrast varies with rating, so stimulus and awareness are not fully separated; latency differs from the face VAN.
- **For us:** Graded VAN with ratings is established; the unseen-side gradient at a fixed stimulus is not.
- **Touches:** cohen-fixed-soa

### Stratification of unresponsive patients by an independently validated index of brain complexity

Casarotto S, Comanducci A, Rosanova M and others; senior author Massimini M (2016). *Annals of Neurology 80, 718-729*. [doi:10.1002/ana.24779](https://doi.org/10.1002/ana.24779). Paper, abstract only, **useful**.

- **Question:** A cutoff on the stimulation-based complexity index, set in people who could report, separated conscious from unconscious perfectly and flagged some 'vegetative' patients as possibly conscious.
- **Data and method:** Benchmark population 150 (healthy and communicative brain-injured; wake, disconnected consciousness, unconsciousness). Optimal cutoff gave 100% sensitivity and specificity in the benchmark; applied to 38 MCS and 43 VS patients: 94.7% sensitivity for MCS; 9 of 43 VS patients above the cutoff.
- **Results:** The team first set a threshold using 150 people whose state was known from their own reports. That threshold then caught almost all minimally conscious patients, and showed 9 of 43 patients judged vegetative with scores like conscious people.
- **For us:** The strongest published L2 result. No open TMS-EEG set of this kind exists, which is the biggest data gap in our plan.
- **Touches:** news

### Neural signatures of conscious face perception in an inattentional blindness paradigm

Shafto JP, Pitts MA (2015). *Journal of Neuroscience*. [doi:10.1523/jneurosci.0145-15.2015](https://doi.org/10.1523/jneurosci.0145-15.2015). Article, abstract only, **useful**.

- **Question:** Which EEG responses track awareness of faces when the faces are irrelevant to the task?
- **Idea tested:** Three-phase inattentional blindness design: faces shown during a demanding task (some people miss them), then the same with awareness, then with the faces task-relevant.
- **Data and method:** EEG ERPs; line-drawing faces and matched controls.
- **Results:** The N170 and the visual awareness negativity (about 260-300 ms) were absent during inattentional blindness and present with awareness. The P3b appeared only when faces were task-relevant, not when they were seen but irrelevant.
- **Limits:** Abstract only. Awareness varies between people and phases, not trial by trial.
- **For us:** Prior for COGITATE experiment 2: expect posterior seen-vs-unseen differences before 300 ms, which counts against GNW's 'no difference before 250 ms'. Used in our sealed forecasts.
- **Touches:** COGITATE forecasts

### The classic P300 encodes a build-to-threshold decision variable

Twomey DM, Murphy PR, Kelly SP, O'Connell RG (2015). *European Journal of Neuroscience 42, 1636-1643*. [doi:10.1111/ejn.12936](https://doi.org/10.1111/ejn.12936). Paper, abstract only, **useful**.

- **Question:** Is the P300 a unitary event or an evidence-accumulation signal?
- **Idea tested:** Response-locked and stimulus-locked P300 analyses for auditory and visual targets, with accumulation-to-bound model fits.
- **Data and method:** EEG, own data.
- **Results:** P300 reaches a fixed amplitude just before the response; its rate of rise scales with difficulty and explains RT variance.
- **Limits:** Detection tasks, not awareness contrasts.
- **For us:** Our P3b seen-unseen difference may be a decision signal; candidate response-locked test.
- **Touches:** cohen-fixed-soa

### Gamma band activity and the P3 reflect post-perceptual processes, not visual awareness

Pitts MA, Padwal J, Fennelly D, Martínez A, Hillyard SA (2014). *NeuroImage*. [doi:10.1016/j.neuroimage.2014.07.024](https://doi.org/10.1016/j.neuroimage.2014.07.024). Article, abstract only, **useful**.

- **Question:** Are induced gamma and the P3 markers of awareness, or of what we do with a stimulus?
- **Idea tested:** EEG experiments that vary awareness and task relevance separately.
- **Data and method:** EEG; inattentional blindness paradigm.
- **Results:** Induced gamma and the P3 were absent for task-irrelevant stimuli whether or not people were aware of them, and present for task-relevant ones.
- **Limits:** Abstract only.
- **For us:** Prior for COGITATE experiment 2: late and gamma-band differences may track the probe task, not awareness. Used in our sealed forecasts.
- **Touches:** COGITATE forecasts

### The Attentional Blink Reveals the Probabilistic Nature of Discrete Conscious Perception

Asplund CL, Fougnie D, Zughni S, Martin JW, Marois R (2014). *Psychological Science 25(3)*. [doi:10.1177/0956797613513810](https://pmc.ncbi.nlm.nih.gov/articles/PMC3954951/). Paper, full text, **useful**.

- **Question:** During the blink, does lag change how precisely a target is seen, or only whether it is seen at all?
- **Idea tested:** People reported the target's colour on a colour wheel; a mixture model split guesses from precise reports.
- **Data and method:** Behaviour, 28 people; continuous-report mixture model.
- **Results:** Lag changed the chance that the target was encoded, not the precision of what was encoded. The authors read this as discrete, all-or-none perception.
- **Limits:** The mixture model assumes a guess state. Cohen, Keefe & Brady 2023 later fitted a single graded model that did better on these same data.
- **For us:** The strongest continuous-report case for all-or-none; reanalysed against it by Cohen 2023.
- **Touches:** Fable#13 item 4, all-or-none vs graded

### A theoretically based index of consciousness independent of sensory processing and behavior (PCI)

Casali AG, Gosseries O, Rosanova M, Boly M, Sarasso S and others; senior author Massimini M (2013). *Science Translational Medicine 5(198)*. [doi:10.1126/scitranslmed.3006294](https://doi.org/10.1126/scitranslmed.3006294). Paper, abstract only, **useful**.

- **Question:** The paper that introduced the perturbational complexity index: tap the brain with a magnetic pulse and measure how complex the echo is.
- **Data and method:** TMS-evoked EEG responses compressed (Lempel-Ziv) after source modelling and binarisation. Tested in wake, dreaming, NREM sleep, midazolam, xenon and propofol sedation, and in vegetative, minimally conscious and locked-in patients; discriminated level of consciousness in single individuals.
- **Results:** If a brain is both well connected and varied, a magnetic pulse should set off a rich, hard-to-compress pattern of activity. The score built on that idea separated wake from deep sleep and anaesthesia in single people, and tracked recovery in patients emerging from coma.
- **For us:** The measure every spontaneous-EEG candidate is judged against.
- **Touches:** news

### Uncovering the Mechanisms of Conscious Face Perception: A Single-Trial Study of the N170 Responses

Navajas J, Ahmadi M, Quian Quiroga R (2013). *Journal of Neuroscience*. [doi:10.1523/JNEUROSCI.1226-12.2013](https://doi.org/10.1523/JNEUROSCI.1226-12.2013). Article, abstract only, **useful**.

- **Question:** Is the N170 larger on single trials when a face at fixed noise is consciously seen?
- **Idea tested:** Faces in noise at a fixed level near threshold; single-trial N170 analysis by report.
- **Data and method:** EEG, face detection with report.
- **Results:** At fixed stimulus noise, seen (supraliminal) faces evoke a larger N170 than unseen ones on single trials.
- **Limits:** Report task, so seen vs unseen also differ in report; a different paradigm (noise, not masking).
- **For us:** A VAN/N170 seen > unseen effect at fixed SOA in Cohen 2024 would replicate this; it is the expected positive result, not a new one.
- **Touches:** cohen-fixed-soa

### Evidence for discrete-state processing in recognition memory

Province JM, Rouder JN (2012). *PNAS 109(36)*. [doi:10.1073/pnas.1103880109](https://pmc.ncbi.nlm.nih.gov/articles/PMC3437893/). Paper, full text, **useful**.

- **Question:** How can a discrete-state account be told apart from a graded one using rating data?
- **Idea tested:** Proposed 'conditional independence': under a discrete-state model, the response distribution in each state keeps its shape across conditions and only the mixing weights change.
- **Data and method:** Recognition-memory experiments with confidence ratings across conditions.
- **Results:** Recognition memory showed the fixed-shape pattern a discrete-state model predicts.
- **Limits:** Memory, not perception. The test needs at least 3 conditions and 3 rating categories to have any power.
- **For us:** The right statistic for any all-or-none test on visibility ratings. Our planning agent's simulation suggests about 5 strength levels are needed.
- **Touches:** Fable#13 item 4, all-or-none vs graded

### Visual processing of contour patterns under conditions of inattentional blindness

Pitts MA, Martínez A, Hillyard SA (2012). *Journal of Cognitive Neuroscience*. [doi:10.1162/jocn_a_00111](https://doi.org/10.1162/jocn_a_00111). Article, abstract only, **useful**.

- **Question:** Which ERPs differ for shapes people did or did not notice?
- **Idea tested:** Inattentional blindness for square contour patterns formed by task-irrelevant line segments, across three phases.
- **Data and method:** EEG ERPs; more than half the subjects missed the patterns in phase 1.
- **Results:** Occipital ERPs at 220-260 ms differed for patterns vs random arrays whether or not people were aware; at 300-340 ms occipito-parietal differences appeared only with awareness.
- **Limits:** Abstract only. Awareness assessed after blocks, not trial by trial.
- **For us:** Some early processing proceeds without awareness, and awareness adds a slightly later posterior response. Prior for our COGITATE experiment 2 forecasts.
- **Touches:** COGITATE forecasts

### Consciousness of targets during the attentional blink: a gradual or all-or-none dimension?

Nieuwenhuis S, de Kleijn R (2011). *Attention, Perception, & Psychophysics 73*. [doi:10.3758/s13414-010-0026-1](https://doi.org/10.3758/s13414-010-0026-1). Paper, abstract only, **useful**.

- **Question:** Does the all-or-none pattern in the attentional blink depend on how awareness is measured?
- **Idea tested:** Repeated the blink visibility-rating test, then measured awareness with post-decision wagering and a harder task.
- **Data and method:** Behaviour; visibility ratings, wagering.
- **Results:** With visibility ratings the two-peak pattern came back. With wagering and a harder task it went away, and awareness looked graded.
- **Limits:** The authors note that group histograms can blur individual patterns. Depth of reading not recorded by the planning agent, so treated as abstract.
- **For us:** The all-or-none shape depends on the measure, which is part of why a behavioural ratings test cannot split theories.
- **Touches:** Fable#13 item 4, all-or-none vs graded

### Brain Dynamics Underlying the Nonlinear Threshold for Access to Consciousness

Del Cul A, Baillet S, Dehaene S (2007). *PLoS Biology*. [doi:10.1371/journal.pbio.0050260](https://doi.org/10.1371/journal.pbio.0050260). Article, abstract only, **useful**.

- **Question:** Which ERP stages track the nonlinear visibility curve under masking?
- **Idea tested:** Backward masking of digits across SOAs; ERPs with mask-only subtraction; visibility ratings.
- **Data and method:** EEG; the source of the SOA-curve bifurcation method Cohen 2024 follows.
- **Results:** Early ERPs grow linearly with SOA; a late divergence from about 270 ms follows the nonlinear visibility curve (P3-like, frontal-parietal).
- **Limits:** Across-SOA curves mix stimulus strength with awareness, the same confound our fixed-SOA test addresses.
- **For us:** Ledger C35 baseline. Our fixed-SOA contrast tests whether divergence at a fixed stimulus also starts this late.
- **Touches:** cohen-fixed-soa

### Detecting Awareness in the Vegetative State

Owen et al. (2006). *Science 313:1402-1402*. [doi:10.1126/science.1130197](https://doi.org/10.1126/science.1130197). Paper, abstract only, **useful**.

- **Question:** Primary source for ledger constraint C20 (clinical).
- **Results:** A quarter of behaviourally unresponsive brain-injured patients follow commands in fMRI or EEG imagery tasks (covert awareness / cognitive-motor dissociation).
- **Limits:** Bodien 2024: 60 of 241 (25%) across six centres. Monti 2010: 5 of 54. Owen 2006: one patient. False negatives are likely, so 25% is a floor for detected covert command-following.
- **For us:** Evidence grade A in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C20

### Breakdown of cortical effective connectivity during sleep

Massimini M, Ferrarelli F, Huber R, Esser SK, Singh H, Tononi G (2005). *Science 309:2228-2232*. [doi:10.1126/science.1117256](https://doi.org/10.1126/science.1117256). Paper, abstract only, **useful**.

- **Question:** Does cortical effective connectivity change in NREM sleep?
- **Idea tested:** TMS-EEG in wake and NREM.
- **Data and method:** TMS-EEG, healthy sleepers.
- **Results:** In NREM the TMS response stayed local and short instead of spreading as in wake.
- **Limits:** Small n; NREM only.
- **For us:** The origin of PCI; ledger row C40.
- **Touches:** constraint_ledger

### The neural correlate of (un)awareness: lessons from the vegetative state

Laureys (2005). *Trends in Cognitive Sciences 9:556-559*. [doi:10.1016/j.tics.2005.10.010](https://doi.org/10.1016/j.tics.2005.10.010). Paper, abstract only, **useful**.

- **Question:** Primary source for ledger constraint C21 (clinical).
- **Results:** Wakefulness and awareness dissociate: patients in the vegetative / unresponsive wakefulness state open their eyes and have sleep-wake cycles without behavioural signs of awareness.
- **Limits:** C20 shows some such patients are covertly aware. Rosanova 2018: TMS triggers sleep-like OFF-periods in UWS patients (N = 16) and never in awake controls (N = 20).
- **For us:** Evidence grade A in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C21

### A multimodal investigation of perceptual awareness in Alzheimer's disease

Huntley J, Barnett B, Bor D, Mancuso M, Mediano PAM, Naci L, Fleming S, et al. (2026). *medRxiv (31 Aug 2026)*. [doi:10.64898/2026.08.27.26356661](https://doi.org/10.64898/2026.08.27.26356661). Preprint, abstract only, **context**.

- **Question:** Do EEG and fMRI awareness signatures persist as Alzheimer's progresses?
- **Idea tested:** VAN, late positivity and frontoparietal activation should decline with severity.
- **Data and method:** Visual masking EEG and movie fMRI in controls, mild-moderate and severe AD.
- **Results:** VAN and late positivity and frontoparietal activation were reduced in mild-moderate AD; limited evidence in severe AD. (abstract only)
- **Limits:** Task insensitivity in severe AD.
- **For us:** Context.

### A three-component dynamical index of consciousness-related neural organisation

Ugail H, Howard N (2026). *Biological Cybernetics*. [doi:10.1007/s00422-026-01049-1](https://doi.org/10.1007/s00422-026-01049-1). Article, abstract only, **context**.

- **Question:** Can combining several EEG properties into one index track consciousness better than any single feature?
- **Idea tested:** They combined scale-free timing, cross-frequency organisation and metastable synchrony into one index, tested on simulated states and real EEG.
- **Data and method:** Generative model of nine EEG-like states plus empirical data (Sleep-EDF, per the coordinator's note).
- **Results:** They report the composite index separates states better than single features.
- **Limits:** Abstract only read here; the empirical test is limited.
- **For us:** One of the composite-index claims a tournament would have to include and test against the spectrum.
- **Touches:** Hypothesis tournament

### A whole-brain dynamical framework linking resting-state activity to TMS-evoked responses

Veronese A, Momi D, Sarasso S, Corbetta M, Allegra M, Suweis S (2026). *bioRxiv (16 Jul 2026)*. [doi:10.64898/2026.07.10.737755](https://doi.org/10.64898/2026.07.10.737755). Preprint, abstract only, **context**.

- **Question:** Can resting EEG predict TMS-evoked responses through a fitted whole-brain model?
- **Idea tested:** Closed-form cross-spectra fit resting EEG; site-specific effective connectivity predicts TEPs.
- **Data and method:** Analytic whole-brain model; resting and TMS-EEG.
- **Results:** The model predicted the spatiotemporal structure of TEPs in unseen trials; group templates captured early site-specific propagation. (abstract only)
- **Limits:** Abstract only.
- **For us:** Context: another resting-to-perturbation bridge, like Maschke 2024 and Newman 2026.

### Advanced meditation stabilizes cortical dynamics through inhibitory gain control linked to absorptive depth

Panda R, Kumar G, Núñez P, Subramaniam B, Bhandare K, Malipeddi S, Major G, Gosseries O, Laureys S, Tewarie P (2026). *bioRxiv (11 Nov 2026)*. [doi:10.64898/2026.11.08.765124](https://doi.org/10.64898/2026.11.08.765124). Preprint, abstract only, **context**.

- **Question:** What stabilises absorptive meditative states?
- **Idea tested:** Corticothalamic gain changes stabilise fast cortical dynamics.
- **Data and method:** 18 long-term Rajyoga meditators, EEG rest vs meditation, corticothalamic model fits.
- **Results:** Meditation raised beta1, beta2 and gamma power with no change in delta, theta or alpha, lowered beta non-stationarity, and fitted stronger cortical inhibitory gain. (abstract only)
- **Limits:** Small.
- **For us:** Context.

### Altered temporal dynamics of resting-state EEG microstates as a neural signature of impaired consciousness: a high-density EEG analysis in chronic disorders of consciousness

Dong X, Wang D, Hou J, Wang P, Jian X, Feng T (2026). *Brain Injury*. [doi:10.1080/02699052.2026.2707614](https://doi.org/10.1080/02699052.2026.2707614). Paper, abstract only, **context**.

- **Question:** Can EEG microstates separate UWS from MCS?
- **Idea tested:** Microstate D coverage should fall with frontoparietal decoupling.
- **Data and method:** High-density resting EEG in 20 UWS, 22 MCS and 20 controls; control-derived templates; leave-one-subject-out logistic regression.
- **Results:** Class D coverage fell from controls to MCS to UWS. (abstract only; the abstract's statistics were truncated)
- **Limits:** Small; single site.
- **For us:** Context.
- **Touches:** Study 2

### Assessing consciousness by near-nerve electrostimulation in intensive rehabilitation

Liuzzi P, Ballanti S, Mannini A, Hakiki B, Burali R, Toci T, Carrozza MC, Oddo CM, Grippo A (2026). *Journal of Neural Engineering*. [doi:10.1088/1741-2552/aea645](https://doi.org/10.1088/1741-2552/aea645). Paper, abstract only, **context**.

- **Question:** Does near-nerve median stimulation give a better EEG marker of consciousness in prolonged DoC than surface stimulation?
- **Idea tested:** Selective sensory activation without motor recruitment should give cleaner evoked complexity.
- **Data and method:** 19 prolonged DoC patients, high-density EEG, evoked potentials, field power and perturbational complexity.
- **Results:** A combined index classified chronic unresponsive patients with leave-one-subject-out accuracy 94.7% (95% CI 77.9-99.4%), sensitivity 100%, specificity 90.9%; surface stimulation gave 63.2%. (abstract only)
- **Limits:** Single-centre pilot of 19; internal cross-validation only, as the authors say.
- **For us:** Context. Small-n perfect-looking classifiers are exactly what our held-out rules guard against.
- **Touches:** #14

### Covert consciousness in behavioral coma

Edlow BL, Fecchio M, Freeman HJ, Rapalino O, Cash SS, Young MJ (2026). *Cortex*. [doi:10.1016/j.cortex.2026.07.008](https://doi.org/10.1016/j.cortex.2026.07.008). Paper, abstract only, **context**.

- **Question:** Can a patient who looks comatose (eyes closed) show task-based covert consciousness?
- **Idea tested:** Awareness may dissociate from wakefulness.
- **Data and method:** Single case, acute severe TBI, task-based fMRI and EEG.
- **Results:** An 80-year-old woman in behavioural coma on every exam showed covert consciousness on both task fMRI and task EEG. The authors cite about 25% covert consciousness among unresponsive patients. (abstract only)
- **Limits:** One case.
- **For us:** Adds to ledger constraint on covert consciousness: wakefulness is not a precondition, which weakens arousal-as-proxy logic in clinical claims.
- **Touches:** constraint_ledger

### Covert consciousness is not cognitive motor dissociation and the vegetative state is not a state of mind

Monti M, Schnakers C, Schiff N, Bodien Y (2026). *PsyArXiv (v2, 30 Oct 2026)*. [doi:10.31234/osf.io/kzt7j_v2](https://doi.org/10.31234/osf.io/kzt7j_v2). Preprint, abstract only, **context**.

- **Question:** Is DoC nosology coherent once covert consciousness is known?
- **Idea tested:** Diagnostic categories mix inferred experience with observed behaviour; CC and CMD identify different patients.
- **Data and method:** Conceptual analysis.
- **Results:** Argues that equating unresponsiveness with unconsciousness is a category error that blocks clinical use of imaging and EEG findings. (abstract only)
- **Limits:** Opinion.
- **For us:** Context for how we label DoC ground truth in any Study 2 DoC arm.
- **Touches:** Study 2, ground_truth

### Decoding sequence auditory expectations for clinical diagnostic and prognostic assessment of prolonged disorders of consciousness

Luo R, Huang Y, Xue C, Yu QY, Hu N, Wei Y, Liu H, Laureys SD, Di H, Meng J (2026). *Journal of Neural Engineering*. [doi:10.1088/1741-2552/aebdcf](https://doi.org/10.1088/1741-2552/aebdcf). Paper, abstract only, **context**.

- **Question:** Can single-trial decoding of global auditory regularities assess prolonged DoC?
- **Idea tested:** A lower-demand Local-Global variant and single-trial classifiers.
- **Data and method:** Modified Local-Global paradigm; CCA, PCA and xDAWN feature pipelines; healthy and DoC participants.
- **Results:** Single-trial classification of global effects improved by up to 15% over the original paradigm in healthy participants. (abstract only)
- **Limits:** Abstract does not give patient numbers.
- **For us:** Context.
- **Touches:** Study 2

### Functional fractionation of large-scale brain networks in the human subcortex

Li J, Atalay AS, Olchanyi MD, Cambareri MK, Ghosh SS, Horn A, Lewis LD, Brown EN, Fischl B, Kinney HC, Edlow BL (2026). *PNAS*. [doi:10.1073/pnas.2608875123](https://doi.org/10.1073/pnas.2608875123). Paper, abstract only, **context**.

- **Question:** Can subcortical network components be separated in resting fMRI?
- **Idea tested:** A tensor decomposition (NASCAR) to split overlapping networks.
- **Data and method:** Resting fMRI from 1,000 HCP participants; proof of principle in severe TBI.
- **Results:** Four large networks split into 15 reproducible subnetworks; individual subnetwork patterns predicted level of consciousness in severe TBI. (abstract only)
- **Limits:** fMRI.
- **For us:** Context.

### Intravenous methylphenidate for acute traumatic disorders of consciousness: a phase 1 dose-finding and target engagement study

Edlow BL, Barra ME, Schreier DR, Fecchio M, et al. (2026). *medRxiv (23 Aug 2026)*. [doi:10.64898/2026.08.20.26359720](https://doi.org/10.64898/2026.08.20.26359720). Preprint, abstract only, **context**.

- **Question:** Is IV methylphenidate safe in acute traumatic DoC, and does it engage brain networks?
- **Idea tested:** Dopaminergic stimulation may reactivate subcortical arousal networks.
- **Data and method:** Open-label phase 1, 9 male ICU patients (3 coma, 3 VS/UWS, 3 MCS), 0.5-2.0 mg/kg; EEG and rs-fMRI change-point analysis.
- **Results:** No serious adverse events at any dose; mild-moderate events at higher doses. (abstract only)
- **Limits:** Tiny, open-label.
- **For us:** Context.

### Lack of vision shifts occipital dynamics toward a frontal-like regime and enhances top-down connectivity

Hassan G, Cuntis ID, Gaglioti G, et al. (2026). *bioRxiv (21 Sep 2026)*. [doi:10.64898/2026.09.18.752597](https://doi.org/10.64898/2026.09.18.752597). Preprint, abstract only, **context**.

- **Question:** Does blindness retune the intrinsic dynamics of occipital cortex?
- **Idea tested:** TMS-EEG should show occipital responses becoming frontal-like.
- **Data and method:** TMS-EEG of frontal and occipital cortex in 16 blind and 16 sighted adults.
- **Results:** Blind participants had faster, lower-amplitude occipital TEPs resembling frontal ones, and stronger frontal-to-occipital connectivity. (abstract only)
- **Limits:** Small.
- **For us:** Context.

### Pharmacological evidence for propagation dynamics of TMS-evoked potentials in the human brain

Bai Z, Belardinelli P, Gordon PC, Ziemann U (2026). *Brain Stimulation*. [doi:10.1016/j.brs.2026.103178](https://doi.org/10.1016/j.brs.2026.103178). Paper, abstract only, **context**.

- **Question:** Which GABA-A drugs change early (feedforward) vs late (recurrent) TMS-evoked propagation, and PCI?
- **Idea tested:** Early beta-band coupling changes should drive later recurrent spread and PCI.
- **Data and method:** Placebo-controlled crossover TMS-EEG with zolpidem, alprazolam and diazepam, plus active vs sham TMS.
- **Results:** Alprazolam lowered early beta-band coupling and, in the late stage, current density, scattering and PCI-lz; zolpidem raised early current density but left coupling and PCI-lz unchanged; diazepam replicated alprazolam. (abstract only)
- **Limits:** Healthy awake volunteers; sedation, not loss of consciousness.
- **For us:** PCI-lz moves with some GABA-A drugs and not others at similar sedation, a reminder that PCI tracks circuit pharmacology as well as consciousness. Relevant to how we grade PCI-based constraints in the ledger.
- **Touches:** constraint_ledger

### Pharmacological treatments in disorders of consciousness

Saleh C, Seyfzadeh F, Szymkowicz E, Alnagger N, Ilia TS, Oancea AA, Gosseries O (2026). *Brain Communications*. [doi:10.1093/braincomms/fcag369](https://doi.org/10.1093/braincomms/fcag369). Review, abstract only, **context**.

- **Question:** What drugs help recovery of consciousness in DoC?
- **Idea tested:** Narrative review.
- **Data and method:** Dopaminergic, GABAergic and other agents; RCTs and lower-class evidence.
- **Results:** Improvements are inconsistent; 12 of 22 RCTs (about 55%) had some concerns or high risk of bias. (abstract only)
- **Limits:** Narrative.
- **For us:** Context.

### Resting-state functional MRI and clinical outcomes after acute disorders of consciousness: a systematic review

Kazazian K, Czink D, Iansavitchene A, Owen AM, Norton L (2026). *Neurology*. [doi:10.1212/wnl.0000000000218674](https://doi.org/10.1212/wnl.0000000000218674). Review, abstract only, **context**.

- **Question:** Does resting fMRI in the acute phase predict outcome after severe brain injury?
- **Idea tested:** Systematic review.
- **Data and method:** 30 of 396 screened studies; 800 patients.
- **Results:** Default mode (20 studies) and executive control networks (11) were most assessed. (abstract only)
- **Limits:** Abstract truncated before conclusions.
- **For us:** Context.

### Spatial spectral narrowing in the corticothalamic neural field model across consciousness states

Sarker RC, Hye MA (2026). *Biological Cybernetics*. [doi:10.1007/s00422-026-01053-5](https://doi.org/10.1007/s00422-026-01053-5). Paper, abstract only, **context**.

- **Question:** Does the corticothalamic model predict a spatial signature of consciousness states?
- **Idea tested:** Analyse the model's spatial noise spectrum across fitted states.
- **Data and method:** Robinson model parameters for wake, eMCS, MCS, N3 and UWS.
- **Results:** Spatial spectral centroid fell by 48% from wake to UWS; no Turing instability in any state. (abstract only)
- **Limits:** Model only; offers predictions, not data.
- **For us:** A testable prediction on high-density data: spatial-frequency content should narrow from wake to N3. Could be scored as one more state-axis measure on Sleep-EDF/BOAS; not an experience marker.
- **Touches:** Study 2

### Thalamic modulation of cortical linearity across arousal states

Müller EJ, Munn BR, Baracchini G, Fulcher BD, et al. (2026). *Science Advances 12(38):eaef5358*. [doi:10.1126/sciadv.aef5358](https://doi.org/10.1126/sciadv.aef5358). Paper, abstract only, **context**.

- **Question:** Does the thalamus regulate how linear or nonlinear cortical dynamics are?
- **Idea tested:** A time-resolved linearity measure should fluctuate along a thalamic axis and fall with lost arousal.
- **Data and method:** Human fMRI and electrophysiology, macaque recordings, pharmacological ablation of arousal and thalamic stimulation.
- **Results:** Awake cortex showed irregular linearity fluctuations following a thalamic anatomical axis; they diminished when arousal was pharmacologically ablated and recovered with thalamic stimulation. (abstract only)
- **Limits:** An arousal measure by construction.
- **For us:** Linearity is another candidate for the arousal axis; it should be scored on Study 2, not claimed as an experience marker.
- **Touches:** Study 2

### The diagnostic and prognostic value of auditory statistical learning ability in patients with disorders of consciousness

Yu M, Xiao X, Ding J, Zhao M, Cruz S, Hu N, Zhang M, Laureys S, Di H, Chen Y (2026). *Frontiers in Neurology*. [doi:10.3389/fneur.2026.1841501](https://doi.org/10.3389/fneur.2026.1841501). Paper, abstract only, **context**.

- **Question:** Is neural tracking of statistical regularities preserved in DoC and does it predict outcome?
- **Idea tested:** Frequency-tagged entrainment to trisyllabic pseudowords indexes residual cognition.
- **Data and method:** EEG in 46 patients and 25 controls.
- **Results:** Controls and MCS showed the learning effect, UWS did not; the effect predicted behavioural scores in MCS and 6-month outcome in traumatic patients. (abstract only)
- **Limits:** Small; task-based.
- **For us:** Context.
- **Touches:** Study 2

### Decoding EEG Bifurcation Dynamics Around Visual Detection Threshold in No-Report

Nicolacoudis A (2025). *Reed College BA thesis (advisor M Pitts)*. [doi:](https://www.reed.edu/psychology/scalp/thesis/files/Nicolacoudis_Thesis_Final_2025.pdf). Thesis, full text, **context**.

- **Question:** Do EEG decoding dynamics bifurcate around detection threshold without report?
- **Idea tested:** New experiment from the same lab: gratings varying in contrast, no masks, report and no-report.
- **Data and method:** EEG, new data (not the Cohen 2024 set).
- **Results:** Argues that the across-SOA VAN analysis in Cohen 2024 was hindered by overlap with mask responses, which motivated a mask-free design.
- **Limits:** Undergraduate thesis, not peer reviewed; different stimuli.
- **For us:** Supports holding the stimulus fixed (one SOA) rather than comparing across SOAs; does not pre-empt our test.
- **Touches:** cohen-fixed-soa

### Neural activity patterns stabilize during wakefulness and conscious experience

van Gaal S (2025). *PLOS Biology*. [doi:10.1371/journal.pbio.3003252](https://doi.org/10.1371/journal.pbio.3003252). Paper, full text, **context**.

- **Question:** Is stable neural activity a common marker of wakefulness and of conscious content?
- **Idea tested:** Primer on Leung et al.'s preregistered fly study (>7,700 time-series markers across wake, sleep and anaesthesia), linked to human stability findings (King, Schurger).
- **Data and method:** Commentary; fly LFP study plus human MEG literature.
- **Results:** Autocorrelation (stable, consistent processing) best marks loss of consciousness in flies; argues stable, sustained patterns are a cross-species marker of arousal and conscious content, plausibly from long-range recurrence.
- **Limits:** Commentary; does not address whether stability measures are confounded by evoked amplitude or SNR.
- **For us:** Shows how widely 'stability' is now used as a marker, which raises the value of a specificity test.
- **Touches:** stability_specificity

### Spatiotemporal brain complexity quantifies consciousness outside of perturbation paradigms

Breyton M et al. (2025). *eLife*. [doi:10.7554/eLife.98920](https://doi.org/10.7554/eLife.98920). Journal article, abstract only, **context**.

- **Question:** Can model-based fluidity track consciousness without TMS?
- **Idea tested:** Whole-brain modelling with fluidity metrics, 15 anaesthesia subjects.
- **Data and method:** Whole-brain modelling with fluidity metrics, 15 anaesthesia subjects.
- **Results:** Fluidity tracks propofol, xenon and ketamine and agrees with PCI.
- **Limits:** No sleep.
- **For us:** Context for spontaneous-activity complexity measures.
- **Touches:** Task #5 transfer

### The P50 predicts conscious perception under tactile but not electrical somatosensory stimulation in human EEG

Förster J, Vardiero G, Nierhaus T, Blankenburg F (2025). *bioRxiv*. [doi:10.1101/2025.02.28.640811](https://doi.org/10.1101/2025.02.28.640811). Preprint, abstract only, **context**.

- **Question:** Which early somatosensory ERP components predict whether a near-threshold touch is consciously perceived?
- **Idea tested:** Compare mechanical tactile with electrical stimulation.
- **Data and method:** EEG, near-threshold somatosensory detection, tactile and electrical stimulation.
- **Results:** Per the title, the P50 predicts conscious perception under tactile but not electrical stimulation; our prior-art read also reports N80, P100 and N140 effects and a persisting P300 difference (secondary summary, not checked against the text).
- **Limits:** Preprint, not peer reviewed; we read only the title and a secondary summary.
- **For us:** Early tactile components are candidate positive controls for a ds001785 screen.
- **Touches:** hypothesis-generator

### Dynamical structure-function correlations provide robust and generalizable signatures of consciousness in humans

Castro P, Luppi A, Tagliazucchi E, Perl YS, et al. (2024). *Communications Biology*. [doi:10.1038/s42003-024-06858-3](https://doi.org/10.1038/s42003-024-06858-3). Article, abstract only, **context**.

- **Question:** Do whole-brain fMRI dynamics give a signature of unconsciousness that holds across anaesthesia and deep sleep?
- **Idea tested:** They clustered transient functional-connectivity states in resting fMRI across anaesthesia and slow-wave sleep.
- **Data and method:** Resting fMRI; dynamic FC clustering; entropy of state transitions.
- **Results:** Unconsciousness is dominated by one recurrent pattern tied to structural connectivity, with fewer transitions; rich dynamics (entropy) go with consciousness.
- **Limits:** fMRI, not EEG; abstract only read here.
- **For us:** Cross-state generalisation has been done in fMRI. Our open EEG data cannot copy this, but it sets the bar for 'generalises across states'.
- **Touches:** Hypothesis tournament

### The temporal asymmetry of cortical dynamics as a signature of brain states

Camassa A et al. (2024). *Sci Rep*. [doi:10.1038/s41598-024-74649-1](https://doi.org/10.1038/s41598-024-74649-1). Journal article, abstract only, **context**.

- **Question:** Does irreversibility index brain state?
- **Idea tested:** Rat field potentials across anaesthesia depth and sleep.
- **Data and method:** Rat field potentials across anaesthesia depth and sleep.
- **Results:** Irreversibility lowest in deep anaesthesia and slow-wave sleep.
- **Limits:** Rat only; abstract read.
- **For us:** Source of the ne2 form we tested on human scalp EEG (atlas).
- **Touches:** Task #5 transfer

### Consciousness among delta waves: a paradox?

Frohlich et al. (2021). *Brain 144:2257-2277*. [doi:10.1093/brain/awab095](https://doi.org/10.1093/brain/awab095). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C42 (state).
- **Results:** High-amplitude delta waves usually come with loss of consciousness, but people with Angelman syndrome, some seizures, and some drug states are conscious with prominent delta.
- **Limits:** Frohlich, Toker & Monti 2021 review. Large EEG change without loss of consciousness.
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C42

### Does the Prefrontal Cortex Play an Essential Role in Consciousness? Insights from Intracranial Electrical Stimulation of the Human Brain

Raccah et al. (2021). *The Journal of Neuroscience 41:2076-2087*. [doi:10.1523/JNEUROSCI.1141-20.2020](https://doi.org/10.1523/JNEUROSCI.1141-20.2020). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C11 (stimulation).
- **Results:** Stimulating lateral prefrontal cortex seldom changes experience; orbitofrontal and anterior cingulate stimulation often does.
- **Limits:** Raccah, Block & Fox 2021 synthesis of iES studies; authors are critics of prefrontal theories. Absence of reported change may reflect what patients notice and report.
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C11

### Graded Visual Consciousness During the Attentional Blink

Eiserbeck A, Enge A, Rabovsky M, Abdel Rahman R (2021). *bioRxiv*. [doi:10.1101/2021.01.15.426792](https://www.biorxiv.org/content/10.1101/2021.01.15.426792.full). Preprint, full text, **context**.

- **Question:** Is awareness in the attentional blink graded when measured with the Perceptual Awareness Scale?
- **Idea tested:** Attentional blink with a 4-point PAS rating on each trial.
- **Data and method:** Behaviour and EEG, 32 people; data on OSF e85hn (CC BY 4.0).
- **Results:** The authors describe awareness as graded; they ran no formal mixture test.
- **Limits:** Only two lags plus target-absent, and 4 rating categories, so a conditional-independence test has very little power (7-33% in our planning agent's simulation).
- **For us:** The only open blink set with trial-wise ratings found; too few strength levels for a decisive test.
- **Touches:** Fable#13 item 4, all-or-none vs graded

### ERP and MEG correlates of visual consciousness: the second decade

Förster J, Koivisto M, Revonsuo A (2020). *Consciousness and Cognition*. [doi:10.1016/j.concog.2020.102917](https://doi.org/10.1016/j.concog.2020.102917). Review, abstract only, **context**.

- **Question:** What has a decade of ERP and MEG work found about correlates of visual awareness?
- **Idea tested:** Narrative review.
- **Data and method:** Review.
- **Results:** Favours the visual awareness negativity (VAN) over the late positivity as the correlate of visual awareness.
- **Limits:** Narrative, not a meta-analysis; Hutchinson et al. 2026 is the quantitative follow-up.
- **For us:** Background for which components count as established.
- **Touches:** hypothesis-generator

### A fast and general method to empirically estimate the complexity of brain responses to transcranial and intracranial stimulations

Comolatti R, Pigorini A, Casarotto S, Fecchio M, Faria G, Sarasso S, Rosanova M, Gosseries O, Boly M, Bodart O, Ledoux D, Brichant JF, Nobili L, Laureys S, Tononi G, Massimini M, Casali AG (2019). *Brain Stimulation 12:1280-1289*. [doi:10.1016/j.brs.2019.05.013](https://doi.org/10.1016/j.brs.2019.05.013). Paper, abstract only, **context**.

- **Question:** Can PCI be computed quickly without source modelling?
- **Idea tested:** State-transition PCI (PCIst) on principal components of the evoked response.
- **Data and method:** TMS-EEG and intracranial stimulation datasets.
- **Results:** PCIst reproduced PCI's separation of conscious and unconscious conditions at a fraction of the cost.
- **Limits:** Needs perturbation data.
- **For us:** The PCI variant cited by Newman 2026 and Maschke 2024 in our news.
- **Touches:** constraint_ledger

### Assessing recognition memory using confidence ratings and response times

Weidemann CT, Kahana MJ (2016). *Royal Society Open Science 3, 150670*. [doi:10.1098/rsos.150670](https://doi.org/10.1098/rsos.150670). Paper, abstract only, **context**.

- **Question:** Can response times stand in for confidence ratings?
- **Idea tested:** Compared RTs and confidence ratings as measures of recognition-memory decisions.
- **Data and method:** Behaviour, own data.
- **Results:** Much of the information in confidence ratings can be recovered from response times.
- **Limits:** Recognition memory, not perception; RT is a noisy proxy at the single-trial level.
- **For us:** Supports RT as a weak confidence proxy in the Cohen data, which recorded no confidence.
- **Touches:** cohen-fixed-soa

### General Markers of Conscious Visual Perception and Their Timing

Rutiku R, Aru J, Bachmann T (2016). *Frontiers in Human Neuroscience*. [doi:10.3389/fnhum.2016.00023](https://doi.org/10.3389/fnhum.2016.00023). Paper, abstract only, **context**.

- **Question:** How variable are the onset times of EEG markers of conscious perception within one study?
- **Idea tested:** Seen vs unseen contrasts on 100 balanced subsets of heterogeneous threshold-contrast stimuli.
- **Data and method:** Human EEG, threshold-contrast visual stimuli.
- **Results:** N200 and P300 are the reliable general markers; their onset varies strongly across subsets; they argue that unseen-trial instability (Schurger 2015) changes how seen/unseen contrasts behave.
- **Limits:** Raises the stability-comparison worry but does not test whether stability differences reduce to amplitude or SNR.
- **For us:** Prior statement of the concern our injection test settles.
- **Touches:** stability_specificity

### Pre-target oscillatory brain activity and the attentional blink

Petro NM, Keil A (2015). *Experimental Brain Research*. [doi:10.1007/s00221-015-4418-2](https://doi.org/10.1007/s00221-015-4418-2). Paper, abstract only, **context**.

- **Question:** Do pre-target alpha and ssVEP phase locking differ between correctly and incorrectly reported T2?
- **Idea tested:** Pre-T1 alpha power and ssVEP inter-trial phase locking, correct vs incorrect trials, word RSVP.
- **Data and method:** Human EEG.
- **Results:** Incorrect trials: lower alpha power and greater ssVEP phase locking long before T1.
- **Limits:** Abstract only; pre-T1 window, which our T2-locked epochs do not cover.
- **For us:** Same direction as Zauner but before T1; our test is at T2.
- **Touches:** rhythm_blink

### Endogenous and rapid serial visual presentation-induced alpha band oscillations in the attentional blink

Janson J, De Vos M, Thorne JD, Kranczioch C (2014). *Journal of Cognitive Neuroscience*. [doi:10.1162/jocn_a_00551](https://doi.org/10.1162/jocn_a_00551). Paper, abstract only, **context**.

- **Question:** Are alpha effects in the blink endogenous alpha or the stream's steady-state response?
- **Idea tested:** Blink paradigms with and without 12 Hz pre-target distracter streams; alpha power and intertrial coherence.
- **Data and method:** Human EEG.
- **Results:** Streams raise coherence and lower power; ssVEP-related power tended to be higher when both targets were detected, endogenous alpha lower.
- **Limits:** Abstract only; trends.
- **For us:** Separates steady-state from endogenous alpha; an opposite-direction trend to Zauner.
- **Touches:** rhythm_blink

### Subjective visibility depends on level of processing

Windey B, Gevers W, Cleeremans A (2013). *Cognition 129(2)*. [doi:10.1016/j.cognition.2013.07.012](https://axc.ulb.be/uploads/2015/11/13-cognition.pdf). Paper, full text, **context**.

- **Question:** Is visibility more all-or-none for high-level than low-level tasks?
- **Idea tested:** The same masked stimuli at 8 durations, judged on either a number (high-level) or a colour (low-level) task, with visibility ratings.
- **Data and method:** Behaviour, 20 people.
- **Results:** The visibility curve was steeper for the number task than for the colour task: more step-like at the higher level.
- **Limits:** A steeper curve is not proof of two states; no mixture test.
- **For us:** The level-of-processing view predicts the answer depends on the task, which weakens all-or-none vs graded as a clean theory test.
- **Touches:** Fable#13 item 4, all-or-none vs graded

### Surge of neurophysiological coherence and connectivity in the dying brain

Borjigin et al. (2013). *Proceedings of the National Academy of Sciences 110:14432-14437*. [doi:10.1073/pnas.1308285110](https://doi.org/10.1073/pnas.1308285110). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C56 (state).
- **Results:** In dying rats, a short surge of coherent gamma activity occurs within 30 s of cardiac arrest.
- **Limits:** Borjigin 2013, rats. No link to experience is measurable here; listed because it is a large activity change with unknown experience.
- **For us:** Evidence grade C in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C56

### Local sleep in awake rats

Vyazovskiy et al. (2011). *Nature 472:443-447*. [doi:10.1038/nature10009](https://doi.org/10.1038/nature10009). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C44 (state).
- **Results:** Parts of an awake brain can go briefly 'offline' with local slow waves while the animal is awake and behaving.
- **Limits:** Vyazovskiy 2011 in rats (performance dropped). Human evidence is one intracranial case of confusional arousal (Terzaghi 2009).
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C44

### Neural “Ignition”: Enhanced Activation Linked to Perceptual Awareness in Human Ventral Stream Visual Cortex

Fisch L, Privman E, Ramot M, et al. (2009). *Neuron*. [doi:10.1016/j.neuron.2009.11.001](https://doi.org/10.1016/j.neuron.2009.11.001). Paper, full text, **context**.

- **Question:** Do ventral visual responses to masked images show an all-or-none jump with recognition?
- **Idea tested:** Intracranial recordings during backward masking at several SOAs, split by recognition.
- **Data and method:** Human iEEG (epilepsy patients).
- **Results:** Recognized trials show a sharp, sustained gamma increase ('ignition') in high-order visual cortex; unrecognized trials do not.
- **Limits:** Clinical sample; electrode coverage varies.
- **For us:** Background for the single-trial reading of SOA curves; no critique of the psychometric criterion.
- **Touches:** psychometric_criterion

### Temporal dynamics of access to consciousness in the attentional blink

Kranczioch C, Debener S, Maye A, Engel AK (2007). *NeuroImage*. [doi:10.1016/j.neuroimage.2007.05.044](https://doi.org/10.1016/j.neuroimage.2007.05.044). Paper, abstract only, **context**.

- **Question:** Which oscillatory dynamics go with detected vs missed T2?
- **Idea tested:** Time-frequency EEG analysis of the attentional blink.
- **Data and method:** EEG time-frequency, attentional blink.
- **Results:** Detected T2 goes with more fronto-parietal beta and less alpha synchrony, and lower pre-T1 alpha (via secondary citations).
- **Limits:** The sign of prestimulus alpha is contested (Petro and Keil 2015; MacLean and Arnell 2011), and the RSVP rate is in the alpha band.
- **For us:** Prestimulus alpha should be left unsigned in a ds001810 screen.
- **Touches:** hypothesis-generator

### Electrophysiological evidence for a postperceptual locus of suppression during the attentional blink

Vogel EK, Luck SJ, Shapiro KL (1998). *Journal of Experimental Psychology: Human Perception and Performance*. [doi:10.1037/0096-1523.24.6.1656](https://doi.org/10.1037/0096-1523.24.6.1656). Paper, abstract only, **context**.

- **Question:** Where in processing does the attentional blink act?
- **Idea tested:** Compare ERP components across lags.
- **Data and method:** ERPs across lags in the attentional blink.
- **Results:** P1, N1 and N400 survive the blink while the P3 is suppressed (from memory, via our prior-art read).
- **Limits:** Compares lags, not seen vs missed.
- **For us:** Background for which ERPs should not differ in a T2 identification contrast.
- **Touches:** hypothesis-generator

## Sleep and dreams (22)

### Cross-Laboratory Validation of EEG Classification of Reported Dream Experience

Bazán Sánchez JE (2026). *ResearchGate preprint (2 Aug 2026), UNAM*. [doi:10.13140/RG.2.2.14388.00642](https://doi.org/10.13140/RG.2.2.14388.00642). Preprint, abstract only, **core**.

- **Question:** Does the DREAM paper's EEG classifier of reported experience (Figure 5) transfer between laboratories?
- **Idea tested:** Re-run the DREAM Figure 5 workflow (spectral power and catch22 features) and split its accuracy into record-wise, participant-held-out, within-lab and lab-held-out parts, with a lab-prevalence-only baseline and a lab-identity decoder.
- **Data and method:** 1,065 reports from the five DREAM collections enumerated by DREAM's released experienceclassification code; NREM spectral power and REM catch22 classifiers.
- **Results:** Record-wise AUROC 0.569 (NREM spectral) and 0.636 (REM catch22). Participant-held-out pooled 0.534 and 0.629. Within the same lab (site-conditioned) 0.498 and 0.498. Lab-held-out macro AUROC 0.493 and 0.470. A baseline that knows only each lab's report prevalence reaches 0.564 and 0.687 pooled. Lab identity is decoded from the same EEG features at macro AUROC 0.808-0.953. Conclusion: pooled discriminability is real but no common EEG marker transports between labs.
- **Limits:** Numbers from the abstract as read in the full text by the coordinator in a browser; our automated fetch was blocked by ResearchGate (403) and not worked around. Generic features (spectra, catch22), NREM pooled across stages as in DREAM Figure 5; no hypothesis-driven consciousness markers, no within-person N2-only analysis reported in the abstract. Single author, not peer reviewed.
- **For us:** Pre-empts #42's cross-lab spectral test and its planned headline contrast (pooled AUC driven by lab and between-person differences). Together with the Michalak within-person null (amendment 5) and our Tononi delta result, the spectral arm of #42 is no longer new. Anything left is within-person, N2-only, cross-lab tests of hypothesis-driven markers, with bounds: atlas material.
- **Touches:** #42

### Immersive NREM2 dreaming preserves subjective sleep depth against declining sleep pressure

Michalak A, Marzoli D, Pietrogiacomi F, Bergamo D, Elce V, Pedreschi B, Mosca G, Navari A, et al. (2026). *PLoS Biology 24(3):e3003683*. [doi:10.1371/journal.pbio.3003683](https://doi.org/10.1371/journal.pbio.3003683). Paper, full text, **core**.

- **Question:** How do cortical activation and the kind of dream relate to how deeply people feel they slept?
- **Idea tested:** Feeling of deep sleep is usually read as unconsciousness; immersive dreaming might instead keep sleep feeling deep.
- **Data and method:** Two N2 serial-awakening experiments at IMT Lucca, four nights each, high-density EEG; 1,024 N2 awakenings with reports, sleep-depth and sleepiness ratings. Five report classes (experience with recall, rich and simple experience without recall, experience of sleep, unconsciousness). Channel-wise delta and gamma power and their ratio.
- **Results:** Deeper perceived sleep went with lower high-to-low frequency power ratio, and this link weakened when a dream was present. The immersive quality of the experience was tied to perceived depth whether or not content was recalled. Data and code are open: Zenodo 10.5281/zenodo.15372992 (CC BY 4.0) holds a per-awakening table of channel-wise delta and gamma power plus the cluster statistics (derivatives 180 MB), not raw EEG.
- **Limits:** Derived spectral features only, so complexity or connectivity markers cannot be computed. One lab. Report categories differ from DREAM's three-way coding.
- **For us:** New open data for #42: an eighth, never-touched lab with 1,024 N2 awakenings. It can test the spectral side only (does posterior gamma/delta separate experience from unconsciousness at N2 in a new lab?). That is a direct out-of-lab check on the spectral baseline that Selte 2026 implies may already be strong. Needs a sealed amendment before anyone opens the labels.
- **Touches:** #42, #22

### Neural correlates of dreaming during N2 sleep: spatial and phenomenological characteristics

Rochas V, Mammeri K, Bayer L, Tononi G, Perogamvros L (2026). *PsyArXiv (v4, 2 Nov 2026)*. [doi:10.31234/osf.io/qbwnf_v4](https://doi.org/10.31234/osf.io/qbwnf_v4). Preprint, abstract only, **core**.

- **Question:** Where and when does N2 EEG differ between awakenings with and without a dream, and does it track the kind of experience?
- **Idea tested:** Extend the posterior hot-zone finding to a larger N2 sample with source localisation, and split experience into perceptual and thought-like dimensions.
- **Data and method:** 256-electrode EEG with source localisation, serial awakenings in N2, 39 participants; several pre-awakening windows; continuous ratings of perceptual and thought-related experience.
- **Results:** Experience with recall vs no experience went with higher beta/gamma over a wide cortical area, peaking in posterior occipito-temporal cortex for the 30 s window and in parietal cortex for the 20 s window. Thought-related ratings, not perceptual ones, were associated with EEG activity. (abstract only)
- **Limits:** Abstract only. One lab, 39 people, no held-out test. The preprint's title and framing changed across versions (v1 'The neural generators of perceptual experiences during sleep', v2 'Content-specific and temporally evolving neural correlates'), so the analysis path may have moved.
- **For us:** Our #42 window is the last 20 s, which is where they place the effect over parietal cortex; their high-frequency effect is exactly what our frozen spectral baseline (with 20-50 Hz power) should absorb. If DREAM packages carry content ratings, 'thought vs perception' could become a sealed secondary label in a later study, not this one.
- **Touches:** #42, #6

### Neural signatures of conscious experience during sleep: a serial awakening study using high-density EEG

Selte A, Haworth SE, Vanasse TJ, Alauddin T, Gjini K, Philibert-Rosas S, Brace C, Sevak B, Riedner B, Kalkach-Aparicio M, Tononi G, Boly M, Struck AF (2026). *bioRxiv (20 Aug 2026)*. [doi:10.64898/2026.08.16.745040](https://doi.org/10.64898/2026.08.16.745040). Preprint, abstract only, **core**.

- **Question:** Can EEG from the minute before an NREM awakening tell whether the sleeper will report a dream?
- **Idea tested:** Dreaming should show as a posterior shift in spectral balance and in network organisation, as the posterior hot-zone account predicts.
- **Data and method:** Overnight 256-electrode EEG in 140 participants, serial awakenings; 699 N2 and N3 awakenings (351 experience, 348 no experience). Features from the 60 s before waking: regional spectral power, lagged coherence, graph metrics, gamma-to-alpha ratios. Participant-level cross-validated classifiers.
- **Results:** Dreaming went with lower posterior alpha and delta power and higher gamma-related measures. All classifiers beat chance; the best ensemble reached ROC-AUC 0.80 and average precision 0.80. (abstract only)
- **Limits:** Abstract only: the bioRxiv full text was not reachable without getting around a bot block. N2 and N3 are pooled, so sleep depth can carry part of the signal: in another serial-awakening cohort no-experience reports were 50% of N3 but 21.9% of N2 awakenings (Bertoni 2026). One lab, no cross-lab test, no spectral-baseline nesting, no surrogate gate. Licence is no-reuse; data availability not stated in the abstract.
- **For us:** This is the strongest claim yet against our 'markers fail on experience' outcome. Our #42 design holds stage fixed (N2), holds labs out and nests every marker in the frozen spectral baseline, so it answers the question this paper leaves open: does the 0.80 survive stage control and a new lab? Report the spectral baseline's own experience AUC as a headline number, because if it is near 0.80 the 'bounded below 0.60' negative applies only to non-spectral markers. Check whether this cohort contains the 39 Wisconsin subjects of the DREAM Tononi set (same lab); that set is already in our exposed tier.
- **Touches:** #42, #22, #6, t1_dream

### A dream EEG and mentation database (DREAM)

Wong W, Herzog R, Andrade KC, Andrillon T and others; senior author Tsuchiya N (2025). *Nature Communications 16, 7495*. [doi:10.1038/s41467-025-61945-1](https://doi.org/10.1038/s41467-025-61945-1). Dataset, full text, **core**.

- **Question:** Twenty sleep studies pooled their brain recordings with what people said they were dreaming when woken up: 505 people, 2,643 awakenings.
- **Data and method:** Initial release: 20 datasets, 505 participants, 2,643 awakenings; each has sleep M/EEG (>= 20 s, >= 100 Hz, >= 2 electrodes) up to waking plus a standardised report class. Experience vs no experience decoded from EEG over 200 random train-test splits against a label-shuffled null: NREM best with spectral power features (mean AUC 0.586, 5th-95th percentile 0.505-0.608); REM best with catch22 features (mean AUC 0.700, 0.663-0.731). Six datasets used for these analyses. Registry open (doi:10.26180/22133105); dataset packages either open access or by request from the contributor. Main text does not say whether splits held out whole subjects.
- **Results:** When you wake someone in the night and ask what was going through their mind, sometimes they report a dream and sometimes nothing. Single labs could only collect a few hundred of these. This database pools them, so we can ask, with far more data, whether brain signals before waking predict a dream report.
- **For us:** The key resource for our dream vs no-dream test (task #6). Their AUCs are the bar to beat, but we split by subject and lab, so our numbers may come out lower.
- **Touches:** news

### A repeated awakening study exploring the capacity of complexity measures to capture dreaming during propofol sedation

Bajwa IJ, Nilsen AS, Skukies R, Aamodt A, Ernst G, Storm JF, Juel BE (2025). *Scientific Reports (data: OpenNeuro ds005620)*. [doi:10.1038/s41598-025-12695-z](https://doi.org/10.1038/s41598-025-12695-z). Paper, abstract only, **core**.

- **Question:** Brain complexity dropped under sedation, but did not differ between people who said they had been dreaming and people who said they had not.
- **Data and method:** 20 healthy participants, propofol, resting EEG and TMS-EEG (PCIst) plus single-channel LZc. 52 attempted awakenings: 24 experience, 5 no experience, 23 unarousable or uninformative. Both measures fell from wake to sedation; no evidence of a difference between experience and no-experience awakenings within sedation (linear mixed models). Data: OpenNeuro ds005620 v1.0.0, CC0, 21 subjects, 83.0 GB in full (OpenNeuro metadata).
- **Results:** Twenty volunteers were sedated and woken several times to ask whether they had experienced anything. Complexity measures fell with sedation as expected. But they did not tell 'I was dreaming' from 'nothing' within sedation. Only 5 wakings gave a clear 'nothing', so the test could only have caught a large difference.
- **For us:** One of our L2 datasets. The full set is far over our 1.5 GB budget; we fetch only the pre-awakening sedation files per subject. The 5 no-experience awakenings make it weak alone for dream vs no-dream; pool with DREAM.
- **Touches:** news

### From high- to low-density EEG for automatic classification of dream experiences during stage 2 of NREM

Moctezuma LA, Molinas M, Abe T (2025). *Sleep Advances 6:zpaf066*. [doi:10.1093/sleepadvances/zpaf066](https://doi.org/10.1093/sleepadvances/zpaf066). Paper, full text, **core**.

- **Question:** Can machine learning classify N2 dream vs no-dream awakenings from EEG, and with how few channels?
- **Idea tested:** Train classifiers on 256-channel EEG and prune channels.
- **Data and method:** DREAM Tononi serial-awakening set (doi 10.26180/23306054.v2): 261 N2 reports (110 experience, 101 no experience, 50 experience without recall), 2 min before waking. 70/30 split and 10-fold cross-validation over awakenings; KNN.
- **Results:** Accuracy up to 0.94 and ROC-AUC 0.97; performance held with 30-40 channels. Experience-without-recall awakenings were classed as experience 0.698 of the time.
- **Limits:** Splits are over awakenings, not subjects, so a person's EEG signature can sit in both train and test. The near-perfect AUC is very likely inflated by subject leakage; compare Wong 2025 (AUC 0.59 in NREM, held out) and the authors' own leave-one-subject-out failure in Moctezuma 2025 (BMRI).
- **For us:** A ready red-team example for #42: rerun this pipeline subject-held-out on the Tononi set (exposed tier) to show how much of 0.97 is leakage. It also supports our rule that no awakening-level split is ever reported.
- **Touches:** #42, #22, #14

### The Dream Catcher experiment: blinded analyses failed to detect markers of dreaming consciousness in EEG spectral power

Wong W, Noreika V, Móró L, Revonsuo A, Windt J, Valli K, Tsuchiya N (2020). *Neuroscience of Consciousness*. [doi:10.1093/nc/niaa006](https://doi.org/10.1093/nc/niaa006). Article, abstract only, **core**.

- **Question:** Can a blinded team tell dreamful from dreamless NREM sleep from EEG alone?
- **Idea tested:** A Data Team collected serial-awakening polysomnograms and reports; a blinded Analysis Team classified each 1-min recording from hypothesis-driven EEG spectral-power and electrode-location features with an unsupervised classifier, over five rounds of gradually removed blindness.
- **Data and method:** 54 one-minute NREM polysomnograms from 9 participants: 27 dreamful, 27 dreamless, three of each per participant (a balanced, within-person design).
- **Results:** At no level of blindness did the Analysis Team classify better than chance.
- **Limits:** Very small (9 participants, 54 recordings), so only large effects are excluded; NREM stage not fixed to N2 in the abstract; unsupervised classifier. Licence CC BY 4.0.
- **For us:** Earliest blinded, within-person spectral null for dream experience in NREM. Prior art for the within-person spectral question #42 and the Michalak check (amendment 5) address; cite it alongside Bazán Sánchez 2026 and Aamodt 2023.
- **Touches:** #42

### Sleep-EDF Database Expanded (v1.0.0)

Kemp B, et al. (2018). *PhysioNet*. [doi:10.13026/C2X676](https://doi.org/10.13026/C2X676). Dataset, full text, **core**.

- **Question:** Open whole-night PSG with hypnograms.
- **Data and method:** 197 whole-night PSG recordings, ODC-By 1.0, 8.1 GB, per-file download.
- **Results:** Used in our sleep-stage analyses (LZ, slope, tra_x, ne2).
- **Limits:** Two EEG channels only; no dream reports.
- **For us:** Our main arousal-axis dataset; any new marker should be scored here first.
- **Touches:** Study 2, lz_slope, nonequilibrium

### Intra-thalamic coordination maintains arousability in slow-wave sleep

Han J, Xie Q, Huang Y, Li M, Hu X, Northoff G, Li Y, Zhang J, Qin P (2026). *bioRxiv (17 Nov 2026)*. [doi:10.64898/2026.11.15.766872](https://doi.org/10.64898/2026.11.15.766872). Preprint, abstract only, **useful**.

- **Question:** How do thalamic nuclei keep a sleeper wakeable during slow-wave sleep?
- **Idea tested:** A centromedian-VPL-pulvinar loop preserves arousability, unlike anaesthesia or UWS.
- **Data and method:** Six fMRI and EEG datasets spanning sleep, propofol and unresponsive wakefulness.
- **Results:** In N2/N3, CM and VPL showed convergent edge communities and more closed-loop intra-thalamic motifs, not seen under anaesthesia or UWS. CM->VPL->pulvinar connectivity rose in N3 and covaried with N3 delta power, which was higher before awakenings than before transitions to N2 and went with 3-month improvement in UWS. (abstract only)
- **Limits:** Abstract only; preprint; fMRI-heavy.
- **For us:** Arousability is a separate axis from experience. In #42, delta before waking is in the baseline; this paper suggests delta may index how close the sleeper is to waking, a covariate worth reporting.
- **Touches:** #42, Study 2

### Multisensory integration in peripersonal space indexes consciousness states in sleep and disorders of consciousness

Bertoni T, Ricci G, Jöhr J, Donno B, Cataldi J, et al. (2026). *Cell Reports Medicine 7:102705*. [doi:10.1016/j.xcrm.2026.102705](https://doi.org/10.1016/j.xcrm.2026.102705). Paper, full text, **useful**.

- **Question:** Does an EEG index of peripersonal-space processing track consciousness across wake, dreaming, dreamless sleep and brain injury?
- **Idea tested:** A minimal-self (body-space) index should be present whenever experience is, regardless of behaviour.
- **Data and method:** 256-channel EEG during an audiotactile near/far paradigm in wake and overnight with about 9 serial awakenings a night; then 72 DoC patients at the bedside.
- **Results:** A centro-parietal high-beta (20-30 Hz) index separated near from far stimuli in wake and in dreaming, not dreamless sleep. Experience reports rose from N3 (32.1%) to N2 (56.2%) to REM (87.9%); no-experience fell from N3 (50%) to N2 (21.9%) to REM (0%). In 72 patients, CRS-R plus the index predicted outcome with accuracy 0.85 (CRS-R alone 0.82).
- **Limits:** Stimulus-evoked, so not usable on spontaneous DREAM recordings. EEG data cannot be deposited. The stage-by-report table shows how strongly stage and report co-vary.
- **For us:** Its stage-by-report numbers are the cleanest argument for holding stage fixed in #42 (and the reason Selte 2026's pooled N2+N3 AUC may be inflated). A stimulus-based experience marker is out of scope for our spontaneous-EEG benchmark.
- **Touches:** #42, #6

### The neural basis of consciousness during evening naps measured by MEG: a registered report

Hemmi C, Leung A, Windt J, Motomura Y, et al. (2026). *PsyArXiv (27 Apr 2026)*. [doi:10.31234/osf.io/zgw6x_v1](https://doi.org/10.31234/osf.io/zgw6x_v1). Preprint, abstract only, **useful**.

- **Question:** Do the posterior low- and high-frequency correlates of dreaming from a landmark EEG study generalise to MEG during evening naps?
- **Idea tested:** A registered report: hypotheses about frontal and posterior low- and high-frequency power fixed before an independent team analyses the data.
- **Data and method:** MEG with targeted serial awakenings during naps; Stage 1 (protocol) accepted with pilot data from two participants.
- **Results:** In one pilot participant the low-frequency hypotheses held and the high-frequency ones did not; the other gave insufficient evidence. (abstract only)
- **Limits:** Stage 2 results not out yet. Naps, not full nights.
- **For us:** A pre-registered, independent replication of the same posterior signature our #42 spectral controls include. When Stage 2 appears, compare its effect sizes with ours.
- **Touches:** #42

### Unlocking dreams and dreamless sleep: machine learning classification with optimal EEG channels

Moctezuma LA, Molinas M, Abe T (2025). *BioMed Research International 2025:3585125*. [doi:10.1155/bmri/3585125](https://doi.org/10.1155/bmri/3585125). Paper, full text, **useful**.

- **Question:** Can EEG classify dream vs dreamless awakenings, and which channels matter?
- **Idea tested:** Common spatial patterns and wavelet features with KNN, then channel selection.
- **Data and method:** DREAM Zhang & Wamsley set: 58 channels, 28 subjects, REM and NREM awakenings.
- **Results:** Accuracies above 0.85 with pooled data; 8-10 channels looked sufficient. When one subject at a time was held out, the models failed to generalise to unseen subjects.
- **Limits:** The headline accuracy is not subject-held-out; the held-out result, which is the one that matters, is weak.
- **For us:** Independent evidence, on one of our exposed-tier labs, that dream decoding collapses under subject hold-out. Cite it next to Wong 2025 when stating priors for #42.
- **Touches:** #42, #22

### The neural correlates of dreaming

Siclari F, Baird B, Perogamvros L, Bernardi G, LaRocque JJ, Riedner B, Boly M, Postle BR, Tononi G (2017). *Nature Neuroscience 20, 872-878*. [doi:10.1038/nn.4545](https://doi.org/10.1038/nn.4545). Paper, abstract only, **useful**.

- **Question:** Less slow activity at the back of the brain marked dreaming in both kinds of sleep, and could predict a dream report in real time.
- **Data and method:** High-density EEG, serial awakenings. Dream reports in NREM and REM associated with local decreases in low-frequency activity in posterior cortex; high-frequency activity there correlated with specific dream contents; real-time monitoring predicted dream vs no-dream reports in NREM.
- **Results:** People were woken many times a night and asked if they had been dreaming. In both dreaming-heavy and dreaming-light stages of sleep, a dream report followed a drop in slow brain waves over a 'hot zone' at the back of the head. Watching that zone live predicted whether the sleeper would report a dream.
- **For us:** The sharpest within-stage test of a measure against report. The DREAM database (2025) lets us test whether it replicates across labs.
- **Touches:** news

### Abnormal local markers of sleep homeostasis in patients with focal epilepsy

Ciliento R, Sevak B, Papantonatos C, et al. (2026). *Brain Communications*. [doi:10.1093/braincomms/fcag294](https://doi.org/10.1093/braincomms/fcag294). Paper, abstract only, **context**.

- **Question:** Is sleep homeostasis altered in focal epilepsy?
- **Idea tested:** Slow-wave activity and slope should decline less overnight in epilepsy.
- **Data and method:** Overnight 256-electrode EEG in 39 patients and 48 matched controls.
- **Results:** Patients had higher slow-wave activity and steeper slopes; their end-of-night values resembled controls' start-of-night values. (abstract only)
- **Limits:** Clinical population.
- **For us:** Same group and EEG platform as Selte 2026; a hint that the Wisconsin/WashU overnight hd-EEG pool is large. Context.
- **Touches:** #42

### Brain network dynamics in the wake-sleep transition reorganize according to task engagement

Kumar SS, Arzi A, Bareham CA, Gonzalez-Castillo J, Fernandez I, Tagliazucchi E, Mediano PAM, Bandettini PA, Bekinschtein TA (2026). *Imaging Neuroscience*. [doi:10.1162/imag.a.1336](https://doi.org/10.1162/imag.a.1336). Paper, abstract only, **context**.

- **Question:** How do falling alertness and task engagement interact in shared circuits?
- **Idea tested:** Active engagement during drowsiness should recruit frontoparietal and sensory networks while thalamocortical sleep-onset changes continue.
- **Data and method:** EEG-fMRI, people drifting between alert and drowsy states during active or passive auditory tasks.
- **Results:** With falling alertness, passive listening raised parietal synchrony and thalamo-cortical synchrony; active engagement raised long-range frontoparietal synchrony and auditory-cortex coupling instead. (abstract only)
- **Limits:** fMRI-heavy.
- **For us:** Context for sleep-onset (N1) analyses; our #34 sleep-onset sign-flip theory could cite it.
- **Touches:** #34

### EEG microstates reveal distinct network dynamics in lucid and non-lucid REM sleep

Wang X, Peters E, Strelen J, Lockhart N, Franklin M, LaBerge S, Koenig T, Dresler M, Erlacher D (2026). *Consciousness and Cognition*. [doi:10.1016/j.concog.2026.104047](https://doi.org/10.1016/j.concog.2026.104047). Paper, abstract only, **context**.

- **Question:** Do EEG microstates differ between lucid and non-lucid REM?
- **Idea tested:** Lucidity should shift large-scale network states towards metacognitive ones.
- **Data and method:** EEG microstate analysis of lucid vs non-lucid REM.
- **Results:** Microstates A and G dominated lucid REM; B, C and D were reduced. (abstract only)
- **Limits:** Sample size not in the abstract; lucidity is a content change, not presence vs absence of experience.
- **For us:** Context only.
- **Touches:** #42

### Sleep homeostasis has circaseptan and circatrigintan cycles over year-long timescales

Vashin V, Magana-Tellez O, Ahrens E, Mosher JC, Lacuey N, Tallavajhula S, Schiess M, Dabaghian Y, Boly M, Duun-Henriksen J, Lhatoo S (2026). *Journal of Sleep Research*. [doi:10.1111/jsr.70487](https://doi.org/10.1111/jsr.70487). Paper, abstract only, **context**.

- **Question:** How does nightly slow-wave decline vary over a year?
- **Idea tested:** Subscalp EEG allows months of continuous recording.
- **Data and method:** Subscalp EEG in 20 healthy adults for 12-15 months.
- **Results:** SWA slope was negative in all subjects; about 7-day and 28-day rhythms appeared in most. (abstract only)
- **Limits:** Small; device-specific.
- **For us:** Context.

### Using real-time reporting to investigate visual experiences in dreams

Konkoly KR, Al-Youssef S, Mazurek CY, Mallett R, Morris DJ, Gales A, Arnulf I, Oudiette D, Paller KA (2026). *Journal of Cognitive Neuroscience 38(2)*. [doi:10.1162/jocn.a.107](https://doi.org/10.1162/jocn.a.107). Paper, abstract only, **context**.

- **Question:** Do lucid dreamers' signalled visual experiences line up with alpha power as in waking?
- **Idea tested:** Real-time sniff signals during REM avoid the distortion of reports given after waking.
- **Data and method:** 13 lucid dreamers (4 with narcolepsy); 150 signals over 19 sessions from 11 people.
- **Results:** No robust alpha increase after signalled dream eye closure; dream eye closure faded visual content only about half the time. (abstract only)
- **Limits:** Very small n; lucid REM only.
- **For us:** A reminder for #42's stated limit (report is not experience): post-waking reports are coarse. Not usable data for us.
- **Touches:** #42

### Increased intra-thalamic and thalamo-cortical functional connections during human REM sleep: a two-night EEG-fMRI study

Yang FN, Picchioni D, de Zwart JA, van Gelderen P, Duyn JH (2025). *Imaging Neuroscience*. [doi:10.1162/imag.a.1026](https://doi.org/10.1162/imag.a.1026). Paper, abstract only, **context**.

- **Question:** How does the thalamus connect to sensory networks during REM, when vivid dreams occur?
- **Idea tested:** Phasic REM, linked to vivid dreaming, should show more thalamic broadcasting than tonic REM.
- **Data and method:** Whole-night EEG-fMRI in 12 participants; HMM split of phasic and tonic REM.
- **Results:** Intra-thalamic connectivity was higher in REM than wake in all 11 participants with good REM fMRI, and higher than NREM in 9 of 11; phasic REM exceeded tonic REM. (abstract only)
- **Limits:** No dream reports; phasic REM is a proxy for vividness.
- **For us:** Context for REM in #42; a phasic/tonic split is a possible covariate if REM awakenings are analysed.
- **Touches:** #42

### Real-time dialogue between experimenters and dreamers during REM sleep

Konkoly et al. (2021). *Current Biology 31:1417-1427.e6*. [doi:10.1016/j.cub.2021.01.026](https://doi.org/10.1016/j.cub.2021.01.026). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C19 (sleep).
- **Results:** Lucid dreamers in verified REM sleep can perceive questions, compute answers and reply with eye signals.
- **Limits:** Konkoly 2021: 36 individuals; correct answers on 29 occasions across 6 of the participants (abstract). One multi-site paper; not yet independently replicated.
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C19

### Neural Decoding of Visual Imagery During Sleep

Horikawa et al. (2013). *Science 340:639-642*. [doi:10.1126/science.1234330](https://doi.org/10.1126/science.1234330). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C18 (sleep).
- **Results:** The visual content of sleep-onset imagery can be decoded from fMRI patterns in visual cortex.
- **Limits:** Horikawa 2013, sleep-onset period; decoders trained on waking perception transferred to sleep imagery. Small sample (count not checked here). Not yet replicated at scale.
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C18

## Drugs and anaesthesia (26)

### Convergent transcriptomic and connectomic controllers of information integration and its anaesthetic breakdown across mammalian brains

Luppi AI, Uhrig L, Tasserie J, Mediano PAM, Rosas FE and others; senior author Stamatakis EA (2026). *Nature Human Behaviour 10, 777-802*. [doi:10.1038/s41562-025-02381-5](https://doi.org/10.1038/s41562-025-02381-5). Paper, abstract only, **core**.

- **Question:** Across humans, monkeys, marmosets and mice, anaesthetics break down the brain's integration of information, and waking a monkey with deep-brain stimulation brings it back.
- **Data and method:** fMRI with anaesthesia in humans, macaques, marmosets and mice. Breakdown of integrated information is a convergent effect of diverse anaesthetics; dynamics become harder to control; both reversed by thalamic DBS-induced awakening in macaque. Regional breakdown follows PVALB expression topography; species-specific computational models.
- **Results:** Brain scans under anaesthesia in four species show the same thing: information stops being combined across the brain. In monkeys, stimulating the thalamus reawakened them and restored it. This points the opposite way from a 2024 rat EEG study where an integration estimate went up under anaesthesia.
- **For us:** Shows that whether a Phi-like proxy rises or falls under anaesthesia depends on the modality and the estimator. Our known-Phi network test (task #9) must check each proxy before we trust its direction.
- **Touches:** news

### Electrophysiological effects of psilocybin co-administered with midazolam

Sutherland M, Nicholas C, Lennertz R, Wenthur C and others (2026). *Translational Psychiatry 16, 160*. [doi:10.1038/s41398-026-03894-x](https://doi.org/10.1038/s41398-026-03894-x). Paper, abstract only, **core**.

- **Question:** With a sedative given alongside psilocybin, brain-signal complexity still rose as the psychedelic effects came on.
- **Data and method:** Oral psilocybin 25 mg plus IV midazolam, high-density EEG. At 15-30 min (midazolam at target, psilocybin likely not): higher beta power, lower spectral exponent. Over the next six hours: higher normalised LZC and spectral exponent, lower broadband power. OAA/S sedation scores improved model fits for alpha power; ASC items improved fits for LZCn and spectral exponent. Small open-label pilot. Preprint bioRxiv 10.1101/2025.07.25.666887.
- **Results:** Psilocybin was given together with a sedative that blunts memory. Early on, when mainly the sedative was acting, the EEG looked sedated. As the psychedelic took hold over six hours, complexity rose and power fell, and these changes tracked people's ratings of altered experience better than ratings of sedation.
- **For us:** A case where complexity and the spectral exponent move together under a drug that changes experience. Our test asks whether complexity adds anything once the exponent is known.
- **Touches:** news

### Psychedelics align brain activity with context

Stoliker D, Novelli L, Khajehnejad M, Biabani M, Greaves MD, et al. (2026). *Nature*. [doi:10.1038/s41586-026-10910-z](https://doi.org/10.1038/s41586-026-10910-z). Paper, full text, **core**.

- **Question:** What brain organisation underlies the self- and boundary-dissolving experiences of psilocybin, and how does context shape it?
- **Idea tested:** Low-dimensional trajectories, not time averages, should reveal structured, context-aligned dynamics.
- **Data and method:** 62 adults, fMRI (about 80 min post-dose) and 64-channel EEG (about 150 min post-dose) during rest, meditation, music and movie, before and on the day of psilocybin. Open data: OpenNeuro ds006110 (v1.2.0).
- **Results:** Psilocybin reorganised activity into structured, context-sensitive trajectories that co-varied with experience; networks that usually segregate internal and external processing integrated in people reporting 'embeddedness'. Half ranked the experience among the most meaningful of their lives.
- **Limits:** Single site; EEG was recorded later than fMRI; no placebo session on the drug day as described in the abstract.
- **For us:** New open data for Study 2: a psychedelic EEG set with rest and naturalistic tasks and experience ratings, on OpenNeuro. It is the 'expanded experience, no arousal loss' contrast our state benchmark lacks; markers that rise here and fall under propofol pass a test that wake vs N3 cannot set.
- **Touches:** Study 2, #5

### The entropic brain today

Carhart-Harris RL (2026). *Brain*. [doi:10.1093/brain/awag206](https://doi.org/10.1093/brain/awag206). Review, full text, **core**.

- **Question:** How well has the entropic brain hypothesis held up?
- **Idea tested:** Brain entropy scales with the 'size' of phenomenal consciousness, separately from arousal.
- **Data and method:** Narrative review of evidence across psychedelics, meditation, REM, DoC, sleep, anaesthesia, ageing and disease.
- **Results:** Claims convergent, correlative, predictive, discriminative and external validity, and that entropy changes selectively index the breadth of experience rather than arousal. LZ on EEG/MEG is named the go-to metric. The review itself says increased high-frequency activity is a major carrier of the entropic brain effect.
- **Limits:** A proponent's review. It does not test entropy against a spectral baseline, although it concedes high-frequency power carries much of the effect; the discriminative-validity claim rests mainly on psychedelic fMRI contrasts.
- **For us:** Our results speak to this directly: LZ adds nothing over the spectrum in sleep and fails the surrogate gate. #42 tests the 'not arousal' claim at fixed sleep stage. A sealed prediction from this review (entropy higher before experience awakenings, beyond spectrum) belongs in #42's measure list, which already includes LZ and entropy measures.
- **Touches:** #42, lz_slope, surrogate_gate, theory_entropic_propofol

### Do all sedatives promote biological sleep EEG patterns? A machine learning framework

Ramaswamy SM et al. (2024). *PLoS One*. [doi:10.1371/journal.pone.0304413](https://doi.org/10.1371/journal.pone.0304413). Journal article, abstract only, **core**.

- **Question:** Does a classifier trained on sleep EEG stage sedated EEG?
- **Idea tested:** A 44-feature sleep stager trained on the MGH sleep set (N=994) applied to propofol (36), sevoflurane (36) and dexmedetomidine (30).
- **Data and method:** A 44-feature sleep stager trained on the MGH sleep set (N=994) applied to propofol (36), sevoflurane (36) and dexmedetomidine (30).
- **Results:** Sleep-trained stager on propofol and sevoflurane: AUC 0.55-0.58; dexmedetomidine 0.80.
- **Limits:** One multivariate model, one direction; no per-measure test, spectral baseline or surrogate.
- **For us:** The prior to cite for #5: sleep-to-propofol transfer of a multivariate stager fails.
- **Touches:** Task #5 transfer

### Evaluation of putative signatures of consciousness using specific definitions of responsiveness, connectedness, and consciousness

Casey CP, Tanabe S, Farahbakhsh ZZ, Parker M, Bo A, et al. (Sanders RD senior) (2024). *British Journal of Anaesthesia*. [doi:10.1016/j.bja.2023.09.031](https://doi.org/10.1016/j.bja.2023.09.031). Paper, abstract only, **core**.

- **Question:** Do EEG markers that were built using 'unresponsive' as a stand-in for 'unconscious' actually track experience, or only contact with the outside world?
- **Idea tested:** Ten published resting-state markers (complexity, connectivity, cross-frequency coupling, graph measures, spectrum) scored against serial-awakening reports, split into connected, disconnected-but-experiencing, and unconscious.
- **Data and method:** UNCCIOUS study (NCT03284307): dexmedetomidine sedation, propofol sedation and natural sleep, with repeated awakenings and interviews.
- **Results:** None of the markers tracked experience alone; each also tracked connectedness, and several tracked connectedness only. Front-to-back symbolic transfer entropy tracked connectedness in all three conditions. Going from disconnected experience to unconsciousness lowered permutation entropy and the spectral exponent (P<0.05 in all conditions). (abstract only)
- **Limits:** Data on request (IRB discretion), not open; small propofol arm.
- **For us:** The closest prior art to our whole benchmark, and it already uses per-awakening reports. It weakens our #5 loose thread (exponent follows slow waves, not experience): here the exponent does separate disconnected experience from unconsciousness. Requesting these data is the best route to a powered sedation-with-reports test.
- **Touches:** #5, #42

### Dexmedetomidine produces more sleep-like brain activity compared with propofol in human participants

Krause BM et al. (2026). *Br J Anaesth*. [doi:10.1016/j.bja.2025.09.050](https://doi.org/10.1016/j.bja.2025.09.050). Journal article, abstract only, **useful**.

- **Question:** Is sedative unresponsiveness sleep-like?
- **Idea tested:** Intracranial EEG in 34 patients under dexmedetomidine and propofol compared with sleep.
- **Data and method:** Intracranial EEG in 34 patients under dexmedetomidine and propofol compared with sleep.
- **Results:** Dexmedetomidine resembles N2; propofol changes delta less and network entropy more than sleep.
- **Limits:** Patients; intracranial.
- **For us:** Explains why sleep-to-propofol transfer can fail.
- **Touches:** Task #5 transfer

### Dreaming during anaesthesia: a scoping review

Sikka P, Hu S, Heifets BD (2026). *British Journal of Anaesthesia*. [doi:10.1016/j.bja.2026.05.002](https://doi.org/10.1016/j.bja.2026.05.002). Review, abstract only, **useful**.

- **Question:** How often do people dream under anaesthesia, and what predicts it?
- **Idea tested:** Pool a century of studies on anaesthesia dreaming.
- **Data and method:** Scoping review of 157 studies (1921-2024), 87,866 participants.
- **Results:** Recall was 40-80% in experimental settings and 3-8% in large clinical trials. Ketamine and propofol were most consistently associated with recall. Recall was not associated with intraoperative awareness. (abstract only)
- **Limits:** Heterogeneous methods; recall depends heavily on when and how people are asked.
- **For us:** Propofol dreaming is common enough that 'unresponsive' does not mean 'no experience', which is why our state benchmark (Study 2) only claims arousal, not experience, for propofol contrasts.
- **Touches:** #42, Study 2, #7

### Emergent multiscale organisation of neural dynamics fragments in anaesthesia

Milinkovic B, Seth AK, Barnett L, Carter O, Andrillon T (2026). *Imaging Neuroscience*. [doi:10.1162/imag.a.1364](https://doi.org/10.1162/imag.a.1364). Paper, full text, **useful**.

- **Question:** How does emergent multiscale organisation change under propofol, xenon and ketamine?
- **Idea tested:** Dynamical independence (DI) should separate drugs that abolish report from ketamine, which keeps dream-like experience.
- **Data and method:** Source-reconstructed 61-channel EEG from the Milan cohort (Sarasso 2015): 14 adults, propofol 4, xenon 5, ketamine 5.
- **Results:** Propofol and xenon showed more emergence but highly variable, fragmented macroscopic structure; ketamine showed less emergence with partial preservation of structure. The authors warn against equating emergence with level of consciousness.
- **Limits:** n = 4-5 per drug, the same single cohort behind most ketamine claims. The paper calls the data open-access; our record has Zenodo 806176 as restricted (access requested 18 Nov 2026).
- **For us:** Another measure that dissociates ketamine from propofol on the one Milan cohort; it does not change our ketamine gap. Worth asking whether DI survives the spectral baseline.
- **Touches:** Study 2, #7

### Opposite network patterns of integration-segregation in psychedelic and sedated states of consciousness

Dai R, Jang H, Hudetz AG, Huang Z, Mashour GA (2026). *Cell Reports*. [doi:10.1016/j.celrep.2026.117830](https://doi.org/10.1016/j.celrep.2026.117830). Paper, full text, **useful**.

- **Question:** Do psychedelic and sedated states shift brain network integration and segregation in opposite directions?
- **Idea tested:** A mirror-image hypothesis: psychedelics integrate, sleep and propofol segregate.
- **Data and method:** fMRI across psychedelics, sleep and propofol; several connectivity, topology and complexity measures. Data: Zenodo 10.5281/zenodo.14029241, OpenNeuro ds003768 (sleep fMRI) and ds003059 (LSD).
- **Results:** Psychedelics showed more integration and less segregation; sleep and propofol the opposite; the pattern held across spatial scales and data-driven classifiers.
- **Limits:** fMRI only; arousal and drug effects are confounded with consciousness in every contrast.
- **For us:** A clean prediction for Study 2's state axis on EEG: if integration measures (wSMI, total correlation) flip sign between psilocybin (ds006110) and propofol, they track something other than plain arousal.
- **Touches:** Study 2

### Psilocybin-induced changes in electroencephalography link acute and long-term effects

Nikolič M, Froese T, Mediano PAM, Koudelka V, Horáček J, Tylš F, Páleníček T (2026). *Journal of Psychopharmacology*. [doi:10.1177/02698811261473445](https://doi.org/10.1177/02698811261473445). Paper, abstract only, **useful**.

- **Question:** How do psilocybin's EEG effects unfold over 24 hours and do they predict lasting change?
- **Idea tested:** Acute entropy rises track acute experience; sub-acute spectral shifts track long-term outcomes.
- **Data and method:** Double-blind placebo-controlled crossover, N = 20, about 0.26 mg/kg, high-density resting EEG at baseline, 1, 3, 6 and 24 h, 28-day follow-up.
- **Results:** Alpha/beta power fell and gamma-band signal diversity rose at 1-3 h; gamma diversity correlated with acute psychological effects (r = 0.71). At 24 h reduced delta/theta correlated with positive life changes at 4 weeks (r = -0.47 to -0.57). (abstract only)
- **Limits:** Small; diversity not tested against a spectral baseline.
- **For us:** A within-subject case where a complexity measure tracks experience intensity while arousal stays wake-like. If the data were open it would be a #42-style test; ask whether gamma diversity survives band-power nesting.
- **Touches:** Study 2, lz_slope

### Spectral mapping reveals a resemblance of the anesthetic brain state to both sleep and coma

Helfrich JD et al. (2026). *PNAS*. [doi:10.1073/pnas.2514098123](https://doi.org/10.1073/pnas.2514098123). Journal article, abstract only, **useful**.

- **Question:** Which natural state does propofol EEG resemble?
- **Idea tested:** Whole-head spectral maps of propofol (35) correlated with wake, SWS, REM and coma.
- **Data and method:** Whole-head spectral maps of propofol (35) correlated with wake, SWS, REM and coma.
- **Results:** Propofol resembles coma most; its reduced aperiodic activity partly overlaps REM.
- **Limits:** Similarity analysis; no classifier transfer.
- **For us:** Background: propofol is not simply sleep-like.
- **Touches:** Task #5 transfer

### Distinct EEG signatures differentiate unconsciousness and disconnection during anaesthesia and sleep

Casey CP, Tanabe S, Farahbakhsh Z, et al. (2022). *British Journal of Anaesthesia*. [doi:10.1016/j.bja.2022.01.010](https://doi.org/10.1016/j.bja.2022.01.010). Article, abstract only, **useful**.

- **Question:** Can EEG tell 'experiencing but cut off from the world' (disconnected) apart from 'no experience at all' (unconscious)?
- **Idea tested:** Volunteers were sedated with dexmedetomidine or propofol, or slept, under high-density EEG, and were woken repeatedly to ask whether they had experienced anything in the previous 20 s.
- **Data and method:** Serial awakenings; derivation on dexmedetomidine, validation on sleep and propofol; source-localised SVM classifiers.
- **Results:** Occipital delta power barely separated the two states (AUC 0.61 for dexmedetomidine, 0.51 for sleep/propofol). Source-localised signatures did well within dexmedetomidine and generalised partly (disconnection AUC 0.74, unconsciousness 0.62).
- **Limits:** Small samples; generalisation AUCs are modest.
- **For us:** A model for splitting state contrasts by report. ds005620 (propofol with repeated awakenings) could support the same disconnected-vs-unconscious split.
- **Touches:** Hypothesis tournament

### Increased spontaneous MEG signal diversity for psychoactive doses of ketamine, LSD and psilocybin

Schartner MM, Carhart-Harris RL, Barrett AB, Seth AK, Muthukumaraswamy SD (2017). *Scientific Reports 7, 46421*. [doi:10.1038/srep46421](https://doi.org/10.1038/srep46421). Paper, abstract only, **useful**.

- **Question:** Psychedelics pushed brain-signal diversity above normal waking levels, the first time such measures went higher than wakefulness.
- **Data and method:** Spontaneous MEG; LZ and entropy measures higher for all three drugs, even when controlling for spectral changes; strongest for single-channel LZ (temporal diversity). Selective correlations with phenomenological intensity ratings.
- **Results:** Complexity scores are usually highest in normal waking. Under psilocybin, ketamine and LSD they went higher still, and some of the rise tracked how intense people said the experience was.
- **For us:** Tests whether a measure rises when contents intensify but level does not obviously change. We re-check the spectral control with phase-randomised surrogates.
- **Touches:** news

### Brain connectivity dissociates responsiveness from drug exposure during propofol-induced transitions of consciousness

Chennu S, O'Connor S, Adapa R, Menon DK, Bekinschtein TA (2016). *PLoS Computational Biology 12:e1004669*. [doi:10.1371/journal.pcbi.1004669](https://doi.org/10.1371/journal.pcbi.1004669). Paper, abstract only, **useful**.

- **Question:** Does EEG connectivity follow responsiveness or drug level under propofol?
- **Idea tested:** Separate behavioural responsiveness from blood drug concentration.
- **Data and method:** High-density EEG during graded propofol sedation; data in the Cambridge repository (10.17863/CAM.68959, CC BY 2.0 UK, 3.44 GB zip).
- **Results:** Alpha network connectivity tracked responsiveness more than drug concentration.
- **Limits:** About 20 participants; one drug.
- **For us:** Open sedation data that could add a within-person responsiveness contrast to Study 2; large download.
- **Touches:** Study 2

### Complexity of multi-dimensional spontaneous EEG decreases during propofol induced general anaesthesia

Schartner M, Seth A, Noirhomme Q, Boly M, Bruno MA, Laureys S, Barrett A (2015). *PLoS ONE 10:e0133532*. [doi:10.1371/journal.pone.0133532](https://doi.org/10.1371/journal.pone.0133532). Paper, abstract only, **useful**.

- **Question:** Does spontaneous EEG complexity fall under propofol?
- **Idea tested:** Lempel-Ziv complexity across channels and time.
- **Data and method:** Resting high-density EEG before and during propofol.
- **Results:** LZ complexity fell under propofol.
- **Limits:** No spectral control.
- **For us:** One of the LZ results our lz_slope work found to be largely spectral.
- **Touches:** lz_slope

### Consciousness and complexity during unresponsiveness induced by propofol, xenon, and ketamine

Sarasso S, Boly M, Napolitani M and others; senior author Massimini M (2015). *Current Biology 25, 3099-3105*. [doi:10.1016/j.cub.2015.10.014](https://doi.org/10.1016/j.cub.2015.10.014). Paper, abstract only, **useful**.

- **Question:** Under ketamine, people stopped responding but their brain's response to a magnetic pulse stayed wake-like, and afterwards they reported vivid dreams.
- **Data and method:** 18 healthy volunteers. Frontal and parietal TMS: propofol gave a local low-complexity slow wave, xenon a global stereotyped low-complexity slow wave, ketamine a wake-like complex pattern. Reports on emergence: none after propofol and xenon; long vivid dreams after ketamine.
- **Results:** Three anaesthetics all made volunteers unresponsive. After propofol and xenon they remembered nothing. After ketamine they described long, vivid dreams, and during it the brain's response to stimulation stayed complex like in waking. This is the classic case where behaviour and experience come apart.
- **For us:** Defines our ketamine dissociation case. The same group's data underlies Colombo 2019 and Maschke 2024, so we need an independent ketamine dataset.
- **Touches:** news

### Feasibility of a multicomponent protocol to promote dreaming during surgical anesthesia

Sikka P, Ngo MC, Hu S, Wilkerson TB, Shull M, Imbordino K, Ishii T, Kawai M, Deverett B, Chow HS, Heifets BD (2026). *Anesthesiology*. [doi:10.1097/aln.0000000000005968](https://doi.org/10.1097/aln.0000000000005968). Paper, abstract only, **context**.

- **Question:** Can routine anaesthesia be steered towards dreaming at emergence?
- **Idea tested:** Priming, propofol emergence, EEG-guided quiet emergence and immediate interviews should raise dream recall.
- **Data and method:** Prospective quality-improvement study, 474 surgical patients, SedLine EEG monitoring.
- **Results:** 69% of 452 interviewed patients reported dreaming; 93% of 57 with full protocol adherence. Dreamers rated sleep quality higher (9.16 vs 7.65). No intraoperative awareness. (abstract only)
- **Limits:** No dream/no-dream EEG analysis reported in the abstract; EEG is a 4-channel clinical monitor.
- **For us:** If emergence EEG with dream reports is ever shared, it would give a propofol 'experience at fixed state' contrast, a third arm beside NREM and REM for #42-style tests.
- **Touches:** #42

### Mapping basal ganglia circuitry in altered states of consciousness: from pathology to pharmacology

Szocs D, Luppi AI, Coppola P, Adapa R, Williams GB, Allanson J, Pickard JD, Owen AM, Naci L, Menon DK, Stamatakis EA (2026). *Brain*. [doi:10.1093/brain/awag272](https://doi.org/10.1093/brain/awag272). Paper, abstract only, **context**.

- **Question:** How do basal ganglia nuclei and neurotransmitter systems change in propofol and DoC loss of responsiveness?
- **Idea tested:** Map 9 nuclei against 19 transmitter systems.
- **Data and method:** fMRI, 16 volunteers under propofol, 22 DoC patients.
- **Results:** Putamen changes correlated with the noradrenaline transporter and GPe with serotonin and acetylcholine transporters under propofol. (abstract only)
- **Limits:** fMRI; small.
- **For us:** Context.

### State-dependent, frequency-specific modulation of electrocortical traveling waves by anesthesia

Li D, Hudetz AG (2026). *bioRxiv (17 Aug 2026)*. [doi:10.64898/2026.08.11.744271](https://doi.org/10.64898/2026.08.11.744271). Preprint, abstract only, **context**.

- **Question:** How does anaesthesia change cortical travelling waves?
- **Idea tested:** Travelling-wave structure should change with depth and with spontaneous state transitions.
- **Data and method:** Hemispheric ECoG in rats at 6, 4, 2 and 0% desflurane.
- **Results:** Delta-band waves became more frequent and stereotyped (more planar, fewer source/sink) at 4-6%; theta and gamma wave rates were largely unchanged; a paradoxical awake-like state in deep anaesthesia partly shifted towards wake patterns. (abstract only)
- **Limits:** Rats; abstract only.
- **For us:** Context.

### Comprehensive profiling of anaesthetised brain dynamics across phylogeny

Luppi AI, Uhrig L, Tasserie J, Shafiei G, et al. (2025). *bioRxiv*. [doi:10.1101/2025.03.22.644729](https://doi.org/10.1101/2025.03.22.644729). Preprint, abstract only, **context**.

- **Question:** Is there a shared dynamical signature of anaesthesia across species?
- **Idea tested:** They extracted over 6,000 time-series features from recordings in wake and anaesthesia in humans, macaques, marmosets, mice, zebrafish and worms.
- **Data and method:** Massive feature extraction (hctsa-style) on multi-scale data; deep-brain stimulation in macaques; biophysical modelling.
- **Results:** Anaesthesia shows a conserved profile: shorter intrinsic timescales and weaker synchrony between regions. Thalamic stimulation reversed it in macaques.
- **Limits:** Preprint; abstract only read here.
- **For us:** A huge feature screen for anaesthesia already exists. A tournament adds value only through sealing, held-out data and beating the spectrum.
- **Touches:** Hypothesis tournament

### Thalamic contributions to predictive coding and disconnected consciousness in human volunteers

Wehrman JJ, Casey C, Redinbaugh MJ, Muller E, Munn B, et al. (2025). *British Journal of Anaesthesia*. [doi:10.1016/j.bja.2025.10.038](https://doi.org/10.1016/j.bja.2025.10.038). Paper, abstract only, **context**.

- **Question:** Does the cortex stop synchronising to surprising sounds when consciousness is disconnected from the world?
- **Idea tested:** Disconnected consciousness (dreaming-like) should reduce surprise-driven cortical synchrony.
- **Data and method:** 18 volunteers, auditory oddball, EEG, awake vs dexmedetomidine sedation with disconnection confirmed by serial awakening.
- **Results:** Surprise was more strongly expressed in awake EEG, with frontal negative (33-356 ms) and posterior positive (37-400 ms) effects that diminished in disconnection; voxel coactivation also dropped (P<0.001). (abstract only)
- **Limits:** Evoked paradigm; small n; data availability not stated in the abstract.
- **For us:** Shows serial awakenings can confirm 'disconnected but experiencing' under sedation; a model for a future sedation arm of the experience benchmark.
- **Touches:** #42

### Measuring the dynamic balance of integration and segregation underlying consciousness, anesthesia, and sleep in humans

Jang H et al. (2024). *Nat Commun*. [doi:10.1038/s41467-024-53299-x](https://doi.org/10.1038/s41467-024-53299-x). Journal article, abstract only, **context**.

- **Question:** Does an fMRI integration-segregation measure index consciousness across states?
- **Idea tested:** Random forest on propofol fMRI datasets; parallel sleep analysis (n=28).
- **Data and method:** Random forest on propofol fMRI datasets; parallel sleep analysis (n=28).
- **Results:** Propofol AUC 0.984, validated across propofol datasets.
- **Limits:** Sleep run in parallel, not as transfer.
- **For us:** fMRI analogue of cross-state generalisation.
- **Touches:** Task #5 transfer

### Cortical functional connectivity indexes arousal state during sleep and anesthesia

Banks MI et al. (2019). *bioRxiv*. [doi:10.1101/823963](https://doi.org/10.1101/823963). Preprint, abstract only, **context**.

- **Question:** Do sleep and propofol change connectivity alike?
- **Idea tested:** Intracranial EEG, n=5.
- **Data and method:** Intracranial EEG, n=5.
- **Results:** Connectivity shifts in N2/N3 and propofol unresponsiveness are strikingly similar.
- **Limits:** n=5, descriptive; abstract read.
- **For us:** Background for cross-state transfer.
- **Touches:** Task #5 transfer

### Incidence of Connected Consciousness after Tracheal Intubation

Sanders et al. (2017). *Anesthesiology 126:214-222*. [doi:10.1097/ALN.0000000000001479](https://doi.org/10.1097/ALN.0000000000001479). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C15 (pharmacology).
- **Results:** Under intended general anaesthesia some patients follow commands with an isolated forearm, yet recall nothing afterwards.
- **Limits:** Sanders 2017: 12 of 260 (4.6%) responded after intubation; none had explicit recall. Shows connected consciousness without memory; report-after is not a full ground truth.
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C15

### Broadband Cortical Desynchronization Underlies the Human Psychedelic State

Muthukumaraswamy et al. (2013). *The Journal of Neuroscience 33:15171-15183*. [doi:10.1523/JNEUROSCI.2063-13.2013](https://doi.org/10.1523/JNEUROSCI.2063-13.2013). Paper, abstract only, **context**.

- **Question:** Primary source for ledger constraint C45 (pharmacology).
- **Results:** Psychedelics intensify experience while reducing spontaneous oscillatory power (alpha most) and, in fMRI, reducing activity in hub regions.
- **Limits:** Mostly one group (Imperial / Cardiff). Large activity decrease with richer experience.
- **For us:** Evidence grade B in the constraint ledger; every theory on the scorecard is checked against it.
- **Touches:** constraint_ledger, C45

## AI (7)

### Identifying indicators of consciousness in AI systems

Butlin P, Long R, Bayne T, Bengio Y, Birch J, Chalmers D and others (20 authors) (2026). *Trends in Cognitive Sciences 30(6), 488-501*. [doi:10.1016/j.tics.2025.10.011](https://doi.org/10.1016/j.tics.2025.10.011). Paper, abstract only, **core**.

- **Question:** A method for judging whether an AI could be conscious by checking its inner workings against what theories of consciousness require, not by what it says.
- **Data and method:** Four guidelines for deriving indicators, e.g. indicators should target the central explanatory posits of a theory; illustrated with the indicator list from the 2023 report (arXiv:2308.08708, 19 authors, which drew on recurrent processing, global workspace, higher-order, predictive processing and attention schema theories and concluded no current AI systems are conscious but saw no obvious technical barriers to meeting the indicators). Issue June 2026 (vol 30, issue 6).
- **Results:** Instead of asking a chatbot whether it feels anything, the authors take the core requirements of several brain theories and check whether an AI system's internal machinery meets them. This builds on their 2023 report, which concluded that no current AI system was a strong candidate.
- **For us:** The rubric for our AI stress tests: we use it to find where theories disagree or give absurd answers, never as a verdict on AI and never scoring an AI's self-report.
- **Touches:** news

### Large language models surpass human experts in predicting neuroscience results

Luo X, Rechardt A, Sun G, et al. (2025). *Nature Human Behaviour 9, 305-315*. [doi:10.1038/s41562-024-02046-9](https://doi.org/10.1038/s41562-024-02046-9). Paper, abstract only, **core**.

- **Question:** Can LLMs forecast neuroscience results better than experts?
- **Idea tested:** BrainBench: pick the real abstract versus an altered one; compared LLMs, a tuned BrainGPT and human experts.
- **Data and method:** Benchmark built from published abstracts.
- **Results:** LLMs beat experts; confidence was calibrated; tuning on neuroscience text helped further.
- **Limits:** Tests outcome prediction, not theory-conditional likelihoods; memorisation of published abstracts is a live issue.
- **For us:** Prior art for our theory ledger: the real-vs-altered format is close to our real-vs-mirrored items, and their leak concerns are ours.
- **Touches:** theory-ledger

### Same behavior, different mechanism: what finite experiments can certify about integrated information

Wu L, He D (2026). *arXiv 2611.08469*. [doi:10.48550/arXiv.2611.08469](https://doi.org/10.48550/arXiv.2611.08469). Preprint, abstract only, **useful**.

- **Question:** When is integrated information identifiable and certifiable from finite, partial experiments?
- **Idea tested:** Test phi on small stochastic networks with known ground truth.
- **Data and method:** Four- and five-unit stochastic networks; partial recordings and interventions.
- **Results:** A recurrent and a feed-forward network with identical input-output laws carried 0.28 and 0 bits, separable from internal recordings in 4-53 trials. Omitted units imposed precision floors of 0.30-1.02 bits; tiny mechanism changes crossing an edge shifted phi by 25-100% at 99% of edges found. (abstract only)
- **Limits:** Tiny networks.
- **For us:** Directly relevant to our phi_proxy recovery test: phi is discontinuous in the mechanism, so any proxy recovery test should report how often near-identical networks give very different phi.
- **Touches:** phi_proxy, phi_proxy_recovery

### Verbalizable representations form a global workspace in language models

Gurnee W, Sofroniew N, Pearce A, Piotrowski M, Kauvar I, Chen R, Soligo A, Bogdan P, et al. (2026). *arXiv 2607.15495*. [doi:10.48550/arXiv.2607.15495](https://doi.org/10.48550/arXiv.2607.15495). Preprint, abstract only, **useful**.

- **Question:** Do language models have a functional analogue of conscious access?
- **Idea tested:** A 'Jacobian lens' finds what a model is poised to verbalise; this J-space should show workspace properties.
- **Data and method:** Interpretability study of large language models.
- **Results:** J-space content can be reported, summoned, held, used for silent reasoning and passed to downstream computation; it is coherent only in a middle band of layers, holds tens of concepts and is broadcast more widely than other representations. (abstract only)
- **Limits:** Functional analogy only; says nothing about experience.
- **For us:** A concrete, testable workspace signature in AI that maps onto the access side of GNWT; relevant if the AI topic page compares indicators. Follow-ups test it in looped transformers and Mamba (Wang & Reid 2026).
- **Touches:** AI

### A cross-entropy audit (CEA) for consciousness tests moved from brain to large language model

van Rooyen P (2026). *arXiv 2609.22300*. [doi:10.48550/arXiv.2609.22300](https://doi.org/10.48550/arXiv.2609.22300). Preprint, abstract only, **context**.

- **Question:** How often is a brain consciousness test wrong when moved to an LLM?
- **Idea tested:** Score competing models on held-out trials in nats per trial; plant known truth.
- **Data and method:** Method proposal with simulations.
- **Results:** Proposes a transfer audit; no method reviewed measured transfer error rates. (abstract only)
- **Limits:** Single author; method proposal.
- **For us:** Its held-out log-score idea matches how we compare theories; context.
- **Touches:** AI, theory_scorecard

### From cacophony to hierarchy: a principled framework for assessing AI consciousness

Chandaria S, Muñoz Morán A, Rosas F, Seth A, Shevlin H, Hutter M, Graepel T, Bales A, et al. (2026). *arXiv 2609.35618*. [doi:10.48550/arXiv.2609.35618](https://doi.org/10.48550/arXiv.2609.35618). Preprint, abstract only, **context**.

- **Question:** How can competing theories be combined into one assessment of AI consciousness?
- **Idea tested:** A five-level hierarchy of functional descriptions plus a Bayesian credence model.
- **Data and method:** Framework with indicators at each level, applied to current LLMs.
- **Results:** Verdicts for current LLMs ranged from below 0.01 to about 0.8 depending on stipulated credences. (abstract only)
- **Limits:** Outcome driven by priors, as the authors show.
- **For us:** Context for the AI topic.
- **Touches:** AI

### Looped transformers under the Jacobian lens: does the global workspace survive recurrence?

Wang W, Reid F (2026). *arXiv 2609.01924*. [doi:10.48550/arXiv.2609.01924](https://doi.org/10.48550/arXiv.2609.01924). Preprint, abstract only, **context**.

- **Question:** Does the workspace analogue appear when depth comes from recurrence?
- **Idea tested:** Extend the Jacobian lens to looped and depth-recurrent models.
- **Data and method:** Ouro-2.6B and Huginn-0125 vs Qwen3.6-27B.
- **Results:** A workspace forms in the iterated part of each architecture, but recurrence changes how it can be read and written. (abstract only)
- **Limits:** Abstract only.
- **For us:** Context; recurrence matters to RPT and IIT-style claims about AI.
- **Touches:** AI
