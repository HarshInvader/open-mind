# Item 1 (round 18): can Sergent's observers' threshold jitter be identified? RESULTS (in progress)

Prereg: `docs/prereg/2026-11-25_sergent_observer_jitter.md` (sealed). Code: `jitter_recovery.py` (sealed).

## Run log

- **2026-11-25, about 17:08:34Z:** the kill test was launched at the pre-stated 200 subjects per cell (21 cells, 4 workers).
- **17:43:10Z: fallback triggered.**
  - The prereg's fallback table says that if the kill-test run time projects above 3 h on 4 workers, the test is rerun "with the optional argument `100` (subjects per cell)… Nothing else changes."
  - The projection: total ≈ 21 cells / 4 workers × cell time, so the run goes past 3 h when a cell takes more than about 34.3 min of wall time. At 34.6 min no cell had finished, and each worker had used about 30 CPU-min.
  - So the 3 h rule applied whenever the first cell would have finished.
  - No 200-subject cell file had been written, so none exist to mix with the new run, and the cell filenames carry `_n100` anyway.
- **17:43:37Z:** the coordinator stopped the run by pid and relaunched `killtest out/killtest 100`, with its log at `out/killtest_n100.log`. Nothing else changed.

- **2026-11-25, evening (old Mac):** the log showed 11 cells done, but only 8 cell files moved to the new Mac: all τ=1 cells and kt0.25/τ2. The other 3 are recomputed. Each cell has its own seed, so the recomputed cells come out identical.
- **2026-11-26, 17:39:12Z (new Mac, resume): not a design change.**
  - The sealed hashes in `docs/prereg/HASHES.txt` match the files on disk, so the path move changed nothing.
  - Relaunched the same command, `killtest out/killtest 100`, with its output appended to `out/killtest_n100.log` (pid 99902, `nice -n 20`). The script skips cells that already exist.
  - New environment: `.venv` with Python 3.15.2, numpy 2.5.5, scipy 1.18.1, pandas 3.1.1, scikit-learn 1.9.1, mne 1.13.2, antropy 0.2.3.
  - Library check before resuming: we recomputed subject 1 of the finished cell kt0.25/τ1 on the new libraries. The true values, the P and S fits (kt, τ, k) and the losses were all identical to the old file (difference 0.0), so old and new cells can be mixed.
  - Workers: the sealed code fixes `Pool(4)`, and we kept it, as the coordinator allowed. This is one more than Mind's cap of 3. Each cell is seeded by `SeedSequence([SEED, kt, tau])`, so the worker count changes only the run time.
  - The harness limits a background command to 2 h. Cells are written atomically, so the run is relaunched with the same command until all 21 cells exist.

## Results

Pending.
