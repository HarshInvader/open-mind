# Rules of evidence and leakage check (task #1)

**Verdict: the toolkit catches every planted leak in the dry run (PASS).** A leaked epoch-level split was flagged in 5 of 5 folds; it inflated AUC to 0.92 on data with no state effect, while the clean subject split gave 0.63 (chance range for 20 subjects). A subject re-uploaded under a new ID, a lab on both sides of a transfer split, and a pre-registration edited after sealing were each caught.

## What exists now

- `experiments/rules/evidence.py`: import it from any experiment.
  - `seal(paths)` appends `sha256  path  UTC-time` to `docs/prereg/HASHES.txt` (append only). CLI: `.venv/bin/python -I experiments/rules/evidence.py seal docs/prereg/X.md`.
  - `require_sealed(path)` raises `SealError` unless the file's current hash was sealed, so edited goalposts fail loudly. CLI: `... evidence.py check FILE`.
  - `Recording(rec_id, subject, lab, dataset, fingerprint)` and `fingerprint(signal)`: a content hash that survives dtype changes and rescaling (V vs uV).
  - `subject_folds(recs, k, mode)`: folds grouped by subject (`within`) or by lab (`transfer`, because same-lab data is a near-copy). Recordings with the same fingerprint are merged into one group.
  - `check_split(train, test, mode)`: raises `LeakageError` if a subject, an identical signal, or (in transfer mode) a lab sits on both sides. Call it on every fold.
  - `ledger_rows_write(path, rows)`: validates rows against `LEDGER_COLUMNS` and writes `ledger_rows.csv`. Confirmatory rows must have a held-out split.
  - `auc`, `perm_auc_within_subject`: Mann-Whitney AUC and a label-permutation null that permutes within subject.
- `docs/test_ledger.csv`: header only. Columns are the Open Indus ledger with `distinct_text_unit` renamed `distinct_subjects` and a `ground_truth` column added (behaviour / delayed_report / none / synthetic). The lead merges agents' `ledger_rows.csv` into it.
- `docs/prereg/TEMPLATE.md`: the nine things every pre-registration states.

## Dry run (`dry_run.py`, output `dry_run.json`)

Synthetic: 20 subjects x 30 epochs, two labs, label fixed per subject, features carry only subject identity (no real effect).

| Planted leak | Expected | Result |
|---|---|---|
| Epoch-level 5-fold split | flagged, AUC inflated | flagged 5/5 folds, AUC 0.92 |
| Subject-level 5-fold split | clean, AUC near 0.5 | clean, AUC 0.63 (one draw; SD of AUC with 10 vs 10 subjects is about 0.13) |
| Subject s00 re-uploaded as s99 in test | flagged by fingerprint | caught; `subject_folds` keeps the twins in one fold |
| Transfer split with labB on both sides | flagged | caught |
| Pre-registration edited after sealing | `require_sealed` fails | caught |

## Not checked

- Fingerprints catch exact or rescaled copies, not re-filtered or re-referenced copies of the same recording. Cross-dataset duplicates of that kind (e.g. one sleep study redistributed in two archives) need a metadata check (age, sex, recording date), which the dataset audit (#2) should supply.
- Multiple-test correction (q columns) is left to the lead's merge script, as in Open Indus.

| Hypothesis | Status |
|---|---|
| Split helper flags epoch-level leakage | supported (5/5) |
| Fingerprint flags a renamed duplicate | supported |
| Transfer mode flags same-lab near-copies | supported |
| Seal check flags an edited pre-registration | supported |
