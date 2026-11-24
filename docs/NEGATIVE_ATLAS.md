# Negative atlas

Closed routes, each with the effect size the test could have caught. Empty until the first tests land.

## AI-rated theories mostly do not commit on post-cutoff findings (post-cutoff ledger, 2026-11-24)

- **Route closed (for now):** "test whether IIT's lead in the AI-rated theory ledger carries over to findings published after the raters' cutoff" with a pool of 15 recent findings. Too few split the theories.
- **Data:** 15 kept post-cutoff findings (12 clusters) and 10 famous findings; 3 models × 2 runs; blind and informed arms. Sealed prereg `docs/prereg/2026-11-24_theory_postcutoff_ledger.md`.
- **Result:** UNINFORMATIVE. 4/15 findings split the theories, in 3 clusters (bar: 8 and 6). 89% of post-cutoff cells sat in p 0.4–0.6. Gates passed. Hindsight BOUNDED, D_H −0.006 [−0.061, 0.049].
- **Descriptive:** IIT lead +0.50 on famous items, −0.14 [−0.29, 0.02] on all post-cutoff items, in the same run.
- **What it could catch:** planted lead 0.55 with no elastic items: SURVIVES 80%; null: false SURVIVES 1–6%. Planted IIT-only hindsight of 0.40 bits: caught 100%.
- **Splitting-first follow-up (stop rule fired):** a blind selector, choosing from 45 new findings, found only 5 with any theory committing |p − 0.5| ≥ 0.25 (maximum 0.30). See `experiments/theory_splitfirst/RESULTS.md`.
- **Not closed:** human raters; purpose-built adversarial studies.
- **Details:** `experiments/theory_postcutoff/RESULTS.md`.

## AI theory raters do not follow a disowned outcome cue (theory leak probe, 2026-11-23)

- **Route closed:** "LLM raters bend a theory's predicted outcome toward an outcome they are told was reported", for a cue they are told is random, on unknowable findings (post-cutoff results and pending outcomes).
- **Data:** 9 items in 6 clusters; 3 models (Fable 5.2, Opus 5.5, Sonnet 5.5); 12 TAG and 6 NOTAG instances. Sealed prereg `docs/prereg/2026-11-24_theory_leak_probe.md`.
- **Result:** LEAK-BOUNDED on both scales. Every per-theory leak is within ±0.02 bits, with 95% CIs inside ±0.07 bits/logit. IIT-versus-access D = +0.012 bits [−0.040, +0.063]. No control flag.
- **What it could catch:** the planted gate on the kept items caught a 0.40-bit IIT-only leak 100% of the time, a 0.25-bit leak across all theories 96%, and a ceiling-masked 0.75-logit IIT leak 92%.
- **Not closed:**
  - leakage under a credited cue (there was no manipulation check);
  - leakage from memory of famous outcomes, which is the pilot's risk;
  - items where theories commit (63% of cells here were near-silent).
- **Details:** `experiments/theory_leak/RESULTS.md`.

## T1 settling-window theory: posterior OFF-period recency does not predict N2 dream reports (task #31, 2026-11-18)

- **Route closed:** "the time since the last posterior OFF-period before waking decides whether an N2 awakening yields experience", in its strong form (odds ratio of 2 or more per within-subject SD of log recency, beyond delta power, slow-wave count, sigma, beta, spectral exponent, clock time and awakening index).
- **Data:** DREAM Tononi Serial Awakenings (Wisconsin, 257-channel), 237 of 287 N2 awakenings (97 experience, 93 no experience, 47 without recall), 35 subjects. Sealed prereg `experiments/t1_dream/PREREG.md` (sha256 5272a976..., 2026-11-18T11:09:27Z).
- **Result:** recency coefficient 0.081 (90% CI -0.177 to 0.349; one-sided p 0.32). The CI lies inside ±0.693 (OR 2), so the sealed rule gives REFUTED. Timing beyond count: +0.015, p 0.45. Posterior minus frontal: -0.134, p 0.69. Without recall vs no experience: 0.037, p 0.40.
- **What it could catch:** at this sample the pipeline gave PASS in 70% of synthetic datasets with a true OR 2 effect and REFUTED in 88% with none (`power_realised.json`).
- **Not closed:** recency effects weaker than OR 2; true (intracranial) OFF-periods; T1's 250 ms hold time itself, which a 10 s window cannot test. The scalp OFF proxy (half-wave plus 25-45 Hz suppression) found no posterior OFF-period in 38-47% of windows.
- **Details:** `experiments/t1_dream/RESULTS.md`.

