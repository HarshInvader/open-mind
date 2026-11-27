# Prior art: transfer of awareness decoders across paradigms or datasets (round 20 #1)

Checked 2026-11-26 with three web searches. Search-result summaries only: **none of these was opened.** All are marked unverified until read.

## Closest
- **"Posterior but not frontal neural signatures of subjective visibility in report-independent EEG decoding"**, bioRxiv 2026.04.20.719596 (unverified).
  - Within one study, classifiers trained on stimulus location in a no-report task were tested on masked trials sorted by visibility.
  - Reported: an early posterior visibility signal at 130–170 ms that generalises across report and no-report, with no frontal contribution. The result is said to depend on the metric (d′ vs AUC).
  - Same lab and same subjects; not zero-shot across datasets. It gives a directional prediction for our early window (rival A).
- **"A late meta-stable code of conscious access in the absence of report"**, bioRxiv 2026.01.30.702733 (unverified).
  - Four no-report inattentional-blindness datasets, temporal generalisation, and report → no-report generalisation.
  - Decoders appear to be trained and tested within each dataset. A late-code prediction (rival B).
- **Sanchez et al. 2020, PNAS, doi:10.1073/pnas.1912584117** (opened in round 18): supramodal detection decoders in MEG, within subjects and session.
- **"Neural representation of consciously seen and unseen information"**, Sci Rep 2025, s41598-025-92490-y (unverified): from a localizer to threshold blocks, within study.
- **"Neural signatures of visual awareness independent of postperceptual processing"**, Cereb Cortex 2024, bhae415 (unverified): no-report masking, temporal generalisation within one task.
- **Noorman et al. 2025, eLife** (opened in round 18): masking vs blink in the same subjects; no awareness-decoder transfer.

## Gap
No search result trains a seen/unseen decoder on one lab's dataset and tests it zero-shot on another lab's dataset with a different cause of unawareness (masking → low contrast, no mask). The novelty sentence is provisional until the two bioRxiv preprints are opened.

## Not covered
EEG foundation-model and cross-dataset work (NEED, NeurIPS 2025; BrainVision; CrossPT-EEG) decodes stimulus content, not awareness.
