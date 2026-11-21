# Sealed forecasts for COGITATE experiment 2 (inattention), 2026-11-21

Sealed before any experiment 2 result is public. Searches on 2026-11-20 and 2026-11-21 (OpenAlex, bioRxiv, web) found no results preprint or paper; the latest public material is an ASSC 2025 poster with behaviour and methods only (N = 139: 76 fMRI, 63 MEG). If a results report appeared before the hash time below, this file is void.

## What is being forecast

The protocol: Melloni et al. 2023, PLOS ONE, doi:10.1371/journal.pone.0268577 (PMC9916582), experiment 2. Faces and objects (2.3°, 250 ms full contrast) appear in the background of a demanding video game. Infrequent awareness probes ask whether a stimulus was seen at a cued location (distracted attention, dAT: seen vs unseen). The same displays are replayed with a go/no-go detection task (attended, AT). Modalities: fMRI, M-EEG, iEEG.

Each item below is one of the protocol's stated predictions (GNW or IIT) or a closely tied empirical outcome. For each, the number is **our probability that the consortium's first public results report says the outcome was found**.

## Priors used (opened sources only)

- **COGITATE experiment 1** (Cogitate Consortium 2025, Nature, doi:10.1038/s41586-025-08888-1).
  - Category was decodable in PFC (iEEG about 70%, 0.2-0.4 s; fMRI MFG/IFG) even for task-irrelevant stimuli, but identity was not.
  - Posterior decoding was strong and sustained.
  - No sustained posterior gamma synchrony (BF01 1.15-4.9).
  - No content-selective PFC-posterior PPC in 0.3-0.5 s, but exploratory DFC found PFC-category-area gamma connectivity.
  - 0/655 PFC electrodes showed offset ignition.
- **GNW reply** (Naccache et al. 2025, doi:10.1093/nc/niaf037): seen vs unseen is GNW's central test, and experiment 1 lacked it.
- **Inattentional blindness EEG.**
  - Shafto & Pitts 2015 (doi:10.1523/jneurosci.0145-15.2015): N170 and the VAN (about 260-300 ms) are absent during inattentional blindness and present with awareness. The P3b is absent for consciously seen but task-irrelevant faces.
  - Pitts et al. 2014 (doi:10.1016/j.neuroimage.2014.07.024): induced gamma and the P3 are absent for task-irrelevant stimuli whether or not they were seen.
  - Pitts et al. 2012 (doi:10.1162/jocn_a_00111): awareness-related differences at 300-340 ms over occipito-parietal sites; earlier pattern differences regardless of awareness.
- **Design difference that cuts the other way.** Probes come every 9-18 s, so subjects know stimuli matter. This makes the stimuli partly task-relevant and makes late and prefrontal seen-vs-unseen differences more likely than in classic one-shot inattentional blindness.

## Forecasts

| # | Theory | Outcome reported as found | P |
|---|---|---|---|
| F1 | IIT / both | Posterior (category-selective and/or early visual) activation: dAT-seen > dAT-unseen | 0.90 |
| F2 | GNW | PFC activation: dAT-seen > dAT-unseen (preregistered ROI, any modality) | 0.65 |
| F3 | both | Face vs object decodable from posterior cortex for dAT-seen | 0.95 |
| F4 | (neither commits) | Face vs object decodable from posterior cortex for dAT-unseen (above chance) | 0.55 |
| F5 | GNW | Face vs object decodable from PFC for dAT-seen, 300-500 ms | 0.55 |
| F6 | GNW | Face vs object **not** decodable from PFC for dAT-unseen in 300-500 ms | 0.75 |
| F7 | GNW (critical) | PFC decoding generalises across AT-go, AT-nogo and dAT-seen | 0.35 |
| F8 | IIT (central) | Posterior decoding / activity patterns generalise across AT-go, AT-nogo and dAT-seen | 0.70 |
| F9 | GNW | Stimulus location (left/right) decodable from PFC for dAT-seen | 0.40 |
| F10 | GNW | Content-specific long-range synchrony PFC-FFA (faces) / PFC-LOC (objects): seen > unseen | 0.30 |
| F11 | IIT | Content-specific synchrony FFA/LOC-V1/V2: seen > unseen | 0.35 |
| F12 | GNW | No seen-unseen difference before 250 ms (activation or decoding), as GNW predicts | 0.30 |
| F13 | GNW | Visibility x time interaction: larger seen-unseen difference late (250-500 ms) than early | 0.75 |
| F14 | GNW | Higher pre-stimulus PFC activity for dAT-unseen than dAT-seen | 0.20 |
| F15 | IIT | Higher pre-stimulus posterior activity or posterior synchrony for dAT-seen | 0.40 |
| F16 | overall | The consortium's summary says neither theory's experiment 2 predictions were fully supported (both challenged) | 0.75 |
| F17 | timing | A results preprint or paper is public by 2027-06-30 | 0.50 |

## Resolution rules (fixed now)

- **Source.** The consortium's first public results report for experiment 2 (preprint or paper, whichever comes first), main text plus supplement. Later versions are not used, except to record changes.
- **Outcome per item.**
  - 1 if the report states the outcome was found, or the prediction was supported, in its primary preregistered analysis in at least one modality, and does not state it failed in another modality.
  - 0.5 if the report calls it partial or mixed across modalities.
  - 0 if the report states it was not found, or not supported.
  - Unresolved if not reported. Unresolved items are left out of scoring and listed.
- **Who resolves.** An agent that did not write these forecasts, given this file and the report. Disagreements are logged, not hidden.

## Scoring

Brier score over resolved items, compared with three baselines:
1. **Coin flip:** 0.5 for every item.
2. **GNW as forecaster:** 1 for every outcome GNW predicts, 0 for every outcome it denies. F1-F16 are coded from the protocol text; items where GNW is silent are scored 0.5.
3. **IIT as forecaster:** the same coding from IIT's predictions.

The coding of each theory's forecast is fixed in `cogitate_exp2_forecasts.json`, sealed with this file.

**Claim being tested:** forecasts built from experiment 1 and the inattentional blindness literature beat both theories, taken as forecasters, and the coin flip. If either theory's coded forecast has a lower Brier score than ours, that is reported as a win for that theory over our reading of the field.
