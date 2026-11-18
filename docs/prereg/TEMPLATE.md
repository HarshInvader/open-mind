# Pre-registration: <name>

Agent: <name>   Task: #<id>   Date: <YYYY-MM-DD>

Seal with `.venv/bin/python -I experiments/rules/evidence.py seal docs/prereg/<file>.md` BEFORE computing any outcome on real data. Check with `... evidence.py check <file>`.

1. Question and hypotheses (H1, H2, ...), each with the direction predicted.
2. Data: dataset, version, subjects used (and excluded, with rule), ground-truth type (behaviour / delayed report / none).
3. Preprocessing: channels, filters, epoch length, artefact rule.
4. Measures: exact definitions and parameters.
5. Split: subject-held-out (or lab-held-out for transfer), built with `experiments/rules/evidence.py`.
6. Statistic, null (permutation scheme, n), multiple-test family and correction.
7. Pass marks: what counts as support, as a null, and as a failure.
8. Planted-answer check and surrogate gate that must pass first.
9. Power: smallest effect detectable at this n.