## LZ complexity adds nothing over the spectrum in sleep (mind-2, 2026-11-18)
Sleep-EDF, 45 subjects, subject-held-out. LZ adds no AUC over the exponent plus 6 band powers. Wake vs N3: +0.0004 [-0.0003, 0.0012], p = 0.19. REM vs N3: -0.0002, p = 0.16. Over the exponent alone, wake vs N3: +0.007, below the 0.01 mark. LZ fails the surrogate gate: 86% of phase-randomised wake surrogates are called awake, and 97% of its separation is spectral. Phase-normalised LZ carries no stage information (AUC 0.47-0.48). Detectable effect: P2 had 85% power at delta AUC 0.0005 (W vs N3). Caveat: the W vs N3 baseline is at ceiling (0.988-0.996). Propofol sets (ds005620, Chennu) are not yet run. Novelty: confirms and quantifies earlier reports that LZ in sleep is driven by oscillatory and spectral content (González 2022, doi:10.1016/j.neuroscience.2022.04.025; Höhn 2024, doi:10.1523/ENEURO.0259-23.2024). What is new is the sealed incremental-AUC test against a full spectral baseline and the phase-surrogate gate. Details: `experiments/lz_slope/RESULTS.md`, `experiments/surrogate_gate/RESULTS.md`.

## Time-irreversibility ("arrow of time") EEG measures add nothing over the spectrum (mind-ne, task #41, 2026-11-19)

- **Route closed (sleep):** scalp-EEG time-reversal asymmetry as a consciousness marker beyond the spectrum. Two forms were tested:
  - higher-order waveform asymmetry, our variant (`tra_x`, excess over phase surrogates);
  - the published second-order lagged-correlation form (`ne2`; after Camassa 2024 doi:10.1038/s41598-024-74649-1, Berjaga-Buisan 2026 doi:10.1016/j.celrep.2026.117782).
- **Data:** Sleep-EDF, 60 subjects; Chennu propofol, 20; ds005620 propofol, 15. All subject-held-out, under the sealed prereg `docs/prereg/2026-11-18_nonequilibrium_vs_spectrum.md`.
- **Result:**
  - `tra_x` is spectrum-free (it passes the gate) and separates wake from N3 (AUC 0.70). It does not separate REM from N3 (AUC 0.50), and it adds at most +0.002 AUC over the exponent plus band powers anywhere (Holm p ≥ 0.55). So it is an arousal or waveform marker, not a consciousness marker.
  - `ne2` alone gives AUC 0.43 to 0.56 and does not replicate on scalp EEG.
- **What it could catch:** P2 found 80% power at d = 0.2 (ΔAUC about 0.0002) in Sleep-EDF wake vs N3, and 100% at d = 0.4 in both sleep contrasts.
- **Not closed:**
  - Propofol: power was 10% (Chennu) and 0% (ds005620) at d = 0.4.
  - Source-level, high-density or OU-model estimators of second-order irreversibility.
  - Irreversibility in intracranial data.
- **Details:** `experiments/nonequilibrium/RESULTS.md`.

## T4 (GNWT extension, posterior bifurcation): headline prediction undecidable on Stockart; theory parked (mind-ne, 2026-11-19)

- **Route closed (for this dataset):** testing "late VVC high-gamma is a two-state mixture at fixed intensity without report" (T4 P1) on Stockart et al. 2025 (OSF 8QE3A) by distribution shape.
- **Why:** planted check with real no-report trial counts (72/48 per level, 16 patients). With fair graded rivals (normal and bounded skew-normal) the pipeline passes 0% of planted two-state data at d′ 1.0-1.5, 10% at d′ 2, 100% at d′ 3. The paper's hit-vs-miss AUROC (about 0.8, best patients) implies d′ ≈ 1.2. No null passed (graded normal, skewed, heavy-tailed, drift, leaky accumulator, accumulator-to-bound).
- **Method warning:** the draft pipeline, with a free skew-normal as the only rival, "found" two states in graded data with none. Unbounded skew-normal fits on about 60 trials predict held-out data badly; any mixture-vs-unimodal likelihood test needs a stable rival.
- **Not closed:** T4 itself; P2 (misses vs correct rejections, delayed report), which was not run on real data; intracranial bimodality with more trials per level.
- **Details:** `experiments/our_theory/t4_planted/RESULTS.md`.

## Within-person N2 markers do not separate experience from no experience (task #42, stopped 2026-11-20)

