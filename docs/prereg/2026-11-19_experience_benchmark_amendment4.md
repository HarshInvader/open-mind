# Amendment 4 to the experience benchmark pre-registration

Amends the pre-registration (de1f44ce…) and amendments 1-3. Written 2026-11-19 during label-blind extraction. **No DREAM label has been joined to any EEG feature.** Sealed on the owner's go-ahead (2026-11-19); the coordinator was notified. Only the extraction status fields (stage, status, channel counts) and, for 7 Rome records, raw EEG amplitude statistics were looked at.

## 1. Problem found during extraction

The first 111 Rome records were extracted under the sealed rule: a channel is bad if, in the main window, SD < 0.5 µV, SD > 200 µV or max |x| > 1000 µV, measured on the raw signal. 29 of 111 records (26%) were dropped for having fewer than 60% good channels: 17 N2, 10 REM and 2 N3.

A label-blind diagnostic on 5 dropped and 2 kept Rome records (script in the commit, `diag_drop.py`) shows that the cause is DC offset and slow drift, not noisy EEG:
- the median channel offset is 136-332 µV;
- the median raw SD is 188-935 µV, and after a 0.5 Hz high-pass it is 28-209 µV;
- after the high-pass, 4 of the 5 dropped records have 21-28 of 28 good channels, and the fifth still has 6 (it is really bad).

The sealed limits were written for drift-free signals, so they were measuring the drift, not the EEG.

## 2. Change

The good/bad channel decision is made on a copy of the tail high-passed at 0.5 Hz (Butterworth order 2, zero-phase, `sosfiltfilt` over the whole 40 s tail, then the same main window). The limits (0.5 µV, 200 µV, 1000 µV) and the 60% rule are unchanged. Features are computed exactly as before: only the decision about which channels are kept changes.

The rule applies to every lab. All records already extracted (Rome, 111) are re-extracted under it, so every record in the analysis uses one rule. The old Rome features and log files are kept, unused, in `experiments/experience_benchmark/superseded_amend4/` (not published, like all features before sealing). `extract.py` is re-sealed with this amendment.

## 3. Why this is allowed

The change is decided from signal quality alone, before any label is joined, and it applies to all labs and classes equally. It is reported as a deviation. The count of records dropped under each rule is reported per lab.
