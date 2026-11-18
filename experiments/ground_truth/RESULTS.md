# Ground-truth schema (task #3)

**Verdict: 2,417 open delayed-report (L2) cases exist, and all of them are sleep awakenings in the DREAM database.** None comes from anaesthesia. The open anaesthesia recordings (ds005620, Chennu 2016, ds004541) rest on behaviour only. ds005620 did collect awakening reports, but they are not released per run.

Every recording in the qualifying datasets is labelled in `labels.csv` (3,679 rows): dataset, family, lab, subject, recording, state, sleep stage, behaviour, report, `truth` (behaviour / delayed_report / none) and `l2_case`.

## Definition used

An **L2 case** is an awakening where behaviour and report can disagree: the person was asleep (N1, N2, N3 or REM by scoring, so unresponsive), then gave a classified report of "experience" or "no experience", and the dataset is open. "Without recall" (experience reported, content not remembered) is labelled but not counted, because its truth is ambiguous for a yes/no test.

## Numbers

| | Count |
|---|---|
| Rows labelled | 3,679 |
| Behaviour-only rows | 488 (ds005620 202 files, Chennu 80, ds004541 9, Sleep-EDF 197 nights) |
| Delayed-report rows (DREAM, all sets) | 3,191 |
| **L2 cases (open, asleep, experience or no experience)** | **2,417: 1,601 experience, 816 no experience** |
| Subjects with L2 cases | 446 |
| Subject × stage cells holding both report types (needed for within-subject contrasts) | 160 cells, 131 subjects |
| Anaesthesia rows with a per-recording report | 0 |

L2 cases by stage (experience / no experience): N1 132 / 18, N2 894 / 595, N3 103 / 109, REM 472 / 94.

By lab (L2 cases; experience / no experience; subjects): Tononi (Wisconsin) 653; 344/309; 39. Rome (five DeGennaro sets) 590; 395/195; 166. Zhang & Wamsley 212; 156/56; 28. DATA1 223; 107/116; 10. Oslo (Aamodt sets, same lab as ds005620) 193; 165/28; 41. LODE 176; 118/58; 28. REM_Turku 126; 123/3; 18. Kumral 66; 42/24; 19. UFRN 41; 25/16; 41. TWC_USA 31; 26/5; 19. Oudiette 29; 23/6; 21. Others below 50 each.

Behaviour checks:
- Chennu at moderate sedation: 13 responsive (≥30/40 hits), 6 impaired, 1 unresponsive. This matches the paper's 13 responsive vs 7 "drowsy" (https://doi.org/10.1371/journal.pcbi.1004669, text read from the repository copy). Column meanings of `datainfo.mat` (level, plasma propofol ng/ml, RT ms, hits out of 40) were inferred from the values and the paper; they are not documented in the file.
- ds004541 events give behaviour within each file: baseline, verbal soft and strong, motor, tetanic stimuli, `loc` and `roc`.

## What this means

- The dream vs no-dream test (#6, #22) has enough data: 595 vs 894 in N2 alone across at least 4 independent labs. REM has few no-experience reports (94), concentrated in a few labs.
- The ketamine case and any "unresponsive but experiencing under a drug" case have **no** per-recording report data in the open. ds005620 only gives the group rate (24 of 29 informative awakenings reported experience), so it can show at most that a measure calls a mostly-experiencing state "unconscious". It cannot score single recordings.
- Sleep-EDF and Chennu give behaviour-grade (L1) labels only.
- Near-copy groups for transfer tests: Rome (5 sets), Oslo (Aamodt sets + ds005620), Tononi/Wisconsin. The `lab` column records this.

## Files

- `labels.csv`: the table. `counts.json` (= `results.json`): the counts above.
- `build_labels.py`, `list_remote.py`: rebuild from metadata only (S3 listings, PhysioNet RECORDS, Chennu `datainfo.mat` fetched by HTTP range, DREAM index tables). No EEG was downloaded. `raw/` holds about 40 KB of listings.

## Not checked

- DREAM labels are taken as published in its records table; I did not re-read any study's raw reports.
- Stage labels for DREAM awakenings are the "last sleep stage" field; artefact proportion was not used to exclude rows.
- Kumral et al. 2023 data sit on a non-Figshare DOI whose access route was not tested, although DREAM lists the set as open.
- Sleep-EDF per-epoch stage counts were not tallied (hypnograms not downloaded).
