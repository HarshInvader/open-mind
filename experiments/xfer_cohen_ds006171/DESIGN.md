# Round 20 #1: does a masked-face awareness decoder transfer zero-shot to unmasked Gabor detection in another lab? (DESIGN DRAFT, not sealed)

Status: draft, 2026-11-26. Fable round 20, ranked first. No ds006171 seen/unseen label has been read. The Cohen hold applies: nothing about results is public before 2026-12-08.

## 1. Question
Train a seen-vs-unseen decoder on Cohen et al. 2024 (masked faces, SOA 50 ms, report block, 40 subjects, about 127 trials each). Apply it unchanged to ds006171 (Melcón et al. 2024, no-cue task, near-threshold Gabors, no mask, 35 subjects, 360 Gabor trials each, seen = code 124 and unseen = code 125). Does it separate seen from unseen
- **early** (150–300 ms, the VAN range), and/or
- **late** (300–600 ms, the P3b range)?

The transfer crosses lab, cap, subjects, stimulus (central face vs lateral Gabor), and the cause of unawareness (masking vs low contrast).

## 2. Prior art (citation search still to do before sealing; all claims unverified)
- Sanchez et al. 2020: detection decoders transfer across sensory modalities within subjects and sessions (MEG).
- Sergent et al. 2021: active → passive transfer within one paradigm.
- Noorman et al. 2025: masking vs attentional blink in the same subjects, without transferring an awareness decoder.
- Round 18 item 3 (masking → blink, ds001810) was dropped because its target label (T2 identification) was too weak. Here the target label is a direct seen/unseen report, and Fable counts a median of about 164 hits and 180 misses per subject (check in code).

## 3. Rivals and where they disagree
| Rival | Early transfer AUC | Late transfer AUC |
|---|---|---|
| A. Shared awareness signature (early, RPT-like) | > 0.5 | > 0.5 |
| B. Shared access/report signature only (GNWT-like; or decision/report) | ≈ 0.5 | > 0.5 |
| C. Contrast leak (seen Gabors about 4% higher contrast) | small > 0.5 | small > 0.5; removed by matching |
| D. Ocular signals (blinks or saccades differ by report) | > 0.5 via frontal channels | > 0.5 via frontal channels; posterior-only must agree |
| E. Montage or lateralisation mismatch (central faces vs lateral Gabors) | spurious ≈ 0.5 | ≈ 0.5 (false negative); the montage kill test and symmetrised features address this |
| F. Generic evoked-amplitude axis (the decoder reads response size, not awareness) | > 0.5 | > 0.5; the present-vs-catch projection is reported to show it |

- **B vs A is the primary contrast.** Late-only transfer is the expected result, and it reads as access/report, not as evidence against an early signature: the absence of early transfer could also be stimulus-specific.
- **What a positive early result would mean:** an early seen/unseen axis shared across masking and low contrast, across labs. This is new if the prior-art search confirms it.

## 4. Common space and preprocessing (fixed before any label is read)
- **Montage.** Cohen has 63 numbered channels (BC-63-X1; θ/φ in the .vhdr). ds006171 has 128 EEG channels with positions in `electrodes.tsv`. ds006171 is mapped onto Cohen's 63 positions with MNE spherical-spline interpolation; the matrix is fixed from positions only.
- **Symmetrised features (primary).** Each homologous left/right pair is replaced by its mean, and midline channels are kept. This removes lateral topography, so central faces and lateral Gabors share a space. Unsymmetrised features are secondary.
- **Both datasets:**
  - 30 Hz low-pass;
  - average reference after mapping;
  - baseline −100 to 0 ms (Cohen epochs start at −100);
  - resample to 250 Hz;
  - features = mean voltage in 50 ms bins: 150–300 ms (3 bins) for early, 300–600 ms (6 bins) for late.
- **ds006171:** a new full-channel, label-blind prep (the round 19 prep kept ROI aggregates only). It uses the same photodiode rule, 0.1–30 Hz filter on the continuous data, and trial rejection (ROI p-p > 150 µV, VEOG > 80 µV). There is no HEOG subject exclusion (features are symmetrised), but posterior-only is a pre-stated secondary.
- **Cohen:** the epochs on disk (raw int16 × 0.1 µV), low-passed per epoch with padding, then the same steps.
- **Decoder:** shrinkage LDA (sklearn, `solver="lsqr"`, `shrinkage="auto"`), z-scored per feature within each training subject. One decoder for early and one for late, trained on all Cohen subjects pooled.

## 5. Statistic and calls (draft)
- **Per test subject:** AUC of decoder output, seen vs unseen, on contrast-matched trials (within hemifield, 1:1, caliper |Δ ln c| ≤ 0.01, averaged over 200 matchings).
- **Group:** mean AUC − 0.5, one-sided sign-flip test over subjects (10,000), plus a bootstrap 95% CI. Holm correction across early and late.
- **Calls:**
  - EARLY TRANSFER: early p < .05 (Holm) and CI excludes 0.5.
  - LATE ONLY: late passes, early does not.
  - NO TRANSFER: neither passes, and both CI upper bounds are < 0.53.
  - INCONCLUSIVE: otherwise.
- **Secondaries:** unmatched trials; posterior-only channels; unsymmetrised; per-hemifield.

## 6. Kill test (label-free; before sealing)
1. **Montage retention** within ds006171: a leave-one-subject-out present-vs-catch decoder (codes 11–22 vs 31–32; stimulus codes only), native 128 vs mapped and symmetrised 63. Retention = (AUC_mapped − 0.5)/(AUC_native − 0.5); lower one-sided 95% bound ≥ 0.80; native lower bound > 0.5.
2. **Planted transfer:**
   - Pseudo seen/unseen labels at the real per-subject counts.
   - Plant onto pseudo-seen trials a pattern equal to Cohen's seen − unseen mean difference (mapped, symmetrised), scaled so the ds006171 posterior ROI difference at 180–280 ms is −0.69 µV (the sourced bilateral VAN, PRIORART.md) for early, and to the sourced P3b dz 1.67 for late.
   - Required: detection ≥ 0.80 per window, and false calls ≤ 0.05 with no plant.
   - Planting Cohen's own pattern is a best case for transfer. It tests the power of the pipeline, not whether the patterns match.
3. **Training-side ceiling:** leave-one-subject-out seen/unseen AUC within Cohen. These labels were read before, in the sealed VAN study; this is a ceiling, not new evidence.

## 7. Open before sealing
- Prior-art search for cross-lab or cross-paradigm awareness decoder transfer.
- Confirm Cohen's recording reference and the θ/φ convention in BC-63-X1.
- Check the eligibility counts in code.
