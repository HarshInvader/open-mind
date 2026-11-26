# Item 1 (round 18): can Sergent's observers' threshold jitter be identified? RESULTS

**Verdict: τ is not identifiable from Sergent's published summaries.** Neither estimator meets the sealed recovery bar, so no real-data estimate is made. This is the pre-stated outcome for this case (prereg fallback table). Item 2 (Sergent's EEG) runs its design gate without k·τ cells.

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

- **2026-11-26, about 19:2xZ:** the run finished, with all 21 cells and the summary written by the sealed code (`out/killtest/killtest_summary.json`). The 2 h harness limit did not interrupt the run.

## Results (100 simulated subjects per cell; 21 cells: k·τ ∈ {0.25 … 3.0} × τ ∈ {1, 2, 3})
- **Recovery bar (prereg §3).** The core cells are k·τ ∈ {0.5, 0.75, 1.0, 1.5, 2.25}, at every τ. In each, at least 90% of studies must have both the median k·τ and the median τ within ±25%.
- **Estimator P:** worst core-cell joint recovery **0.014**. The best cell anywhere was 0.41 (k·τ 1.5, τ 3), and 45–83 of 100 subjects per cell ended at a parameter bound.
- **Estimator S:** worst core-cell joint recovery **0.000**. It recovers well only at large k·τ with τ = 1 (0.73–0.89 at k·τ ≥ 1.5), and fails at small k·τ (0.00–0.06).
- **Envelope (validity range of the fits):** fitted τ runs from 0.1 (the floor) to 6.3 (P) or 3.7 (S).
- **What the bar would have needed:** ≥ 0.90 in every core cell. Both estimators are far below it, so the verdict does not hang on the threshold.

## What this means
- Sergent's published per-condition summaries (behaviour plus decoder means) cannot separate how much observers' thresholds jitter from the rate of the underlying accumulation. Any placement of their data on our false-call map that needs τ is unsupported.
- This does not say that their observers lack jitter, only that these summaries cannot measure it.
- This closes the gate input for item 2. Item 2's prereg (§6 table) says: "τ not identifiable → the gate runs without k·τ cells."

## Not checked
- Trial-level behaviour, if the authors shared it, might identify τ. It is not in the public package; only summaries are.
- With 200 subjects per cell (the pre-stated primary size), recovery could be higher. The 100-subject fallback was triggered by run time. Since the worst core cells are at 0.00–0.01, against a 0.90 bar, doubling the subjects would not close the gap.
