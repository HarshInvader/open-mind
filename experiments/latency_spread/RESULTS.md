# Latency spread of the late seen-trial signal (Cohen et al. 2024, SOA 50): RESULTS

Prereg: `docs/prereg/2026-11-25_latency_spread_cohen.md` (sealed 2026-11-25T11:35:53Z). Run 11:36Z, 38 subjects, 4 workers, nice 20.

## Verdict: INVALID (shape fit failed, prereg section 4)

- The group seen-minus-unseen P3b-ROI difference wave, fitted over 200–600 ms by one Gaussian, gave **R² = 0.693**, below the pre-registered 0.70. The other criteria passed (A 3.62 µV, μ 435 ms, σ_obs 102 ms).
- By the stated fallback there is no refit, no ladder, no gate and no real-data lag. **No seen-trial latency was estimated.**
- The chain's gate step then stopped on the missing ladder file, as expected.

## What the shape step showed (descriptive; group averages only)

Difference wave (µV), every 20 ms:

| ms | 160 | 180 | 200 | 220 | 260 | 300 | 320 | 360 | 400 | 440 | 480 | 520 | 560 | 580 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| µV | 2.31 | 2.59 | 1.42 | 0.66 | −0.92 | 1.13 | 2.91 | 3.50 | 3.72 | 3.25 | 2.78 | 2.43 | 1.99 | 2.01 |

- **An early positive deflection at 160–200 ms**, a dip near 260 ms, then **a broad plateau from about 320 ms that is still ~2 µV at the epoch end (598 ms)**. A single bump is a poor description: the late signal is sustained or truncated by the epoch, not a brief peak.
- Moment SD of the positive wave over 200–600 ms: 89 ms. Under the prereg's assumptions (single non-negative component, inside the window) this would bound the latency SD; here the signal runs past the epoch end, so the bound does not apply.
- 6 of 38 subjects had a non-positive window difference (amplitude scale 0).

## Reading

- The study cannot say how much the late signal jitters. The single-code ladder was the wrong model for this waveform, and the prereg caught that before any lag was read.
- A plateau running to the end of the report-block epoch fits a sustained signal, or overlapping response-related activity (median RT ≈ 560 ms per the reviewer's label-free count), or broad latency spread. These data cannot separate them.
- **No re-run.** The waveform is now seen, so any redesign (a plateau model, a longer epoch) is a new study with its own prereg, not a fix to this one.
