# Pre-registration: where do published EEG measures place REM sleep, using wake-vs-N3 cutoffs frozen on another dataset? (board #5, redesigned, 2026-11-23)

## Question
Does each published measure, with its cutoff frozen on wake vs deep sleep (N3) in one dataset, put REM sleep on the wake side or the N3 side in an independent dataset?
- **Wake side:** follows disconnected experience. REM usually carries vivid dreams.
- **N3 side:** follows arousal or behavioural state.
- **Also asked:** do the measures disagree with a frozen full-spectrum baseline, or is there only one spectral axis?

**Why this replaces #5 as written** (`experiments/transfer_5/CENSUS.md`, Fable round 8 in `docs/RESEARCH_STATE.md`):
- **Propofol labels:** the open propofol sets have no unconscious state. ds005620 sed2 is unresponsive, but 24 of 29 informative awakenings reported experience. Chennu's moderate sedation is mostly responsive.
- **Power:** for increments over the spectrum it is about 0-10% on those sets.
- **The old criterion:** "AUC ≥ 0.80 everywhere" ignores the threshold, so it is not a zero-shot test.

REM is the powered, open stand-in for "unresponsive but experiencing". ds005620 sed2 is kept as a descriptive replication.

## Prior art (opened; `docs/library/library.json`, topic tag "Task #5 transfer")
- **Ramaswamy 2024** (10.1371/journal.pone.0304413): a sleep-trained multivariate stager tested on propofol and sevoflurane reached AUC 0.55-0.58. One model, one direction, no per-measure test.
- **Lendner 2020** (10.7554/eLife.55092): the spectral slope separates wake from N3, REM and propofol, but with a separate classifier per contrast and no shared threshold.
- **Ugail & Howard 2026** (10.1007/s00422-026-01049-1): on Sleep-EDF, LZc, slope and alpha order N2 vs REM below 0.5 (REM looks less awake than N2).
- **Höhn 2024**: narrowband slope best separates REM. **Frohlich 2022**: cross-population transfer within sleep.
- **Our own:** LZ and time-irreversibility add about 0 over the spectrum (`docs/NEGATIVE_ATLAS.md`).

**What is new here:**
- per-measure cutoffs frozen on one dataset and applied unchanged to another;
- REM placement scored against a frozen full-spectrum competitor;
- a phase-surrogate flag;
- sealed thresholds.

Expected value: an atlas-grade table, not a discovery.

## Data
- **Fit: Sleep-EDF Expanded** (ODC-BY 1.0). 60 subjects, first night, up to 40 seeded epochs each of W, N3 and R. W comes from within 30 min of the sleep period. Derivations Fpz-Cz and Pz-Oz at 100 Hz (`experiments/nonequilibrium/raw`, from `experiments/lz_slope/fetch.py`).
  - **Exposure:** W and N3 features from these epochs were used in earlier studies (LZ, slope, band powers, irreversibility). Sleep-EDF REM features for the new measures have not been computed.
- **Test: HMC sleep staging v1.1** (PhysioNet, CC BY 4.0). All 151 nights.
  - **Epochs:** the same seeded rule, up to 40 each of W, N3 and R.
  - **Derivations:** F4-C4 = (F4-M1) - (C4-M1) and C4-O2 = (C4-M1) - (O2-M1), resampled 256 to 100 Hz (`fetch_hmc.py`).
  - **Status:** fetched only after sealing; no HMC signal has been seen. Before sealing, only the file listing, one EDF header (channel labels, 1-s records at 256 Hz) and the first lines of one scoring file were read.
  - **Montage caveat:** the two HMC derivations share C4 with opposite sign, which adds a common component to the between-channel measure (wSMI). The eligibility gate is meant to catch montage effects like this.
- **Replication (secondary): OpenNeuro ds005620** (propofol).
  - **Epochs:** awake eyes-closed (two 30-s epochs, 130-190 s) vs sed2 (the last 30 s of each sed2 run).
  - **Derivations:** Fpz-Cz and Pz-Oz, the same as Sleep-EDF (`extract_ds.py`).
  - **Status:** run after sealing.
- **Clean-epoch rule:** after detrend and a 40 Hz low-pass, peak-to-peak ≤ 500 µV and SD ≥ 1 µV on both channels.

