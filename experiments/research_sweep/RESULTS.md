# Research sweep and citation check (tasks #12, #13)

**Verdict.** Every "(memory)" citation in `docs/fable_plan.md` is real and now has a DOI. Four claims in the plan need correcting. COGITATE's iEEG n is 34 in the paper, not 38. The Chennu propofol set (3.44 GB) and ds005620 (83.0 GB) are both over our 1.5 GB download budget. ds003059 is LSD fMRI only, not MEG. The unnamed July 2026 reanalysis is Bandara, Rowe and Garrido. Three plan statements could not be confirmed and are marked struck/unverified below. The News page now has 20 items, all with the source opened and `verified: true`: 11 latest (2025-2026) and 9 landmarks.

Two findings matter most for the bench:
1. **The ketamine dissociation evidence rests on one small cohort.** Sarasso 2015 (PCI, n = 18), Colombo 2019 (spectral exponent, n = 5 per drug) and Maschke 2024 (criticality, 15 subjects, 5 per drug) all use the same Milan/Liège propofol-xenon-ketamine volunteers. Under our rules they count as one near-copy, not three replications. We need an independent ketamine dataset with delayed report.
2. **The spectral confound is now documented directly.** Maschke et al. 2025 (Cerebral Cortex, 303 patients) found shuffle-normalised LZC correlated r(197) = 0.86 with the 1-40 Hz exponent. Phase normalisation cut that to r = 0.24, and every LZC diagnostic effect vanished. This is the PMC12448740 paper the plan cites.

Method: each DOI was resolved on Crossref, and abstracts or full text were read via Europe PMC (and arXiv, OSF, OpenNeuro GraphQL, PhysioNet and the Cambridge repository pages). Every number on the News page was found in the source text. Numbers I could not find in the source were left out (for example, decoding accuracies for Bryant & Whyte 2026).

## 1. Citation table for docs/fable_plan.md

