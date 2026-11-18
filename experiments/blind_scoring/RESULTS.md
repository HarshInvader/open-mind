# Blind strict scoring of T1, T2, IIT 4.0 and GNWT (task #30)

## Conclusions

1. **Neither candidate leads IIT or GNWT under strict rules.** Out of 250, the strict totals are GNWT 110, IIT 98, T1 97 and T2 97. T1 minus IIT is −1 (95% CI −18 to +17). T1 minus GNWT is −13 (CI −42 to +13). T2 gives the same differences: −1 (CI −21 to +20) and −13 (CI −42 to +13). Every interval includes zero. On the ledger alone, the four theories cannot be told apart.
2. **The authors' self-scoring was inflated.** coverage.csv gives T1 156 and T2 141. My blind totals are 97 for both. Most of the gap comes from "explains" marks: the authors gave 20 to T1 and 18 to T2. Those findings were all in the ledger before either theory was written, so each one is a retrodiction. When I cap the authors' "explains" at "compatible", their totals fall to 108 (T1) and 100 (T2), close to mine. After that cap, agreement rises from κ ≈ 0.21 to κ = 0.63 (T1) and 0.56 (T2). In short, the authors applied a lenient rule to their own work, and their reading of the evidence was otherwise close to mine.
3. **The strict rule also cuts IIT and GNWT**, which is why the comparison stays fair. The scorecard gave IIT 119 and GNWT 115. Under the same strict rule I give 98 and 110. IIT drops more because many of its "explains" cells (cerebellum, posterior lesions, posterior stimulation, NREM dreams) are findings that came before the theory and motivated it. I kept IIT's "explains" only where a prediction was written down before the test: PCI, the ketamine complexity result, TMS-EEG bistability in sleep, and posterior slow waves in dreams.
4. **Only new tests can separate T1 and T2 from the rivals.** Under strict rules, T1 and T2 cannot earn "explains" from this ledger at all. Their maximum is "compatible" on every row. Whether either theory is better than IIT or GNWT depends on its risky predictions, such as T1-P1 on DREAM data, and not on fit to the ledger.

## Totals (58 constraints, C59 excluded, max 250, 10,000 constraint bootstraps, seed 30)

| Theory | Strict total | 95% CI | explains | compatible | silent | strained | contradicts |
|---|---|---|---|---|---|---|---|
| GNWT | 110 | 86 to 134 | 7 | 37 | 10 | 4 | 0 |
| IIT 4.0 | 98 | 74 to 121 | 4 | 38 | 12 | 4 | 0 |
| T1 (settling window) | 97 | 75 to 117 | 0 | 45 | 9 | 4 | 0 |
| T2 (anterior-posterior settling) | 97 | 75 to 117 | 0 | 45 | 9 | 4 | 0 |

| Difference | Value | 95% CI | Bootstrap share > 0 |
|---|---|---|---|
| T1 − IIT | −1 | −18 to +17 | 43% |
| T1 − GNWT | −13 | −42 to +13 | 16% |
| T2 − IIT | −1 | −21 to +20 | 44% |
| T2 − GNWT | −13 | −42 to +13 | 16% |
| T1 − T2 | 0 | −12 to +12 | 35% |
| IIT − GNWT | −12 | −39 to +14 | 17% |

T1 and T2 tie by coincidence. T1 is strained on C51, where prefrontal cholinergic stimulation reverses anaesthesia. T2 is strained on C08, where large prefrontal lesions leave people conscious. Both rows have the same weight.

**Sensitivity check.** For every cell where my mark and the original mark differ by two levels or more, I took the stricter of the two. That gives GNWT 102, IIT 92, T1 93 and T2 85. The order does not change, and every difference stays inside the intervals above.

## Agreement with the original marks (compared only after marks.csv and totals.json were written)

| Theory | Compared with | Exact agreement | Cohen's κ | Linear-weighted κ | Their total | Blind total |
|---|---|---|---|---|---|---|
| GNWT | scorecard.csv | 46/58 | 0.67 | 0.72 | 115 | 110 |
| IIT 4.0 | scorecard.csv | 37/58 | 0.47 | 0.53 | 119 | 98 |
| T1 | coverage.csv | 31/58 | 0.22 | 0.34 | 156 | 97 |
| T2 | coverage.csv | 31/58 | 0.21 | 0.31 | 141 | 97 |

After capping the authors' "explains" at "compatible", κ is 0.63 for T1 and 0.56 for T2.

## Every cell that differs by two levels or more (13; full text in `disagreements.csv`)

