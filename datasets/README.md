# Consciousness data, in one place

**Sleep and anaesthesia data are plentiful and open. Patient data are not.** We list 118 outside datasets relevant to the science of consciousness, plus the 16 tables we made. No open raw EEG from disorders-of-consciousness patients exists: every set we found needs an application, and most need proof of ethics approval. Open data with reports after unresponsive ketamine anaesthesia does not exist either.

This folder lists every relevant dataset we could find, used by us or not: what it is, where it lives, its exact terms, and how to get it. Every row was opened at its DOI, API or landing page on 18 Nov 2026, except the 5 marked `verified=no`.

The access audit that came first is `../docs/DATASETS.md`. It says which datasets can test what, and why. This folder does not repeat it.

## What is here

| Path | What |
|---|---|
| `catalog.csv` | All 134 rows: 16 included here, 93 public and fetchable, 22 on request or behind an account, 3 cited but with no data record. |
| `open/` | 16 tables this project made (CC BY 4.0). `open/MANIFEST.csv` says where each came from. |
| `fetch.py` | Lists the catalogue, lists any dataset's files, and fetches subsets of the sets we use into `local/`. |
| `build.py` | Rebuilds `open/` from the experiments and checks `catalog.csv`. |

Columns of `catalog.csv`: `id, title, kind, tier, origin, terms, size, n, labels, serves_tasks, used_by_us, verified, notes`. `labels` says what ground truth the set has; `serves_tasks` names board tasks (`#22`) or experiments; `notes` says how the row was checked.

## The tiers

- **included**: our own tables, in `open/`.
- **fetch**: public with no account. `fetch.py` can fetch a subset of the ones we use.
- **request**: an account, a signed agreement or an application is needed. Here we keep metadata only. Agents never apply, sign up or write to anyone; the lead decides.
- **reference-only**: cited in our audit, but no data record could be opened.

## Get the data

```bash
python3 -I datasets/fetch.py list                                    # the catalogue, by tier
python3 -I datasets/fetch.py index ds005620                          # file list only, no data
python3 -I datasets/fetch.py fetch dream_index                       # the DREAM index tables (0.5 MB)
python3 -I datasets/fetch.py fetch sleep_edfx --n 4                  # 4 Sleep-EDF nights with hypnograms
python3 -I datasets/fetch.py fetch dream_tononi --member s01_ep01    # one awakening, read out of a remote zip
python3 -I datasets/fetch.py meta milan_806176                       # a request-tier set: what it is and how to ask
```

The project has a 1.5 GB download budget in total. Most sets are far larger: ds005620 is 83 GB, the Tononi DREAM set 8.4 GB. So `fetch` reads single members out of remote zips with HTTP range requests, and refuses to go past the budget. For large sets you must name what you want with `--member`. Downloads go to `datasets/local/`, which git ignores. Nothing fetched is republished.

`fetch` has recipes for the sets our results use: the DREAM index, Zhang & Wamsley, LODE, Young Adults, Tononi, Multiple awakenings, DATA1, Chennu 2016, ds005620, ds004541, ds006394 and Sleep-EDF. `index` works for any figshare, Zenodo, Dryad or OpenNeuro row.

## What we use

| Dataset | Family | Ground truth | Used in |
|---|---|---|---|
| DREAM index + Tononi, Zhang & Wamsley, Young Adults | Sleep | Delayed report per awakening | `t1_dream`, `theory_tests`, `ground_truth` |
| ds005620 (propofol) | Anaesthesia | Behaviour (RASS -4) | `lz_slope` |
| Chennu 2016 (propofol) | Anaesthesia | Behaviour + drug level | `lz_slope`, `theory_tests` |
| Sleep-EDF Expanded | Sleep | Stage scoring | `lz_slope`, `surrogate_gate` |

## Open, and worth using next

- **ds006623, Michigan propofol fMRI** (CC0, 26 subjects). Subjects do mental imagery tasks through graded sedation, including while unresponsive. It is the closest open data to "unresponsive but aware".
- **eeg_power_anesthesia, MGH** (PhysioNet, signed licence). Conscious / unconscious labels from monitored responsiveness, for 10 volunteers and 44 patients. Spectra only.
- **doc_alpha_coherence** (Harvard Dataverse, CC0). Derived EEG features from 33 DoC patients and 28 controls. It is the only open DoC EEG table we found.
- **fc_anaesthesia_patients** (Zenodo, CC BY, 0.2 GB). Connectivity under propofol, ketamine and sevoflurane from five fMRI sites.
- **ds006394** (CC0, 0.56 GB) and **ds001785** (CC0). Report-based seen vs unseen EEG, for the contrastive tests in `#18` and `#28`.
- **farnes2020** (CC0, 0.93 GB). Subanaesthetic ketamine EEG and TMS-EEG. Subjects stay responsive.
- **DOSE-I** (CC BY, 0.8 GB). Real-world propofol sedation EEG; a cheap out-of-lab transfer set.
- **isruc**. Two scorers per epoch, so we can measure how noisy stage labels are.

## Missing, and wanted

The data that would most raise the odds of our goals, and is not open anywhere:
- **Raw EEG from disorders-of-consciousness patients** with CRS-R diagnosis. Bath (`bath_doc`) and Della Bella 2025 (`dellabella_doc`) are on request. Without it, the third state family in criterion R3 stays empty.
- **EEG with reports after unresponsive ketamine anaesthesia.** The Milan set (`milan_806176`) is restricted and is the same cohort as several published papers.
- **Per-awakening report labels for ds005620.** The paper has them; the release does not.
- **The original PCI benchmark** (TMS-EEG across wake, sleep, anaesthesia and DoC). We found no data record.
- **COGITATE experiment 2**, still "coming soon"; experiment 1 needs an account.
- **REM and N3 no-experience reports**: rare in every open set (29 REM in one DeGennaro zip, 87 N3 in DATA1).

## Rows not verified

`cogitate_paper`, `ds003600`, `ds007350`, `liege_ketamine_fmri`, `michigan_ketamine_eeg`. Each row's `notes` says why.

## Terms

Our tables in `open/` are CC BY 4.0. Each outside dataset keeps its own terms, in the `terms` column. Several are non-commercial (CC BY-NC, CC BY-NC-SA): the EBRAINS rodent sets, I-CARE, the MNI iEEG atlas and MASS-EX.
