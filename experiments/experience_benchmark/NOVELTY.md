# #42 experience benchmark: what is new after the prior art (2026-11-20)

Status: **stopped 2026-11-20 (coordinator, after an independent Fable read).** DREAM labels were never opened; extraction stopped at 170 of 452 Rome records. See the NEGATIVE_ATLAS entry "Within-person N2 markers do not separate experience from no experience".

## Closest work (opened)

| Paper | Design | Result |
|---|---|---|
| Wong et al. 2020, Dream Catcher ([doi:10.1093/nc/niaa006](https://doi.org/10.1093/nc/niaa006)) | Blinded; 54 one-minute NREM recordings from 9 people, balanced within person; spectral power | Not better than chance at any level of blindness |
| Aamodt et al. 2023 ([PMC9871639](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9871639/)) | Markers vs stage and report, in data that is in our Tier 1 | Markers track stage, not dreaming; LZ at N2 p = 0.79 |
| Wong et al. 2025, DREAM ([PMC12350935](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12350935/)) | Spectral power and catch22 classifiers; StratifiedKFold over epochs (no subject or lab grouping) | NREM AUC 0.586, REM 0.700 |
| Selte et al. 2026 ([doi:10.64898/2026.08.16.745040](https://doi.org/10.64898/2026.08.16.745040)) | One site, 699 N2+N3 awakenings, participant-grouped folds | Ensemble AUC 0.80 (stage pooled; no external lab) |
| Bazán Sánchez 2026 ([doi:10.13140/RG.2.2.14388.00642](https://doi.org/10.13140/RG.2.2.14388.00642)) | DREAM Figure 5 workflow, 1,065 reports, 5 collections | Record-wise 0.569 / 0.636; participant-held-out 0.534 / 0.629; within lab 0.498 / 0.498; lab-held-out 0.493 / 0.470; lab-prevalence-only baseline 0.564 / 0.687; lab identity decodable at 0.808-0.953 (NREM spectral / REM catch22) |
| Michalak et al. 2026 data, our check (amendment 5, `michalak.json`) | 660 N2 awakenings, 41 people within person; posterior gamma/delta | Within-person AUC 0.512 [0.449, 0.580], gamma 0.481 [0.414, 0.559], delta 0.507 [0.445, 0.562]; sealed reading OTHER (all upper bounds < 0.60, CIs wider than the [0.43, 0.57] null band) |
| Our Tononi result (`experiments/t1_dream/RESULTS.md`) | 35 people, N2, within person | Posterior delta AUC 0.46-0.47 (not tested inferentially) |

The Bazán Sánchez numbers are from the full text as read by the coordinator in a browser. Our own fetch was blocked (HTTP 403) and was not worked around.

## What is already established

1. **Cross-lab spectral null for the DREAM workflow:** within a lab and across labs, the published features sit at about 0.50 (Bazán Sánchez).
2. **Pooled AUC is lab and between-person structure:** a lab-prevalence-only baseline beats the pooled classifier, and lab identity is easy to decode (Bazán Sánchez). Our Michalak pooled-vs-within contrast for delta, 0.576 vs 0.507, points the same way.
3. **The within-person spectral null at N2** is now seen three ways: Dream Catcher (small, blinded), Michalak (our check) and Tononi (ours).
4. **Markers track stage, not dreaming:** Aamodt 2023, on data in our own Tier 1.

## What would still be new (one sentence)

A within-person, N2-only, lab-held-out test of hypothesis-driven markers (posterior hot-zone integration such as wSMI, and complexity: LZ, PE, HFD), with bounds on what they add beyond the spectrum.

**Assessment:** this is thin. Generic spectra already fail within lab (Bazán Sánchez, Michalak), so a marker that adds to the spectrum would have to predict experience where nothing has so far. The most likely outcome is a set of bounds near zero that extend Aamodt 2023 to more labs: atlas material, not a paper. The spectral arm of #42 (headline spectral AUC, pooled-vs-within contrast, Selte comparison) is pre-empted and should not be presented as new.
