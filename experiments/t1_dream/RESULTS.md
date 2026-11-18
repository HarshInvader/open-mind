# T1 sealed test on DREAM Tononi Serial Awakenings (task #31)

Agent: mind-t1-test. Date: 2026-11-18. Prereg: `PREREG.md` (identical copy `docs/prereg/2026-11-18_t1_dream_tononi.md`), sha256 `5272a97655c8fc89cb0212926315a5e1954bfc58cf43d076f5b787f8eecc387f`, sealed 2026-11-18T11:09:27Z together with all code, before any EEG feature met a label.

## Verdict: REFUTED (no recency effect of the stated size)

**T1's DREAM prediction failed.** It said N2 awakenings with experience follow a longer stretch free of posterior OFF-periods than awakenings with no experience. That does not hold here, beyond what sleep-depth measures already explain, and the without-recall test also failed:
- the effect is near zero (log-odds 0.08 per within-subject SD; 90% CI -0.18 to 0.35);
- the confidence interval excludes the strong effect T1 implies (odds ratio 2 per SD, log-odds 0.69), so the sealed equivalence rule returns REFUTED, not INCONCLUSIVE;
- none of the four primary tests came close to significance;
- the without-recall awakenings did not look like experience awakenings.

This closes T1's strong form on scalp data. Weaker recency effects, and the 250 ms hold time itself, remain untested (see Limits).

## Numbers

Sample: 237 of 287 N2 awakenings (97 experience E, 93 no experience NE, 47 without recall WR) from 35 of 39 subjects; all from one lab (Wisconsin, 257-channel EGI). All effects are within subject: features are centred per subject, and p-values come from label permutations within subject.

| Test (one-sided, Holm over 4) | Estimate | 90% CI | 95% CI | p | Holm threshold | Rejected |
|---|---|---|---|---|---|---|
| TA recency, E vs NE, beyond Model A (log-odds per SD) | 0.081 | [-0.177, 0.349] | [-0.227, 0.407] | 0.316 | 0.0125 | no |
| TB timing at fixed count (real minus median of 1,000 timing-only surrogates) | 0.015 (real 0.081, surrogate 0.066) | | | 0.451 | 0.025 | no |
| TC posterior minus frontal recency | -0.134 | [-0.498, 0.282] | [-0.601, 0.354] | 0.685 | 0.05 | no |
| TD without recall vs no experience | 0.037 | [-0.391, 0.343] | [-0.471, 0.421] | 0.403 | 0.0167 | no |

- **Verdict rule applied:** TA's 90% CI lies inside (-0.693, +0.693), giving REFUTED (rule 2). The recall-specific rule 3 did not apply, because TA was not significant.
- **Secondary (pre-stated, not part of the verdict):** dropping the first awakening of each night (a sleep-onset proxy; 88 E / 76 NE / 39 WR) gives the same verdict. TA 0.038 [90% CI -0.241, 0.377], TB -0.005, TC -0.179, TD -0.155.
- **Single features (descriptive):** within-subject AUC for E vs NE.
  - The baselines behave as known: higher values go with no experience.
    - delta5: 0.468
    - delta10: 0.460
    - count10: 0.447
  - Other features:
    - exp10: 0.546
    - clock_h: 0.582
    - awak_idx: 0.583
    - logL_post: 0.526
    - logL_front: 0.553
- **OFF-period yield:** the detector found no posterior OFF-period in 47% of E, 39% of NE and 38% of WR windows. Those windows have recency fixed at the 10 s cap. Mean posterior OFF-periods per 10 s window: 0.86 (E), 0.85 (NE), 0.92 (WR).
- **Planted checks (before sealing, synthetic EEG, `planted_results.json`):**
  - Detector: recall 0.98, precision 0.99, decoy rejection 0.96, median OFF-end error 76 ms.
  - At the planned n of 287, with a true OR 2:
    - PASS 0.90;
    - false PASS under the null 0.01;
    - false PASS on shuffled labels 0.02;
    - REFUTED 0.94 under the null and 0.95 in the recall world.
  - At OR 1.5 the test is underpowered (PASS 0.42), so the claim was resized to OR 2 before sealing.
- **Power at the realised sample** (`power_realised.json`; run after sealing, before the analysis; labels used only for class counts):
  - PASS 0.70 with a true OR 2 effect;
  - REFUTED 0.88 with no effect, and 0.78 in the recall world;
  - false PASS 0.00.

  So PASS was somewhat below the planned 0.8 at the sample actually obtained. A null result was still very likely to be detected.

