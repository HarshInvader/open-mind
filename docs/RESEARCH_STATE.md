# Open Mind: research state

A running log of planning decisions: what Fable (the planning advisor) said, and what we decided. Newest first. Results themselves live in each experiment's RESULTS.md and in docs/NEGATIVE_ATLAS.md.

## 2026-11-23: overnight session (coordinator brief)

### AI2 self-model kill test: what follows the void
- **Result:** VOID (`experiments/self_model_agents/RESULTS.md`, Step 1). The planted control TF reversed in 0 of 4 cells, and T in 0 of 4. All 32 trained agents learned blanket suppression, because e·s^g > k for every s ≥ 0.05. The planted floor gated the input, not the action, so it could never produce a reversal.
- **Fable's advice:**
  - The void says nothing about self-models.
  - Do one sealed amendment with a hard stop.
  - The key change is to validate the design with scripted agents before any training:
    - (1) show analytically that every cell has an interior crossover s* (about 0.3 to 0.7), so blanket suppression is not optimal;
    - (2) show that a hand-coded action-gated oracle reverses in 4 of 4 cells, and a hand-coded blanket suppressor in 0 of 4.
  - If the amended run is void again, drop AI2 and log it.
- **Decision:** agreed. The amendment is queued behind tonight's human study. It is not sealed yet.

### Choosing tonight's human-consciousness study
- **Candidates:**
  - **A:** Confidence Database test of the metacognition marker in Thorat & Chopra 2026. That marker rests on one blindsight patient (Persaud 2011).
  - **B:** board #39, a red-team of LZ over the exponent for REM vs N3.
  - **C:** ds005273 neural seen/unseen. At 47.7 GB it does not fit the disk.
- **Header check (column names only, no outcome data):** only 6 Confidence Database sets have a separate trial-wise awareness rating: Jachs_2015 Exp1-3, Mei_2019 Exp1-2 and Rausch_2016. Mazor_2020, Hu_2017, Mazancieux_2018 and the Wierzchon sets do not, despite the info-sheet notes.
- **Fable novelty read on A:** incremental but useful. No multi-dataset, accuracy-matched seen-vs-unseen metacognition test was found. Jachs et al. 2015 (10.1037/xhp0000026) asked the single-study version and found awareness affects type-2 sensitivity far less than type-1. The main confound: rating-defined "unseen" subsets restrict the range of evidence that confidence also uses, so even a plain SDT observer shows seen > unseen. The test must be the excess over a simulated SDT null.
- **Fable plan, round 1:** pick B, with a confirmatory test on the 19 unfetched Sleep-EDF subjects. The primary test was LZ over the exponent plus band powers.
- **Our check:** that test has already been run. Sealed H3 in `experiments/lz_slope/RESULTS.md` gives REM vs N3 delta -0.0002 and wake vs N3 +0.0004, and it is already in the atlas. B fails its own kill test on existing data. We sent this back to Fable to re-decide.

### Fable round 2 (after the H3 fact and the readme facts)
- **#39 closed.** H3 plus the surrogate gate already answer it. The gain is over the exponent alone and is spectral shape. The 19 new subjects would test only whether the exponent is an incomplete summary of the spectrum, not anything about consciousness. **Decision:** agreed. #39 is logged as answered and nothing is run.
- **Option A narrowed.** The 5 Soto-lab sets are closed by prior art: Jachs 2015 asked this question, and Mei 2019 states it is a replication. Their awareness ratings are binary with no stimulus manipulation, and Mei told participants to rate confidence independently of awareness. Rausch_2016 (n = 20, 6 contrasts, continuous scales) is the only usable set. Fable estimated about 50-60% power. Its plan:
  - (1) prior-art read of Rausch & Zehetleitner 2016;
  - (2) a synthetic power gate on the statistic "confidence × visibility interaction in a trial-level logistic of accuracy, minus the same coefficient under a refitted single-evidence null". The gate needs power ≥ 0.80 at a planted AUROC2 excess of 0.05, and FPR ≤ 0.05.
  - Only if both pass: seal, then run.
- **Step 1 done** (PMC4874366, read 2026-11-23). The paper compares meta-d_a of visibility vs confidence by contrast, and conditional rates at a 25% cut. It does not test whether confidence's metacognitive sensitivity depends on visibility level, so the question is not established there. The later Rausch WEV-model papers were not checked (unverified).
- **Step 2 running:** `experiments/metacog_awareness/power_gate.py`, synthetic data only. Early calibration: the single-evidence null alone produces a seen-minus-unseen AUROC2 gap of +0.048. This is Fable's predicted artefact, so a naive seen > unseen comparison would mislead.