## Measures (`measures.py`; all scale-free; no per-subject normalisation)
1. Spectral exponent (log-log OLS slope, 1-40 Hz).
2. Lempel-Ziv complexity (LZ76, median-binarised).
3. Permutation entropy (order 3, lag 1).
4. Spectral entropy (1-40 Hz).
5. Log relative delta power (1-4 Hz).
6. Log relative alpha power (8-12 Hz).
7. Log relative beta power (15-30 Hz).
8. DFA exponent.
9. wSMI between the two derivations (κ = 3, τ = 4 samples; King et al. 2013 weighting).

**Baseline:** a full-spectrum competitor. It is an LDA on the exponent plus six log relative band powers (delta, theta, alpha, sigma, beta, 30-40 Hz), standardised on the fit data, with equal priors.

Measures were picked from those benchmarked in the prior art. PCI (it needs TMS) and the composite Ψ were left out.

## Analysis (`analyse.py`; all scripts and the Sleep-EDF fit features are hashed with this file)
1. **Fit:** per measure, the sign and the Youden-optimal cutoff on pooled Sleep-EDF W vs N3 epochs (at most 40 per subject per stage). Fitted and literature signs are both printed; a mismatch is reported, not overridden.
2. **Viable in-dataset:** the measure's Sleep-EDF fit balanced accuracy is ≥ 0.80. Measures below this "fail in-dataset" and are not called hardware-bound.
3. **Eligible:** viable, and the frozen cutoff's subject-averaged balanced accuracy on HMC W vs N3 is ≥ 0.80 (subjects with ≥ 5 clean W and N3 epochs). Viable but ineligible measures are hardware-bound.
4. **Normalised REM position** per measure, on HMC subjects with ≥ 5 clean W, ≥ 5 clean N3 and ≥ 10 clean REM epochs:
   - **Definition:** pos = (REM − N3) / (W − N3), where each term is the subject-mean share of that stage's epochs on the wake side of the frozen cutoff. 0 means like N3; 1 means like W.
   - **Why normalise:** raw wake fractions depend on each measure's accuracy, and pos does not (a W/N3 mixture with share m gives pos = m).
   - **CIs:** a 95% CI from one joint 2000-sample subject bootstrap, shared by all measures so that differences are paired.
   - **Placement:** "wake side" if the CI lower bound > 0.5; "N3 side" if the CI upper bound < 0.5; otherwise "in between".
5. **Comparator:** the full-spectrum baseline if it is eligible, otherwise the exponent if eligible, otherwise none. For each other eligible measure, the paired bootstrap CI of the position difference (measure − comparator) gives one of three calls:
   - **same:** the CI lies inside ±0.10;
   - **different:** the CI lies wholly outside ±0.10;
   - **inconclusive:** otherwise.
6. **Surrogate:** every measure is recomputed on one multichannel phase-randomised copy of each REM epoch (spectrum and cross-spectrum kept), with the same frozen cutoffs. The paired CI of (real − surrogate) position gets the same three-way call; "same" means spectral.

