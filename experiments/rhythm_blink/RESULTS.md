# Are blink trials more alpha-band phase-locked at T2? RESULTS (ds001810, CC0)

Prereg: `docs/prereg/2026-11-25_rhythm_blink.md`, sealed 2026-11-25T14:02:18Z.
- **Hashes:** prereg b1fc60ae…, script 65e7da96…, calibration 098868b4…; the imported `ab_killtest.py` is unchanged since its 2026-11-24 seal.
- **Run:** the gate, then the real-label run, once each at about 14:03Z, on 1 process at nice 20.
- **Data:** ds001810 is CC0 and is not Cohen data, so the Cohen hold does not apply.

## Verdict: NO DETECTABLE DIFFERENCE at n = 42; the equivalence clause is INVALID

- **The sealed script printed "EQUIVALENT WITHIN ±0.02". That clause is INVALID** (coordinator ruling, 2026-11-25).
  - The ±0.02 bound replaced the original ±0.05 after the first shuffled-label calibration.
  - That change was not one of the pre-stated fallbacks. Under the standing rule, any such post-calibration change makes the affected part INVALID, even though it was conservative and made before the seal.
  - Nothing was re-run, and no bound is re-picked.
- **What stands:** the two-sided difference test, which was unchanged. It finds no detectable difference. The CI below is descriptive.

- **Gate:** PASS. Label-free, count-independent, debiased all-trial phase-locking: median subject ρ 0.21 (floor 0.10), t(41) = 9.2.
- **Primary.** Count-matched ITC in the ±50 ms around T2, over the central–parietal ROI (C1, Cz, C2, CP1, CPz, CP2, P3, Pz, P4), with a 3-cycle Morlet at 10.9 Hz (about 7–15 Hz). Blink minus no-blink, 42 subjects, 76 blocks:

| Measure | Value |
|---|---|
| Mean Δ | −0.0019 |
| SE | 0.0075 |
| 95% CI | [−0.017, +0.013] |
| t(41), p | −0.25, 0.80 |
| TOST p (±0.02) | 0.010, INVALID (bound changed after calibration) |
| Subjects dropped | 0 |

- **How large the CI is, descriptively:** in calibration, a 1 µV 10.9 Hz signal phase-locked to T2 and added to blink trials gave Δ 0.029–0.138, depending on its phase. An amplitude-preserving 5% phase concentration gave Δ 0.037. Both lie outside the 95% CI. Shuffled-label directional false positives were 5.5%.

## Secondaries (no verdicts)

- **Alpha-band power at T2:** log ratio, blink/no-blink, +0.023 (t 0.89, p 0.38).
- **Count-matched evoked alpha-band amplitude:** log ratio −0.007 (t −0.24, p 0.81).
- **Between subjects:** label-free phase-locking vs blink rate, r = −0.22 (p 0.16, n 42). The sign matches Kranczioch 2017 (more locking, better performance), but it is not significant.
- **Time course:** Δ from −50 to +660 ms, every 20 ms. It stays within ±0.018; one of 36 centres has |z| > 2 (550 ms, z 2.5), which is what chance gives.

## What this does and does not mean

- **Means:** at lag 3 in 42 people, there is no detectable difference in alpha-band phase-locking around T2 between trials where T2 was missed and trials where it was identified.
  - The 95% CI excludes the differences a 1 µV phase-locked signal produced in calibration.
  - This does not support Zauner et al.'s conclusion that alpha entrainment is "the critical factor" for the blink, at least in its within-trial form.
  - No formal equivalence claim is made.
- **Context:** Zauner's own pairwise PLI test was significant only for AB vs control, not AB vs NoAB.
- **Does not mean:** that entrainment plays no role at other lags, in pre-T1 periods (Petro & Keil 2015 report effects there), at the exact stream frequency, or with Zauner's 7-cycle wavelet and linked-ear reference.
- **Limits:**
  - "Blink" means a T2 identification error, not unseen.
  - One dataset, pre-tDCS blocks only.
  - The short wavelet blurs 7–15 Hz.
  - These labels were used before, by the INVALID hypothesis-generator test, for ERP measures only.
