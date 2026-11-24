# Pre-registration, part A (selection rules): a splitting-first pool of post-cutoff findings for the theory ledger

Agent: Open Mind thread   Date: 2026-11-24   Code: `experiments/theory_splitfirst/`

- **Why:** the sealed post-cutoff ledger (`2026-11-24_theory_postcutoff_ledger.md`) was UNINFORMATIVE. Only 4 of 15 findings split the theories, so the test it was built for (does IIT's lead on famous findings carry over to findings the raters could not have seen?) could not run.
- **This part:** freezes how items are found, written and selected, before any outcome is looked up. Part B (scoring) is sealed later, before any rating packet is built. It reuses the sealed scorer `experiments/theory_postcutoff/score.py` unchanged.
- **Blindness:** the only agent that decides which items enter the pool (the selector) sees findings only as two mirrored outcomes, in random A/B order, and never learns which is real. The writer agent sees outcomes but cannot select. This thread (the orchestrator) does not read titles, abstracts or keys before the run; scripts print only counts.

## A1. Candidate search (frozen)

- Europe PMC REST search, `resultType=core`, default relevance order, query:
  `(consciousness OR "conscious perception" OR "conscious access" OR "visual awareness" OR "perceptual awareness" OR "disorders of consciousness" OR "loss of consciousness" OR "inattentional blindness" OR "backward masking" OR "no-report" OR dreaming OR "global workspace" OR "integrated information") AND FIRST_PDATE:[2026-07-01 TO 2026-11-24] AND HAS_ABSTRACT:Y`
- The first 200 records are kept, with abstracts saved locally (`datasets/local/splitfirst_abstracts/`, gitignored). Only counts are printed.
- Records whose DOI is already in the earlier pool (N01–N19, P02–P04) are dropped.
- Bytes: abstracts only, about 0.5 MB.

## A2. Writer (one agent, not blind; cannot select)

The writer works through the records in search order and stops after 45 eligible items or at the end of the list. A record is eligible only if all of these hold:
1. It is empirical (new data or a new analysis of data); not a review, theory paper, protocol or commentary.
2. It reports a primary result with a direction that can be mirrored, written as "X rather than Y".
3. The result bears on consciousness: awareness, report, levels or states of consciousness, anaesthesia, sleep or dreaming, disorders of consciousness, or consciousness-relevant computation in AI systems.
4. First public posting is on or after 2026-07-01, checked as in the earlier ledger (bioRxiv/medRxiv/arXiv v1 date, or Crossref plus a Europe PMC search for an earlier preprint).

For each eligible record the writer:
- writes `actual` and `mirror` texts that name no theory, author, lab, dataset or journal, and do not hint at which is real;
- assigns a cluster id (one per paper);
- records the DOI and first-posting date.

The writer stores outcomes only in the key file and never in the item text. At most 2 items per paper.

## A3. Selector (one agent, blind)

- **Input:** each item as A/B in seeded random order (seed 1125), with the six real theories and their canonical references (same theory block as the ledger). No outcome, no key, no abstract.
- **Task:** for each (theory, item), p = probability of A rather than B if the theory were true. Same instructions as the ledger's BLIND arm.
- **Inclusion rule:** an item enters the pool if, for at least one of the six real theories, |p − 0.5| ≥ 0.25 (stricter than the ledger's 0.2 splitting bar). If more than 2 items from one cluster qualify, keep the 2 with the largest max |p − 0.5|.
- This rule is symmetric in A and B, so it cannot favour the real side. Selecting on one rater's commitment can inflate splitting by regression to the mean; part B reports how many selected items still split in the test raters.

## A4. Then (rules fixed now, details in part B)

- Recognition gate as in the ledger: exclude an item if any rater model gives p_real ≥ 0.75 or says it recalls the study.
- BLIND and INFORMED arms, 3 models × 2 runs, the sealed scorer, and the same verdict rules, gates and thresholds.
- Toy Z is silent on all new items.
- **Stop rule:** if fewer than 12 items survive selection and recognition, the pool is not rated. That result is reported as "theories rarely commit on new findings, even when selected for it".
