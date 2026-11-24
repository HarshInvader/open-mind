# Results: splitting-first post-cutoff pool (part A only; stop rule fired)

Prereg part A: `docs/prereg/2026-11-24_theory_splitfirst_pool_A.md` (sealed 2026-11-24T20:20:24Z, commit 9497381). Part B was never needed.

## Outcome: STOP. The pool is not rated.

- **Search (frozen, Europe PMC):** 200 records taken in relevance order; 198 kept after dropping the earlier pool's DOIs.
- **Writer (Fable 5.2, not blind, cannot select):** screened 157 records and wrote 45 eligible items, one per paper.
  - 112 records were ineligible: review 32, theory 23, not about consciousness 14, case report 13, preprint before the cutoff 12 (one found only by a keyword search, because the earlier preprint had a different title), no mirrorable result 6, commentary 3, protocol 2, simulation only 2, duplicate 2, earlier pool 1, erratum 1, online before the cutoff 1.
- **Blind selector (Fable 5.2):**
  - Rated 270 (theory, item) pairs with outcomes in random A/B order, and never saw which was real.
  - **Only 5 of 45 items** had a real theory with |p − 0.5| ≥ 0.25. The largest commitment on any item was 0.30.
  - The rule needed 12, so the stop rule fired.
- **Commitment distribution** (each item's maximum over the six theories of |p − 0.5|):
  - 2 items at 0.30, 3 at 0.25, 7 at 0.20, 5 at 0.15, 10 at 0.10, 7 at 0.05, 11 at 0.
  - 12 of 45 (27%) reach 0.20, the same rate as the sealed ledger's 4/15.

## What this says

- This is the result part A named in advance: *theories rarely commit on new findings, even when selected for it.*
- These were 45 recent empirical findings on consciousness, written as mirrored pairs. A blind AI rater judged that none of the six theories clearly predicts which way they come out.
  - 73% get no commitment of 0.2 or more from any theory.
  - None gets more than 0.3.
- The sealed ledger found the same thing on a different pool (89% elastic cells), so the pattern repeats.
- **Consequence for the ledger:** the famous-item IIT lead cannot be tested out of sample with the current kind of post-cutoff findings. Recent consciousness papers mostly test questions the big theories do not take sides on, at least as AI models read the theories.
- **Not shown:**
  - whether human experts would read the theories as more committal;
  - whether purpose-built adversarial studies (COGITATE-style), which are rare in a 5-month window, would split them.

## Files

- Code: `search.py`, `select.py`.
- Selection output: `selected.json` (item ids and commitment values; no outcomes).
- Kept local and gitignored: abstracts, the writer's items with outcomes and key, and the selector packet and answers.
- Nothing was rated beyond the selector, and nothing was re-run.
