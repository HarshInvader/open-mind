# Pre-registration: T1 settling-window test on DREAM Tononi Serial Awakenings (N2)

Agent: mind-t1-test   Task: #31   Date: 2026-11-18
Revises `experiments/our_theory/PREREG_DRAFT.md` after `docs/fable_review_1.md` (section 3, "Changes before sealing").
Sealed together with `t1lib.py`, `planted.py`, `features.py`, `analysis.py`, `tailzip.py`. `analysis.py` refuses to run unless all six hashes are in `docs/prereg/HASHES.txt`. An identical copy is at `docs/prereg/2026-11-18_t1_dream_tononi.md`.

## 0. What changed from the draft

| Fable's requested change | What this prereg does |
|---|---|
| Richer Model A | Model A = last-5 s and last-10 s posterior 1-4 Hz power, last-10 s slow-wave count, sigma (12-15 Hz), beta (16-30 Hz, last 5 s, arousal), 1-30 Hz spectral exponent, clock time of the awakening, awakening index in the night (section 5) |
| PASS needs H2 or a count-matched timing test | PASS needs the recency test TA **and** the count-matched timing test TB **and** the three-class test TD (section 7) |
| Pre-stated posterior-minus-frontal contrast | Test TC: coefficient of posterior recency minus that of frontal recency, in one model |
| Three-class test with "experience without recall" | Test TD, primary. T1 predicts WR awakenings look like experience (longer posterior recency than no-experience) |
| One fixed ROI, one re-reference, within-lab results | One lab only (all data are from Wisconsin), so every result is within-lab. ROI fixed below. One average reference |
| Holm | Holm over the four primary tests, family-wise one-sided alpha 0.05 |
| 200+ timing-only surrogates that keep wave shape | TB uses 1,000 timing surrogates per awakening: the same detected events (same durations and shapes), placed at random non-overlapping positions |
| Smallest effect of interest and an equivalence test | SESOI = conditional odds ratio 2.0 per within-subject SD of log recency (section 7; chosen by the power analysis in section 9). REFUTED via equivalence (90% CI inside ±log 2) |
| Detector closer to OFF-periods | OFF-period = negative half-wave plus 25-45 Hz suppression (ratio ≤ 0.8), planted-answer check on synthetic EEG with known OFF-periods and decoy waves (section 8) |
| Declare prior exposure | Section 1 |
| Delete "scalp null counts less" | Deleted. A null here counts at full weight within the stated effect size |

## 1. Prior exposure (declared before sealing)

- **This project.** Task #16 (mind-3) computed posterior and frontal 1-4 Hz power before N2 dream vs no-dream reports on DREAM Zhang & Wamsley 2019 and De Gennaro YoungAdults (132 awakenings), and found an exploratory sign flip between sleep-onset and later N2. Those two labs are **exposed** and are not used here, not even as a fold (lead's instruction, 2026-11-18). No agent in this project has computed any EEG feature on the Tononi Serial Awakenings set before this prereg: a repo search finds only metadata uses (dataset audit, access tables, ground-truth counts). I (mind-t1-test) have seen: the Tononi metadata (file names, per-subject class counts, clock times), the EDF header, and the raw signal of one awakening (`s01_ep01`) in `method_check.py`, which checks the byte-level reader and where the alarm sits. No label was joined to any EEG.
- **Literature.** This set is one of the DREAM sets analysed for EEG in the DREAM paper, and the Wisconsin serial-awakening data are the discovery data of Siclari et al. 2017 (doi:10.1038/nn.4545, verified) and Siclari et al. 2018 (doi:10.1523/jneurosci.0855-18.2018, verified), which reported lower posterior low-frequency power and fewer/smaller posterior slow waves before NREM dream reports. **So a delta-power effect is already known here; that is why delta power and wave count sit in Model A, and why only effects beyond them count.** Whether the deposited 287 awakenings are exactly the papers' awakenings is not known. This test is therefore low-severity for "posterior slow waves relate to dreaming" (not tested) and full-severity only for what T1 adds: recency and timing beyond count and power, and the without-recall class.

## 2. Hypotheses (T1, `experiments/our_theory/T1.md`)

