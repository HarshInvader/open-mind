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
