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

## Status: T4 PARKED (2026-11-19, research coordinator's decision)

- **P1: undecidable** at realistic separation on Stockart (above). Not run on real data.
- **P2: not run on real data.** Its planted check is **not finished** and **not part of any decision**. A first synthetic pass ran before the park order arrived; it is recorded below as exploratory only.
- **Why parked:** T4 is this project's own theory, its headline was undecidable, and P2 would be a second try on the same small iEEG set (Fable: under 3% odds of a major result). The process risk is real: P1's draft pipeline "passed" on data with no states in it, and a thread that wants its theory to work will tend to find a P2 pipeline that passes.
- **No Stockart signal has been analysed.** Only the structure of one file (G8) was opened.

### P2 exploratory synthetic pass (not a planted check of record)

`p2_decidability.py` (`p2_decidability.json`, `p2_lapse_followup_b0.2.json`, `p2_lapse_followup_b0.25.json`). Mark 1: 90% patient-bootstrap CI of (miss − correct rejection)/sd inside ±bound.
- Graded / accumulation worlds, calibrated to hit-vs-miss AUROC 0.55-0.84: misses exceed correct rejections by 0.47-1.57 SD; mark 1 never passes; "T4 fails" in 95-100% of runs.
- T4 worlds, no report lapses, 16 patients: pass 85-88% (8 patients: 49-53%).
- T4 worlds with 10% lapses: pass 6-27%. High-confidence misses only (3-5% lapses): pass 42-76% at bound 0.2.
- **Disclosure:** after seeing those numbers I re-ran with a looser bound (0.25), giving 68-92%. That is the tuning-toward-pass risk the coordinator flagged. If T4 is ever revived, the bound must be fixed from a stated argument and re-checked by someone outside this thread before sealing; 0.25 is not a pre-committed value.
