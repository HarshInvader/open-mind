# Addendum to the sealed prereg `2026-11-25_bifurcation_onset_jitter.md` (disclosure, written before any verdict)

Written 2026-11-25T14:34:33Z. The sealed prereg is not edited. At this time the run (`out_jit/`) has not produced a summary, and no cell output has been looked at.

## What was known before the design

The round 17 planner ran a throwaway simulation for this study, recorded in `docs/RESEARCH_STATE.md` (round 17 section). It used the repo's audit/extended code, a true two-state generator with jittered onset, and 16 studies per cell; "called" means Model 3 pxp > 0.95:

| Latency SD | Window (ms re mean onset) | 3-model called | 5-model called |
|---|---|---|---|
| 60 ms | +50 | 1.00 | 0.31 |
| 100 ms | +100 | 1.00 | 0.94 |
| 100 ms | +50 | 1.00 | 0.56 |
| 60 ms | 0 | 0.56 | 0.00 |

I (the Open Mind thread) read this table before writing the prereg. The prereg's line "No model-comparison outcome of any cell was seen before these changes" is true of the prereg's own cells, but it should have named this prior simulation.

## Why the design was not tuned to it

- **Different grid.** The prereg's σ values (0, 40, 80 ms) come from the single-trial P3b latency SD of about 80 ms (Kim et al. 2024), used as an upper anchor. Its windows are a regular 40 ms grid (−80 to +160), plus a dense σ = 0 grid fixed by the 30 ms window algebra after the pre-seal review. None of the planner's σ (60, 100) or windows (+50, +100) is used.
- **Bars not taken from it.** The ±40 ms lag bar is set from Sergent's 30 ms window width (about one and a half windows). The 0.5 crossing level and the 0.95 call threshold are Sergent's, or the midpoint rule.
- **No reference crossing.** The planner's cells do not include σ = 0, so they give no lag. The primary outcome (the lag relative to σ = 0) could not be read from them.

## What it does suggest, stated so readers can weigh it

- With 3-model calls already 0.56 at the mean onset for σ 60, and 1.00 by +50 ms, a large 3-model lag looked unlikely before the run.
- The 5-model calls were much lower near onset (0.00–0.56), so a 5-model (secondary) lag looked more likely.
- A reader may treat the primary 3-model verdict as partly anticipated. The 5-model secondary and the σ = 0 reference were not anticipated by any prior run.

This disclosure is repeated in `experiments/bifurcation_specificity/RESULTS.md` when the results are written.
