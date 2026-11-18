# Brief for every agent on this project

Repo: `.`. Python: `.venv/bin/python` (create with `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`). EEG work uses MNE-Python; fetch data with scripts into `data/` (never committed).

Goal: see `README.md`. We test theories of consciousness by what they predict about brain data. We never claim to solve the hard problem, never score an AI system's self-report as evidence, and never call a measure a diagnostic. A well-supported negative result is worth more than an impressive one.

## Data
`docs/DATASETS.md` lists each dataset with its access route, licence, size and ground-truth type: behavioural, delayed report, or none. Read it before downloading anything. Big sets (COGITATE MEG at 700 GB) are out of scope on this laptop; work on subsets and say so.

## Rules of evidence (non-negotiable)
1. **Held-out by subject and by lab.** Never split epochs of one subject across train and test. Data from the same lab or protocol counts as a near-copy when testing transfer.
2. **Pre-register.** Measure, preprocessing, threshold, metric and pass mark go in `docs/prereg/<name>.md`; append its sha256 to `docs/prereg/HASHES.txt` before you look at outcomes.
3. **Spectral baseline.** Every measure is compared with the 1-40 Hz spectral exponent, band power and a simple arousal classifier. A measure that adds nothing over these goes in the negative atlas.
4. **Surrogate gate.** Every measure runs on phase-randomised, spectrum-matched surrogates first. If it calls surrogates of conscious data "conscious", it measures the spectrum.
5. **Planted answer.** A pipeline must recover an injected effect of known size at our sample size, and Φ proxies must rank known-Φ toy networks correctly, before their brain-data output counts.
6. **Ground-truth grading.** Label every recording by what its truth rests on: behaviour, delayed report, or none. L2 claims need delayed report.
7. **Nulls, power and multiple tests.** Use permutation nulls, give the detectable effect size for every negative, and add a row to the project test ledger for every test.
8. **Confounds.** Check age, drug-specific EEG signatures, muscle artefact, eyes open or closed, site and amplifier.
9. Write plainly. Lead with the conclusion.

## Output
Work in `experiments/<area>/` and give each area a `RESULTS.md`:
- the verdict first;
- numbers, nulls, CIs and the held-out result;
- what was not checked;
- a hypotheses table.

Also write `results.json` and `ledger_rows.csv` in the same folder. Do not edit other agents' folders. Do not git commit.
