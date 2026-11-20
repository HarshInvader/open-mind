# No-report bifurcation: planted power kill test (2026-11-20)

**Result: killed.** At the d' these datasets likely have, the T4 planted two-state pipeline detects a real planted mixture in 0 of 50 simulated studies. Power below 80% was the kill rule (coordinator brief); the observed power is 0%.

| Design (real counts) | d' = 1.0 | d' = 1.25 | d' = 1.5 |
|---|---|---|---|
| Cohen 2024 (40 people, 135 trials per level, 160 reference) | 0/10 | 0/10 | 0/10 |
| Sergent 2021 (20 people, 150 per level, 150 reference) | 0/10 | 0/10 | not run |

- One-sided 95% upper bound on power for 0/10: 0.26 (Clopper-Pearson), so every cell is well below 0.80.
- Expected d' is about 0.95, from Sergent 2021's report-prediction AUC > 0.75. Single timing runs passed at d' = 3, consistent with T4 (`experiments/our_theory/t4_planted/RESULTS.md`: 0% at d' 1-1.5, 100% at d' 3 at Stockart counts).
- More subjects and trials (Cohen) did not lift power at d' <= 1.5: the limit is the overlap of the two states, not the sample.
- Null false-pass scenarios were not run: they matter only if power survives.
- No real data was looked at; Cohen's OSF data has no licence stated and was not downloaded.

**What this means.** Single-trial bimodality at fixed strength cannot be tested decisively on these EEG datasets with this pipeline: a null result would be uninformative, and a positive one would need a separation about three times what the report decoding implies. The originating lab's mixture-model results (Sergent 2021; Boyer 2026) also have no published planted check; whether their model comparison is better powered than ours is an open question, not tested here.

Files: `kill_planted.py` (generators, scenarios), `kill_power.py` (the cut-down run, one line per rep in `kill_power.jsonl`), `PRIOR_ART.md`.
The first full-grid run (`kill_planted.py 30`) was stopped by the 2-hour limit before any scenario finished (about 230 s per Cohen rep) and produced no results.
