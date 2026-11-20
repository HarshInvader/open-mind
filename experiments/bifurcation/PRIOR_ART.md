# No-report bifurcation: prior-art check (2026-11-20)

**Verdict: still open, but narrower.** The originating lab (Sergent) has already fitted single-trial bifurcation models without a task, in EEG (2021) and now fMRI (2026). No one outside the originating labs has tested single-trial bimodality at fixed strength under one sealed pipeline with planted bounds, and no one has done it across Cohen and Sergent.

| Paper | What it does | Single-trial bimodality at fixed strength? | Planted / recovery check? |
|---|---|---|---|
| Sergent et al. 2021, Nat Commun ([doi:10.1038/s41467-021-21393-z](https://doi.org/10.1038/s41467-021-21393-z)) | Auditory near-threshold EEG, 20 people; trial-by-trial mixture model, Bayesian comparison favours bifurcation 250-700 ms; also fitted in passive (mind-wandering) trials | Yes (originating lab) | No |
| Cohen et al. 2024, Cereb Cortex ([doi:10.1093/cercor/bhae415](https://doi.org/10.1093/cercor/bhae415)) | Visual masking EEG, 40 people, report vs no-report; only the fronto-central N2 (250-290 ms) bifurcates without report, the VAN does not | No (condition averages) | No |
| Boyer ... Sergent 2026, bioRxiv ([doi:10.64898/2026.06.17.732590](https://doi.org/10.64898/2026.06.17.732590)) | Auditory near-threshold **fMRI**, task and no-task; single-trial modelling finds bifurcation beyond primary sensory cortex in both contexts (abstract only; licence CC BY-NC-ND) | Yes (originating lab, fMRI) | Not stated in abstract |
| Ellinghorst et al. 2026, bioRxiv ([doi:10.64898/2026.10.05.755932](https://doi.org/10.64898/2026.10.05.755932)) | No-report inattentional deafness; AAN and P3 with awareness | No (ERPs) | No |
| Klatzmann et al. 2025, Cell Rep ([doi:10.1016/j.celrep.2025.115372](https://doi.org/10.1016/j.celrep.2025.115372)) | The "cortex-wide bifurcation" paper: macaque connectome simulation only (not by Garnier-Allain) | Model only | n/a |
| Hatamimajoumerd et al. 2022, Curr Biol ([doi:10.1016/j.cub.2022.07.068](https://doi.org/10.1016/j.cub.2022.07.068)) | fMRI no-report decoding | No | No |
| Our T4 (`experiments/our_theory/t4_planted/RESULTS.md`) | Planted two-state pipeline at Stockart 2025 counts | Pipeline | Yes: PASS 0% at d' 1-1.5, 100% at d' 3 |

## Novelty sentence (draft, before compute)

An outside, sealed, planted-bounded test of single-trial bimodality at fixed stimulus strength, run with one pipeline on two public no-report EEG datasets (Cohen, visual; Sergent, auditory), reporting both what the pipeline can detect and what it finds.

## Data licences

- Sergent (OSF aw3t5): CC BY 4.0.
- Cohen (OSF 6d5av): **no licence stated.** Not used until this is settled.
