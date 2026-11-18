# Dataset audit (task #2)

**Verdict: the root goal's data criterion fails as written.** Open data covers 2 of the 3 required families (sleep and anaesthesia). Disorders of consciousness have no fully open EEG set. Ketamine, one of the three dissociation cases, has no open data either: the only set with post-ketamine reports (Zenodo 806176) is restricted. Within the two families, 7 open datasets qualify, and the DREAM database gives about 2,000 open awakenings with delayed reports. Full table and per-dataset notes: `docs/DATASETS.md`.

## Numbers

- Qualifying (open, no login, subset fits the budget): ds005620, Chennu 2016, ds004541 (anaesthesia); Sleep-EDF, DREAM Tononi, DREAM LODE, DREAM DeGennaro_YoungAdults (sleep).
- DREAM records table (Figshare 22133105 v9): 3,191 awakening rows; Experience 1,953, No experience 860, Without recall 316.
- ds005620: per-awakening report labels are **not** in the OpenNeuro release. The paper gives group counts only: 52 awakenings, 24 experience, 5 no experience, 23 no information. So 24 of 29 informative awakenings at RASS -4 reported experience.
- Chennu zip: 3.69 GB, but the server answers range requests (206), so single recordings (about 48 MB compressed) can be pulled. `zip_range_list.py` reads the central directory remotely (stdlib only; usage: `.venv/bin/python -I zip_range_list.py URL SIZE`). The bitstream is https://api.repository.cam.ac.uk/server/api/core/bitstreams/e94a6722-da5b-4e53-8673-5e8ec106e0f7/content, size 3694326663.

## Files

- `dream_sets.csv`: per-set counts (awakenings, subjects, report classes), sample rate, channels, size, licence.
- `dream_records.csv`, `dream_datasets_index.csv`: copies of the DREAM index tables (CC BY 4.0), kept because task #6 will need them. Raw downloads were deleted; total kept 0.5 MB.

## What was not checked

- No EEG was downloaded; channel quality and event timing were not inspected.
- ds004541 events (whether induction is marked) were not opened.
- Kumral et al. 2023 (DREAM set 19) sits on a non-Figshare DOI; not checked.
- COGITATE's Sci Data paper and the Bath DoC repository were seen only in search snippets (marked unverified in DATASETS.md).
- OpenNeuro's search API returned null to an anonymous query, so the search for other anaesthesia or ketamine sets relied on web search and may have missed some.

## Hypotheses

| Hypothesis | Result |
|---|---|
| ≥4 open datasets across ≥3 families qualify | Rejected: 7 datasets, 2 families |
| ds005620 supports within-sedation dream vs no-dream | Rejected for now: labels not released; 5 no-experience reports at best |
| An open ketamine EEG set with reports exists | Not found; Zenodo 806176 is restricted |
| DREAM supports dream vs no-dream within stage | Supported: e.g. Tononi N2 344 vs 309, LODE 118 vs 58 |
