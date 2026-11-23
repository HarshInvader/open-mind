# Does Lempel-Ziv complexity add anything over the spectral exponent? Sleep-EDF (task #4, first dataset)

**Verdict: no, once the spectrum is described properly. Against the full spectral baseline (the exponent plus six band powers), LZ adds nothing. In wake vs N3 the change is +0.0004 AUC (p = 0.19); in REM vs N3 it is -0.0002 (p = 0.16). Against the 1-40 Hz exponent alone, LZ adds 0.061 AUC for REM vs N3 (0.915 to 0.976, Holm p = 0.008). That is the one cell that meets the sealed pass mark. But LZ failed the surrogate gate (task #8), and the gain vanishes when band powers are added, so it is spectral shape the single exponent misses, not complexity beyond the spectrum. In wake vs N3 the exponent alone is already at AUC 0.988, which leaves no room: LZ adds 0.007, below the 0.01 mark.** Within subjects, LZ correlates with the exponent at Spearman rho 0.85 (Maschke et al. report 0.86 in patients, as cited in the plan; unverified).

Pre-registration: `docs/prereg/2026-11-18_lz_vs_slope_sleepedf.md`, sealed 2026-11-18T06:49Z before any measure was computed on real EEG. It has two amendments (fetch fixes, and P1b after P1 failed), one deviation (59 of 78 subjects fetched) and one note (`finish.py`). All are hashed in `docs/prereg/HASHES.txt`, and each says exactly what changed and when.

## Data and method
Sleep-EDF Expanded, sleep-cassette (PhysioNet, DOI 10.13026/C2X676, ODC-BY). 45 subjects (59 fetched, 45 with at least 10 clean epochs per stage). 1800 W, 1670 N3 and 1779 REM 30-s epochs; Fpz-Cz + Pz-Oz; 0.5-40 Hz. Ground truth: behaviour (R&K scoring). REM counts as the "conscious" side in C2 because REM awakenings usually yield dream reports (an assumption here, not a per-epoch label). Logistic regression, 5-fold subject-held-out CV (`experiments/rules/evidence.py`, `check_split` on every fold). Null: 1000 within-subject Freedman-Lane permutations of the added measure's residual on the baseline. CIs: 1000-resample subject-cluster bootstrap. Holm correction over the 8 tests.

## Planted checks
- **P1 (slow-wave plant) FAILED** (`planted1.json`): exponent AUC was 0.50, 0.56, 0.64 and 0.76 at k = 0, 0.5, 1 and 2, against a mark of 0.80. The plant only touched 1-2 Hz, 3 of the 79 points in the fit. The failure stays on record.
- **P1b (spectral tilt, sealed amendment before any H1-H4 outcome) PASSED** (`planted1b.json`): exponent AUC 0.50, 0.66, 0.79 and 0.95 at beta = 0, 0.25, 0.5 and 1. LZ recovers the same tilt even better (0.50, 0.71, 0.88, 0.99), which shows directly that LZ responds to a pure spectral change.
- **P2 (calibration and power) PASSED** (`planted2.json`): false-positive rate 0/20 at d = 0. Power 0.85 at d = 0.2, which corresponds to a mean delta AUC of 0.0005 in W vs N3. The test is sensitive, so the C1 negatives are not for lack of power; the problem is the ceiling.

## Sealed tests

| Test | Baseline AUC | + added | Delta AUC [95% CI] | p (perm) | p (Holm) | Verdict |
|---|---|---|---|---|---|---|
| H1 W vs N3: slope + LZ | 0.988 | 0.995 | 0.007 [0.002, 0.014] | 0.001 | 0.008 | does not add (< 0.01) |
| H2 W vs N3: slope + pnLZ | 0.988 | 0.991 | 0.004 [0.000, 0.008] | 0.001 | 0.008 | does not add |
| H3 W vs N3: full spectral + LZ | 0.996 | 0.996 | 0.0004 [-0.0003, 0.0012] | 0.19 | 0.32 | does not add |
| H4 W vs N3: full spectral + pnLZ | 0.996 | 0.997 | 0.002 [0.000, 0.005] | 0.003 | 0.015 | does not add |
| **H1 REM vs N3: slope + LZ** | 0.915 | 0.976 | **0.061 [0.031, 0.093]** | 0.001 | 0.008 | **adds (but spectrum-carried; see H3)** |
| H2 REM vs N3: slope + pnLZ | 0.915 | 0.920 | 0.005 [-0.004, 0.015] | 0.010 | 0.030 | does not add |
| H3 REM vs N3: full spectral + LZ | 0.991 | 0.990 | -0.0002 [-0.001, 0.0005] | 0.16 | 0.32 | does not add |
| H4 REM vs N3: full spectral + pnLZ | 0.991 | 0.992 | 0.001 [-0.001, 0.004] | 0.006 | 0.024 | does not add |

## Single measures (subject-held-out CV AUC; descriptive)

| Measure | W vs N3 | REM vs N3 | W vs REM |
|---|---|---|---|
| LZ | 0.981 | 0.972 | 0.707 |
| Phase-normalised LZ | 0.482 | 0.468 | 0.482 |
| Spectral exponent | 0.988 | 0.915 | 0.887 |
| Permutation entropy | 0.967 | 0.921 | 0.815 |
| Relative delta power | 0.973 | 0.986 | 0.676 |
| Full spectral baseline (7 features) | 0.996 | 0.991 | 0.956 |
| Arousal classifier (EMG + EOG; 152 NaN-EMG epochs dropped) | 0.905 | 0.700 | 0.940 |

## Reading
- In sleep, LZ is a spectral summary. It tracks the exponent (rho 0.85), it keeps 97% of its separation on phase-randomised surrogates (#8), and it adds nothing once band powers are in the model.
- Phase-normalisation removes the spectral part and leaves nothing that separates stages (AUC 0.47-0.48).
- On this dataset, REM looks closer to wake than N3 on every measure. That is a stage result, not an experience result: no per-epoch reports exist here.

## Not checked
- Only one family (sleep), one lab and two bipolar channels. The plan's ds005620 and Chennu propofol sets are not done yet (they are the rest of #4). 19 of 78 subjects were not fetched because of compute-lock contention; selection was by file order only.
- Age is not controlled (cassette ages are 25-101). All comparisons are within subject, but the thresholds pool ages.
- Only one LZ variant (median-binarised, LZ76). The Hilbert-envelope LZs of Schartner et al. is not run.
- Raw epochs were deleted after extraction. `features.jsonl` (about 7 MB) holds every feature.

| Hypothesis | Result |
|---|---|
| H1 LZ adds over exponent, W vs N3 | no (delta 0.007 < 0.01; ceiling) |
| H1 LZ adds over exponent, REM vs N3 | yes, delta 0.061, but spectrum-carried |
| H2 pnLZ adds over exponent | no |
| H3 LZ adds over full spectral baseline | no (both contrasts) |
| H4 pnLZ adds over full spectral baseline | no (delta at most 0.002) |

## Related framing: Thorat and Chopra (2026)

Thorat and Chopra, "Towards full-stack functionalist theories of consciousness: Identifying the functional profile" (arXiv:2609.33366, v3, 10 Nov 2026, doi:10.48550/arXiv.2609.33366; full text read 2026-11-20), set a rule for behavioural evidence that this result applies to neural evidence.

- **Their rule:** an awareness-linked difference in how a content is used counts only if it cannot be reduced to a difference in the information available about that content. They enforce this with matched first-order performance or diagnostic designs.
- **Our analogue:** a state-linked difference in a complexity measure counts only if it cannot be reduced to a difference in the power spectrum. We enforce this with a full spectral baseline and phase-randomised surrogates. On Sleep-EDF, LZ fails that test (H3: +0.0004 and -0.0002 AUC; 97% of its separation kept on surrogates).
- **Where the two meet:** they already decline to treat awareness-linked neural signatures as functional associations unless the computation behind them is characterised. This result gives one concrete reason: a widely used marker is, in this data, a spectral summary.
- **Their caution about nulls applies here too:** they note that the absence of a detectable difference does not establish equivalence (citing Meyen et al. 2021, unverified here). That is why the planted power check (P2: power 0.85 at a mean delta of 0.0005 AUC) is reported next to every null above.

## Prior art and novelty (added 2026-11-23)
**The direction of this result is not new.**
- González et al. 2022 (Neuroscience, doi:10.1016/j.neuroscience.2022.04.025; abstract read) showed in rats that low-frequency oscillations (delta, theta, sigma) drive EEG complexity changes across sleep and wake.
- Höhn et al. 2024 (eNeuro, doi:10.1523/ENEURO.0259-23.2024; full text read) report in humans that "Lempel–Ziv complexity is still strongly influenced by oscillatory activity". They also found the spectral slope "yields more information" than LZ.

**What this study adds.** It confirms and quantifies their finding; it does not discover it.
- A sealed, subject-held-out test of incremental validity: LZ adds +0.0004 / -0.0002 AUC over the exponent plus band powers.
- A phase-randomised surrogate gate: 97% of LZ's wake-vs-N3 separation survives when only the spectrum is kept.
- Phase-normalised LZ carries no stage information.

Neither paper ran an incremental-AUC test against a full spectral baseline or a phase-surrogate test.

**Counter-evidence to keep in view.** Frohlich et al. 2022 (Commun Biol, doi:10.1038/s42003-022-04331-7; abstract read) studied children with Angelman syndrome and Dup15q syndrome. In those conditions, oscillations dissociate from conscious state. They found that entropy-based classifiers of conscious state were not upper-bounded by spectral features and outperformed them. So "complexity collapses to the spectrum" is a result for typical sleep EEG in Sleep-EDF. It is not a general law.