| Row (grade) | Theory | Blind | Original | Who is stricter |
|---|---|---|---|---|
| C24 (A) attentional blink | T1 | strained | compatible | blind. T1 needs a capacity assumption it does not state; coverage.csv's own reason says so, yet marks the row compatible. |
| C24 (A) | T2 | strained | compatible | blind (same reason) |
| C42 (B) conscious delta | T1 | strained | compatible | blind. The fit depends on the untested P4; coverage.csv's reason says "allowed only if…" |
| C42 (B) | T2 | strained | compatible | blind |
| C42 (B) | IIT | strained | compatible | blind (the same assumption, applied to IIT for fairness) |
| C14 (B) ketamine dreams | T2 | compatible | strained | authors. Lee 2013 shows ketamine cuts frontal-to-parietal feedback, yet people dream. That is a real problem for T2's anterior loop, and I missed it. |
| C17 (B) posterior slow waves in dreams | T2 | compatible | strained | authors. Siclari 2018 links frontal slow waves to recall, which is the opposite sign to T2. I missed this. |
| C31 (B) rivalry without report | T2 | compatible | strained | authors. T2 has to say frontal re-entry is invisible to fMRI. |
| C09 (B) prefrontal lesion and masking | T1 | compatible | strained | authors |
| C11 (B) prefrontal stimulation | GNWT | compatible | strained | scorecard |
| C14 (B) ketamine | GNWT | compatible | strained | scorecard |
| C32 (B) prefrontal rivalry neurons | IIT | compatible | strained | scorecard |
| C04 (C) split-brain unity | IIT | compatible | strained | scorecard |

The disagreements run both ways. On T2, the authors were harsher than I was on three rows. Each of those points is a real weakness of T2's anterior-loop condition. That is why T2's sensitivity total (85) is the lowest of the four.

## Method

- **Inputs read before marking:** ledger.csv and its RESULTS.md; the claim, mechanism, conditions and prediction sections of T1.md and T2.md, extracted by line range; the method section of theory_scorecard/RESULTS.md; and the DOI citation columns of scorecard.csv for IIT and GNWT. The statements of IIT and GNWT came from the cited proponent papers: Albantakis et al. 2023 (IIT 4.0, doi:10.1371/journal.pcbi.1011465), Tononi & Koch 2015 (doi:10.1098/rstb.2014.0167), Tononi et al. 2016 (doi:10.1038/nrn.2016.22), Mashour et al. 2020 (doi:10.1016/j.neuron.2020.01.026) and Dehaene et al. 2006 (doi:10.1016/j.tics.2006.03.007). I added no new citations.
- **One leak to disclose.** T1.md opens with a "Status" paragraph, above its claim section, that states T1's self-scored totals (156, and 108 under strict reading) and the scorecard's IIT 119 and GNWT 115. I saw those four numbers before marking. They contain no cell marks. I did not read coverage.csv, CRITIQUE.md or the scorecard's mark column until the totals were written.
- **Strict rule, applied the same way to all four theories:**
  - **explains:** a prediction written before the finding was known, or derived independently of it, that the finding then confirmed. A finding that came before a theory and motivated it counts as "compatible" for that theory too.
  - **T1 and T2:** both were written after the whole ledger had been read, so no row can be "explains".
  - **strained:** the fit needs an assumption that is not in the stated theory.
- **Weighting:** the same as the scorecard. Grade A counts 3, B counts 2 and C counts 1. Marks score explains +2, compatible +1, silent 0, strained −1 and contradicts −2. C59 is excluded, which gives a maximum of 250.
- **CIs:** resample the 58 constraints with replacement 10,000 times, recompute each total and each difference, and take the 2.5th and 97.5th percentiles.
- **Kappa:** unweighted Cohen's κ over the five ordered levels, plus a linear-weighted κ.

## Limits

- I am the only rater. I am also an AI model of the same kind that wrote T1 and T2, so the marks are blind to the earlier marks but not independent of their reasoning style.
- Several cells are judgement calls. In particular, GNWT's "explains" on C13 and C32, and the cutoff I used for "predates and motivated" when grading IIT, could reasonably go the other way. Each B-grade cell is worth 2 to 4 points, well inside every CI.
- coverage.csv has no row for C59. That row is excluded from all totals anyway.

## Files

- `build_marks.py` → `marks.csv`: 236 cells, one line of reasoning each.
- `totals.py` → `totals.json`: totals and bootstrap CIs.
- `compare.py` → `compare.json` and `disagreements.csv`. This script was run only after marking and totals were finished.