- **Route closed (partly):** EEG markers as within-person predictors, at fixed stage (N2), of whether an awakening yields a report of experience. Tested here: posterior spectral markers only (gamma/delta ratio, gamma, delta). For all three, a within-person AUC of 0.60 or more is excluded.
- **Evidence:**
  - **Michalak et al. 2026, PLoS Biol (doi:10.1371/journal.pbio.3003683); open features, Zenodo doi:10.5281/zenodo.15372992, CC BY 4.0.** 660 N2 awakenings (432 experience, 228 none), 48 people, 41 with both classes; 256-channel EEG, log power over 90-120 s before the alarm, 13 posterior electrodes. Our sealed amendment 5 and `michalak_check.py` (sha256 a6f1f137…, 2026-11-20T01:03:27Z) were fixed before any label was read. Within-person pair AUC (95% CI):
    - ratio 0.512 [0.449, 0.580], one-sided p 0.35;
    - gamma 0.481 [0.414, 0.559];
    - delta 0.507 [0.445, 0.562].

    The sealed reading is OTHER, not "null settled": two bounds fall just outside the pre-set [0.43, 0.57] band. Pooled between-person AUCs are higher for delta (0.576 [0.517, 0.628]) and the ratio (0.562), consistent with pooled figures carrying between-person differences.
  - **Siclari/Tononi serial awakenings (DREAM Tononi set), our task #31.** 35 people, N2: posterior delta within-person AUC 0.46-0.47, in the expected direction but small. This was not tested inferentially (`experiments/t1_dream/RESULTS.md`).
- **Prior art:**
  - Bazán Sánchez 2026 (doi:10.13140/RG.2.2.14388.00642). The DREAM Figure 5 workflow gives within-lab AUROC 0.498 and lab-held-out 0.493 (NREM spectral), and 0.498 and 0.470 (REM catch22). Lab identity is decodable from the same features at 0.81-0.95.
  - Wong et al. 2020, Dream Catcher (doi:10.1093/nc/niaa006). A blinded, within-person NREM spectral null: 9 people, 54 recordings.
  - Aamodt et al. 2023 (PMC9871639). Markers track stage, not report; LZ at N2 p = 0.79.
- **What it could catch:** within-person AUC above about 0.58 (ratio) or 0.56 (gamma, delta). Smaller effects are not excluded.
- **Not closed:**
  - within-person effects below about 0.56-0.58;
  - non-spectral and integration markers (wSMI, LZ, PE, HFD) at N2 within person;
  - other windows, such as the 20 s before waking.
- **Why #42 stopped:** after this prior art, the only open part (hypothesis-driven markers, within person, N2, across labs) was judged too thin for its cost. The label-blind DREAM extraction was stopped at 170 of 452 Rome records. **DREAM labels were never opened**, so the sealed #42 plan (prereg and amendments 1-5) remains unspent and could still be run blind later.
- **Details:** `experiments/experience_benchmark/michalak.json`, `experiments/experience_benchmark/NOVELTY.md`.

## No-report single-trial bifurcation is undetectable at realistic separation on Cohen and Sergent counts (killed 2026-11-20)

- **Idea:** an outside, sealed test of single-trial bimodality at fixed stimulus strength on two public no-report EEG datasets (Cohen 2024, doi:10.1093/cercor/bhae415; Sergent 2021, doi:10.1038/s41467-021-21393-z).
- **Kill test:** the T4 planted two-state pipeline at each dataset's real counts, planted mixture at d' 1.0-1.5 (expected d' about 0.95 from Sergent's report AUC > 0.75). Rule: power below 80% kills.
- **Result:** 0 of 50 simulated studies passed (each cell 0/10; one-sided 95% upper bound 0.26). Passes at d' 3. More trials (Cohen) did not help.
- **Lesson:** the bottleneck is state overlap, not sample size. Do not attempt single-trial bimodality on scalp EEG at near-threshold separation with this pipeline. The originating lab's mixture results (Sergent 2021; Boyer 2026, doi:10.64898/2026.06.17.732590) have no published planted check either.
- No real data was opened. Details: `experiments/bifurcation/RESULTS.md`.

## Self-model AI2 kill test: void, planted check failed (2026-11-23)

