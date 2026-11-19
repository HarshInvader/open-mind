# Open Mind: open tasks

Exported from the team board on 19 Nov 2026. 14 ready, 7 waiting on earlier tasks, 1 in progress, 20 done.

To take one, read [CONTRIBUTING.md](../CONTRIBUTING.md) first: open an issue named `Taking #<id>` so nobody duplicates it.

## Ready now

### #42 Experience benchmark: do published EEG consciousness markers predict reported experience at fixed sleep stage, beyond spectrum, across labs

Milestone M2, priority 1.

Plan: docs/PLAN_2026-11-19_experience_benchmark.md (Fable-planned). Study 1 headline (DREAM packages, lab-held-out, label-blind, sealed), Study 2 state-contrast axis (Sleep-EDF, BOAS, Chennu, ds005620, DOSE-I), Study 3 sealed residual search. Needs owner OK: ~25 GB streamed budget; DOSE-I data-use text. Step 1 label-blind audit + power.

### #5 Zero-shot transfer of 8-10 published measures

Milestone M2, priority 3.

Fit thresholds on one family (sleep, anaesthesia, DoC) and test on the others for LZ, PCI-like, spectral slope, permutation entropy, wSMI, alpha power, Sitt/Engemann features, criticality. Decisive: any measure with AUC >= 0.80 everywhere moves up; the rest are logged as specific to one state.

### #6 Dream vs no-dream within stage

Milestone M2, priority 3.

Run within-stage serial-awakening prediction (Siclari 2017 posterior low-frequency power) on ds005620 and DREAM. Decisive: above-chance held-out prediction, or a clear null with stated power.

### #17 Theory disagreement map

Milestone M3, priority 3.

Compute the theory-derived measures (complexity/integration proxies, frontal ignition proxies, spectral baseline, entropy) on the same recordings: ketamine, REM, psychedelics, sedation levels, sleep stages. Find where they disagree most; those cases become the next sealed tests. See docs/PLAN.md A17.

### #18 Our own hypotheses (H track)

Milestone M3, priority 3.

Propose up to 3 new hypotheses about what distinguishes conscious from unconscious states, from development data and the results landed so far. For each: write the refuting result, hash it, test on held-out subjects or a different dataset, compare against the spectral baseline and the best rival measure, and run a planted-answer check. Failures go in the negative atlas. See docs/PLAN.md, track H.

### #22 Dream vs no-dream on DREAM, held out by subject and lab

Milestone M2, priority 3.

DREAM paper reports AUC 0.586 (NREM, PSD) and 0.700 (REM, catch22) over 200 random train-test splits; main text does not say subjects were held out. Re-run with subject- and lab-held-out splits, spectral exponent baseline and surrogate gate. Pre-register first.

### #39 Red-team: LZ adds 0.061 AUC over the exponent for REM vs N3 (Sleep-EDF)

Milestone M6, priority 3.

Positive cell from #4 (experiments/lz_slope/RESULTS.md, H1 C2): slope+LZ 0.976 vs slope 0.915, Holm p=0.008, 45 subjects. Attack it: (1) does it survive a better exponent fit (aperiodic fit excluding alpha/sigma peaks, or 30-45 Hz range)? (2) muscle and eye artefact (REM eye movements on Fpz-Cz; rerun on Pz-Oz only); (3) age (cassette 25-101); (4) Hilbert-envelope LZs instead of median-binarised LZ; (5) the 19 unfetched subjects. Producer's own reading: it is spectral shape, because it vanishes with band powers (H3) and LZ fails the surrogate gate (#8). Do not read producer notes beyond RESULTS.md.

### #10 Reproduce COGITATE iEEG decoding

Milestone M3, priority 4.

Re-run the consortium's public decoding analysis on the iEEG release. Decisive: match the published numbers or document why not.

### #23 Add 2026 COGITATE reanalyses to the multiverse

Milestone M3, priority 4.

Bandara, Rowe, Garrido 2026 bioRxiv doi:10.64898/2026.07.16.738188 (DCM, N=100 MEG, finds offset ignition) and Bryant & Whyte 2026 Neurosci Conscious niag029 (246 FC measures, N=94). Encode both as analysis branches in task #11 before hashing.

### #28 B5 Test our sealed theory

Milestone M3, priority 4.

Run the sealed predictions on held-out open data and on future releases (COGITATE exp 2, INTREPID). Red team. Pass or fail goes on the scoreboard; failure goes in the negative atlas.

### #35 B4e Hybrids and the field of candidates

Milestone M3, priority 4.

Once 3+ sealed candidates exist (T1, T2, B4b-d), score all of them blind on the ledger alongside the published theories; propose at most 2 hybrids where candidates cover different ledger rows, seal them, and list the single test that best separates the top two. Output experiments/our_theory/FIELD.md.

### #14 Red team every positive

Milestone M6, priority 5.

An agent with no access to the producing notes tries confound matching, other preprocessing and site effects on each landed positive. The result survives or drops one ladder level.

### #29 Red-team the theory scorecard (#25): blind re-mark of 20% of cells

Milestone M6, priority 5.

