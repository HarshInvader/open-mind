# One sealed open-data test per theory (task #16)

Agent: mind-3. Date: 2026-11-18. Pre-registrations were sealed at 2026-11-18T07:00:20Z, before any EEG was downloaded (hashes in `docs/prereg/HASHES.txt`).

## Verdict

**No theory passed a test. Three theories got a sealed test on open data. Four could not be tested with data we can reach.**

| Theory | Test | Result | Verdict |
|---|---|---|---|
| IIT 4.0 | Before N2 awakenings with a dream report, is posterior 1-4 Hz power lower, more so than frontal power, and does it add over the spectral exponent? | AUC 0.537 (p 0.24). Posterior minus frontal: -0.040 [-0.114, 0.022]. Held-out gain over the exponent: -0.100 [-0.195, -0.008] | **Failed this test** |
| GNWT | Before N2 awakenings with a dream report, is frontal 1-4 Hz power lower, and does it add over the exponent? | AUC 0.577 [0.458, 0.680], p 0.066 (alpha 0.025). Held-out gain over the exponent: +0.025 [-0.115, 0.166] | **Failed this test** |
| Entropic brain | Is spectrum-matched (phase-normalised) LZ lower at moderate propofol than at baseline? | Primary test uninformative: pnLZ could not tell real EEG from its own surrogate (planted check P1). Raw LZ went the other way: it ROSE by +0.056 [0.025, 0.090], d_z 0.92. Surrogate LZ rose by about the same amount (+0.051), so the change is spectral | **No verdict on the primary test. The simple form (raw LZ falls) failed this test in the opposite direction** |
| Higher-order | PFC tracks awareness when performance is matched | No reachable data | Not tested |
| Recurrent processing | Local sensory recurrence, without report, tracks experience | No reachable data | Not tested |
| Predictive processing | Mismatch or local-global responses change with state | No open oddball EEG across sleep or sedation | Not tested |
| Attention schema | Awareness tracks the model of attention | No reachable data | Not tested |

Both failed dream tests had little power. Each could detect a true AUC of about 0.66-0.70 with 80% power (planted check below), so an effect as small as the one Siclari et al. 2017 might have produced on scalp EEG is not ruled out. These are failures of this test on this data. They do not refute either theory. Scoreboard: `scoreboard.csv`.

## What each test was, and why a proponent should accept it

**IIT (prereg `docs/prereg/2026-11-18_theory_iit_posterior_dream.md`, sha256 2ea17ddb...).** IIT places the substrate of experience in a posterior "hot zone" (Koch, Massimini, Boly & Tononi 2016, doi:10.1038/nrn.2016.22; IIT 4.0, Albantakis et al. 2023, doi:10.1371/journal.pcbi.1011465). The IIT group's own dream study (Siclari et al. 2017, doi:10.1038/nn.4545) reported lower posterior low-frequency power before NREM dream reports. We tested this in two labs that are not the discovery lab:
- Zhang & Wamsley 2019 (Furman University; 58 channels; DREAM, doi:10.6084/m9.figshare.22226692).
- De Gennaro YoungAdults (Rome; 19 channels; doi:10.6084/m9.figshare.14899506).

To pass, all three parts had to hold: the posterior effect is present, it is larger than the frontal effect, and it adds over the exponent on held-out subjects.

**GNWT (prereg `..._gnwt_frontal_dream.md`, sha256 d31a688e...).** In GNWT, conscious content requires the prefrontal-parietal workspace (Mashour, Roelfsema, Changeux & Dehaene 2020, doi:10.1016/j.neuron.2020.01.026). Dreams are conscious, so frontal slow-wave power should fall before a report. Caveat written into the prereg: GNWT's sharpest signature is ignition to a stimulus, which sleep data cannot probe, so a proponent may weigh this failure less than a failed ignition test.

**Entropic brain (prereg `..._entropic_propofol.md`, sha256 6b468c1c...).** The entropy of spontaneous activity indexes how rich a conscious state is, with anaesthesia at the low end (Carhart-Harris et al. 2014, doi:10.3389/fnhum.2014.00020; Carhart-Harris 2018, doi:10.1016/j.neuropharm.2018.03.010). The riskiest form is that the entropy drop survives control for the spectrum. Data: Chennu et al. 2016 propofol EEG (doi:10.17863/CAM.68959; paper doi:10.1371/journal.pcbi.1004669), baseline vs moderate, 20 subjects, the first 120 s of each recording.

## Numbers

### Dream tests (`dream_results.json`)
- Included: 132 N2 awakenings (82 experience, 50 no experience) from 54 subjects. Zhang: 102 (66/36). YoungAdults: 30 (16/14).
- Excluded:
  - 3 Zhang morning awakenings had no clean 4-s segment.
  - 2 YoungAdults files had only 2 clean segments.
  - 1 YoungAdults file had none.
  - 2 YoungAdults members (DG41, DM02) are corrupt in the Figshare zip.