## Decision rule (primary)
- **Killed (hardware-bound):** fewer than 3 viable measures are eligible. The cross-dataset cutoff table is then published as the result (Fable's next-best).
- **Killed (no comparator):** neither the baseline nor the exponent is eligible.
- **Measures disagree on REM:** at least one eligible measure is "different" from the comparator. Each is reported with its placement and surrogate call. A measure that is "different" from the comparator and whose surrogate call is also "different" carries REM information beyond the spectrum. If its surrogate call is "inconclusive", that question is unresolved. The gate gives no evidence that this outcome is reachable for these measures, which were all spectral in the gate.
- **One axis, spectral:** every other eligible measure is "same" as the comparator.
- **Inconclusive:** otherwise (none different, at least one inconclusive).

## Secondary (reported, not gating)
- **Sleep-EDF REM** placement with the same (in-sample) cutoffs.
- **ds005620:** the wake-side fraction in awake and sed2 for every measure (no W/N3 anchors exist in this set, so raw fractions are reported). If at least 3 eligible measures have sed2 data, the Spearman correlation between their HMC REM positions and their sed2 wake-side fractions is computed. `extract_ds.py` stops if Fpz, Cz, Pz or Oz is missing from any header (they are present in sub-1010's header). Prediction: ρ > 0, meaning measures that call REM "awake" also call sed2 "awake". With about 9 measures this is descriptive.

## Gate (passed before sealing; `planted.py`, `planted.json`)
The gate uses Sleep-EDF W and N3 only, with subjects split in half. Cutoffs are fitted on half A. In half B, pseudo-REM sets are built per subject from real epochs, 17 W + 3 N3 (mix 0.83) and 3 W + 17 N3 (mix 0.17). **Attempt 1-2 requirements** (superseded by attempt 3 below), for every measure eligible in half B (at least 3):
- the 0.83 mix placed on the wake side and the 0.17 mix on the N3 side;
- the recovered fraction within 0.05 of the value expected from that measure's own half-B accuracy, mix × P(wake side | W) + (1 - mix) × P(wake side | N3);
- the purely spectral measures (exponent, band powers, spectral entropy, baseline) flagged "spectral" when the pseudo-REM surrogates are phase-randomised copies;
- a positive control for the flag: no measure flagged "spectral" when each pseudo-REM set is paired with surrogates of the opposite mix.

**Disclosed:** attempt 1 (`planted_attempt1.json`) required the raw mix to be recovered within 0.10. DFA (0.673 vs 0.83) and permutation entropy (0.323 vs 0.17) missed, because a measure with imperfect accuracy cannot recover the raw mix by construction. All 16 placements were already correct. The check was replaced by the expected-fraction check, and the surrogate positive control was added, before any REM or HMC data were touched.

**Attempt 2 (`planted_attempt2.json`)** passed those checks. **Fable's pre-seal review** then found that the verdict rule itself, which used raw wake fractions, returned "measures disagree" on pure W/N3 mixtures, and that the gate never tested `verdict()`. The analysis was changed to the normalised position, three-way calls, the comparator fallback and the in-dataset viability rule above.

**Attempt 3 (`planted.json`, passed; mixes 0.83, 0.5 and 0.17).** It checks:
1. placement for 0.83 and 0.17;
2. position within 0.05 of the mix;
3. spectral measures with surrogate "same";
4. the opposite-mix surrogate control giving "different";
5. `verdict()` returning "one axis" on all three pure mixtures;
6. `verdict()` returning "measures disagree … lz" when LZ's pseudo-REM values are swapped for its values in the opposite mix.

| | Mix 0.83 | Mix 0.5 | Mix 0.17 |
|---|---|---|---|
| Eligible in half B | 7 measures + baseline | same | same |
| Ineligible | rel_alpha (BA 0.77), wSMI (0.64): fail in-dataset | same | same |
| Positions | 0.843-0.857 | 0.476-0.514 (spectral entropy, at 0.476, was called "N3 side" because its CI fell just below 0.5; placement was not required at 0.5) | 0.144-0.170 |
| Verdict, pure mixture | one axis | one axis | one axis |
| Verdict, LZ shifted | disagree: lz | (not run) | disagree: lz |
| Opposite-mix surrogate control | 8/8 "different" | (not run) | 8/8 "different" |

**Note:** LZ, permutation entropy and DFA were also spectral in the gate, in line with our earlier surrogate result. The positive control tests the flag logic, not a real non-spectral measure; no non-spectral measure here separates W from N3 well enough to serve as one. HMC epochs are fetched with a 2-s margin and resampled with linear-trend padding, so resampling edges fall outside the epoch.

## Prediction
"One axis, spectral", or a disagreement only among spectral measures. We also expect most measures to place REM in between or on the N3 side: REM's EEG is wake-like in band power but not in slope (Lendner; Ugail & Howard).

## Limits stated in advance
- **REM is not verified experience on each epoch.** Report rates in REM are high but not 100%, and HMC has no reports.
- **N3 is not a clean "unconscious" anchor:** some N3 awakenings yield reports.
- **Hardware and montage** differ between Sleep-EDF and HMC. The eligibility gate addresses this but cannot remove it.
- **ds005620 sed2 labels** are behavioural (RASS -4), with only group-level report rates.
- **No propofol arm has power** without DOSE-I, which needs owner sign-off on its Data Use Agreement.

## Sealed files
- this prereg;
- `experiments/transfer_5/` files `analyse.py`, `measures.py`, `fetch_hmc.py`, `extract_ds.py`, `planted.py`, `planted.json`, `feats_sedf_wn.jsonl` and `CENSUS.md`;
- the imported helpers `experiments/lz_slope/features.py`, `experiments/nonequilibrium/extract.py` and `experiments/lz_slope/fetch.py` (the last defines the Sleep-EDF epochs).

## Amendment 1 (2026-11-23, before any HMC signal was fetched)
`fetch_hmc.py` read the HMC record list from physionet.org, which returned HTTP 502 (and later a redirect). The record list is now read from PhysioNet's open S3 mirror (`physionet-open.s3.amazonaws.com/hmc-sleep-staging/1.1/RECORDS`, 151 recordings), which the script already used for every data file. Nothing else changed. No HMC signal had been downloaded: the failed run stopped at the record list.