T1: the report describes what posterior cortex held just before waking; presence depends on the final stretch being free of OFF-periods, not on total slow-wave activity.

- **TA (recency).** Longer time since the last posterior OFF-period (L_post) before Experience (E) than before No experience (NE), beyond Model A. Positive coefficient.
- **TB (timing at fixed count).** The TA coefficient exceeds what the same events give when only their timing is randomised. Positive.
- **TC (posterior minus frontal).** The posterior recency coefficient exceeds the frontal recency coefficient in one model. Positive. (A frontal/HOT or workspace account predicts the reverse or no difference.)
- **TD (without recall, primary).** Before "Without recall" (WR: the subject reported having experienced something but could not recall content) posterior recency is longer than before NE, beyond Model A. Positive. **This is the test that separates T1 from a recall account**: if recency indexes recall rather than experience, WR awakenings look like NE (coefficient ≤ 0).

## 3. Data

- DREAM set 13, Tononi Serial Awakenings, v3 (doi:10.26180/23306054.v3; Figshare article 23306054; CC BY 4.0). Labels from `experiments/dataset_audit/dream_records.csv`, Set ID 13, **Amendment 2 only** (the CSV holds three amendments of this set; 809 rows = 261 + 261 + 287; use 287). Trap for others: counts like "344 experience / 309 no experience" for this set are triple-counted.
- 287 N2 awakenings with EEG, 39 subjects: 124 E, 107 NE, 56 WR. Ground truth: delayed report (L2).
- 257-channel EGI HydroCel GSN, 500 Hz, 121 one-second records per file; file end = the awakening.
- **Download:** only the last 12 s of each EDF, read from the zip by HTTP range with a mid-stream inflate (`tailzip.py`; tainted bytes masked; verified byte-exact against a full download in `method_check.json`). Expected ≈ 0.9 GB fetched in total, hard cap 0.95 GB in `features.py`; raw bytes stay in memory and are never written to disk. Saved per awakening: ROI signals only (about 30 MB total).
- **Exclusions** (applied label-blind in `features.py`): fetch or parse failure; fewer than 5 of 9 good channels in either ROI; ROI-mean signal beyond ±400 µV anywhere in the 12 s. Excluded counts by class are reported.
- **Sleep onset.** #16 found the sign of the delta relation flips at sleep-onset N2. The set gives no time since sleep onset. Pre-stated: all awakenings are used in the primary test, with clock time and awakening index in Model A; a secondary analysis drops the first awakening of each night (awakening index 1), the closest available proxy for sleep-onset N2. If primary and secondary disagree in verdict, this is reported and the primary stands.

## 4. Preprocessing

1. Last 12 s of the file (file time [-12, 0] s). Analysis window **[-11, -1] s**. The header says 121 one-second records for a 120 s awakening file; in the one file inspected (`method_check.json`, no label) the last record is near-flat (median channel SD 0.82 µV vs 9-24 µV in the 10 s before), so it is padding and the window ends where the recording ends. Reader check: the mid-stream inflate reproduced all 4,215,107 untainted bytes of that file's tail exactly (0 mismatches); the 161 tainted bytes were all in the first 29 KB of output, far before the 12 s needed, and were all masked.
2. Band-pass 0.3-45 Hz (Butterworth order 4, zero phase) at 500 Hz.
3. Bad channel: SD over the 12 s < 0.5 µV or > 200 µV.
4. **One re-reference**: average of the good channels within 90° of the vertex on the package's own `.sfp` layout (sphere fit), including Cz (the recording reference).
5. Resample to 128 Hz (polyphase, with its anti-alias filter).
6. **Fixed ROIs** (the 3 GSN electrodes nearest each 10-05 site, by angle from the sphere centre, MNE GSN-HydroCel-257 vs standard 10-05 montages; computed before any data):
   - Posterior (P3, Pz, P4): E98, E87, E86; E101, E100, E129; E152, E153, E162.
   - Frontal (F3, Fz, F4): E35, E39, E40; E22, E14, E21; E3, E4, E223.

## 5. Measures (`t1lib.py`)

