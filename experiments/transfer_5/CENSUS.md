# Task #5 kill test: dataset census for sleep plus propofol (2026-11-23)

**Criteria (coordinator):**
- matched conscious and unconscious states;
- enough subjects for any power;
- a usable licence.

Sources:
- `datasets/catalog.csv` and `docs/DATASETS.md`;
- DOSE-I's Zenodo record (metadata, data use agreement and release notes read on 2026-11-23);
- our own earlier power checks (`experiments/nonequilibrium/RESULTS.md`, P2).

## Sleep: qualifies

| Set | Licence | n | States | Notes |
|---|---|---|---|---|
| Sleep-EDF Expanded | ODC-BY 1.0 | 78 SC subjects (60 already extracted) | W, N3, REM per 30 s | Fpz-Cz and Pz-Oz only. Held locally. |
| HMC sleep staging | CC BY 4.0 | 151 nights | AASM stages | Independent second sleep set (not yet fetched, 15.7 GB). |

Sleep has more open data than needed. Sleep has no report labels here, but the W vs N3 contrast is standard; REM is the known dissociation.

## Propofol: the bottleneck

| Set | Licence | n | Contrast available | Problem |
|---|---|---|---|---|
| ds005620 (Bajwa 2025) | CC0 / CC BY 4.0 | 20 extracted, 15 with enough clean epochs | awake vs sed2 (RASS -4, unresponsive) | 24 of 29 informative awakenings at this depth reported experience. "Unresponsive" is not "unconscious". Our P2 power check: 0% power at d = 0.4 for increments (baseline AUC 0.99). |
| Chennu 2016 | CC BY 2.0 UK | 20 | baseline vs moderate sedation | Most subjects stay responsive at moderate sedation, so this is a drug-level contrast. P2: 10% power at d = 0.4. |
| ds004541 | CC0 | 8 | before vs during surgical GA | Too few subjects. |
| **DOSE-I** (Garbe et al., Zenodo 10.5281/zenodo.18483291) | CC BY 4.0 **plus a Data Use Agreement** | 171 recordings | Repeated bedside MOAA/S (7,328 assessments) and 1,129 annotated transitions of consciousness; 2-channel fronto-temporal EEG at 125 Hz | The only open propofol set with dense responsiveness labels and real power. Its DUA asks "the User" to agree to no re-identification, lawful use and use only for a stated purpose. **Not downloaded: accepting it would bind the owner.** Needs owner sign-off. |

## Verdict
- **Without DOSE-I, the propofol arm fails the kill test.**
  - Neither held set has an unconscious state (ds005620's deep state is mostly disconnected but conscious; Chennu's is mostly responsive).
  - Power for any increment over the spectrum is about 0-10%.
  - A zero-shot transfer scored against these labels would reward measures that track responsiveness or drug level, not consciousness.
- **With DOSE-I**, a responsive (MOAA/S 5) vs unresponsive (MOAA/S 0-1) contrast exists at n ≈ 171 recordings. Its montage (2 frontal channels) is close to Sleep-EDF's Fpz-Cz, which suits zero-shot transfer. Even so, MOAA/S 0-1 is unresponsiveness, not verified unconsciousness, and the limit must be stated.
- **The one thing ds005620 can score** is a disconnected-consciousness check at group level: a measure fitted on sleep W vs N3 should call sed2 "conscious" at about the reported rate (24/29), and an arousal marker would call it N3-like. This ties to board #24 (ketamine and REM) and is noted for Fable.
