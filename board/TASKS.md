# Open Mind: open tasks

Exported from the team board on 18 Nov 2026. 14 ready, 7 waiting on earlier tasks, 3 in progress, 14 done.

To take one, read [CONTRIBUTING.md](../CONTRIBUTING.md) first: open an issue named `Taking #<id>` so nobody duplicates it.

## Ready now

### #38 Dataset catalogue for consciousness research (Indus-style datasets/)

Milestone M1, priority 1.

Build datasets/ the way indus-decipher/datasets/ does (read its README.md, catalog.csv, fetch.py and build.py first, and copy the structure). (1) datasets/catalog.csv listing EVERY open or requestable dataset relevant to this project, not only ones we use, with columns: id, title, kind, tier (included / fetch / request / reference-only), origin URL or DOI, terms/licence, size, n subjects or records, what ground truth or labels it has, which of our tasks it serves, used_by_us, notes. Verify each entry from its landing page or API (no memory-only rows; mark unverified rows). (2) datasets/open/: the derived tables this project made (copy from experiments, CC BY 4.0) with a MANIFEST.csv. (3) datasets/fetch.py: list, and fetch subsets of the datasets we use into datasets/local/ (gitignored), respecting the 1.5 GB budget and range reads; metadata only for request-tier sets. (4) datasets/README.md in plain words. (5) Add a Data page (or section) to the site built from catalog.csv, styled like the rest of the site. Metadata research only: download nothing beyond index files, no compute lock needed, contact no one. Never include personal emails of researchers. Start from docs/DATASETS.md and experiments/data_access/. Cover at least: all DREAM packages, OpenNeuro sleep/sedation/anaesthesia/psychedelic sets, Sleep-EDF and other PhysioNet sleep sets, NSRR (account), COGITATE, TMS-EEG/PCI sets, ketamine (Farnes, Zenodo 806176), disorders-of-consciousness sets (Bath, Della Bella), masking/no-report and blindsight data, Human Connectome and anaesthesia fMRI sets.

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

### #32 B4b Theory from the shared gaps

Milestone M3, priority 3.

Draft a theory built first to explain the gaps no current theory explains in the scorecard (#25): temporal integration/postdiction window (C36), which unresponsive brains are conscious (C20), large activity changes with consciousness intact (C42, C44), real-time REM communication (C19). Must also cover the A-graded ledger rows. Same rules as T1: mechanism, necessary and sufficient conditions, >=3 risky predictions no rival makes, at least one testable on open data not yet seen by any agent; seal by hash in experiments/our_theory/. Do not reuse T1's hold-time parameter.

### #36 Score Strange Loop (Hofstadter) on the ledger

Milestone M3, priority 3.

Add a 12th theory to the scorecard: Hofstadter's strange-loop view (Godel, Escher, Bach 1979; I Am a Strange Loop 2007), which says the self and consciousness arise from a self-referential symbol system modelling itself, and come in degrees. Mark explains/compatible/silent/strained/contradicts on all 59 ledger rows, quoting Hofstadter's own words (book page or published interview) for every non-silent cell; where he is silent, say silent, do not extrapolate. Note its relatives already scored (AST, HOT) and the key strains: psychedelic ego dissolution, dreaming with weak self-reflection, minimal-phenomenal-experience reports, infants/animals. Update scorecard.csv and totals.csv via build_scorecard.py.

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

### #5 Zero-shot transfer of 8-10 published measures

Milestone M2, priority 3. Waits for #4.

Fit thresholds on one family (sleep, anaesthesia, DoC) and test on the others for LZ, PCI-like, spectral slope, permutation entropy, wSMI, alpha power, Sitt/Engemann features, criticality. Decisive: any measure with AUC >= 0.80 everywhere moves up; the rest are logged as specific to one state.

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

### #11 Pre-registered multiverse on COGITATE

Milestone M3, priority 4. Waits for #10.

Hash a set of reasonable analysis variants for prefrontal ignition at offset and sustained posterior synchrony, then run them all. Report the share of variants that supports each theory. Note the July 2026 bioRxiv directed-connectivity reanalysis (authors unverified).

### #37 B4f Two-layer theory: basic experience plus a self-loop

Milestone M3, priority 4. Waits for #35.

Draft a candidate where a basic layer (e.g. sustained posterior activity gated by bistability) decides whether anything is experienced, and a self-referential layer (strange loop / self-model, midline and frontoparietal) decides whether there is a reflective 'I'. It must make >=3 risky predictions no rival makes, including a dissociation testable on open data: self-model signals track reports of a sense of self, separately from signals that track whether any experience was present (dream reports with vs without self-presence; psychedelic ego dissolution data if open). Seal by hash; blind-scored with the field in #35.

## In progress (do not duplicate)

- #4 LZ complexity vs spectral slope

- #9 Phi-proxy recovery on known-Phi networks

- #31 Seal and run the open-data prediction of the best candidate

## Done

- #1 Port rules of evidence and dataset leakage check: **tool**, `experiments/rules/RESULTS.md`

- #2 Dataset audit: **data**, `experiments/dataset_audit/RESULTS.md`

- #3 Ground-truth schema: **data**, `experiments/ground_truth/RESULTS.md`

- #8 Surrogate gate: **negative**, `experiments/surrogate_gate/RESULTS.md`

- #12 Verify the plan's (memory) citations: **data**, `experiments/research_sweep/RESULTS.md`

- #16 One sealed open-data test per theory: **negative**, `experiments/theory_tests/RESULTS.md`

- #19 Independent ketamine EEG with delayed report: **negative**, `experiments/data_access/RESULTS.md`

- #20 DREAM database open-access audit: **data**, `experiments/data_access/RESULTS.md`

- #24 B1 Constraint ledger: **data**, `experiments/constraint_ledger/RESULTS.md`

- #25 B2 Theory x constraint scorecard: **data**, `experiments/theory_scorecard/RESULTS.md`

- #21 Chennu propofol set exceeds download budget: **tool**, `experiments/chennu_access/RESULTS.md`

- #27 B4 Draft our own theory: **untestable**, `experiments/our_theory/T1.md`

- #30 Blind ledger scoring of our candidate theories by an agent who did not write them: **negative**, `experiments/blind_scoring/RESULTS.md`

- #13 Standing research sweep: **data**, `experiments/research_sweep/RESULTS.md`
