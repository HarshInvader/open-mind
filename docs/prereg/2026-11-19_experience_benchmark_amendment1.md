# Amendment 1 to the experience benchmark pre-registration

Amends `docs/prereg/2026-11-19_experience_benchmark.md` (sealed 2026-11-19T14:31:26Z, sha256 de1f44ce…). Written 2026-11-19 at the coordinator's request to aim the design at the strongest result it can produce. **No EEG sample from any DREAM lab has been read since the original seal.** The only new inputs are public per-awakening metadata (`dream_records.csv`, `dream_sets.csv`) and a synthetic simulation (`experiments/experience_benchmark/bounds_sim.py`, which reads no EEG). Everything in the original prereg stands unless it is changed below.

## A. The result that would change what researchers do

The field ranks states of consciousness with EEG markers: complexity (LZ, permutation entropy, fractal dimension), integration (wSMI, total correlation), the spectral exponent and the "posterior hot zone" signature. Nearly all of them have been validated on contrasts in which arousal changes along with experience: wake vs deep sleep, sedation vs recovery, patients with vs without behaviour. Two results would change practice:

1. **The dissociation.** Every major marker separates wake from deep sleep almost perfectly in two independent sleep labs, yet none tells apart dreaming from dreamless awakenings within the same stage, within the same person, across 5 to 7 independent labs. The none is stated as tight bounds (AUC inside 0.40-0.60), not as a failure to reach significance. If this holds, the standard markers measure arousal and not experience. Every consciousness-detection study that relies on them would then need an experience-matched control. Disorders-of-consciousness and anaesthesia work would need to stop reading these markers as "consciousness meters".
2. **The positive version.** A single frozen model, fitted in two labs and tested once in five labs it never saw, predicts reported experience within subject at fixed stage. It does so beyond the spectrum, beyond pre-awakening arousal, and on surrogate-controlled features. This would be the first cross-lab, arousal-free, spectrum-free correlate of reported experience: a concrete target that theories (IIT, GNW, RPT, HOT) would have to explain.

A result between these two (a weak, lab-dependent spectral effect) changes nothing. It goes to the negative atlas.

## B. Why the sealed design could not reliably deliver result A1

`bounds_sim.py` uses the real per-subject N2 counts, the within-subject pair AUC and the within-lab subject bootstrap. It gives the probability that one measure's 95% CI lands inside [0.40, 0.60]:

| Labs | Subjects | Exp / no-exp | True AUC 0.50 | True AUC 0.53 | CI half-width |
|---|---|---|---|---|---|
| 4 confirmation labs (as sealed) | 47 | 252 / 151 | 51% | 43% | 0.070 |
| + Kumral 2023 (set 19) | 53 | 261 / 158 | 57% | 48% | 0.068 |
| + Tononi and Zhang & Wamsley (7 labs) | 108 | 435 / 296 | 87% | 76% | 0.053 |

With 4 labs, "6 of 8 bounded" would be unlikely even if every marker truly had nothing to do with experience. The dissociation needs all 7 labs.

## C. Changes

### C1. Labs: two tiers
- **Tier 1 (unexposed, confirmatory for any positive claim).** The 4 sealed confirmation labs, plus **Kumral et al. 2023 (DREAM set 19; 128 channels, 1000 Hz; 6 subjects, 9 / 7 N2)**.
  - Set 19 is included only if its licence permits reuse and its files download without a signed agreement. This is checked before any of its EEG is read and recorded in the extraction script.
  - Its channel map comes from its header, mapped as Aamodt's is (10-10 labels).