- **Test:** does a trained stimulus-only controller show the Tsushima reversal, with a planted visibility-floor agent as the positive control? Sealed `docs/prereg/2026-11-21_self_model_kill_trained_control.md`.
- **Result:** void. Both agents learned to suppress at every strength (reward-optimal in all four sealed cells), so neither could reverse (0 of 4 cells each).
- **Lesson:** a planted floor must gate the action, not only the input, and cells must make blanket suppression costly. Do not reuse these four cells.
- **Closed (step 2, exact, no training):** the Bayes-optimal detect-then-suppress agent shows the reversal in 0 of 56 cells (largest 0.017). A blanket suppressor shows it in none. An action-gated floor set above the reward-optimal threshold shows it robustly. So the reversal flags a mis-set threshold (capacity limit, wrong costs or another objective, which this model cannot tell apart), not detection-gating as such. It is not a marker of awareness-gated control either. The trained-agent amendment was dropped: it would only test whether REINFORCE converges.
- **Details:** `experiments/self_model_agents/RESULTS.md` (steps 1 and 2), `oracle_check.py`.

## Awareness-linked metacognition vs a single-evidence observer: void, null misfit (Rausch 2016, 2026-11-23)
- **Route tested:** at fixed contrast, does confidence track accuracy better on high-visibility trials than a single-evidence SDT observer predicts? This is the "knowing when you are right" marker in Thorat & Chopra 2026.
- **Data:** Rausch & Zehetleitner 2016 (Confidence Database), 20 subjects, 6,300 trials. Sealed prereg `docs/prereg/2026-11-23_metacog_awareness_rausch2016.md` (commit e5df6c2).
- **Result: void (terminal).** The fitted null misfits the confidence-accuracy correlation (z = 3.95; moment z [3.95, 2.36, 0.39, -2.61]), even with confidence noise at its floor (sc = 0.068). Not interpreted: p = 0.89, AUROC2 gap excess 0.037 [-0.044, 0.142].
- **What it could catch:** gate 2 gave 98% "supports" at a 0.05 excess and 42% at 0.03; the null false-positive rate was 1.7%.
- **Lesson:** a single-sample SDT null is inadequate for confidence in this paradigm. Check a null against the known confidence-model literature (2DSD, WEV) before sealing.
- **Not closed:** whether an excess survives a WEV-type null. That needs a several-times-larger dataset with both ratings on every trial.
- **Details:** `experiments/metacog_awareness/RESULTS.md`.


## Frozen sleep cutoffs place REM with wake, and nothing beyond the spectrum (task #5, 2026-11-23)
- **Route tested:** do consciousness measures (exponent, LZ, PE, band powers, spectral entropy, DFA, wSMI) agree on where REM sits, if their wake-vs-N3 cutoffs are frozen on one lab (Sleep-EDF) and applied to another (HMC, 143 subjects)? The spectral baseline and phase surrogates are the competitors. Sealed prereg `docs/prereg/2026-11-23_transfer5_rem_placement.md` (8b08564; amendment 1 in 89e5172).
- **Result:**
  - **Transfer:** 5 of 9 measures transfer (HMC BA 0.81-0.95). Spectral entropy, DFA and alpha are hardware-bound. wSMI (2 channels) fails even within Sleep-EDF.
  - **Placement:** all 5 put REM on the wake side, at positions 0.83-1.04 (baseline 0.875).
  - **Surrogates:** every surrogate call is "same", so no measure carries REM information beyond the power spectrum.
  - **Sealed verdict:** "measures disagree", but only relative delta differs from the baseline, by degree and not by side.
  - **Prediction:** REM in between or on the N3 side. It failed.
- **Lesson:** at a wake-vs-N3 cutoff, REM simply reads as "no slow waves". This tells you nothing about experience. Frozen cutoffs for spectral entropy, DFA and alpha do not survive a hardware change.
- **Not closed:**
  - REM vs wake at its own cutoff;
  - the unsealed hint that the exponent calls propofol sed2 N3-like while calling REM awake (ds005620, n = 20, group-level reports only).
    - It is weakened by prior art: Casey et al. 2024 (Br J Anaesth, doi:10.1016/j.bja.2023.09.031) found the exponent steepens from disconnected consciousness to unconsciousness on per-awakening reports, under dexmedetomidine, propofol and sleep.
    - DOSE-I cannot test it: it has responsiveness labels only and no interviews.
    - Testing it needs ds005620's per-awakening labels (not released) or the Wisconsin data (on request).
- **Details:** `experiments/transfer_5/RESULTS.md`.

