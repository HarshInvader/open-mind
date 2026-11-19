# Amendment 3 to the experience benchmark pre-registration

Amends `docs/prereg/2026-11-19_experience_benchmark.md` (sha256 de1f44ce…) and amendments 1 (bc1db71e…) and 2 (c70139f9…). Written 2026-11-19 after the library review (commit 684888b). **No DREAM label has been joined to any EEG feature, and no DREAM EEG has been extracted** (extraction is queued behind the compute lock). The Michalak per-awakening table has not been read: only its README, its analysis code, the paper's methods, the variable names in the `.mat` file and its electrode labels. The analysis script was amended for this and re-sealed: `analysis.py` sha256 69c940f0bf722f787cba3305e2601d6d936c424f920bc2c84c70089a547c80eb (2026-11-19T15:55:01Z). Everything else stands.

## 1. What counts as new (Selte et al. 2026, bioRxiv 10.64898/2026.08.16.745040, abstract read)

Selte et al. report that EEG predicts a report of experience with people held out, at AUC 0.80. They used 699 NREM awakenings from one lab, pooled N2 and N3, and had no spectral baseline. "EEG can predict dream reports" is therefore already claimed. What this benchmark alone can add:
- (a) prediction across held-out labs;
- (b) with sleep stage fixed (N2);
- (c) whether any consciousness marker adds anything beyond the spectrum.

**New headline number.** The frozen spectral baseline's own experience AUC is a headline result, reported with its 95% CI whatever it is.
- It is a logistic model on the baseline columns only (exponent and band powers, or the 1-30 Hz variant chosen by the §4 rule), with no covariates.
- It is leave-one-lab-out over the 5 Tier 1 labs, with the discovery labs in training (as K4).
- The held-out predictions are pooled and scored with the within-subject pair AUC.
- One-sided p comes from 5,000 within-subject label permutations, refitting each time. The 95% CI comes from the within-lab subject bootstrap (2,000 draws, refitting each time).

Also reported, with no test: the same model plus the covariates (model 0), and a leave-one-lab-out version over all 7 labs (Tier 2, exposed labs included).

**Possible overlap.** Selte's cohort comes from the same group as the DREAM Tononi set (Wisconsin). It may contain those subjects. Tononi is in the exposed tier and is never a confirmation lab, so this does not affect the held-out claim. It is noted for the comparison only. Any comparison with Selte's 0.80 is descriptive, because features, windows, stages and labs all differ.

## 2. How each outcome is read (fixed now; computed in `analysis.py: reading()`)

Definitions:
- **The spectrum predicts (SP):** the spectral headline's 95% CI lower bound is > 0.50 and its one-sided p is < 0.05.
- **A marker adds:** a Family B measure is Holm-significant with ΔAUC ≥ 0.03 and its lower 95% bound is > 0. Or the Study 3 score (not killed at fitting) has one-sided p < 0.05, ΔAUC ≥ 0.03 and a lower bound > 0.
- **No marker adds (bounded):** every Family B upper 95% bound of ΔAUC is < 0.03, and so is the Study 3 ΔAUC upper bound.

| Reading | Condition | Status |
|---|---|---|
| R1, spectrum-sufficient | SP, no marker adds (bounded), K1 met | **Publishable.** At fixed stage, in labs never analysed, the ordinary power spectrum predicts reported experience, and no published consciousness marker adds anything beyond it. This runs against the claims made for markers and is not a failure. If A1 also holds, both are reported: the named markers are bounded while the full spectrum predicts. |
| R2/R4, correlate | any measure or Study 3 meets every A2 mark (amendment 1, C5), with or without SP | Publishable (A2). |
| R3, dissociation | not SP, and A1 holds | Publishable (A1). |
| R5a | SP and some marker adds, but short of the A2 marks | Atlas and ledger, no paper. |
| R5 | anything else | Messy middle: atlas and ledger, no paper. |

Every reading still goes through the red-team before any packaging.

## 3. Michalak et al. 2026 (PLoS Biol, doi:10.1371/journal.pbio.3003683; Zenodo 10.5281/zenodo.15372992, CC BY 4.0)

**Decision: it does not map onto the frozen baseline, so it is not added to the spectral-only arm.** The published features are, per channel (256 electrodes):
- absolute delta power (0.5-4 Hz) and gamma power (25-50 Hz);
- from Welch PSDs (4 s Hamming windows, 90% overlap) over the 120 s before the alarm (the table file is named `_w90`, so possibly 90 s; unverified).

Our baseline is the 1-40 Hz exponent plus six relative band powers over the 20 s ending 2 s before awakening. Neither the bands, nor the normalisation, nor the window can be reconstructed from these features.

**Added instead: a separate out-of-lab spectral check, sealed here.** It is outside every Holm family and outside A1, A2 and R1-R5, and is reported next to them.
- **Score:** log10(gamma / delta), averaged over a posterior ROI. This is the nearest analogue of measures 1 and 2. Direction: higher with experience.
- **ROI:**
  - The electrodes whose positions (from the file's `chanlocs`, EEGLAB frame converted to MNE head frame as (−Y, X, Z), unit sphere) are nearest to each of P3, P4, Pz, P7, P8, PO3, PO4, POz, PO7, PO8, O1, O2, Oz in mne `standard_1020`.
  - One electrode per position; duplicates are kept once.
- **Labels:** their CE (`Recall` = 2, contentful experience) = 1 versus NCE (`Recall` = 0) = 0, both at N2 (`Stage` = 2). CEWR (without recall) is left out. This matches DREAM's Experience versus No experience.
- **Statistic:** the within-subject pair AUC (subjects with both classes), a one-sided permutation p (5,000 within-subject permutations), and a 95% CI from a subject bootstrap (5,000).
- **Feasibility:** the per-awakening data are MATLAB `table` objects, opaque to scipy. The check runs only if a reader can decode them, and the reader's code and the scoring script must be sealed before any value is read. The labels are this lab's own, so the check can run before or after the DREAM unblinding without leaking anything. If no reader can be made, it is reported as not run.

## 4. Rochas et al. 2026 (PsyArXiv 10.31234/osf.io/qbwnf_v4, abstract read): limitation, no change

Rochas et al. report more beta/gamma over parietal cortex in the last 20 s before awakenings with a dream, which is our window.
- The frozen baseline does include beta (15-30 Hz) and 30-40 Hz relative power, but averaged over all channels, not over parietal channels.
- Its gamma also stops at 40 Hz, because of the 100 Hz branch.
- Posterior high-frequency power (20-45 Hz, posterior ROI) is primary measure 2 in Family A, but it is not in the baseline.

The frozen baseline is not changed. **Limitation, stated now:** a spatially specific parietal beta/gamma effect could be only partly absorbed by an all-channel baseline. A non-spectral marker that carries that spatial-spectral information could then show a ΔAUC that is really spectral. The surrogate gate guards against this: multichannel FT surrogates keep every channel's spectrum, so a purely spectral effect keeps its AUC under surrogates and fails the gate. The limitation is reported with any Family B result.

## 5. Noted, not part of #42

Re-running the high-AUC dream decoders (Moctezuma et al. 2025) with subjects held out, on the exposed labs, to measure how much leakage inflates them. This is on file in `docs/library/IDEAS.md` §3 as a possible short side result after #42.