### AI2: scripted-agent check, then closed (Fable round 3)
- **Exact check** (`experiments/self_model_agents/oracle_check.py`, 56 cells): the Bayes-optimal stimulus-only agent shows the reversal in 0 of 56 cells (largest 0.017), and the blanket suppressor in 0. An action-gated floor shows it robustly when the floor is well above s*. Fable's earlier pair of checks (s* in 0.3-0.7 with the floor at 0.3) would have conflicted, because a floor at or below s* gives no reversal.
- **Fable's advice:**
  - The reviewer's claim is refuted within this task family.
  - Call it "a threshold above the reward-optimal one", not a "capacity floor".
  - The reversal is still not an awareness marker.
  - Drop the trained-agent amendment: it would only test whether REINFORCE converges.
  - Carry the scope, assumed-reward, Tsushima and metric caveats.
- **Decision:** agreed. AI2 is closed and written up in `experiments/self_model_agents/RESULTS.md` step 2 and the atlas.

### Owner idea: a "hypothesis tournament" of consciousness markers (Fable round 4)
- **Prior art opened** (abstracts):
  - Engemann 2018 (Brain, 10.1093/brain/awy251): about 30 EEG markers cross-site, DoC only, AUC ~0.77.
  - Ma 2024 (HBM, 10.1002/hbm.26586): 380 metrics in 296 DoC patients; relative alpha and delta power were most dependable.
  - Castro, Luppi et al. 2024 (Commun Biol, 10.1038/s42003-024-06858-3): fMRI signatures that generalise across anaesthesia and slow-wave sleep.
  - Luppi et al. 2025 (bioRxiv, 10.1101/2025.03.22.644729): more than 6,000 hctsa features under anaesthesia across species.
  - Berjaga-Buisan 2026 (Cell Rep, 10.1016/j.celrep.2026.117782).
  - Sitt 2014: not opened (unverified).
- **Fable verdict:**
  - The many-marker screens and cross-state generalisation have been done.
  - The only gap is a sealed, subject-held-out, multiplicity-counted screen where each marker must beat a full-spectrum baseline plus phase surrogates across state families. That is our board #5 with our spectral rule, not a new programme.
  - Seen vs unseen should be dropped from it: content markers on trials and state markers at rest are different quantities.
  - Feasible today: sleep (Sleep-EDF; other PhysioNet sets unverified) and propofol (Chennu, ds005620).
  - Infeasible today: ketamine (no open EEG known), DoC (request-only) and matched seen/unseen (per-subject streaming might work; unverified).
  - With only 2 state families, a "survives in ≥3 contrasts" rule cannot be met.
  - Power: Holm over 40 markers needs incremental d_z ≈ 0.9-1.05 at n = 15-20, while our measured incremental effects over the spectrum are about 0.
- **Fable's kill test:**
  - (1) Census: kill unless at least 3 state contrasts each have at least 2 open datasets with n ≥ 20 and a checked licence.
  - (2) Pilot #5's 8-10 published measures on the datasets we hold. Proceed only if a marker gains ΔAUC ≥ 0.05 over spectrum plus surrogates, with CI above 0, in ≥2 datasets.
  - (3) Otherwise publish as the #5 result and stop.
- **Our note:** two of those measures (LZ; time-irreversibility) have already failed the pilot criterion on Sleep-EDF and both propofol sets.
- **Decision:** not opened as a new study. It is folded into #5 as "census, then pilot", ranked second behind the Rausch metacognition test. The census is cheap metadata work and can run next session.

### Tournament: coordinator's prior art, census and final verdict (Fable round 5)
- **Opened** (abstracts unless noted; all added to the library):
  - Aru 2012, Tsuchiya 2015, Duman 2022, arXiv 2510.08736;
  - Lee 2022 (Nat Commun), Casey 2022 (BJA), Frohlich 2022 (Commun Biol), Ugail & Howard 2026, Yaron 2022 ConTraSt;
  - Höhn 2024 (eNeuro, full text) and González 2022.
- **LZ claim downgraded.** Höhn 2024 and González 2022 already report that LZ in sleep is driven by oscillations. Our sleep result is now labelled "confirms and quantifies", in its RESULTS files, the atlas and the site text. What is new is the sealed incremental-AUC test and the phase-surrogate gate. Frohlich 2022 (entropy beats spectral features where oscillations and state dissociate) is recorded as counter-evidence, so the result is limited to typical sleep EEG.
- **Census** (`datasets/catalog.csv`, open human EEG, n ≥ 20):

  | Contrast | Open datasets |
  |---|---|
  | Sleep | many |
  | Propofol | 2 (ds005620, Chennu); DOSE-I is borderline |
  | Ketamine anaesthesia | 0 (subanaesthetic sets only) |
  | DoC, UWS vs MCS raw EEG | 0 open (I-CARE is post-arrest coma; Bath and Paris are on request) |
  | Trial-level seen/unseen | 4 (ds006394, ds001810, ds005273, ds001785) |

  Fable's rule (at least 3 state contrasts with at least 2 datasets each) fails.