## What this means for T1, IIT and higher-order theories

- **T1:** its one open-data prediction failed. The final stretch before waking does not decide report, beyond delta power, slow-wave count, sigma, beta, exponent and time of night, at the scale T1 claims. The three-class test gives no support either. Without-recall awakenings sit with no-experience awakenings (and the secondary estimate is negative), the pattern a recall account expects; but TD's interval is wide, so it does not clearly favour recall either. `T1.md` itself says that if P1-P3 fail, T1 reduces to RPT plus bistability. P1 has now failed.
- **IIT / posterior hot zone:** this test does not address it. IIT does not predict recency or timing. Posterior delta (in Model A) showed only the weak expected direction (AUC 0.46-0.47), which was not tested inferentially here.
- **Higher-order / frontal accounts:** not supported either. The posterior-minus-frontal contrast pointed slightly frontal (-0.134), and frontal recency had a slightly higher single-feature AUC (0.553 vs 0.526). Both are far from significant and were not tested as a frontal hypothesis.
- **Recall vs experience:** the without-recall class did not separate from no-experience on this measure. This is uninformative about recall accounts, because the recency measure itself carried no signal.

## Prior exposure (as declared in the prereg)

- Zhang & Wamsley and De Gennaro YoungAdults were used by #16 and are exposed. They were not used.
- No agent in this project had computed EEG features on the Tononi set before this.
- The Tononi set is the discovery data of Siclari et al. 2017 (doi:10.1038/nn.4545) and 2018 (doi:10.1523/jneurosci.0855-18.2018). This is why delta and slow-wave count were placed in Model A.

## Deviations after sealing (all before any result was seen)

1. **Download cap hit, and some files could not be read; all exclusions are technical and label-blind.**
   - Feature extraction streamed 906 MB (logged), plus about 75 MB in 24 failed reads that the log recorded as 0 bytes. I stopped it at the sealed 0.95 GB cap.
   - Not fetched or not usable:
     - Subjects 37-39 (26 awakenings): budget, plus an EDF header with unequal sampling rates.
     - Subject 23 (5 awakenings): 256-channel files with no Cz row, which crash the sealed channel code.
     - 19 awakenings: the mid-stream reader locked onto a false deflate block start and errored.
   - I wrote fixes for the last two, then reverted them unused so the sealed code ran as hashed.
   - Excluded by class: E 27, NE 14, WR 9.
2. **`analysis.py` output fix.** It crashed while writing `features.csv`, after the tests were computed but before anything was printed. I changed one line (`errors="ignore"` on a column drop), re-sealed it (2026-11-18T13:49-13:50Z) and reran.
3. **Realised-sample power.** `power_realised.py` and `run_analysis.sh` were added and sealed at 2026-11-18T12:51:47Z, before the analysis.

## Limits

- **Scalp proxy.** The OFF-period detector is a half-wave plus 25-45 Hz suppression, validated only on synthetic data. It found no posterior OFF-period in about 40-47% of windows, so recency was censored at 10 s in those. A real OFF-period effect could be invisible to this proxy. The verdict is about the proxy at the scalp.
- **Effect size.** Only OR ≥ 2 per SD is refuted. A smaller recency effect (for example OR 1.3) is compatible with the data (95% CI up to 0.41, about OR 1.5).
- **Window.** The window is 10 s, so H (about 250 ms) is not tested.
- **One lab.** There is no transfer claim.
- **Self-reported class.** WR rests on self-report.
- **Data handling.**
  - Raw bytes were never written to disk.
  - The ROI signal cache (`roi/`, 16 MB) was deleted after `features.csv` was written.
  - The folder keeps only features and logs (under 1 MB).

## What would make the untested parts testable

- Intracranial or high-density data with validated OFF-periods (multi-unit silence) before awakenings with reports. No such open set is known to us.
- Wake masking data with a timed probe (T1 P3, Andrillon-style). Whether these are public is unconfirmed.

## Files

- Prereg and code:
  - `PREREG.md`
  - `t1lib.py`
  - `features.py`
  - `analysis.py`
  - `planted.py`
  - `tailzip.py` (range-request tail reader for deflated zip members)
  - `power_realised.py`
- Outputs:
  - `results.json`
  - `features.csv`
  - `planted_results.json`
  - `power_realised.json`
  - `method_check.json`
  - `fetch_log.jsonl`
  - `ledger_rows.csv`
