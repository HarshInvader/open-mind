# T4 P1 planted decidability check (synthetic only)

Run 2026-11-19 by mind-ne. Script: `p1_decidability.py` (30 runs per scenario, `p1_run.log`). No Stockart signal was read.
Setup: real no-report trial counts (72 per intensity level in Grenoble, 48 in Brno), 16 VVC patients (10 as a pessimistic case), late score anchored to a pre-onset reference, trial drift removed within block, 5-fold held-out likelihood within patient, patient bootstrap across patients.

## Finding 1: the draft pipeline was invalid
Against the draft's only rival (a free skew-normal), the two-state model "won" on graded data with no states in it (3 of 3 quick runs). The skew-normal fit is unstable at about 58 training trials and predicts held-out trials badly. Fix: the mixture must beat both a normal and a bounded skew-normal (|shape| ≤ 5). After the fix, no null passed.

## Finding 2: P1 is decidable only for very well separated states

| Scenario | Pass rate |
|---|---|
| Two states, d′ = 1.0 | 0% |
| Two states, d′ = 1.5 | 0% |
| Two states, d′ = 2.0 | 10% |
| Two states, d′ = 2.0, heavy-tailed noise (t5) | 0% |
| Two states, d′ = 3.0 | 100% |
| Two states, d′ = 3.0, 10 patients | 97% |
| Graded normal, d′ 1 and 2 | 0% |
| Graded right-skewed | 0% |
| Graded heavy-tailed | 0% |
| Graded + attention drift | 0% |
| Leaky accumulator | 0% |
| Accumulator absorbed at a bound | 0% |

The draft rule calls P1 testable only if it passes ≥ 80% of planted mixtures and ≤ 5% of nulls, at the separation the data plausibly have. Stockart report hit-vs-miss AUROC of about 0.8 in their best patients, which is d′ ≈ 1.2. At that separation the pass rate is 0%.

**Verdict: P1 as written cannot decide on this dataset.** It is not run on the real data. A real "fail" would be uninformative and a "pass" would require separation far above what the paper reports.

The accumulator-to-bound case also failed to pass, so with this pipeline a bound in the authors' model would not fake a two-state result. That is reassuring but moot.

## Next
P2 (misses vs correct rejections, and label-free state assignment predicting report, on delayed-report trials) uses the no-stimulus trials as an anchor rather than distribution shape, and should have more power. It gets the same planted check before anything is sealed.
