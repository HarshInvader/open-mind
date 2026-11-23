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

### Rausch metacognition test: pre-seal gate 2 (in progress)
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
  - Gate 2 is being rerun from scratch. Nothing in the data or decision rule changed; no real data has been seen.
