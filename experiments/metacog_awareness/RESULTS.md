# Does awareness add metacognition beyond a single-evidence observer? (Rausch 2016)

**Verdict: VOID (terminal).** This is the sealed rule's outcome; we make no claim either way about awareness-linked metacognition.

## What was tested
Thorat & Chopra (2026, arXiv:2609.33366) list "knowing when you are right at matched first-order performance" as a functional marker of awareness. We asked:

> At a fixed contrast, does confidence track accuracy better on high-visibility trials than a single-evidence observer predicts?

- **Pre-registration:** `docs/prereg/2026-11-23_metacog_awareness_rausch2016.md`, sealed in commit e5df6c2 (sha256 1b226526...) before the trial data was downloaded.
- **Gates passed before sealing:** the null rejected in 1.7% of datasets and the planted effect was caught in 98% (`gate2.json`).

## Data
- **Source:** Confidence Database, `data_Rausch_2016.csv` (OSF zy43r; sha256 b9fd2ac0...; 8,399 rows).
- **Exclusions:** 840 training rows and 1,260 contrast-0 rows dropped; 0 unparsable.
- **Kept:** 6,300 trials, 20 subjects, 5 contrasts (2.2-6.9%). 18 subjects had a computable AUROC2 gap.

## Result
The sealed void rule fired: one fitted-null moment lay more than 3 null SDs from the observed value.

| Moment | Observed | Null mean | z |
|---|---|---|---|
| Confidence-accuracy r (within cell) | 0.341 | 0.283 | **3.95** |
| Visibility-accuracy r | 0.244 | 0.210 | 2.36 |
| Confidence-visibility r | 0.673 | 0.669 | 0.39 |
| Visibility-contrast r (within subject) | 0.723 | 0.735 | -2.61 |

The fit pushed confidence noise to its floor (sc = 0.068, so confidence is close to a noiseless |e|), with sv = 0.51 and gamma = 0.54. Even then the null cannot make confidence as predictive of accuracy as it is in the data. In plain terms, confidence here carries more information about accuracy than a one-sample read-out of the decision evidence allows.

**What may be said:** the single-sample SDT observer is not an adequate null for confidence in these data.
- **Candidate explanations:** extra or post-decisional evidence (two-stage or WEV-type models); d′ drift within a subject × contrast cell; lapses; non-Gaussian evidence. We did not test between them.
- **Awareness:** the void neither supports nor excludes awareness-linked metacognition. A real effect could itself raise moment z (the planted maximum in gate 2 was 3.28).

**Reported for completeness, not interpreted** (computed against a misfitting null):
- primary p = 0.89, interaction-coefficient excess -0.075;
- AUROC2 gap excess 0.037, 95% CI [-0.044, 0.142].

The secondary analyses (by rating order, and without the lowest contrast) all have confidence-accuracy z of 2.5-2.9. They are non-gating and are not interpreted either.

## What follows (Fable round 7, agreed)
- **Stop and log.** That confidence needs more than a single evidence sample appears established: Pleskac & Busemeyer 2010 (2DSD, unverified) and Rausch's weighted-evidence-and-visibility (WEV) model papers from 2018 on (unverified; some were fitted to this paradigm). A new prereg with a two-sample null would mostly rediscover this.
- **The one open question** is whether a confidence × visibility excess survives a WEV-type null. This dataset can't answer it:
  - power at a 0.03 excess was 42%, and a richer null absorbs more;
  - the CI half-width is about 0.09.
- **Reopen only if both hold:**
  - a reading of Rausch 2018/2020 shows the split-by-visibility test is not already done;
  - a dataset several times larger with both ratings on every trial exists.
- **Lesson for future preregs:** check the null against the known confidence-model literature before sealing.

## Files
- `run_rausch.py` (sealed);
- `rausch_result.json` (full output);
- `gate2.py`, `gate2.json` and `power_gate.py` (gates).