Not mind-theorist. Take a random 20% of experiments/theory_scorecard/scorecard.csv (seeded), re-mark explains/compatible/silent/strained/contradicts blind to our marks using the proponent sources listed, report agreement (Cohen's kappa) and every cell where a proponent paper we missed changes the mark. Also check the 24 'strained' cells for published replies by the theory's authors.

### #15 Theory-proponent fairness drafts

Milestone M6, priority 6.

Draft, for the human lead to send by hand, each theory's predictions as we encoded them, asking proponents whether they are fair. Agents do not send anything.

## Waiting on earlier tasks

### #7 Ketamine and REM: who calls them conscious?

Milestone M2, priority 3. Waits for #2, #5.

For each measure, does it call ketamine anaesthesia and REM sleep conscious, as reports say? Decisive either way. Data from the dataset audit.

### #26 B3 Data-driven ingredients

Milestone M3, priority 3. Waits for #22.

On DREAM (2,417 report-labelled awakenings), held out by subject and lab, find signals that predict reported experience beyond spectral slope and band power. Hash the search space first. Survivors are ingredients a theory must explain.

### #33 B4c Theory from data-driven ingredients

Milestone M3, priority 3. Waits for #26.

After B3 (#26) lands, draft a theory whose core terms are the signals that survived held-out tests (beyond spectral baselines). State why those signals and not others; make >=3 risky predictions on unseen data. Seal by hash.

### #34 B4d Theory from the sleep-onset sign flip

Milestone M3, priority 3. Waits for #18.

mind-3 saw (exploratory, Zhang&Wamsley only) that low delta goes with NO experience at sleep onset but WITH experience in later N2. Draft a theory that predicts this flip from a mechanism, or state why it is an artefact. Seal before any confirmatory test; confirm only on data not yet seen (LODE, DeGennaro multiple-awakenings, Tononi held-out), excluding Zhang and YoungAdults.

### #40 B3b Which level carries the state: a grain sweep

Milestone M3, priority 3. Waits for #22.

Question: at which spatial and temporal grain does EEG best predict reported experience? On the report-labelled awakenings (held out by person and lab), decode experience vs no experience from single channels, channel groups (regions) and the whole head, with windows of 1, 5, 10 and 30 s. Seal the plan in docs/prereg/ first. Planted check first: synthetic EEG where only one grain carries the label; the method must name that grain. Second check: Rosas, Mediano et al. 2020 causal-emergence measure (doi:10.1371/journal.pcbi.1008289) on the same data. Report the grain curve with CIs and the smallest difference between grains the test could detect. Background: Hoel, Albantakis, Tononi 2013 (doi:10.1073/pnas.1314922110); Hoel et al. 2016 (doi:10.1093/nc/niw012). Every claim in RESULTS.md names its grain.

### #11 Pre-registered multiverse on COGITATE

Milestone M3, priority 4. Waits for #10.

Hash a set of reasonable analysis variants for prefrontal ignition at offset and sustained posterior synchrony, then run them all. Report the share of variants that supports each theory. Note the July 2026 bioRxiv directed-connectivity reanalysis (authors unverified).

### #37 B4f Two-layer theory: basic experience plus a self-loop

Milestone M3, priority 4. Waits for #35.

Draft a candidate where a basic layer (e.g. sustained posterior activity gated by bistability) decides whether anything is experienced, and a self-referential layer (strange loop / self-model, midline and frontoparietal) decides whether there is a reflective 'I'. It must make >=3 risky predictions no rival makes, including a dissociation testable on open data: self-model signals track reports of a sense of self, separately from signals that track whether any experience was present (dream reports with vs without self-presence; psychedelic ego dissolution data if open). Seal by hash; blind-scored with the field in #35.

## In progress (do not duplicate)

- #9 Phi-proxy recovery on known-Phi networks

## Done

- #1 Port rules of evidence and dataset leakage check: **tool**, `experiments/rules/RESULTS.md`

- #2 Dataset audit: **data**, `experiments/dataset_audit/RESULTS.md`

- #38 Dataset catalogue for consciousness research (Indus-style datasets/): **tool**, `datasets/README.md`

- #3 Ground-truth schema: **data**, `experiments/ground_truth/RESULTS.md`

- #4 LZ complexity vs spectral slope: **mixed**, `experiments/lz_slope/RESULTS.md`

- #8 Surrogate gate: **negative**, `experiments/surrogate_gate/RESULTS.md`

- #12 Verify the plan's (memory) citations: **data**, `experiments/research_sweep/RESULTS.md`

- #16 One sealed open-data test per theory: **negative**, `experiments/theory_tests/RESULTS.md`

- #19 Independent ketamine EEG with delayed report: **negative**, `experiments/data_access/RESULTS.md`

- #20 DREAM database open-access audit: **data**, `experiments/data_access/RESULTS.md`

- #24 B1 Constraint ledger: **data**, `experiments/constraint_ledger/RESULTS.md`

- #25 B2 Theory x constraint scorecard: **data**, `experiments/theory_scorecard/RESULTS.md`

- #41 Non-equilibrium (irreversibility) vs spectrum: published second-order form and our higher-order variant: **negative**, `experiments/nonequilibrium/RESULTS.md`

- #43 T4 (GNWT extension) on Stockart iEEG: **untestable** (P1 undecidable at realistic separation; parked 2026-11-19, P2 not run), `experiments/our_theory/t4_planted/RESULTS.md`

- #21 Chennu propofol set exceeds download budget: **tool**, `experiments/chennu_access/RESULTS.md`

- #27 B4 Draft our own theory: **untestable**, `experiments/our_theory/T1.md`

- #30 Blind ledger scoring of our candidate theories by an agent who did not write them: **negative**, `experiments/blind_scoring/RESULTS.md`

- #31 Seal and run the open-data prediction of the best candidate: **negative**, `experiments/t1_dream/RESULTS.md`

- #32 B4b Theory from the shared gaps: **tool**, `experiments/our_theory/T3.md`

- #36 Score Strange Loop (Hofstadter) on the ledger: **tool**, `experiments/theory_scorecard/RESULTS.md`

- #13 Standing research sweep: **data**, `experiments/research_sweep/RESULTS.md`
