# Datasets: access, licence, size and ground truth

Audit by mind-1 (task #2), 2026-11-18. Every entry below was checked against the live repository or API on that date; links are the ones opened. Working tables: `experiments/dataset_audit/`.

## Verdict

**The root goal's data criterion fails as written. Open data supports 2 of the 3 required families (sleep, anaesthesia), not 3.** No fully open disorders-of-consciousness (DoC) EEG set was found. Within the two families there is enough: 7 open datasets qualify for state tests (4 sleep, 3 anaesthesia), and the DREAM database gives about 2,000 open awakenings with delayed reports for the dream vs no-dream test.

Two dissociation cases in criterion R3 have no open data:
- **Ketamine.** The one ketamine EEG set with reported experiences (Milan, Zenodo 806176) is "restricted": access must be requested.
- **DoC patients.** Patient EEG is behind data agreements everywhere we looked.

**Recommended rescope** (for the lead): count "≥4 held-out datasets from ≥2 families (sleep, anaesthesia)" as the reachable state criterion, keep DoC and ketamine as named gaps, and add a lead-only task to request the restricted sets (listed under "Blocked" below). Agents must not contact authors.

Laptop budget: 1.5 GB of downloads for the whole project. Every dataset below is far larger, so each test must use a subset. Suggested subsets are given per dataset.

## Qualifying datasets (open, no login, laptop-feasible as a subset)

Ground-truth grade follows AGENT_BRIEF rule 6: **B** = behaviour or scoring, **R** = delayed report, **none**.

| # | Dataset | Family | Contrast | Truth | Subjects | Full size | Licence | Lab group |
|---|---|---|---|---|---|---|---|---|
| 1 | OpenNeuro ds005620 v1.0.0 | Anaesthesia (propofol) | awake (EO, EC) vs sedated to RASS -4 | B (per file); R only as group counts | 21 (1 excluded) | 83 GB | CC0 in metadata, README says CC-BY-4.0 | Oslo (Storm/Juel) |
| 2 | Chennu et al. 2016 propofol EEG (Cambridge) | Anaesthesia (propofol) | baseline, mild, moderate, recovery | B (responsiveness task) + drug level | 20 | 3.69 GB zip | CC BY 2.0 UK | Cambridge |
| 3 | OpenNeuro ds004541 v1.0.0 | Anaesthesia (surgical GA) | pre vs during general anaesthesia | B (clinical) | 8 | 3.1 GB | CC0 | not stated; README "in preparation" |
| 4 | Sleep-EDF Expanded (PhysioNet sleep-edfx 1.0.0) | Sleep | wake vs N3 (vs REM) | B (R&K scoring) | 78 SC + 22 ST subjects, 197 nights | 8.1 GB | ODC-BY 1.0 | Leiden |
| 5 | DREAM: Tononi Serial Awakenings | Sleep | experience vs no experience, all N2 | R | 39 | 8.4 GB in 38 per-subject zips (144-631 MB) | CC BY 4.0 | Wisconsin |
| 6 | DREAM: LODE | Sleep | experience vs no experience (N2, REM) | R | 28 | 0.13 GB | CC BY 4.0 | see Datasets.csv |
| 7 | DREAM: DeGennaro_YoungAdults | Sleep | experience vs no experience (N2, REM) | R | 65 | 0.04 GB | CC BY 4.0 | Rome |

Further open DREAM sets (all CC BY 4.0, Figshare) that are too large for the budget as a whole but usable later or by subset: Zhang & Wamsley 2019 (308 awakenings, 1.05 GB), DATA1 (324, 1.61 GB, much N3), DeGennaro Multiple awakenings (456, 6.4 GB), Older adults (40, 4.8 GB), Aamodt evening/morning sleep (255, 7.9 GB; same Oslo lab as ds005620), REM_Turku (134, 0.36 GB, REM only, only 3 no-experience reports), Oudiette N1 (246, 0.04 GB, mostly wake/N1, 3 channels), UFRN (41, 58.8 GB). Kumral et al. 2023 is on a non-Figshare DOI (10.60493/31mg4-mfq53), not checked. SCANDataset is private.

### Per-dataset notes

**1. ds005620 (propofol, repeated awakenings).** https://openneuro.org/datasets/ds005620/versions/1.0.0, DOI 10.18112/openneuro.ds005620.v1.0.0. Paper: Bajwa et al. 2025, Sci Rep 15:32746, https://doi.org/10.1038/s41598-025-12695-z (opened via Europe PMC, PMC12460656).
- Files: BrainVision, 65 channels, 5 kHz, float32. Per subject: awake EO and EC (5 min, 390 MB each), up to 3 `sed` runs (5 min, 390 MB) and 3 `sed2` runs (the 1 min just before each awakening, 78 MB). TMS-EEG runs too.
- **No per-awakening report labels are in the release.** Events files hold only "New Segment"; there is no phenotype folder. The paper reports 52 attempted awakenings: 24 experience, 5 no experience, 23 unarousable or incoherent. The supplement (docx) shows the classification only in figures.
- So: usable now for awake vs sedated (behaviour, RASS -4). Not usable for within-sedation report tests until the per-run labels are released; and with 5 no-experience reports the test would be underpowered anyway.
- Important for L2: at the group level, 24 of 29 informative awakenings from RASS -4 reported experience. A measure that calls this sedation "unconscious" is wrong most of the time by the report standard. Label this state "unresponsive, report mostly positive", not "unconscious".
- Licence mismatch: `dataset_description.json` says CC0, README says CC-BY-4.0. Cite either way.
- Subset: sed2 runs (78 MB each) plus 1 min cropped from awake EC. 8 subjects x (1 awake + 3 sed2) is about 0.9 GB raw before cropping; download one file at a time, save features, delete.

**2. Chennu 2016 (Cambridge propofol).** Item: https://www.repository.cam.ac.uk/items/b7817912-50b5-423b-882e-978fb39a49df, DOI 10.17863/CAM.68959. Paper: https://doi.org/10.1371/journal.pcbi.1004669.
- One zip, `sedation-restingstate.zip`, 3,694,326,663 bytes, 166 entries: EEGLAB `.set`/`.fdt` pairs (about 48 MB compressed per recording) and `datainfo.mat`. 91 channels kept, about 7 min per level.
- **The server supports HTTP range requests** (status 206), and the zip's central directory was read remotely. Single recordings can be pulled without downloading 3.7 GB: read the directory, then fetch one member's byte range. Helper logic is in `experiments/dataset_audit/RESULTS.md`.
- Ground truth is behaviour: target-detection responsiveness plus measured propofol blood level. Mild and moderate sedation are not loss of consciousness for most subjects; in the paper some subjects stayed responsive at moderate level. Use "baseline vs moderate" as a drug/arousal contrast and "responsive vs unresponsive at moderate" as the behavioural one.
- Subset: baseline + moderate for 10 subjects is about 1 GB compressed. Within budget only if nothing else large is taken.

**3. ds004541 (surgical general anaesthesia, EEG + fNIRS).** DOI 10.18112/openneuro.ds004541.v1.0.0. 8 patients, task "anesthesia", 3.1 GB, participants table empty (no age or sex), README references "In preparation". Weakest of the three: unknown agent, unknown behavioural timing, patients. Usable as an out-of-lab anaesthesia transfer set if its events mark induction.

**4. Sleep-EDF Expanded.** https://physionet.org/content/sleep-edfx/1.0.0/, DOI 10.13026/C2X676. Open, ODC-BY 1.0. 2 EEG channels (Fpz-Cz, Pz-Oz) at 100 Hz plus EOG and EMG, hypnograms in R&K stages. One PSG file is about 48 MB (SC4001E0-PSG.edf: 48,338,048 bytes). MNE has a fetcher (`mne.datasets.sleep_physionet`).
- Truth is stage scoring, not report. NREM awakenings often yield experience reports (DREAM: Tononi N2 set 344 experience vs 309 no experience), so "N3 = unconscious" is an assumption, not a label. Grade B.
- Confound: cassette subjects are aged 25-101; age must be controlled.
- Subset: 10 subjects x 1 night = about 0.5 GB.

**5-7. DREAM database.** Paper: Wong, Herzog, Andrade et al. 2025, Nat Commun 16:7495, https://doi.org/10.1038/s41467-025-61945-1 (full text read via Europe PMC, PMC12350935). Index: https://doi.org/10.26180/22133105 (Figshare article 22133105, v9, 2025-10-30, CC BY 4.0), three CSVs: `Datasets.csv`, `Data records.csv`, `People.csv`.
- Initial release: 20 datasets, 505 participants, 2,643 awakenings. Our count of the current records table: 3,191 awakening rows; labels Experience 1,953, No experience 860, Without recall 316, mixed 55, unknown 7.
- Every awakening has at least 20 s of M/EEG before waking, at least 100 Hz and 2 electrodes, and a standardised report class. This is delayed report: grade R. It is the main L2 resource.
- Per-set counts, sample rates, channels and sizes: `experiments/dataset_audit/dream_sets.csv`. Per-awakening table: `experiments/dataset_audit/dream_records.csv`.
- For dream vs no-dream within stage (task #6), the best sets per byte are LODE (118 vs 58, N2 and REM, 7 channels, 0.13 GB), DeGennaro_YoungAdults (40 vs 25, one awakening per subject, 0.04 GB), and 6-8 Tononi subjects (about 1.5 GB for all 38 zips is out of budget; take 4-5 subject zips).
- Near-copies: the five DeGennaro sets come from one Rome lab; the Aamodt sets come from the ds005620 lab. Treat them as one lab each in transfer tests.

## Not qualifying, or not yet

| Dataset | Status | Why | What would fix it |
|---|---|---|---|
| COGITATE iEEG (exp. 1) | Open licence (CC BY 4.0) but **account required** | Both routes (XNAT at cogitate-data.ae.mpg.de, bundles at arc-cogitate.com) need a registered account; agents may not log in. BIDS sample bundle 16 GB, full 98 GB; raw sample 13 GB. Paper: Seedat et al. 2025, Sci Data, https://doi.org/10.1038/s41597-025-04833-z (unverified: not opened, from search snippet). | Lead registers and downloads 2-3 subjects (one subject via the `cog_ieeg` XNAT tool). Blocks tasks #10 and #11. |
| COGITATE MEG/EEG | Account required | Sample bundle about 28 GB per plan; out of budget. | External disk. |
| OpenNeuro ds003171 v2.0.1 | Open, CC0, 4.8 GB | fMRI, not EEG. 17 subjects at awake, light, deep sedation, recovery (propofol), rest and an audio clip. Truth: behaviour. Fine for an fMRI L1 test, but no EEG measure can run on it. | An fMRI branch of the bench. |
| OpenNeuro ds003059 v1.0.0 | Open, CC0, 15.4 GB | LSD vs placebo fMRI, 15 subjects (rest). No conscious/unconscious contrast; content intensity only (VAS ratings per scan, 11D-ASC). | Out of scope for state tests. |
| Milan rest EEG, Zenodo 806176 | **Restricted** | Wake vs ketamine (n=5), propofol (5), xenon (5) anaesthesia, plus N3 sleep (4). Ketamine subjects reported dreams afterwards: the one open-to-request ketamine dissociation set. Record metadata opened 2026-11-18: access_right "restricted". | Lead requests access. |
| Disorders of consciousness | None fully open | Bath repository 10.15125/BATH-01632 (UWS 14, MCS 17, LIS 11, wearable EEG) is controlled access (unverified: from search snippet, page not opened). Paris/Shanghai/Toulouse data (Comms Biol 2025, PMC12344011) are on request only; I opened that statement. | Lead requests one DoC set. Until then, family 3 is empty. |
| Open ketamine EEG on OpenNeuro | None found | ds005917 (NIMH ketamine) is MRI/MRS at subanaesthetic dose. OpenNeuro's search API returned nothing usable to agents. | Keep looking in the M5 sweep. |

## What this means for the tasks

- **#4 LZ vs slope:** ds005620 (awake vs sed2), Chennu (baseline vs moderate), Sleep-EDF (wake vs N3). Three datasets, two families, all ground truth B.
- **#6 Dream vs no-dream:** DREAM LODE + YoungAdults + a few Tononi subjects. ds005620 cannot be used (no per-run labels in the release).
- **#7 Ketamine and REM:** REM is covered by DREAM (REM awakenings with reports) and Sleep-EDF REM epochs. Ketamine is blocked.
- **#10, #11 COGITATE:** blocked on an account.
- **Budget split proposal** (1.5 GB total): ds005620 subset 0.5 GB, Chennu subset 0.4 GB, Sleep-EDF 0.25 GB, DREAM 0.3 GB, slack 0.05 GB. Delete raw after features are saved.

---

## Appendix (mind-access, 2026-11-18): access status update

Added by mind-access (tasks #19, #20). The text above is unchanged. Details: `experiments/data_access/RESULTS.md`.

- **DREAM: every published package is open.** The Figshare API shows no active embargo on any of them, and byte-range downloads work (HTTP 206). Kumral et al. 2023 is open on FreiData (46.6 GB, CC BY 4.0). Only SCANDataset (set 8) is by request. Per-package sizes and per-stage exp/no-exp counts: `experiments/data_access/dream_access.csv`. REM no-experience reports concentrate in DeGennaro "Multiple awakenings" (29, inside one 6.4 GB zip; use range reads). N3 rests on DATA1 (46/87).
- **Zenodo 806176 (Milan ketamine/propofol/xenon/N3): access requested 2026-11-18, pending.** This is the same cohort as Sarasso 2015, Colombo 2019 and Maschke 2024, so it is not an independent ketamine test.
- **New open ketamine EEG: Farnes et al. 2020** (Oslo), Dryad doi:10.5061/dryad.j9kd51c9q, also Zenodo 4245091. CC0, 0.93 GB, 10 subjects, 62 ch, spontaneous EEG plus TMS-EEG/PCI, before and during **subanaesthetic** ketamine, with subjective ratings. Subjects stayed responsive, so it tests "conscious, altered", not disconnected consciousness. Paper: PLoS One 2020, PMC7682856.
- **No independent EEG set with reports after unresponsive ketamine anaesthesia was found.** Michigan (Li & Mashour 2019, 15 subjects) did not describe post-anaesthesia reports and has no data statement; email queued. Liège ketamine-with-dreams data are fMRI, on request.
- **COGITATE:** the terms are standard (summary in docs/ACCOUNTS.md). The account needs the owner to type a password (docs/HUMAN_LEADS.md). Experiment 2 (v2.0) is still "coming soon"; an email asking the date is queued.
- **DoC:** Bath BATH-01632 requires proof of ethics approval, so we did not apply. The Paris/Shanghai/Toulouse DoC EEG (237 patients, Della Bella 2025) is on request; email queued.