- **Fable verdict:**
  - The gap is real on paper but not actionable: the conjunction is unclaimed mainly because the data are not open.
  - The tournament as specified is killed by data availability.
  - Fold the state part into #5 as sleep plus propofol.
  - Seen/unseen is a separate content screen and should be parked.
  - Narrower option: a Casey-style split of disconnected vs unconscious within ds005620, gated on at least 15 subjects having both report classes.
- **Our check on the narrower option.** It fails its own gate on published counts. Bajwa et al. 2025 (PMC12460656) report 52 awakenings in 20 participants: 24 with experience, 5 with no experience, and 23 unarousable or incoherent. The labels are also unreleased. Even if the authors sent the labels, 5 negatives cannot support a split, so no email was sent: a reply would not unblock a viable study.
- **Decision:** the tournament is not opened. Ranking: (1) the Rausch metacognition test, if the power gate passes; (2) #5 rescoped to sleep plus propofol (census, then pilot); (3) a parked seen/unseen content screen.

### Rausch metacognition test: gates, seal and result
- **Fable's pre-seal review** (round 6) said not to seal yet. Its edits:
  - tie-averaged AUROC;
  - rank-map the null onto each subject's observed ratings (floors, ties);
  - skip degenerate cells;
  - neutral verdict labels;
  - drop-count and ScaleOrder checks;
  - a no-lowest-contrast secondary.
  It asked for gate 2: the exact analysis code run on floored, tied synthetic data. **Decision:** all applied.
- **Bug found by gate 2 (first attempt, stopped after 12 datasets):**
  - 2 of 12 nulls were void, and the confidence-accuracy moment z was biased upward;
  - the fitted sc sat at 1.000, its start value. scipy's Nelder-Mead uses a 0.00025 step for a zero start coordinate, so on the step-shaped loss from rank-mapped ratings it never moved.
  - **Fix:** an explicit initial simplex with 0.3 steps. The probe now gives sc 0.60-0.79 (true 0.8) and moment z near 0.
  - Gate 2 was rerun from scratch and passed: null supports 0.017 (all three nulls), void 0; planted 0.98.
- **Fable round 6b (pre-seal):**
  - Fable said to add the gate-2 table and the disclosure to the prereg, and to add a NaN/Accuracy guard to `load()`;
  - it also said to state that inconclusive is likely and that void is terminal.
  - **Decision:** all done, then sealed (commit e5df6c2) and only then the data downloaded.
- **Sealed run: VOID.**
  - Confidence-accuracy moment z = 3.95 (> 3), with sc at its floor (0.068). The single-sample null cannot reach the observed confidence-accuracy correlation (0.341 vs 0.283).
  - Primary p = 0.89 and excess 0.037 [-0.044, 0.142] are not interpreted.
- **Fable round 7 (interpretation):**
  - Only conf-accuracy crosses 3 SD.
  - Several mechanisms fit: post-decisional evidence, d′ drift, lapses, non-Gaussian evidence.
  - The void says nothing either way about awareness.
  - Don't quote the without-lowest-contrast CI.
  - Stop and log: multi-sample confidence is established (2DSD; Rausch WEV, both unverified), and this dataset lacks the precision for the one open question.
- **Decision:** agreed. Written up in `experiments/metacog_awareness/RESULTS.md` and the atlas. Next: #5 rescoped to sleep plus propofol (census, then pilot).

### Task #5: census, prior art, and the redesign (Fable round 8)
- **Census** (`experiments/transfer_5/CENSUS.md`):
  - Sleep qualifies (Sleep-EDF; HMC 151 nights, CC BY 4.0).
  - Propofol fails on open-now data:
    - ds005620 sed2 is unresponsive but mostly conscious (24/29 reports);
    - Chennu's moderate sedation is mostly responsive;
    - increment power is 0-10%.
  - DOSE-I (171 propofol recordings, dense MOAA/S labels, CC BY 4.0) is the only powered propofol set. It carries a Data Use Agreement, so it was not downloaded: it needs owner sign-off.
- **Prior art** (18 opened, 9 new to the library):
  - Ramaswamy 2024 (sleep-trained stager on propofol, AUC 0.55-0.58) is the closest.
  - Lendner 2020 fits slope per contrast, with no shared threshold.
  - Casarotto 2016 uses a pooled PCI cutoff.
  - No one has run per-measure, frozen-cutoff, two-direction transfer with a spectral competitor and a surrogate gate.