| Plan item | Status | Correct citation |
|---|---|---|
| Casarotto et al. 2016, Annals of Neurology (memory) | Confirmed | Ann Neurol 80:718-729. doi:10.1002/ana.24779. Benchmark n = 150, cutoff 100% sens/spec, MCS sensitivity 94.7%, 9/43 VS above cutoff |
| Albantakis et al. 2023, PLoS Comput Biol, IIT 4.0 (memory) | Confirmed | PLOS Comput Biol 19:e1011465, 17 Oct 2023. doi:10.1371/journal.pcbi.1011465 |
| IIT "pseudoscience" open letter, 2023 | Confirmed | IIT-Concerned et al., PsyArXiv 16 Sep 2023, doi:10.31234/osf.io/zsr78. Follow-up: Nature Neuroscience 28:689-693 (2025), doi:10.1038/s41593-025-01881-x. Signatory count of the 2023 letter not verified |
| GNWT "July 2026 bioRxiv reanalysis... did not get its authors" | Confirmed, authors found | Bandara KH, Rowe EG, Garrido MI. bioRxiv 22 Jul 2026, doi:10.64898/2026.07.16.738188. DCM on COGITATE MEG N = 100; supports onset and offset prefrontal ignition. Not peer reviewed |
| "One secondary source says more collaborations are running (HOT, RPT, AST)" | Unverified | No primary source found. Only blog/secondary posts. Keep as unverified |
| Corcoran et al. 2026, Neurosci Biobehav Rev (INTREPID) | Confirmed | Neurosci Biobehav Rev 187:106742 (Aug 2026; online 14 May 2026). doi:10.1016/j.neubiorev.2026.106742; arXiv:2509.00555. No results, as the plan says |
| Aru, Suzuki, Larkum 2020, Trends Cogn Sci (memory) | Confirmed | "Cellular mechanisms of conscious processing", TiCS 24:814-825. doi:10.1016/j.tics.2020.07.006 |
| COGITATE: n = 256 across fMRI, MEG, iEEG | Confirmed | Nature 642:133-142 (30 Apr 2025). doi:10.1038/s41586-025-08888-1. fMRI 120, MEG 102, iEEG 34 |
| COGITATE experiment 2: "139 participants across fMRI and MEG" | Unverified | Not found in any source I opened. The data page lists v2.0 (Exp 2 MEG + fMRI) as "coming soon". Not released as of 2026-11-18 |
| Schartner et al. 2015, PLoS One (memory) | Confirmed | PLOS ONE 10:e0133532. doi:10.1371/journal.pone.0133532 |
| Maschke et al., PMC12448740: LZ vs exponent r = 0.86, effect vanishes when phase-normalised | Confirmed, citation completed | Maschke, Belloli, Manasova, Sitt, Blain-Moraes, Cerebral Cortex 35(9):bhaf254 (2025). doi:10.1093/cercor/bhaf254. r(197) = 0.86 shuffle-normalised, 0.24 phase-normalised; diagnostic effects vanished |
| Colombo et al. 2019, NeuroImage (memory) | Confirmed | NeuroImage 189:631-644. doi:10.1016/j.neuroimage.2019.01.024. n = 5 per drug |
| Casali et al. 2013 (PCI) | Confirmed | Sci Transl Med 5(198). doi:10.1126/scitranslmed.3006294 |
| Comolatti et al. 2019 (PCIst) | Confirmed | Brain Stimulation 12:1280-1289. doi:10.1016/j.brs.2019.05.013 |
| Maschke et al. 2024, Communications Biology: resting EEG predicts PCI in healthy adults | Confirmed, with a caveat | Commun Biol 7:946. doi:10.1038/s42003-024-06613-8. 15 adults under anaesthesia (5 per drug); LOSO MAE 0.065. Follow-up preprint in 26 DoC patients (Newman et al. 2026, doi:10.64898/2026.06.04.730221) did not generalise across the full cohort |
| "A rat study (Neurosci Conscious 2024)": Φ rose under propofol/sevoflurane, opposite to PCI | Confirmed | Nilsen AS, Arena A, Storm JF. Neurosci Conscious 2024(1):niae021. doi:10.1093/nc/niae021 |
| Siclari et al. 2017, Nature Neuroscience (memory) | Confirmed | Nat Neurosci 20:872-878. doi:10.1038/nn.4545 |
| Sitt et al. 2014 (memory) | Confirmed, venue added | Brain 137:2258-2270. doi:10.1093/brain/awu141 |
| Engemann et al. 2018, Brain (memory) | Confirmed | Brain 141:3179-3192. doi:10.1093/brain/awy251. 327 DoC recordings + 66 controls; cross-site AUC 0.73-0.78 |
| COGITATE iEEG: "38 patients" | Corrected | The Nature paper reports iEEG n = 34. The data page gives no count. Check the portal before using either number |
| COGITATE MEG-EEG: sample bundle "about 28 GB", full "about 700 GB" | Unverified | The data release page gives no sizes. Releases v1.0 (48 MEG), v1.1 (52 MEG), v1.2 (iEEG + fMRI). Account needed (website or XNAT); CC BY 4.0 |
| OpenNeuro ds005620 | Confirmed, size added | "A repeated awakening study exploring the capacity of complexity measures to capture dreaming during propofol sedation". CC0, 21 subjects, **83.0 GB**. Paper: Bajwa et al., Sci Rep 2025, doi:10.1038/s41598-025-12695-z. Only **5 no-experience awakenings** (24 experience) |
| OpenNeuro ds003171 | Confirmed, plan wording corrected | Name: "Modeling an auditory stimulated brain under altered states of consciousness using the generalized ising model". MRI, 17 subjects, CC0, 4.8 GB. I did not check whether it has four sedation levels |
| Chennu et al. 2016, PLoS Comput Biol, Cambridge repository (memory, verify) | Confirmed, size flagged | PLOS Comput Biol 12:e1004669, doi:10.1371/journal.pcbi.1004669. Data: doi:10.17863/CAM.68959, CC BY 2.0 UK, single zip **3.44 GB** (over budget). n = 20 per Newman et al. 2025 preprint (not checked in the original) |
| Sleep-EDF on PhysioNet (memory) | Confirmed | Sleep-EDF Expanded v1.0.0, doi:10.13026/C2X676, ODC-By 1.0, 197 whole-night PSG recordings, 8.1 GB total (per-file download possible) |
| DREAM database, Wong et al. 2025, Nature Communications (memory, verify) | Confirmed | Nat Commun 16:7495 (13 Aug 2025). doi:10.1038/s41467-025-61945-1. 20 datasets, 505 participants, 2,643 awakenings. Registry doi:10.26180/22133105; packages open or by request per contributor |
| Imperial LSD fMRI, OpenNeuro ds003059 (memory, verify) | Corrected | ds003059 = "Neural correlates of the LSD experience revealed by multimodal neuroimaging", **MRI only** on OpenNeuro, 15 subjects, CC0, 15.4 GB. No MEG in this record. Psilocybin MEG/fMRI not located |
| Butlin, Long et al. 2023, arXiv (memory) | Confirmed | arXiv:2308.08708 (17 Aug 2023), 19 authors. Peer-reviewed successor: Butlin et al., TiCS 30(6):488-501, doi:10.1016/j.tics.2025.10.011 |
| PyPhi (memory) | Not checked | Software, not a citation; T10 owner to confirm the version |
| Bayne, Hohwy, Owen 2016, Trends Cogn Sci (memory) | Confirmed | "Are there levels of consciousness?", TiCS 20:405-413. doi:10.1016/j.tics.2016.03.009 |
| "Press coverage notes workspace areas gave no sharp offset response" | Confirmed via primary | The Nature abstract itself says GNWT is challenged by "the general lack of ignition at stimulus offset" |