## Attentional-blink T2 identification screen: invalid, P3b gate failed on held-out (hypothesis generator, 2026-11-24)
- **Route tested:** do theory-tagged EEG signatures beyond the known P3b and posterior N2 track lag-3 T2 identification (correct vs incorrect, given T1 correct) in held-out subjects? The targets were frontal late positivity, global field power and late posterior positivity. A pass would have licensed a transfer test into touch (ds001785, hit vs miss).
- **Data:** OpenNeuro ds001810 pre-tDCS blocks, range-read T2-locked epochs (8,391 trials, 1.2545 GB). 42 eligible subjects, split 21 discovery and 21 held-out. Sealed prereg `docs/prereg/2026-11-24_ab_t2_identification_killtest.md` (2026-11-24T09:55:23Z, commit e391fe1), applying a Fable pre-seal review.
- **Result: INVALID (terminal; the line is closed, and no redesign of this test will be run).**
  - **Discovery:** no target survived (AUC 0.489–0.499). The P3b was 0.530.
  - **Held-out:** the P3b gate failed, at AUC 0.491 [0.468, 0.512], p = 0.78. The posterior N2 was 0.495, and the P1/N1 were null.
  - **Descriptive decoder:** 0.529 [0.507, 0.548], which cannot earn a pass.
  - ds001785 was skipped.
- **What it could catch:** on the real epochs with shuffled labels, false PASS occurred in 0 of 200 runs. A planted 1.5 µV P3b/N2 was recovered 50 of 50 times. A planted 1.0 µV frontal effect beyond the P3b passed 18 of 20 times.
- **Lessons (untested explanations for the failed gate):**
  1. **Measure basis.** The whole-epoch mean was chosen to avoid a baseline that holds the T1 response, since T1 comes 275 ms before T2. It subtracts a broad late P3b from itself, while T1-locked activity still overlaps the window. In a lag-3 blink design, fetch pre-T1 samples so a clean baseline is possible.
  2. **Outcome label.** "T2 identification" mixes guesses into correct and seen-but-misnamed trials into incorrect, which may dilute the seen/unseen contrast far below published effects. Prefer datasets with a visibility or detection report.
  3. **Alignment.** The planted check validates only the steps after preprocessing, not the alignment of range-read epochs to the T2 event code. Add a label-free alignment check before sealing, such as evoked T1/T2 latencies against the stream onset.
- **Not closed:** whether this dataset carries the standard T2 P3b effect under a pre-T1 baseline. Testing that would be a new study, and is deliberately not pursued after a sealed failure.
- **Details:** `experiments/hypothesis_generator/ab_out/result.json`, `docs/RESEARCH_STATE.md` (Hypothesis generator, steps 1–3).

## Authors' N2 window at a fixed stimulus: KILLED in report trials (Cohen 2024 data, 2026-11-24)
- **Route tested:** does Cohen et al. 2024's fronto-central N2 (250–290 ms, electrodes 1–11 and 17–19), which they read as a report-free awareness marker, separate seen from unseen when the stimulus is held fixed? Masked faces at SOA 50 ms, report block.
- **Data:** OSF 6d5av, range-read face-locked epochs (5,079 trials, 223,983,900 bytes). 24 held-out subjects, excluding the authors' 15 window-defining pilots. Sealed prereg `docs/prereg/2026-11-24_cohen_fixed_soa_killtest.md` (2026-11-24T18:18:22Z, commit 9bf289c), after two Fable pre-seal reviews.
- **Result: KILLED** (calibrated: KILLED fired in 3% of runs with a planted 1 µV effect).
  - The N2 was +0.15 µV seen − unseen [−0.94, +1.20], AUC 0.498, Holm p 0.67, with 10/24 subjects in the predicted direction. Without the P3b electrodes: +0.25 µV.
  - In the same run, the P3b gate passed (+3.28 µV) and the VAN passed (−1.16 µV [−1.54, −0.80], 22/24). The P1 control flag fired (AUC 0.525, two-sided p 0.03).
- **What it means and does not:**
  - It replicates the authors' own report-condition finding: no N2 when the P3b overlaps.
  - It does not test their no-report claim, which needs trial-level awareness without report.
  - In the pilot set the N2 leaned the predicted way (−1.24 µV, INCONCLUSIVE).
- **Lesson:** a fronto-central window that overlaps the P3b's onset cannot be tested for awareness in report trials, even with the shared electrodes removed. The VAN, which comes earlier and sits posterior, is the testable candidate.
- **Not closed:** the N2 in no-report trials (no labels); the VAN's report-independence.
- **Details:** `experiments/cohen_fixed_soa/RESULTS.md`, `out/result.json`.
