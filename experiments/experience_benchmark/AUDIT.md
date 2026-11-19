# Task #42, step 1: label-blind audit (2026-11-19)

**Verdict: the experience benchmark can go ahead for N2. REM is underpowered and becomes secondary.** No EEG samples were read; only zip directories, EDF headers (`audit.py` -> `audit.json`) and the public per-awakening metadata (`experiments/dataset_audit/dream_records.csv`).

## K1 (enough data): passes for N2, narrowly

Within-subject analysis needs subjects with both an experience and a no-experience report at the stage. Counted that way, in the four labs this project has never opened:

| Lab (DREAM set) | N2 exp / no-exp (subjects) | REM exp / no-exp (subjects) | EEG | Zip |
|---|---|---|---|---|
| Rome multiple awakenings (9) | 171 / 85 (18) | 90 / 29 (12) | 32 ch (+EOG, EMG), 250 Hz, 641 s per file | 6.4 GB |
| LODE (3) | 41 / 28 (15) | 14 / 11 (7) | 7 **bipolar forehead-headband** derivations (Fp1-O1, F7-O1, F8-O2, ...), 250 Hz, 140 s | 0.13 GB |
| DATA1, Noreika (16) | 15 / 18 (5) | 13 / 4 (3) | 27 ch, 2000 Hz, 60 s, prefilter field NaN | 1.6 GB |
| Aamodt evening + morning (17, 18) | 22 / 17 (9) | none | 62 ch, 1000 Hz, 61-182 s | 7.9 GB |
| **Total** | **249 / 148 (47)** | **117 / 44 (22)** | | 16 GB |

- K1 needs ≥ 300 awakenings, ≥ 120 no-experience and ≥ 3 labs: N2 passes (397 / 148 / 4). Two thirds of the N2 data comes from the Rome lab, so per-lab estimates will be noisy outside Rome.
- Discovery (exposed) labs:
  - Tononi: 344 / 309, 39 subjects, all with both classes; 257 ch.
  - Zhang & Wamsley: 50 / 31, 16 subjects.
  - Rome young adults: 0 subjects with both classes, so it adds nothing within-subject.

## K2 (power): `power_sim.py` -> `power_sim.json`

Synthetic subject-centred feature, real per-subject counts, within-subject permutation null:

| Stage | AUC 0.55 | AUC 0.59 (d 0.36) | AUC 0.63 | FPR at d 0 |
|---|---|---|---|---|
| N2, alpha 0.05 | 52% | 94% | 100% | 6.5% |
| N2, Holm-worst alpha 0.05/28 | 11% | 59% | 94% | 0.5% |
| REM, alpha 0.05 | 26% | 58% | 82% | 4.5% |

## Design changes for the prereg (from this audit, before any signal is read)

1. **Primary family = N2 only**, with at most about 8 primary measures (Holm over 8 is alpha ≥ 0.006, so power at AUC 0.60 is about 80%). Other measures and all of REM become secondary or exploratory.
2. **No common F4/C4/O2 montage across all labs**, because LODE is a forehead headband. Primary features are computed per lab on its own channels: the average over available channels, plus a posterior ROI where one exists. LODE uses its frontal-occipital bipolar pairs. This is stated as a limitation.
3. The sealed analysis uses ≥ 5000 within-subject permutations, so Holm-level p values are reachable.
4. **A null can be stated as a bound:** with 397 N2 awakenings the AUC standard error is about 0.03, so an upper CI below 0.60 is reachable if the true AUC is about 0.5.
5. Files are deflated zip members. Only the last 20 s before waking is needed, so `t1_dream/tailzip.py` (inflate only the member's tail) can cut the download below the 25 GB approved.

## Budget

The owner approved raising the download budget to about 25 GB streamed, nothing kept (2026-11-19). The owner also accepted the DOSE-I data-use terms (no re-identification; research use only).
