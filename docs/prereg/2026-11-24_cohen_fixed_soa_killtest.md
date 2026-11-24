# Pre-registration: does the "report-free" N2 separate seen from unseen at a fixed stimulus? (Cohen et al. 2024, SOA 50 ms)

Agent: Open Mind thread   Date: 2026-11-24   Status: DRAFT (not sealed; revised after the Fable pre-seal review)

- **Script:** `experiments/cohen_fixed_soa/cohen_killtest.py`.
- **Data:** Cohen, Dembski, Ortego, Steinhibler & Pitts 2024, Cereb Cortex, doi:10.1093/cercor/bhae415, OSF 6d5av.
  - Report-block face trials at SOA 50 ms with a seen (S1) or unseen (S2) answer.
  - Range-read by `fetch_epochs.py`: −100 to +600 ms around face onset, 63 channels at 500 Hz.
- **Sealed together, before any label–EEG statistic is computed on real labels:**
  - this file;
  - the script;
  - `out/eligibility.csv`;
  - `out/prep_hashes.json` (sha256 of `out/prep.npz`, the frozen per-trial component values).
- **Before sealing, label-free only:**
  - prep (rejection, bad channels);
  - the alignment check on pooled ERPs;
  - the eligibility counts (behaviour only; the same counts are already public in the authors' sheet);
  - calibration, which uses shuffled labels only.
- **Pre-seal review:** one Fable review (2026-11-24). Its 4 must-fixes and most should-fixes are applied; section 9 records them.
- **Licence:** OSF 6d5av states no licence.
  - The data stays local (gitignored) and is never republished. Only derived statistics are published, with full citation.
  - The coordinator approved the analysis on 2026-11-24. The corresponding author was emailed the same day about reuse terms and citation.
  - The public site write-up waits for his reply or 14 days, whichever comes first.

## 0. Question and why it matters

- **The paper's claim:** Cohen et al. 2024 call a fronto-central N2 a marker of awareness that does not depend on report. Two pieces of evidence:
  - it follows the psychometric curve nonlinearly across five SOAs;
  - it does so in both the report and no-report conditions.
- **The confound:** SOA changes the stimulus as well as awareness. Nonlinearity across SOAs is not the same as tracking awareness when the stimulus is held fixed.
- **Our contrast:** at SOA 50 ms the same masked face is seen on about half of report trials. We compare seen vs unseen trials within that SOA.
  - **Prediction if the N2 tracks awareness:** seen is more negative than unseen at 250–290 ms on the authors' electrodes.
  - **Same test for the VAN** (N170 window, PO9/PO10): predicted more negative for seen. Navajas et al. 2013 found a larger N170 for seen faces at fixed noise, so a VAN effect would be a replication.
- **What this can and cannot say:**
  - Every trial here has a report, so a pass does not show the marker is report-free.
  - **N2 KILLED is not news.** The authors already report that the N2 did not appear in the report condition, which they blame on P3b overlap. A KILLED N2 replicates that report-block finding and says nothing against their no-report claim.
  - **Informative outcomes:**
    - N2 PASS: an N2-window difference at a fixed stimulus despite the P3b overlap;
    - the VAN result, either way;
    - N2_frontal (the N2 electrodes minus those shared with the P3b) as a secondary.
- **Prior art (read 2026-11-24):**
  - **The authors' prereg** analyses only SOA curves: mask-only subtraction, no fixed-SOA seen/unseen contrast.
  - **The paper:** the N2 did not bifurcate in the report condition; the authors blame overlap with the P3b. The VAN was added post hoc.
  - **Nicolacoudis 2025 (Reed thesis):** new data (gratings). It argues that mask overlap hindered the across-SOA VAN analysis.
  - **Gnodde et al. 2026 (JoCN):** visibility enhances early posterior decoding, different stimuli.
  - **Del Cul et al. 2007:** late divergence at about 270 ms.
  - **Novelty:** none of these runs a fixed-SOA seen vs unseen test on this dataset or tests this N2.

## 1. Subjects and split

- **Pilot set (15):** 1001, 1002, 1003, 1004, 1005, 1007, 1008, 1009, 1014, 1015, 1016 (file 10162), 1017, 1018, 1020, 1022 (file 2022).
  - The authors fixed their windows and electrodes on "15 pilot participants". These are the first 15 recordings by date (2021-04-20 to 2021-07-09), and the only IDs ≤ 1022. That this is the authors' pilot set is our inference; the paper gives no IDs.
  - Here they are a secondary replication only.
- **Confirmatory set:** the other 25. **The verdict comes from this set only.**
- **Eligibility:** at least 20 seen and 20 unseen trials after rejection. This is fixed in `out/eligibility.csv` before sealing.

## 2. Preprocessing (frozen; label-free)

- **Units:** int16 × 0.1 µV.
- **Reference:** the recording reference is the right mastoid; Ch58 is the left mastoid. We re-reference to linked mastoids (subtract Ch58/2), as the authors did.
- **Baseline:** −100 to 0 ms. The authors used −200 to 0; the shorter baseline keeps the download within budget.
- **Eye channels:** HEOG = Ch62 − Ch63; VEOG = Ch61 − Ch50 (Fp1).
- **Trial rejection** (the authors' thresholds, fixed rather than adjusted per participant). Peak-to-peak over the whole epoch:
  - HEOG > 50 µV;
  - VEOG > 150 µV;
  - any good scalp channel > 150 µV.
- **Bad channels:** a channel whose median peak-to-peak is more than 3 × the median over channels is dropped from the ROIs and from rejection, per subject.
- **Filter:** zero-phase 4th-order Butterworth low-pass at 30 Hz, applied before everything else.
  - Why: without it, high-frequency noise in the unfiltered HEOG pushed 36% of subject 1001's trials over 50 µV, and 41% were rejected in all; with it, 6% are.
  - This was decided on pooled, unlabelled trials. The ds001810 pipeline needed the same fix.
- **Trial value:** the mean over ROI channels and window samples. These values are frozen in `out/prep.npz` and hashed.

- **Label-free alignment check** (pooled over seen and unseen; must pass before sealing):
  - the grand-average occipital (P1 ROI) N1 trough falls in 140–200 ms;
  - the 140–200 ms mean is below baseline across subjects (t-test, p < 0.01).

## 3. Components (authors' electrode numbers)

| Name | Electrodes | Window (ms) | Role | Predicted seen − unseen |
|---|---|---|---|---|
| P3b | 1, 4–6, 13–15 (Cz, CP2, CPz, CP1, P2, Pz, P1) | 300–500 | positive-control gate | > 0 |
| N2 | 1–11, 17–19 | 250–290 | **target** | < 0 |
| VAN | 53, 57 (PO10, PO9) | 140–200 | **target** | < 0 |
| P1 | 41–45, 53–57 | 100–140 | null control | 0 (two-sided) |
| N2_frontal | N2 set minus 1, 4–6 (the P3b overlap) | 250–290 | secondary | < 0 |
| N2roi_0_60 | N2 electrodes | 0–60 | early control | 0 (two-sided) |

## 4. Statistics

- **Per subject:** AUC of the trial values for seen vs unseen, oriented so that AUC > 0.5 is the predicted direction. P1 is oriented to seen > unseen and tested two-sided.
- **Group statistic:** the mean AUC over subjects.
- **p_perm:** 10,000 label shuffles within subject, inside time-on-task quintiles, so slow drift in both visibility and EEG cannot create an effect.
- **p_signflip:** 10,000 random sign flips of the per-subject (AUC − 0.5). This is the random-effects test across subjects.
- **p = max(p_perm, p_signflip).**
- **Effect size:** seen − unseen in µV, with a 95% bootstrap CI over subjects.
- **Sensitivity analyses** (reported, not part of the verdict), for P3b, N2 and VAN:
  - **Identity strata:** shuffles also stratified by the face's visibility tercile, where each face's seen rate comes from the other subjects (leave-subject-out).
  - **Late answers only:** trials answered more than 500 ms after face onset, so the motor response falls outside the windows. Subjects need 10 trials per cell. In subject 1001 the median response time is about 500 ms.

## 5. Decision rules (confirmatory set)

1. **Gate:** P3b p < 0.05 with mean AUC > 0.5. If it fails, the verdict is INVALID and nothing else is interpreted.
2. **Targets N2 and VAN:** Holm step-down at α = 0.05 over the two p values.
   - **PASS:** Holm-adjusted p < 0.05.
   - **KILLED:** not a pass, the 95% CI of seen − unseen lies above −1.0 µV (it excludes a predicted effect of 1.0 µV or more), and the CI includes or is above zero (no significant predicted-direction effect).
     - The bound is 1.0 µV because the trial SD is about 9 µV for N2 and 7 µV for VAN, so the CI half-width with about 24 subjects is roughly 0.5–0.75 µV.
     - Calibration reports how often KILLED fires under a true zero and under a planted effect of 1.0 µV.
   - **INCONCLUSIVE:** neither.
3. **N2 interpretation:** see section 0. If N2 fails but N2_frontal passes (p < 0.05), it is reported as "secondary, needs replication", never as a rescue.
4. **Controls:** every target result is flagged if P1 (100–140 ms) or the N2 electrodes at 0–60 ms differ, two-sided, with either p < 0.05.
   - A difference there means seen trials differ before awareness is thought to arise: pre-stimulus state such as alpha, or the stimulus.
   - The −100 ms baseline is only about one alpha cycle, so this control matters.
5. **Pilot set:** the same analysis, reported as a secondary replication with the circularity caveat (the windows were chosen on these subjects, though not on this contrast).

## 6. Limits fixed in advance

- **P3b overlap.** At 250–290 ms the P3b may already push seen trials positive on the shared electrodes, which would cancel an N2 difference. N2_frontal and N2_resid_P3b address this only partly. A KILLED N2 means "this window and ROI do not show it", not "no frontal awareness signal exists".
- **Seen and unseen are reports.** A "seen" answer includes guesses and a criterion. Confidence was not recorded.
- **Face identity** varies across trials, and some faces may be more visible. The identity-strata sensitivity analysis addresses this only partly.
- **Motor responses** can fall inside the P3b window: the earliest answer in subject 1001 is 318 ms. Different buttons mean different motor potentials, which can inflate the P3b gate. The late-answer sensitivity analysis addresses this.
- **The −100 ms baseline** is shorter than the authors' and sits at the low-pass edge. This adds noise, not bias.
- **Eligibility also needs electrode coverage:**
  - both VAN channels good;
  - at least half of every other ROI good;
  - no left-mastoid flag (median peak-to-peak more than 3 × the scalp median).
- **The pilot IDs** are inferred (section 1).

## 7. Calibration (shuffled labels only; run before sealing)

- **False positives:** 200 runs with labels shuffled within subject. We count how often any target passes (2,000 permutations per run, gate forced open). It must be ≤ 0.06; `run` refuses otherwise.
- **KILLED under a true zero:** the rate is reported.
- **Planted bound:** a −1.0 µV seen effect planted into N2 and VAN separately, 50 runs each.
  - The PASS rate (power) and the KILLED rate are reported.
  - If the KILLED rate under the planted bound is above 0.05, KILLED for that target is reported as "not calibrated" rather than as a kill.
- **Run gates:** `run` also refuses unless the alignment check passed on all 40 subjects.

## 8. Run order

1. prep, hashes, align, eligibility, calibrate (label-free);
2. a Fable pre-seal review;
3. fixes;
4. seal;
5. (licence: coordinator OK given 2026-11-24);
6. `run`;
7. report all results, whatever they are, in `RESULTS.md`, with the NEGATIVE_ATLAS entry if KILLED or INVALID.

## 9. Pre-seal review (Fable, 2026-11-24) and changes

- **Must-fixes, all applied:**
  1. N2 residualised on the P3b is removed. It was biased toward a pass because the N2 and P3b correlate across trials (r ≈ 0.44).
  2. KILLED now also requires that there is no significant predicted-direction effect.
  3. The bound went from 0.5 to 1.0 µV to match trial noise, and calibration now plants the bound and reports the KILLED rates.
  4. Interpretation: N2 KILLED replicates the authors' report-condition result and is not news.
- **Should-fixes applied:**
  - response-time sensitivity analysis (late answers only);
  - a same-electrode 0–60 ms control;
  - control flags on either p value;
  - coverage and NaN guards, and the mastoid check;
  - identity-strata sensitivity analysis;
  - `run` checks the label-free gates;
  - everything is rerun on all subjects before sealing;
  - the baseline note.
- **The reviewer checked as OK:**
  - AUC orientation, planted sign, Holm and the stratified shuffle;
  - masks are identical across seen and unseen at a fixed SOA;
  - channel roles from the `.vhdr` coordinates;
  - the 15 + 25 split matches the 40 files.
