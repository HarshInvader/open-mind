# COGITATE (2025) and the GNWT reply: notes for Open Mind

Read in full by mind-ne on 2026-11-19 (PMC open-access XML).
- Cogitate Consortium et al. 2025, Nature, "Adversarial testing of global neuronal workspace and integrated information theories of consciousness", doi:10.1038/s41586-025-08888-1 (PMC12137136).
- Naccache, Wang, Changeux, Sergent, Dehaene, Farisco 2025, Neuroscience of Consciousness, "GNW theoretical framework and the 'adversarial testing…'", doi:10.1093/nc/niaf037 (PMC12510449).

## Design
- 256 participants: fMRI 120, MEG 102, iEEG 34 (29-31 analysed).
- Preregistered predictions with pass/fail criteria, theory-neutral analysts, an optimisation third and a held-out two-thirds.
- **Suprathreshold** faces, objects, letters and false fonts, shown for 0.5, 1.0 or 1.5 s, with relevant/irrelevant task blocks. Key analyses use task-irrelevant trials.
- **No seen/unseen contrast and no visibility reports.**

## Results (as the paper states them)

| Prediction | IIT | GNWT |
|---|---|---|
| 1. Where content is decodable | Posterior: category > 95% (iEEG HG), sustained for the stimulus duration. Orientation decodable posteriorly in all modalities. Passes (non-critical for IIT). | PFC category about 70%, but only about 0.2-0.4 s; fMRI PFC about 60%, restricted to MFG/IFG. **No identity in PFC; orientation only in MEG.** |
| 2. Maintenance over time | 25/657 posterior electrodes track duration; only 8/53 face-selective ones. "Sparse." Passes by the preregistered criterion. | **0/655 PFC electrodes show onset + offset ignition** (BF01 > 3 for all). 99 non-selective and 24 category-selective PFC onset responses. The model did detect the onset/offset pattern in 10 visual electrodes. |
| 3. Connectivity | **No sustained gamma synchrony within posterior cortex** (PPC early, 2-25 Hz, mostly evoked; BF01 1.15-4.9). This is the main challenge to IIT. | No content-selective PPC with PFC in 0.3-0.5 s (BF01 2.6-5.3). **Exploratory DFC: gamma connectivity between PFC and category areas in the GNWT window**, plus brief connectivity with V1/V2. |

The consortium's conclusion: both theories are substantially challenged. For IIT, the lack of sustained posterior synchronisation. For GNWT, no offset ignition and limited PFC representation of some conscious dimensions. It raises the question of whether PFC broadcasts only a subset of content (abstract or category).

## GNWT proponents' reply (Naccache, Changeux, Dehaene et al.)
1. Several core GNWT predictions were **confirmed**: transient onset ignition at 200-800 ms, independent of duration and of task relevance; content decoding in IFC; frontal-visual synchronisation.
2. **COGITATE could not test GNWT's most central prediction, conscious vs non-conscious processing, because all stimuli were clearly visible.**
3. Offset ignition is not a core GNWT prediction. It is expected only if offset is consciously attended, and no GNW simulation produced it.
4. Missing PFC decoding of identity and orientation may reflect mixed selectivity without columnar organisation in PFC. The right test is single-cell recording.
5. Activity-silent maintenance is not required. GNWT predicts continuous decoding while the content stays in awareness, and lapses in awareness could explain gaps.

## Why this matters for us
- The contrast that both sides call decisive (same stimulus, seen vs unseen, separating report from experience) **was not in COGITATE**.
- Stockart et al. 2025 (OSF 8QE3A, 29-30 sEEG patients, threshold faces, report / delayed / **no-report** conditions) has exactly that contrast. See `docs/DATASETS.md`.
- A GNWT extension that commits in advance to what ignition looks like on seen vs unseen trials **without report** would test the prediction the reply says matters most, on open data.
