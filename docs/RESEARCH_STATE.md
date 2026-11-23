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