- **Half-waves:** negative half-waves (zero crossing down to up) of the 0.5-4 Hz ROI-mean signal, 0.25-1.0 s long, trough inside the window.
- **HF suppression ratio:** 25-45 Hz band power (ROI channels, squared, averaged, 100 ms moving mean) over the central half of the half-wave, divided by its median over the window.
- **OFF-period:** a half-wave with |trough| ≥ the subject's median |trough| (all of that subject's half-waves, label-blind) **and** HF ratio ≤ 0.8.
- **Slow wave (for the count covariate):** |trough| ≥ the subject's 75th percentile.
- **L_post / L_front:** seconds from the up-crossing of the last OFF-period to the window end (10 s if none), analysed as log(L + 0.25).
- **Timing surrogates:** the same OFF-periods (same count and durations) placed uniformly at random without overlap in the window, 1,000 per awakening (seed 0); surrogate L from the gap after the last event.
- **Model A:** delta5 = log10 1-4 Hz power, posterior ROI mean, [-6, -1] s; delta10 = same over [-11, -1] s; count10 = posterior slow-wave count; sigma = log10 12-15 Hz, [-11, -1]; beta5 = log10 16-30 Hz, [-6, -1] (arousal); exp10 = 1-30 Hz log-log slope, [-11, -1]; clock_h = hours after 18:00; awak_idx = awakening number in the night.
- All predictors are **centred within subject** (label-blind, all three classes together) and then z-scored. Effects are within-subject.

## 6. Statistics