Totals (31 rows): 24 confirmed (several of them with additions such as a found author list, completed citation or added size). 3 corrected (iEEG n, ds003059 modality, ds003171 description). 3 unverified/struck as stated (HOT/RPT collaborations, Exp 2 n = 139, COGITATE bundle sizes). 1 not checked (PyPhi).

## 2. News page (site/news.json)

The 5 existing items: all 5 had placeholder or homepage URLs and no authors. All were fixed and verified; none was removed.
- COGITATE: author list, volume/pages and modality counts added.
- INTREPID: the homepage URL was replaced with doi:10.1016/j.neubiorev.2026.106742, the full title and authors were added, and the date was set to 14 May 2026.
- Maschke 2024: the headline was a paraphrase. It now uses the real title, plus doi:10.1038/s42003-024-06613-8 and the n = 15 caveat.
- Rat Φ: real title, authors (Nilsen, Arena, Storm) and doi:10.1093/nc/niae021 added.
- Pseudoscience letter: the PsyArXiv DOI and the 2025 Nature Neuroscience follow-up were added. The "more than 100 researchers" claim was dropped because I could not verify the 2023 signatory count.

15 items added. Latest: Bandara 2026, Bryant & Whyte 2026, DREAM 2025, Bajwa/ds005620 2025, Maschke 2025, Newman 2026, Luppi 2026, Butlin 2025/26, Sutherland 2026. Landmarks: IIT 4.0, Siclari 2017, Casarotto 2016, Casali 2013, Sarasso 2015, Schartner 2017. Total 20 (11 latest, 9 landmark), all `verified: true`. `site/news.json` is generated by `experiments/research_sweep/make_news.py`. Edit that file and rerun it, then run `python3 -I site/build.py`.

Not added, and why:
- Agnorelli 2025 (Mol Psychiatry, ketamine in bipolar patients): clinical, subanaesthetic, no report-based ground truth.
- Stoliker 2026 (Nature, psilocybin): not a complexity-vs-confound test.
- A DMT complexity-dip item: secondary source only.
- No 2026 results from COGITATE Exp 2, INTREPID, or HOT/RPT collaborations were found.

## 3. Dataset access findings (for other agents)

- **ds005620**: 83.0 GB full. Fetch per file; the sedation pre-awakening runs are what matter. Only 5 clear no-experience awakenings, so it can only detect large effects alone.
- **Chennu propofol** (Cambridge): one 3.44 GB zip, over the 1.5 GB team budget. Needs a lead decision or a streaming/partial extract.
- **Sleep-EDF Expanded**: open, 8.1 GB total, but per-file download works. Take a few subjects.
- **DREAM**: the registry is open (doi:10.26180/22133105). Each dataset package is open or by request. Only open ones are usable for us (no contact allowed). monash.edu/dream-database returned 403 to a scripted fetch; use the figshare DOI.
- **COGITATE**: account required for both routes (website or XNAT), CC BY 4.0. Exp 2 not released.
- **Independent ketamine EEG with delayed report**: none found yet.

## 4. New tasks added to the board

1. #19 M1: Find an independent open ketamine EEG dataset with delayed reports (the current evidence is one cohort).
2. #20 M1: DREAM open-access audit. Which packages are open, their sizes, and a subset under budget.
3. #21 M1: Chennu set exceeds the budget. Find a partial route or get a lead decision.
4. #22 M2: Dream vs no-dream on DREAM with subject- and lab-held-out splits vs a spectral baseline (DREAM's own AUCs used random splits).
5. #23 M3: Add the two 2026 COGITATE reanalyses (Bandara DCM; Bryant & Whyte 246 FC measures) as branches in the hashed multiverse.

## What was not checked

- Supplementary methods (for example, whether DREAM splits held out subjects).
- Full texts of Luppi 2026 and Sutherland 2026 beyond the abstracts.
- The ds003171 sedation levels.
- The Chennu n in the original paper.
- Signatory count of the 2023 letter.
- Sources that are only on bioRxiv are not peer reviewed and are labelled as such.