- Per dataset, posterior AUC was 0.551 (Zhang) and 0.487 (YoungAdults). Frontal AUC was 0.575 and 0.580.
- The exponent alone gave an AUC of 0.575 in-sample (flatter means experience) but only 0.504 out-of-fold.
- Adding posterior delta to the exponent lowered the held-out AUC to 0.404. Adding frontal delta gave 0.529.
- Lab transfer (train on one lab, test on the other) was at or below chance for every model, between 0.40 and 0.50.
- Surrogate gate: band power is fully set by the spectrum, so phase-randomised surrogates give identical values by construction. The exponent control (H3) is the beyond-spectrum test for these measures.
- Planted check (`planted_dream.json`), run with random labels on the real data:
  - False-positive rate was 0.025 at alpha 0.025.
  - Reducing posterior 1-4 Hz amplitude by 15% gave power 0.65 (mean AUC 0.61).
  - Reducing it by 25% gave power 0.98 (AUC 0.70).
  - For the frontal ROI, the same reductions gave power 0.46 and 0.87 (AUC 0.60 and 0.66).
  - It passed, so the real result counts.

### Entropic test (`chennu_results.json`)
- 20 subjects. All 480 ten-second epochs were clean.
- Median paired change, moderate minus baseline:

| Measure | Change | 95% CI | d_z |
|---|---|---|---|
| LZ | +0.056 | [0.025, 0.090] | 0.92 (Wilcoxon p 0.0002 for a rise) |
| pnLZ | -0.002 | [-0.004, 0.006] | — (p 0.64 for a fall) |
| Exponent | +0.078 (flatter) | — | p 0.09 for a rise |
| Permutation entropy | +0.011 | — | p 0.10 for a rise |

- Planted check P1 failed: baseline pnLZ was 0.999 ± 0.010, and pnLZ did not differ between real EEG and its own surrogate (p 0.43). With LZ binarised at the median on 100 Hz, 10-s, 91-channel epochs, LZ carries no detectable structure beyond the spectrum. The pnLZ test therefore cannot detect a non-spectral entropy change, and the prereg declares it uninformative. P2 (the null check, first vs second minute) passed: p 0.38.
- Subject-held-out AUC, baseline vs moderate: exponent 0.575, exponent + LZ 0.770, exponent + pnLZ 0.618. LZ adds over the 1-40 Hz exponent, but surrogate LZ separates the levels just as well (AUC 0.758 vs 0.760). The extra information is spectral shape (likely the beta and alpha changes under propofol), not entropy.
- H4: the change in LZ correlated with the change in target hits, rho 0.55 (one-sided p 0.006). The change in pnLZ did not (rho 0.16). Behaviour-linked but spectrum-carried.

## What was not checked
- REM awakenings. Both sets are low-passed at 30-35 Hz, which removes the high-frequency REM effect Siclari reported.
- Source localisation. Siclari used 256-channel source space; we used 5 posterior and 3 frontal scalp channels.
- Tononi serial awakenings (the discovery lab) and LODE (no posterior-only derivation).
- Entropy measures other than median-binarised LZ, such as multiscale or amplitude-coalition LZ.
- Deep sedation and loss of responsiveness, which Chennu does not reach.
- The ketamine and psychedelic contrasts, which are blocked (see `docs/DATASETS.md`).
- Zhang & Wamsley 2019 (doi:10.1111/psyp.13368) analysed the same Zhang recordings. I read its abstract only after the test (via Europe PMC). It reports an inverted-U: more low-frequency power with dream imagery at sleep onset, less with dreaming in later N2. Our pooled N2 sample mixes both, which biases toward a null. The prereg named this risk in advance.

## Data and disk
- Downloaded about 0.98 GB compressed in total, by HTTP range request (`ziprange.py`):
  - Zhang: 105 N2 files, about 0.36 GB.
  - YoungAdults: about 0.05 GB.
  - Chennu: the first 120 s of 40 `.fdt` members, about 0.56 GB.
  - Metadata.
- All raw EEG is deleted. Kept: per-awakening PSDs (`features/psd_*.npy`, 17 channels, 0-50 Hz), `features/dream_measures.csv`, `features/chennu_epochs.jsonl` and `features/chennu_subject_measures.csv`. Task #22 can reuse the DREAM PSDs.

## Hypotheses table

| Hypothesis | Status | Next step |
|---|---|---|
| Posterior delta is lower before N2 dreaming (IIT) | Failed this test, AUC 0.54 | Re-test with source space or a different lab, excluding sleep-onset awakenings |
| Frontal delta is lower before N2 dreaming (GNWT) | Failed this test, AUC 0.58, p 0.066 | Same |
| Spectrum-matched entropy falls under propofol (entropic brain) | Uninformative: the measure could not see non-spectral structure | Needs an entropy measure that passes P1 on this data first, such as a different binarisation or a longer window |
| Raw LZ falls under moderate propofol | Opposite direction, spectral | Logged for the negative atlas |
| H-track lead (board note, not tested): the delta-dream relation flips sign between sleep-onset N2 and later N2, and frontal > posterior in later N2 | Exploratory (`dream_exploratory_split.json`) | Seal and test on LODE, DeGennaro multiple awakenings or Tononi, excluding sleep onset |

## Files
- Code: `ziprange.py`, `dream_features.py`, `dream_analysis.py`, `chennu_features.py`, `chennu_analysis.py`, `build_outputs.py`.
- Outputs: `scoreboard.csv`, `results.json`, `ledger_rows.csv`, `dream_results.json`, `chennu_results.json`, `planted_dream.json`, `planted_chennu.json`.
- Preregs:
  - `docs/prereg/2026-11-18_theory_iit_posterior_dream.md`
  - `docs/prereg/2026-11-18_theory_gnwt_frontal_dream.md`
  - `docs/prereg/2026-11-18_theory_entropic_propofol.md`
