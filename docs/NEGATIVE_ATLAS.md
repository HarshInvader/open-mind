# Negative atlas

Closed routes, each with the effect size the test could have caught. Empty until the first tests land.

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