- **Fable verdict:**
  - #5 as written is killed: "AUC >= 0.80 everywhere" ignores the threshold; frozen cutoffs across hardware are confounded; the propofol labels are responsiveness.
  - Redesign (b'): fit wake-vs-N3 cutoffs per measure on Sleep-EDF, then ask where each places HMC REM (wake side = follows disconnected experience; N3 side = follows arousal). It has three gates:
    - eligibility (HMC W-vs-N3 balanced accuracy >= 0.80);
    - planted 83/17 mixes;
    - phase-surrogate flag.
  - ds005620 sed2 is a descriptive replication.
  - Kill if fewer than 3 measures are eligible. If all match the spectral baseline: "one axis, spectral".
  - Ask the owner about DOSE-I.
- **Our novelty note:** REM placement for some single measures is already reported (Lendner 2020: slope; Ugail & Howard 2026: LZc, slope and alpha place REM below N2 on Sleep-EDF). What is new is frozen cross-dataset cutoffs, the spectral competitor and the surrogate gate, so this is an atlas-grade result, not a discovery.
- **Decision:** agreed. Planted gate running; then Fable pre-seal review, seal, HMC fetch and run.

### Task #5: pre-seal review, seal, run and result (Fable rounds 9-10)
- **Fable round 9 (pre-seal):**
  - The verdict used raw fractions, so pure mixtures read as "disagree".
  - It was rewritten to the normalised position (REM − N3)/(W − N3), with three-way calls against a ±0.10 band, a comparator fallback (baseline, else exponent) and a viability rule (train BA ≥ 0.80).
  - The planted gate now tests verdict() itself and passed on attempt 3; attempts 1-2 are disclosed.
  - Sealed in 8b08564.
- **Amendment 1 (89e5172):** physionet.org returned 502 for the HMC record list, so the list now comes from the PhysioNet S3 mirror. This was resealed before any data was read.
- **Run:**
  - HMC 151/151 fetched; 143 subjects analysed.
  - ds005620: 20 subjects, 0 skipped.
  - Run under the Mind lock at nice 20.
- **Result:** sealed verdict "measures disagree (vs baseline): rel_delta". All 5 eligible measures put REM on the wake side (0.83-1.04), and every surrogate call is "same". Our placement prediction failed. The ds005620 secondary is ρ = 0.6, p = 0.28 (not confirmed).
- **Fable round 10 (interpretation):**
  - The headline is a transfer table: REM sits with wake, and the information is all spectral. The disagreement verdict is correct by the rule but thin.
  - The ds005620 exponent pattern (REM awake, sed2 N3-like at about 83% reports) is a hypothesis, not a claim.
  - Close #5 and log it in the atlas; no paper.
  - Next: ask for DOSE-I, but first confirm it has per-awakening reports.
  - It did not rank #24.
- **Decision:**
  - #5 closed: RESULTS.md, atlas entry, a site "closed" entry and a Latest-updates item.
  - Ask the owner about DOSE-I, conditional on per-awakening reports.
  - #24 waits until we know whether its ketamine data have per-subject reports.

### Next study after #5 (Fable round 11): nothing unblocked clears the bar
- **Correction:** DOSE-I is not owner-blocked. Zenodo 22145442 v2 is open-access with no login, and the owner accepted its data-use terms on 2026-11-19 (`experiments/experience_benchmark/AUDIT.md`). The #5 census was wrong on this. DOSE-I has MOAA/S and transition labels but no experience interviews (technical report, arXiv 2607.02570).
- **Fable's search** (OpenNeuro GraphQL, Zenodo, Figshare, OSF, PhysioNet) found no open sedation EEG with per-awakening experience reports.
  - ds005620: v1.0.0 only, no labels.
  - DREAM: sleep only.
  - Zenodo 15497531 (Iowa dexmedetomidine/propofol iEEG): no reports.
  - Wisconsin serial awakenings: on IRB request.
  - Turku: no public repository.
- **Prior art against the #5 loose thread:** Casey et al. 2024 (doi:10.1016/j.bja.2023.09.031; the DOI was checked via Crossref). The exponent steepens from disconnected consciousness to unconsciousness on per-awakening reports, in all three conditions.
- **Candidates rejected:**
  - DOSE-I frozen cutoffs: montage Fp2-Fp1/Fz-F7 with unreported filters, a short artefact-prone awake baseline, and an already-known result.
  - DREAM REM report vs no report: about 100 negatives across 7 labs; Bazán Sánchez 2026 gives REM AUROC 0.498.
  - ds005620 bound from group counts: uninformative (2-24 of 24 experience awakenings could be N3-side).
- **Decision:** no study started. Nothing sealed, no lock taken, no data downloaded. Owner actions, best first:
  1. Ask the ds005620 authors for the 52-row (subject, run, report class) table. A calibration test on the 24 experience awakenings needs no download. Kill test: fewer than 16 of them map to clean runs.
  2. Request the Wisconsin serial-awakening data (per-report labels with pre-awakening EEG, or just the exponents).
  3. Finish the Zenodo 806176 email verification.

### Task #5b: sealed before asking, then two data requests sent (Fable round 12)
- **Coordinator approval:** both emails were approved under the owner's email rule, because a study is blocked on outside data.
- **Sealed before any email:** `docs/prereg/2026-11-23_transfer5b_ds005620_report_calibration.md` (commit f718942, hash in HASHES.txt).
  - **Question:** do report-confirmed experience awakenings fall on the N3 side of the frozen exponent cutoff?
  - **Stop:** fewer than 16 experience awakenings on clean runs.
  - **Call:** a 95% Clopper-Pearson interval against 0.5.
- **Planted gate:** passed. Power is low at the expected rate (31% at n = 24), so the likely outcome is "inconclusive". This is disclosed.
- **Fable round 12 pre-seal review:** five must-fix items, all fixed:
  - exposure counts (51 available runs, 44 clean);
  - a duplicate-row stop;
  - a mechanical "not mappable" stop;
  - blind class mapping;
  - subject-string parsing.
  Run non-independence is disclosed.
- **Emails sent (AgentMail, 2026-11-23):**
  - (1) the ds005620 corresponding author (Oslo), asking for the 52-row subject / sed2 run / report class table;
  - (2) the first corresponding author of Casey et al. 2024 (Wisconsin), asking for per-awakening report class, condition and subject, plus either the 20-s pre-report EEG or their exponent, or what an IRB request would need.
  Addresses came from official institution pages. Drafts and the send log are in `.local/outreach_mind_5b/`. No follow-up before 2026-12-03.
- **Owner only:** the Zenodo 806176 verification and the COGITATE account.

## 2026-11-23 (day): new main line from the owner; Fable round 13 ranking
- **Owner direction:**
  - Never sit idle. Data requests are side bets and stay open, including #5b and COGITATE.
  - Marker-vs-spectrum benchmarking has run its course.
  - The main line is now: (a) a constraint ledger scored under sealed rules; (b) tests of theory predictions, not markers; (c) the owner's hypothesis generator (screen fast, confirm on held-out data).
- **Fable round 13: ranked unblocked studies** (all checked open with no login unless marked):
  1. **A sealed, blind, likelihood-scored theory ledger** (track a, no data). It scores P(real outcome | theory) against mirrored outcomes, so elastic theories earn 0 bits. Pilot: 6 theories × 10 split constraints × 3 raters, with toy-theory recovery and placebo-leak gates and α ≥ 0.67. About 3 hours.
  2. **Front vs back without report, Stockart sEEG** (OSF 8QE3A, 29 patients). Does a hit-vs-miss decoder trained on report trials transfer to the no-report stream in frontal contacts, or only in ventral visual ones? Kill test: power from planting 50% of the frontal effect; stop if fewer than 8 patients have frontal contacts. About 1 day.
  3. **A theory-signed hypothesis generator** (track c). Screen on ds006394 (surprise-induced misses), confirm on ds001785 (tactile hit/miss), with known ERPs as positive controls. About 2 days.
  4. **All-or-none vs graded awareness in visibility ratings** (Confidence Database, Rausch 2014/2016 and the PAS sets). This is GNWT's ignition prediction moved to behaviour. Half a day.
  5. **Confidence-model family as the null.** 6 Confidence Database sets have both ratings (Jachs 2015, Mei 2019, Rausch 2016; about 44k trials), but five of them come from one lab. The ceiling is low.
  6. **Supramodal detection in MetaMosquito sEEG.** Low novelty: the authors pre-registered the same question.
  - **Blocked:** COGITATE experiment 2 (account), #5b (replies), ketamine and DoC. DREAM #42 is unblocked but not recommended (marker vs spectrum).
- **Decision:** start item 1 now. Items 2, then 4, then 3 follow in that order. Item 4 moves above 3 because it takes half a day and the data is in hand.
- **Item 1, first steps:**
  - Mirrors written for C05, C08, C11, C14, C17, C21, C28, C31, C32 and C55.
  - Canonical references checked on Crossref.
  - Blinded packets built.
  - Planted gate run: the clean version came out SCORABLE and the planted leak came out VOID.
  - Prereg `docs/prereg/2026-11-23_theory_likelihood_pilot.md`.

### Theory-likelihood pilot result (2026-11-23)
- **Verdict under the sealed rules: SCORABLE.**
  - G1: toy recovery 27/27.
  - G2: placebo bias 0.00 (every placebo rating was 0.5).
  - G3: α = 0.762.
- **Bits on 10 items, 95% CI:**
  - IIT 4.58 [1.70, 7.33]
  - RPT 3.11 [−0.15, 6.14]
  - PP 1.66 [0.21, 3.35]
  - AST 0.94 [−0.85, 2.84]
  - HOT −0.80 [−4.56, 2.86]
  - GNWT −1.09 [−5.59, 3.17]
- **Separated pairs:** IIT ahead of every other theory; no other pair separates. The sealed prediction that IIT, GNWT and RPT would not separate failed.
- **Not a verdict on theories yet.** Three reasons:
  - LLM raters know the outcomes, so theory-specific leakage is unmeasured.
  - The items were chosen as splitting items, and six of the ten are posterior-versus-prefrontal contrasts.
  - Each theory rests on one reference.
- **Write-up:** `experiments/theory_likelihood/RESULTS.md`.
- **Decision:** next is the sealed amendment for the 59-item run. Before rating, it adds a retrodiction split and fictional-twin leak probes. Meanwhile, Fable list items 4 and 3 continue. Item 2 (Stockart) is demoted: the authors already decoded across conditions (PMC12475450), so little is novel.

### Fable item 4 (all-or-none vs graded visibility): prior art read, no-go (2026-11-23, evening)
- **Context:** the Stockart frontal-transfer idea was already dropped (the authors decoded across conditions). Item 4 was next on the list.
- **Prior art** (opened by a Fable agent; all eight added to the library):
  - Sergent & Dehaene 2004: blink ratings look two-state, but under masking they shift gradually.
  - Nieuwenhuis & de Kleijn 2011: the two-state pattern goes away with wagering.
  - Asplund 2014: a mixture model suggests discrete perception.
  - Cohen, Keefe & Brady 2023: one graded model beats the mixture models across tasks, including Asplund's data (27 of 28 people).
  - Rausch, Hellmann & Zehetleitner 2021: graded models fit 5-SOA visibility ratings.
  - Province & Rouder 2012: the conditional-independence statistic.
  - Eiserbeck 2021: 4-point PAS in the blink.
  - Windey 2013: level of processing.
- **Novelty sentence:** at most, a per-subject conditional-independence test against an ordinal-probit null. That is a method increment, not a new question.
- **Fable's planted check** (rough, one setting; script kept in /tmp only):
  - With 3 strength levels the test recovers a planted mixture only 7-33% of the time.
  - With 5 or more levels it recovers it 100% of the time.
- **Why no-go:**
  - The only open blink set with trial-wise ratings (Eiserbeck, OSF e85hn) has 2 lags and 4 categories, so the test has no power on it.
  - The well-powered sets (Rausch_2016, 6 contrasts; Rausch 2021, 5 SOAs) vary masking strength, where GNWT already concedes graded visibility. So a graded result would split nothing.
  - It adds nothing beyond the neural Sergent 2021 single-trial question.
- **Decision:** item 4 closed, nothing sealed or downloaded. Next: the ledger amendment (item 1), with the theory-specific leak probe run first as its kill test. Item 3 (hypothesis generator) follows.

### Ledger amendment, step 1: leak probe designed, reviewed and sealed (2026-11-24)
- **Fable design:** B and E merged, with C as a separate gate.
  - Attach a random, openly disowned "Reported outcome" cue to items the raters cannot know: post-cutoff results or pending outcomes.
  - Measure how far each theory's rating follows the cue.
  - Recognition gate: the 10 pilot items as a positive control; known test items are excluded.
  - Rejected alternatives: fictional twins (they remove legitimate knowledge) and flat misinformation (it fails on famous items and is not honest).
  - Fable's other threats, kept for the 59-item run: generic lean that the liver placebo misses (add a brain-relevant decoy), and the canonical reference not being what raters actually score (add quote-only commitment cards).
  - Expectation: IIT over GNWT/HOT probably keeps its sign but shrinks; IIT over RPT probably does not survive.
- **Items:** a drafting agent read the candidates and checked first-posting dates via the bioRxiv API.
  - Usable: 4 results posted after 2026-07-01, 1 borderline (2026-06-22), and 6 pending outcomes (MEG naps registered report; an adversarial collaboration's planned experiments).
  - Skipped: 9 (pre-cutoff, a replication, or no theory contrast).
- **Pre-seal review** (a fresh Fable agent ran the scoring paths on fake data): 7 must-fix items, all applied.
  - Excluded items and voided instances crashed the scorer.
  - A mislabelled theory id silently gave INCONCLUSIVE.
  - A contrarian rater scored BOUNDED, so BOUNDED is now two-sided and reactance gives INCONCLUSIVE.
  - Bits depend on which side is labelled real, so a logit scale was added and both scales must agree.
  - There was no manipulation check, so BOUNDED no longer licenses scaling on its own.
  - There was no rule for cue-following by the controls, so a Q/Z control flag was added.
  - Should-fix items applied: cluster bootstrap, P07 made self-contained, P03 and P08 cues removed, pending-item exclusion, reproducible seeds.
- **Planted gate:** 0 false positives in every no-leak scenario. A 0.40-bit IIT leak is caught 100% of the time and a ceiling-masked one 99%. A true null reads INCONCLUSIVE 60% of the time.
- **Sealed:** `docs/prereg/2026-11-24_theory_leak_probe.md`. Next: the recognition gate, then the rating packets.

### Leak probe result: LEAK-BOUNDED, scaling not licensed (Fable interpreting review)
- **Run:**
  - Recognition passed (28/30). P01 and P05 were excluded, leaving 9 items.
  - All 18 rating instances completed. The first launch hit a gateway 503; the 15 missing instances were rerun in batches of 6, as first answers, not re-requests.
- **Result:** LEAK-BOUNDED on both scales, with no control flag.
  - Every L_t is within ±0.02 bits, and every CI is inside ±0.07 bits/logit.
  - D = +0.012 bits [−0.040, +0.063].
  - Z was recovered 36/36 times in NOTAG. Q was exactly 0.5 everywhere.
  - Details: `experiments/theory_leak/RESULTS.md`.
- **Fable's read:**
  - **What it shows:** raters ignore a disowned cue. None of the 864 TAG rationales mentions it.
  - **What it doesn't show:** without a manipulation check, it says nothing about raters' beliefs and nothing about the memory path behind the pilot's IIT lead.
  - **Why the CIs are so narrow:** real instances vary far less than the planted 0.48-logit noise, and many cells sit at exactly 0.5.
  - **Errors:** none found that would change the verdict. Fable recomputed the counterbalancing, Q, Z recovery, α and elastic fraction from the raw ratings.
- **Scaling to 59 items: no.** α is 0.79 (passes ≥ 0.67), but the elastic fraction is 0.63 (fails < 0.5).
- **Forecast bits (descriptive only, P02–P04):** GNWT +1.06, IIT −0.81. This is the reverse of the pilot, but it rests on 3 items.
- **Decision:**
  - The next ledger study is the **manipulation check**: the same packets, with the cue framed as believed ("assume this outcome was observed") and a per-item belief probe.
  - **Kill:** any L ≥ 0.25 bits / 0.43 logit, or D ≥ 0.28 / 0.48, with CI > 0. That demotes the ledger.
  - **Void:** belief does not follow the cue.
  - **In parallel:** the hypothesis generator (ds006394 screen, ds001785 confirm).
  - The 59-item amendment is parked.

### Manipulation check sealed (2026-11-24T04:06:50Z)

The leak probe showed that raters ignore an outcome cue that is labelled random. The check now asks whether they also ignore one that is stipulated as observed.
- **Prereg:** `docs/prereg/2026-11-24_theory_leak_manipulation_check.md`.
- **Packets:** the 12 leak-probe TAG packets, changed in two places only:
  - the disowning note is replaced by "take it as the outcome that the experiment observed", with the same closing "Rate what the theory implies";
  - a closing belief probe asks for q (the gate) and q_own (descriptive).
- **Planted gate:** `planted_mc.json`, calibrated on the leak-probe data (instance SD 0.25 logit). No leak gives BOUNDED 0.90 and never DOMINATED. A 0.40-bit IIT leak gives DOMINATED 1.00; a uniform 0.25-bit leak gives DOMINATED 0.96.
- **Fresh Fable pre-seal review:** "seal after fixes". All 9 must-fix items were applied; they are listed in the prereg header.
- **Kill:** LEAK-DOMINATED in either analysis (passing instances, or all valid instances).
  - Branch D demotes the ledger and the IIT lead.
  - Branch L-only drops AI rating of famous findings but does not demote the IIT lead.

### Manipulation check result: LEAK-BOUNDED, ledger not demoted (2026-11-24)
- **Run:** 12 of 12 instances returned in two batches of 6, with no 503s. Every instance passed the belief gate on 9 of 9 items (q_cued 0.95–0.97). Z scored 72/72, and Q was exactly 0.5.
- **Result:** LEAK-BOUNDED in both the primary and sensitivity analyses, on both scales.
  - Every L_t is between +0.01 and +0.06 bits. Only PP's CI excludes 0: +0.062 [+0.015, +0.118], still inside the 0.15 limit.
  - D = +0.010 bits [−0.055, +0.081].
- **Compared with the disowned cue:** stipulating the outcome adds a small, uniform pull of about +0.03 bits, largest for PP. It does not favour IIT.
- **Limit:** belief was stipulated, not held. q_own moved only to 0.57 toward the cued side. The memory path stays untested.
- **Rationales:** 1 of 648 "why" strings matched the sealed regex, and that match was a false positive ("reported experience").
- **Decision:** neither kill branch fired, so the ledger is not demoted. The 59-item amendment stays parked on the elastic-fraction rule. Next is the hypothesis generator (ds006394 screen, ds001785 confirm).
- **Fable interpreting review** (no computational error; the point estimates were recomputed from the raw files):
  - **May claim:** a stipulated outcome moves every theory by less than 0.12 bits and IIT-vs-GNWT/HOT by less than 0.08 bits on these 9 items. A text-level outcome cue, disowned or stipulated, does not produce the IIT lead.
  - **May not claim:**
    - that raters hold steady under belief, because no q_own reached 0.9;
    - that the leak stays small under real recall, because the exploratory pull rises with q_own;
    - that the pilot's IIT lead is leak-free;
    - that the bound generalises, because Fable carries most of the pull.
  - **Wording:** MC_RESULTS was softened: "believed" became "stipulated", and "closes the gap" became "narrows".
  - **Next ledger test:** a knowledge-cutoff difference-in-differences (AI-only). Compare models that know an item with models that don't, on items published between their cutoffs, and subtract the same contrast on the 9 unknowable items.
- **Details:** `experiments/theory_leak/MC_RESULTS.md`.

### Hypothesis generator, step 0: prior art and data kill test. ds006394 killed as the discovery set (2026-11-24)
- **Prior art:** read by a Fable research agent. 7 papers were added to the library: Leong 2026, Pereira 2021, Sanchez 2020, Schröder 2021, Förster 2025, Dembski 2021 and Förster 2020.
  - **Established, do not redo:**
    - VAN/AAN and N140 track awareness within each sense.
    - The P3b is larger for seen stimuli but depends on report (Schröder 2021).
    - Late cross-modal decoding of detected vs undetected stimuli exists in MEG (Sanchez 2020, replicated in a second sample).
    - The surprise-induced blindness/deafness effect is explained by a novelty P3 (Leong 2026).
  - **Open:**
    - A preregistered, theory-tagged component screen on ds001785. Pereira 2021 reports a decoder and a 0.5–1.5 s mixed model, but no named components, time-resolved maps or spectral contrasts.
    - EEG transfer from a visual set into touch. No EEG study found does this.
- **Kill test (trial counts, from behaviour files only): FAILED.** Counts are in `experiments/hypothesis_generator/trial_counts.csv`.
  - **Too few unaware trials:** surprise-induced misses have a median of 3 per subject (visual) and 1 (auditory); all misses, a median of 9 and 6.
  - **Weak recording:** 16-channel OpenBCI at 125 Hz with an earlobe reference.
  - **Confound:** misses are confounded with surprise and trial number.
  - **So:** ds006394 cannot carry a many-candidate screen.
- **Replacement checked: ds001810** (attentional blink; Biosemi, 64 channels, 512 Hz; about 40 subjects with both visits).
  - **Clean blocks:** the two pre-tDCS blocks per subject are free of tDCS artefact.
  - **Trial counts:** in 3 subjects sampled, one pre block had 23–59 lag-3 T2 errors and 32–95 correct, given T1 correct.
  - **Caveat:** T2 is scored as correct or incorrect identification, not seen/unseen, so "miss" includes seen-but-misidentified trials.
- **Proposed redesign (not sealed):**
  - **Screen:** ds001810 pre blocks, lag-3 T2 correct vs incorrect given T1 correct.
  - **Confirm:** ds001785 (tactile hit vs miss), with candidates signed by theory.
  - **Positive controls:** known effects within each dataset.
  - **Prior-art expectation:** early negativities will not transfer across senses (topography), while late effects may. A clean result would therefore mostly separate "late, content-free" from "early, sense-specific" signatures.
  - **Next:** read Reteig et al. on ds001810 (what EEG they report), then the strongest kill test: does any screen survivor beat a label-shuffled null on held-out ds001810 subjects before touching ds001785?

### Ledger knowledge-cutoff DiD: power check. DiD underpowered with current items (2026-11-24)
- **Models we can call:**
  - Current: Fable 5.2/5.1/5, Opus 5.5/5, Sonnet 5.5, Haiku 5.5.
  - Older: Opus 4.8/4.7, and Haiku 4.5 via OpenCode, with a published cutoff of Feb 2025.
  - Only Haiku 4.5's and Opus 5.5's (June 2026) cutoffs are documented. The recognition gate would sort knowers from non-knowers empirically anyway.
- **Ledger items whose outcome first became public between those cutoffs (roughly 2025 to mid-2026): 0 of 59.**
  - By Crossref year of key sources, only C16 and C17 cite a 2025 paper (the DREAM consortium, Nat Commun 2025).
  - Both outcomes were established earlier: Siclari 2017, and C16's 2000 BBS source.
  - P02–P04 (Jul–Oct 2026) fall after every callable model's cutoff, so they are unknowable to all of them, not split between them.
- **Verdict: DiD underpowered with current items.** With 0 informative items (2 at most if the dating were generous, from one source cluster), there is no item-level variance to bootstrap. A 0.25-bit leak cannot be detected at any reasonable power.
- **Decision: parked.** It reopens only if we build at least about 10 new items from findings first published between Feb 2025 and the newer models' cutoffs, in several independent clusters, and the recognition gate splits the models on them.

### Site deploy deferred (2026-11-24)

The hub repo (`open-citizen-science`) has uncommitted `dist/` changes that belong to other threads. Per the coordinator, nothing was rebuilt over them. These Mind-side changes go live at the next hub build:
- the leak-probe and manipulation-check `site/updates.json` entries;
- the library additions (+8 earlier, and the P02–P04 key results);
- the paper pages that follow from them.
