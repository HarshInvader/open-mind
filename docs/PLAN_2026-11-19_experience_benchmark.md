# Plan, 2026-11-19: the experience benchmark

Owner direction (relayed 2026-11-19): aim for a paper that leading researchers would treat as a major contribution, within days, on open data. A paper goes out only if the result really is strong. The evidence rules do not change.

Planned with Fable (claude-fable-5-2, read-only, 2026-11-19). It read the repo docs and RESULTS files and did its own literature and dataset search. mind-ne checked its key dataset claim (DOSE-I, below) independently.

## Verdict on the relayed candidate (spectral-confound benchmark across state contrasts)

Keep it, but as the supporting axis, not the headline.
- The LZ half is published: Maschke 2025 doi:10.1093/cercor/bhaf254 (225 DoC patients, phase-normalised LZ loses the diagnostic effect) and Höhn 2024 doi:10.1523/ENEURO.0259-23.2024 (abstract).
- On wake vs N3 the spectral baseline is already at AUC 0.99, so "adds nothing" is near-trivial there.
- Fable's odds for the state benchmark alone: a clean result 60%; treated as major 8-10%.
- No DoC EEG set is openly downloadable (OpenNeuro search, Zenodo, PhysioNet I-CARE files withdrawn), so the DoC arm cannot run.

## Top pick: Study 1, the experience benchmark

**Question.** Holding sleep stage fixed, does any published EEG consciousness marker predict a report of experience on held-out subjects and held-out labs? If so, does it survive the frozen spectral baseline and the phase-surrogate gate?

**Why.** This contrast removes arousal, which is what every positive result so far has turned out to track (`experiments/nonequilibrium/RESULTS.md`: waveform asymmetry separates W from N3 but gives REM ≈ N3). Prior work on it is small or not held-out:
- Wong 2025 doi:10.1038/s41467-025-61945-1: AUC 0.59 in NREM and 0.70 in REM, no spectral nesting, no surrogates.
- Aamodt 2023 doi:10.3389/fnhum.2022.987714 and Bajwa 2025 doi:10.1038/s41598-025-12695-z (abstract): nulls on 5-10 no-experience awakenings.

**Data.** DREAM database packages on figshare, all CC BY 4.0:
- Rome multiple awakenings, LODE, DATA1 and Aamodt. None has been opened by this project. These are the confirmation labs.
- Tononi, Zhang & Wamsley and Rome young adults. These were already used (delta, exponent, OFF-periods). These are the exposed or discovery labs.
- About 800 N2 experience / 530 no-experience awakenings in total before exclusions, plus REM.
- About 25 GB streamed, nothing kept. **This needs the owner's OK** (the current budget is 1.5 GB).

**Measures (frozen list of about 14):**
- Complexity: LZ76, Hilbert LZs, permutation entropy, sample/multiscale entropy, Higuchi dimension.
- Connectivity and integration: wSMI, Gaussian total correlation.
- Dynamics: the 0-1 chaos test, DFA where the window allows, `tra_x`.
- Spectral controls: the exponent, CSER.
- Prior claims to replicate: catch22 (Wong's REM claim), posterior delta and 20-50 Hz power (Siclari's posterior signature).

**Design.**
- Window: the last 20 s before each awakening.
- Montage: common F4/C4/O2, plus a high-density posterior ROI where available.
- Primary inference only on the unexposed labs, lab-held-out.
- Features extracted label-blind; the sealed script opens the labels once.
- Baseline: the frozen spectral baseline, with a sealed 1-30 Hz variant for labs low-passed below 40 Hz.
- Gate: FT and IAAFT surrogates.
- Statistics: Freedman-Lane nulls, subject bootstrap, Holm over measure × stage.
- Covariates: time of night, awakening index, age.
- Equivalence bounds so a null can be stated as a bound: single AUC 0.60, incremental AUC 0.03.
- Positive control: every measure must reproduce its wake vs N3 separation on Sleep-EDF.

**Kill criteria.**
- K1: fewer than 300 usable unexposed N2 awakenings, fewer than 120 no-experience, or fewer than 3 labs.
- K2: planted AUC 0.60 recovered with under 80% power, or FPR above 5%.
- K3: the pooled effect exists but the within-lab effect does not (a lab artefact). Then only within-lab results count.
- K4: extraction unfinished by day 3. Cut to N2 and four labs.

**What counts.**
- **Major positive:** a gate-passing measure with lab-held-out AUC ≥ 0.65, incremental AUC ≥ 0.03 (Holm), and the same sign in ≥ 3 labs.
- **Major negative:** about 14 published markers that all track arousal (> 0.9) and all fail on experience (bounded < 0.60), across > 1,000 awakenings and ≥ 4 labs. This is a double dissociation.
- **Messy middle** (a weak, lab-dependent spectral effect): negative atlas, no paper.
- **Stated limits:** report ≠ experience (recall), and scalp ≠ source.

**Odds (Fable's estimates, which mind-ne agrees with):**

| Outcome | Odds |
|---|---|
| A marker survives everything | 5-8% |
| Clean double dissociation | 40-45% |
| Messy middle | about 35% |
| Killed by K1-K4 | about 15% |
| **Treated as major by leading researchers, overall** | **about 15%** |
| Seminal | 2-4% |

**Time:** 4-5 days.

## Riding along

- **Study 2 (axis 1 of the same paper): the state-contrast spectral-confound benchmark.** Same measure list, scored on Sleep-EDF (done), BOAS ds005555 (an independent sleep lab, subset), Chennu, ds005620 and **DOSE-I**.
  - DOSE-I is Zenodo 22145442: 171 propofol recordings, 2-channel EEG at 125 Hz, 7,328 MOAA/S scores, CC BY 4.0, 0.72 GB. mind-ne opened the record and its data-use text. The text forbids re-identification and limits use to the stated research purpose; **the owner should accept it**.
  - DOSE-I fixes the propofol power problem from task #41.
  - Each marker gets three numbers: arousal score, spectral share and experience score.
- **Study 3: sealed residual search.** One model on surrogate-excess features is discovered on the exposed labs, frozen and hashed before the Study 1 unblinding, then tested once in it.
  - Kill: discovery CV AUC < 0.58.
  - Odds positive 4-6%. It is the only route to a seminal result ("first cross-lab, arousal-free, spectrum-free correlate of reported experience").

## First steps

1. Run a label-blind audit of the 7 DREAM packages by range read: channels, sampling rate, low-pass, window length. Simulate realised power and apply K1/K2. No labels are opened.
2. Seal the prereg: measure definitions, both baselines, the gate, the bounds, the discovery/confirmation split, the exposure declaration, the Holm families and the publish gate. Run the planted checks and the Sleep-EDF positive control for every measure.
3. Run one heavy job under the compute lock: stream, extract, delete. Freeze the Study 3 model. Unblind once. Red-team, then update the atlas and the merged ledger.

## Housekeeping found by Fable

`docs/test_ledger.csv` holds only its header row. The per-experiment `ledger_rows.csv` files need merging into it before any project-wide correction.