- **Tier 2 (all labs, for the dissociation bounds).** Tier 1 plus Tononi (set 13, de-duplicated) and Zhang & Wamsley (set 1).
- **Exposure in Tier 2, declared.**
  - On Tononi (task #31), labels were already related to delta power, the spectral exponent and OFF-periods. These are related to measures 1 and 3, computed on a different window (10 s) and ROI.
  - No measure in 2 or 4-8, and no secondary measure, has been computed with labels in any lab.
  - Family A has no free parameters, and every choice is sealed before Tier 2 labels are joined, so the exposure cannot steer the analysis. It is still reported. Measures 1 and 3 are also reported on Tier 2 without Tononi.
- **Study 3 still fits on Tononi and Zhang & Wamsley.** This exposes their labels jointly with the features before the Tier 2 unblinding, so the Study 3 fit must be blind to single features (C4).

### C2. Measures in the dissociation
- The dissociation table covers **all 8 primary measures and all secondary measures** (sample entropy, multiscale entropy, 0-1 chaos K, DFA alpha, `tra_x`, CSER, plus catch22 as one decoder score) in Tier 2.
- Equivalence across many measures uses the intersection-union principle: each claimed bound is a separate 95% CI. Requiring all of them to hold is conservative, so no multiplicity correction is applied to the bounds.
- The headline count stays on the 8 primary measures. "Every marker" may be written only if every measure in the table is bounded.

### C3. Arousal side: two independent labs
- A measure counts as **arousal-tracking** only if its within-subject wake-vs-N3 AUC, in the predicted direction, has a **95% lower bound ≥ 0.85 in both Sleep-EDF and BOAS (OpenNeuro ds005555)**.
  - Both use the same 100 Hz code and 20 s windows.
  - For BOAS, a fixed set of 30 subjects is chosen by sorted participant ID before any file is read, with multichannel EEG, streamed within the approved budget.
- DOSE-I (propofol, responsive vs unresponsive by MOAA/S) is reported as a third arousal contrast. It is secondary because of its 2 channels.
- For wSMI and total correlation, BOAS is required (Sleep-EDF has one channel pair). If BOAS cannot be run before unblinding, these two measures are left out of the headline count.

### C4. Study 3 frozen properly
1. The Study 3 fit script (`study3_fit.py`) is sealed before it runs.
2. It prints and saves only:
   - the outer-fold AUC of the nested 5 × 5 subject-grouped cross-validation;
   - the frozen model (`study3_model.json`);
   - the model's sha256.

   It computes no univariate statistics. The analyst does not open the model file before Tier 1 unblinding.
3. `study3_model.json` is sealed (HASHES.txt) and pushed before any Tier 1 label is joined. The analysis script refuses to run unless the model hash matches.
4. If the outer-fold AUC is < 0.58, the model is logged as negative, and H3 is still tested once on Tier 1 for completeness (as in the original prereg, the kill means no claim).

### C5. Outcome definitions, stated as bounds

**Clean double dissociation (result A1).** All of the following must hold:
- At least 6 of the 8 primary measures are arousal-tracking (C3). For each of them:
  - the Tier 2 experience AUC 95% CI lies inside [0.40, 0.60];
  - the Tier 1 point estimate lies inside [0.40, 0.60].
- No primary measure passes Holm (over 8) in Tier 1 or in Tier 2.
- At least 5 labs in Tier 2 keep ≥ 2 subjects with both classes after exclusion, and Tier 2 keeps ≥ 600 N2 awakenings.
- The bounds hold with and without the pre-awakening arousal index adjustment (§8 of the original).

**Arousal-free, spectrum-free correlate (result A2).** A non-spectral measure (4-8) or the Study 3 score that:
- has a Tier 1 within-subject AUC ≥ 0.65 in the predicted direction (Study 3: AUC > 0.5 direction fixed by the model), significant after Holm (Study 3: one-sided p < 0.05);
- adds ΔAUC ≥ 0.03 over the spectral baseline plus covariates, with the lower 95% bound > 0;
- passes the FT and IAAFT gate;
- keeps AUC ≥ 0.60 after a label-blind within-subject residualisation on the pre-awakening arousal index;
- has the same sign in ≥ 4 of the 5 Tier 1 labs.

**Anything else** is the messy middle: atlas and ledger, no paper. The original K1-K4 still apply. K1 is evaluated on Tier 1.

### C6. Secondary additions
- **N3 at fixed stage.** DATA1 has 46 / 69 N3 awakenings in 9 subjects with both classes. Family A is run on them, reported as secondary.
- **Ceiling statement.** Report-based labels are noisy (forgetting, confabulation), so the best achievable AUC is below 1. That is why the bounds are set at 0.60 and not 0.55. A null here means "not detectable at the level reports allow", and is written that way.

### C7. Rules found while writing the extraction code (label-blind; no confirmation-lab EEG read)
These come from the lab descriptions inside the DREAM packages (text files, no labels) and a test run on 2 Tononi and 2 Zhang & Wamsley N2 records (EEG only, labels not read, output discarded).
- **End of record.**
  - Aamodt's README says its files end with padding silence, and the alarm is an EDF+ annotation.
  - So for every lab, trailing silence is trimmed before the window is placed: 0.5 s blocks in which every EEG channel has SD < 0.1 µV.
  - Aamodt is read with a 90 s tail; the others with 40 s. A record with < 32 s left is dropped.
  - EDF+ annotation texts in the tail are logged. If they show that a lab's awakening marker is not at the trimmed end, a sealed amendment before unblinding moves the window to the marker.
- **Kumral 2023 (set 19).** Its README says up to 1 min before waking may be cut (30 s scoring). Its window therefore may sit up to 60 s before the awakening.
  - Pre-specified sensitivity check: every Tier 1 result is recomputed without set 19.
  - If set 19 is the only thing that moves a result across a mark, the result is reported as dependent on it.
- **Zhang & Wamsley.** Its README says a few seconds of wake may precede the report marker. The 2 s offset and the arousal-index sensitivity check (§8) address this. Zhang & Wamsley is Tier 2 only.
- **Tononi montage.** The EGI-256 electrodes nearest (on the unit sphere, mne montages) to the 10-10 positions of mne `standard_1020`, about 76 electrodes. This keeps its density comparable with the 58-128-channel labs and keeps compute feasible. The recording reference is dropped, and the average reference is over these electrodes.
- **Posterior ROI for Aamodt.** The §3.7 list governs (P3, P4, Pz, P7, P8, PO3, PO4, POz, PO7, PO8, O1, O2, Oz). The broader list in the original Appendix A (P1-P8, Iz) is an error and is not used.
- **Study 3 gate draw (Tier 1 N2 only).** For each kind (FT, IAAFT): one surrogate s of the window, then for each measure m(s) minus the mean of m over 5 FT surrogates of s.
- **Surrogates** are computed for N2 records only. The REM and N3 secondary analyses report no gate.
- **Out of reach.** The largest independent N2 set found (Bernardi lab, IMT Lucca, about 1,024 labelled N2 awakenings, bioRxiv 10.1101/2025.09.03.673907) has no public data. It is listed for owner outreach and is not part of this test.

## D. Order of operations (replaces §11 step order where it differs)
1. Seal this amendment.
2. Seal the extraction script (all 7 labs, label-blind), then run extraction under the compute lock: Rome first, then the other Tier 1 labs, then Tononi and Zhang & Wamsley.
3. Run the positive controls (Sleep-EDF, BOAS, DOSE-I) and the planted checks P1-P2 in parallel with extraction (no DREAM labels).
4. Seal `study3_fit.py`, run it, then seal and push `study3_model.json` (C4).
5. Seal the analysis script, then do one unblinding: Tier 1 and Tier 2 together.
6. Red-team. Packaging stays off until the red-team is complete.
