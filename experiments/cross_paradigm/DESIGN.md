# Item 3 (round 18): cross-paradigm awareness decoder, masking → attentional blink. DESIGN DRAFT (not a prereg, not sealed)

Status 2026-11-25: prior-art read done; kill-test design below; two decisions open for the coordinator (§5).

## 1. Question

Does a seen-vs-unseen EEG decoder trained on backward masking (Cohen et al. 2024, masked faces at SOA 50 ms, report block) predict T2 outcome in the attentional blink (ds001810, lag 3, T1 correct), zero-shot? The transfer crosses labs, caps, subjects, stimuli and access-failure mechanisms.

## 2. Prior art (library entries added 2026-11-25)

| Paper | What it did | Gap for us |
|---|---|---|
| Sanchez et al. 2020 PNAS (`sanchez-2020-supramodal-decoding`, full) | Detected-vs-undetected MEG decoders transfer across touch, vision and hearing within subjects and within a session; late window | Same subjects, sensors and task; no masking-vs-attention or cross-lab transfer |
| Noorman et al. 2025 eLife (`noorman-2025-masking-vs-blink`, full) | Performance-matched masking vs blink, same subjects: late integration (~200–250 ms) impaired by masking, spared by the blink | Decodes stimulus features, never transfers an awareness decoder between the two |
| Fahrenfort et al. 2017 PNAS (`fahrenfort-2017-integration-without-access`, abstract) | Integration signatures survive the blink, not masking | Same |
| Salti et al. 2015 eLife (`salti-2015-conscious-codes`, abstract) | Seen-only information from ~270 ms in parietal and frontal cortex | Single paradigm |
| Sergent et al. 2021 | Decoder transfers from active to passive sessions | Same paradigm and subjects |

We found no zero-shot cross-dataset transfer of an awareness decoder between masking and the blink. Noorman 2025 gives a directional prediction: if the masking decoder leans on integration stages that the blink spares, transfer should be weak in the 200–250 ms window and survive only in the later access window (≥ 300 ms, P3b-like).

## 3. Data on disk (layout checked; no labels touched)

| | Cohen 2024 (train) | ds001810 (test) |
|---|---|---|
| Epochs | 40 subjects, SOA-50 report trials, −0.1 to 0.6 s, 500 Hz | 84 files (42 subjects × 2 pre-tDCS blocks), T2-locked, −0.2 to 0.8 s, 512 Hz |
| Channels | 63, numbered cap (BC-63-X1); positions only as spherical θ/φ in the .vhdr | 64 Biosemi 10-10 names (+ EXG, Status) |
| Label | seen / unseen report | T2 identification correct / incorrect (not seen vs unseen) |
| Licence and hold | no licence stated; Cohen hold until a reply or 2026-12-08 (no site or post) | CC0 |

## 4. Kill test first: montage transfer inside ds001810

Coordinator's condition: a montage-transfer control inside ds001810 must keep at least 80% of AUC.

- **Common space.** Cohen's 63 positions (θ/φ to unit sphere). ds001810's 64 channels are mapped onto them by spherical-spline interpolation (MNE's interpolation matrix, fixed before any label is read). Average reference after mapping; 30 Hz low-pass; 250 Hz resampling for both sets; features = mean voltage in 50 ms bins over 0–600 ms (the part both epochs share).
- **Control.** Within ds001810, a leave-one-subject-out decoder (shrinkage LDA, fixed) is trained and tested twice: on the native 64 channels and on the 63 mapped channels. Retention = (AUC_mapped − 0.5) / (AUC_native − 0.5). It passes if retention ≥ 0.80 (lower one-sided 95% bound by a subject bootstrap), and AUC_native's lower bound is above 0.5.
- **Second control (Cohen side).** Within Cohen, leave-one-subject-out seen/unseen AUC on native channels gives the training-side ceiling (our sealed VAN/P3b result implies clear above-chance decoding).
- **Main test (only if both controls pass).** Train on all Cohen subjects, test on every ds001810 subject; per-subject AUC; one-sided t against 0.5; transfer is also reported as a share of the within-ds001810 ceiling. Window-wise (Noorman's prediction): 200–250 ms vs ≥ 300 ms, pre-stated.

## 5. Open decisions for the coordinator (before any prereg)

1. **The target label is weak, and its held-out half has been used.** In the sealed hypothesis-generator test, the T2 P3b gate failed on the held-out 21 subjects (AUC 0.491). The descriptive cross-subject decoder was 0.529 [0.507, 0.548]. So:
   - the within-ds001810 ceiling is about 0.53, and "80% of AUC" taken literally (0.8 × 0.53 = 0.42) is meaningless; the draft above uses 80% of the excess over chance;
   - even so, a ratio of two near-chance AUCs is noisy, and the control may fail for power reasons alone;
   - item 3 is a new question, but it reuses labels from a sealed failure line that was closed with "no redesign with new labels". Is that acceptable?
2. **If (1) is a no-go,** the cleaner target is a blink dataset with a seen/unseen report. None is on disk, and it would need a download exception.

## 6. Cost

No streaming. Features are small (≈ 13 bins × 63 channels × ~10k trials). Minutes on 1–2 workers, so no coordinator launch is needed for the kill test itself.
