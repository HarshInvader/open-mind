# Item 2 (round 18): Sergent 2021's own EEG under the 5-model set. RESULTS (in progress)

Prereg: `docs/prereg/2026-11-25_sergent_eeg_five_models.md` (sealed 2026-11-25T18:02:49Z, commit 6c24525). Design: `DESIGN.md`.

## Run log
- **2026-11-26, about 19:30Z: design gate launched.**
  - **Item 1 outcome:** "τ not identifiable from Sergent's published summaries" (`../sergent_jitter/RESULTS.md`). Prereg §6 therefore says the gate runs without k·τ cells. Command: `sergent_gate.py run` with no arguments, at nice 20.
  - **Seal check:** the hashes match (checked 17:39Z on the new Mac).
  - **Environment:** `.venv`, Python 3.15.2, numpy 2.5.5, scipy 1.18.1.
  - **Workers:** the sealed code fixes `WORKERS = 4`. This is kept, as for item 1. Each cell's seed is fixed, so the worker count changes only the run time.
  - **Resuming:** the run is resumable per cell file and is relaunched with the same command if the 2 h harness limit stops it.
  - **Log:** `out_gate/gate_run.log`. No Sergent EEG byte has been fetched.
- **Worker cap (coordinator, 2026-11-26):** this gate run keeps the sealed 4 workers and is not interrupted. From the next launch on (`rerun`, `summary`, and `analyse.py fit`), item 2 runs through `capped.py`. That is an unsealed wrapper that imports the sealed modules unchanged and caps their Pool at 3. Per-study seeds come from a SeedSequence keyed by the cell, and `Pool.map` keeps order, so results do not depend on the worker count. A check confirmed that both patched pools start 3 processes.
- **2026-11-26, about 21:30Z: gate stopped at the 2 h harness limit; tier-deciding cells complete.**
  - Done: all 6 d0.89 cells (B_bifurcation plus the 5 graded cells), and het0.89 B_bifurcation and G_jitter_mid. Remaining het0.89 cells and B sensitivity points are resumable with `capped.py sergent_gate run` (3 workers).
  - `summary` (run through `capped.py`) gives **TIER 2** at d0.89: every graded cell's 5-model Model 3 call rate is 0.00 (spec ≤ 0.10 met), but B_bifurcation recall is also 0.00 (< 0.80).
  - Per prereg, tier 2 means: streaming is allowed, and the reading is one-sided. Only a Model 3 call on the real data counts; anything else is UNRESOLVED, never evidence against bifurcation.

  | d0.89 cell | 5-model call | 3-model call | winner counts (none, M1..M5) |
  |---|---|---|---|
  | B_bifurcation | 0.00 | 0.22 | 0,0,15,16,58,11 |
  | G_heavy | 0.00 | 0.73 | 0,0,0,0,0,100 |
  | G_jitter_hi | 0.00 | 0.02 | 0,0,7,6,52,35 |
  | G_jitter_mid | 0.00 | 0.05 | 0,0,21,6,48,25 |
  | H_gain | 0.00 | 0.00 | 0,0,76,0,0,24 |
  | H_jitter_t | 0.00 | 0.70 | 0,0,0,0,0,100 |

  - **Note (descriptive):** the 3-model comparison (null, 2B, M3) would falsely call Model 3 in 73% (G_heavy) and 70% (H_jitter_t) of graded studies. This is why the sealed call uses the 5-model set; it is the reason the 3-model column is not used for any call.
  - het0.89 (partial): B_bifurcation 0.00 (3-model 0.30), G_jitter_mid 0.00 (0.05).
- **2026-11-26T21:31:33Z: gate resumed** with `capped.py sergent_gate run` at nice 20. The process list shows 3 spawn workers plus multiprocessing's resource tracker. Finished cell files are skipped. Output is appended to `out_gate/gate_run.log`. After this: `summary`, then streaming once, per the prereg.
- **2026-11-26T23:31:44Z: resumed gate stopped at the 2 h harness limit; 1 cell left.**
  - Newly done: all 6 het0.89 cells and d1.0 B_bifurcation. With between-subject DMAX spread, every graded cell's 5-model call rate is still 0.00 (3-model: G_heavy 0.76, H_jitter_t 0.77, G_jitter_hi 0.04, H_gain 0.00). B_bifurcation recall stays 0.00 at d1.0 (3-model 0.37).
  - Remaining: d1.25 B_bifurcation (sensitivity only; it does not change the tier). Resumable with the same `capped.py sergent_gate run` command, about 25 min.
  - The summary is unchanged: **TIER 2** at d0.89.
