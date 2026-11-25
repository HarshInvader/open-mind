# Are blink trials more alpha-band phase-locked at T2? RESULTS (ds001810, CC0)

Prereg: `docs/prereg/2026-11-25_rhythm_blink.md`, sealed 2026-11-25T14:02:18Z.
- **Hashes:** prereg b1fc60ae…, script 65e7da96…, calibration 098868b4…; the imported `ab_killtest.py` is unchanged since its 2026-11-24 seal.
- **Run:** the gate, then the real-label run, once each at about 14:03Z, on 1 process at nice 20.
- **Data:** ds001810 is CC0 and is not Cohen data, so the Cohen hold does not apply.

## Sealed verdict: NO DIFFERENCE: EQUIVALENT WITHIN ±0.02

- **Gate:** PASS. Label-free, count-independent, debiased all-trial phase-locking: median subject ρ 0.21 (floor 0.10), t(41) = 9.2.
- **Primary.** Count-matched ITC in the ±50 ms around T2, over the central–parietal ROI (C1, Cz, C2, CP1, CPz, CP2, P3, Pz, P4), with a 3-cycle Morlet at 10.9 Hz (about 7–15 Hz). Blink minus no-blink, 42 subjects, 76 blocks:

| Measure | Value |
|---|---|
| Mean Δ | −0.0019 |
| SE | 0.0075 |
| 95% CI | [−0.017, +0.013] |
| t(41), p | −0.25, 0.80 |
| TOST p (±0.02) | 0.010 |
| Subjects dropped | 0 |

- **What ±0.02 rules out:** in calibration, a 1 µV 10.9 Hz signal phase-locked to T2 and added to blink trials gave Δ 0.029–0.138, depending on its phase. An amplitude-preserving 5% phase concentration gave Δ 0.037. Both lie outside the CI. Shuffled-label directional false positives were 5.5%.

## Secondaries (no verdicts)

- **Alpha-band power at T2:** log ratio, blink/no-blink, +0.023 (t 0.89, p 0.38).
- **Count-matched evoked alpha-band amplitude:** log ratio −0.007 (t −0.24, p 0.81).
- **Between subjects:** label-free phase-locking vs blink rate, r = −0.22 (p 0.16, n 42). The sign matches Kranczioch 2017 (more locking, better performance), but it is not significant.
- **Time course:** Δ from −50 to +660 ms, every 20 ms. It stays within ±0.018; one of 36 centres has |z| > 2 (550 ms, z 2.5), which is what chance gives.

## What this does and does not mean

- **Means:** at lag 3 in 42 people, the trials where T2 was missed are not more phase-locked in the alpha band around T2 than the trials where it was identified. Any difference is smaller than what a 1 µV phase-locked signal would produce. This counts against Zauner et al.'s conclusion that alpha entrainment is "the critical factor" for the blink, at least in its within-trial form.
- **Context:** Zauner's own pairwise PLI test was significant only for AB vs control, not AB vs NoAB.
- **Does not mean:** that entrainment plays no role at other lags, in pre-T1 periods (Petro & Keil 2015 report effects there), at the exact stream frequency, or with Zauner's 7-cycle wavelet and linked-ear reference.
- **Limits:**
  - "Blink" means a T2 identification error, not unseen.
  - One dataset, pre-tDCS blocks only.
  - The short wavelet blurs 7–15 Hz.
  - These labels were used before, by the INVALID hypothesis-generator test, for ERP measures only.