Logistic regression (Newton-IRLS, ridge 1e-4), intercept + Model A + test column(s).
- **TA:** E vs NE, coefficient of z(log L_post). p from 2,000 label permutations within subject (one-sided). CIs (90%, 95%) from 2,000 subject-cluster bootstraps.
- **TB:** statistic = TA coefficient minus the median coefficient over 1,000 surrogate datasets (each replaces every awakening's L_post by one timing surrogate and refits). p = (1 + #surrogate coefficients ≥ real) / 1,001.
- **TC:** E vs NE with both z(log L_post) and z(log L_front); statistic = posterior minus frontal coefficient; permutation p and bootstrap CIs as TA.
- **TD:** WR vs NE, coefficient of z(log L_post); permutation p and bootstrap CIs as TA.
- **Family:** {TA, TB, TC, TD}, Holm, family-wise alpha 0.05, one-sided.
- No held-out-lab split is possible (one lab); nothing is trained and then tested, so `check_split` is not needed. The within-subject permutation null is the guard against subject effects.

## 7. Verdict rules (applied in this order; `t1lib.verdict`)

SESOI delta = log(2) (odds ratio 2 per within-subject SD of log recency).
1. **PASS:** TA, TB and TD all rejected under Holm. **STRONG PASS:** PASS and TC rejected too.
2. **REFUTED (no recency effect of the stated size):** TA's 90% CI lies inside (−log 2, +log 2) (equivalence, TOST at 0.05), or TA's 95% CI lies wholly below 0.
3. **REFUTED (recency tracks recall, not experience):** TA rejected under Holm and TD's 90% CI upper bound < log 2 (non-superiority: WR is not shifted toward E by the stated effect).
4. **INCONCLUSIVE:** anything else, logged with the partial pattern (for example "recency without timing specificity").

T1 on TC: T1 expects TC positive; a TC failure with PASS is reported as "posterior specificity not shown".

What each outcome means for rivals: IIT/hot-zone accounts predict posterior slow-wave activity matters (TA) but make no timing (TB) or without-recall (TD) prediction of their own beyond "WR had experience". A recall/higher-order account predicts TA may pass but TD fails (WR ≈ NE). A pure arousal account predicts TA vanishes once Model A is in.

## 8. Planted checks (must pass before this is sealed; `planted.py`, results in section 9)

1. **Detector on synthetic EEG with known OFF-periods** (10 subjects × 20 awakenings; pink background, 25-45 Hz activity gated to 0.35 amplitude during OFF-periods; decoy slow waves with no gating). Pass: recall ≥ 0.8 (trough within ±100 ms), precision ≥ 0.8, decoy rejection ≥ 0.8, median error of the OFF-period end ≤ 100 ms.
2. **Full pipeline on synthetic datasets with the real structure** (39 subjects, real per-subject E/NE/WR counts; a sleep-depth confound pushes reports toward lighter sleep in every world):
   - null world (labels depend on depth only): P(PASS) ≤ 0.05;
   - label-shuffled T1 datasets: P(PASS) ≤ 0.05;
   - T1 world at OR 2: P(PASS) ≥ 0.8;
   - null world: P(REFUTED) ≥ 0.8; recall world at OR 2: P(REFUTED) ≥ 0.8.
   Reduced resampling in simulation (400 permutations, 400 bootstraps, 300 surrogates).

## 9. Power analysis (synthetic, before any label touched EEG)

From `planted_results.json` (`planted.py 100`; 100 synthetic datasets per world, 50 shuffled), run before sealing and before any real label met any EEG feature.

**Detector check: passed.** Recall 0.98, precision 0.99, decoy rejection 0.96 (91 decoys over the amplitude gate), median OFF-end error 0.076 s, r(true vs detected log L) = 0.91. An earlier version with a 75th-percentile amplitude gate for OFF-periods failed (recall 0.54), so the OFF gate was moved to the median and the HF criterion does the selecting; the 75th percentile is kept only for the slow-wave count covariate.

| World | PASS + STRONG PASS | REFUTED (either kind) | INCONCLUSIVE | Mean TA estimate |
|---|---|---|---|---|
| null (depth confound only) | 0.01 | 0.94 | 0.05 | 0.09 |
| T1 at OR 2, labels shuffled | 0.02 | 0.94 | 0.04 | -0.01 |
| T1 at OR 1.5 | 0.42 | 0.37 | 0.21 | 0.48 |
| **T1 at OR 2** | **0.90** | 0.04 | 0.06 | 0.77 |
| T1 at OR 2.5 | 0.98 | 0.01 | 0.01 | 0.93 |
| recall at OR 1.5 | 0.00 | 0.96 | 0.04 | 0.16 |
| **recall at OR 2** | **0.00** | **0.95** | 0.05 | 0.25 |
| recall at OR 2.5 | 0.00 | 0.90 | 0.10 | 0.27 |

Per-test rejection rates at OR 2 (T1 world): TA 0.99, TB 0.97, TC 0.91, TD 0.91. Null world: TA 0.06, TB 0.03, TC 0.01, TD 0.03 (these are single-test rates; the family-wise false-PASS rate is 0.01).

**Resized claim.** At OR 1.5 per SD the test cannot reach PASS or REFUTED reliably (0.42 / 0.37). At OR 2 both are reachable with power ≥ 0.9, and the false-PASS rate is ≤ 0.02. So the SESOI is set to OR 2: **this test confirms or refutes only a strong recency effect (OR ≥ 2 per within-subject SD of log recency, roughly AUC ≥ 0.69 for a single standardized predictor), which is what T1's strong claim (the final stretch decides presence) implies. Weaker recency effects are left untested.**
Two caveats on the simulation: the synthetic OFF-periods are clean (HF gated to 35%), so real-data power is lower if the scalp suppression is weak; and in the recall world most REFUTED verdicts come from rule 2 (the E-vs-NE recency effect is diluted below OR 2), not rule 3.

## 10. Secondary (reported, not part of the verdict)

Excluding awakening 1 of each night; per-class means of all features; within-subject single-feature AUCs; fraction of awakenings with no posterior OFF-period.

## 11. Known limits, stated before data

- Scalp OFF-period proxy: the 25-45 Hz suppression at the scalp may be weak or muscle-dominated; the detector is checked only on synthetic data. If most awakenings have no detected OFF-period, L is capped at 10 s and power falls; the fraction is reported.
- One lab, so no transfer claim.
- The analysis window is 10 s; T1's hold time (about 250 ms) is far shorter, so this tests the final-stretch claim, not H itself.
- The SESOI (OR 2 per SD) is large. Effects smaller than this are not tested; REFUTED means "no recency effect as large as T1's strong form implies", not "no effect".
- WR is a self-report category; some WR awakenings may be confabulated feelings of having dreamt.
