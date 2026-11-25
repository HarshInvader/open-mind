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

## Results

Pending.
