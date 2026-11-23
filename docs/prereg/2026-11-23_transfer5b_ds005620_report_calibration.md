# Task #5b: does the frozen sleep exponent cutoff call report-confirmed experience under propofol "N3-like"? (prereg)

Sealed on 2026-11-23, before any report labels exist on our side. We have asked the ds005620 authors for a 52-row table (subject, run, report class); there has been no reply. The coordinator asked for this seal so the table cannot shape the plan.

## Question

In ds005620 (Bajwa et al. 2025, doi:10.1038/s41598-025-12695-z), some propofol awakenings at RASS −4 were followed by a report of experience. The last 30 s of sed2 EEG before each attempt is already extracted. We take the 1/f exponent cutoff frozen on Sleep-EDF wake vs N3 in task #5 (sign +1, threshold −2.1637). What fraction of report-confirmed experience awakenings falls on that cutoff's N3 side?

This calibrates a widely used measure against reports. It is not a test of a theory.

## Exposure (what we have already seen)

- **Seen:** the exponent value of every clean sed2 run: 44 clean runs out of 51 available in the release for our 20 subjects (7 failed the amplitude check). Of these, 30 are N3-side and 14 wake-side (`experiments/transfer_5/ds005620_runmap.json`, label-free). Expect about 20 clean experience runs, so the stop check is a live outcome.
- **Seen:** the paper's group counts: 52 attempted awakenings, 24 experience, 5 no experience, 23 unarousable or incoherent.
- **Not seen:** any per-run report label.
- **Prior art against the hypothesis:** Casey et al. 2024 (doi:10.1016/j.bja.2023.09.031, abstract read) found the exponent steepens from disconnected experience to unconsciousness under propofol, dexmedetomidine and sleep. That is a within-study contrast. Ours asks about absolute calibration against a sleep cutoff.

## Data mapping (sealed)

- **Joining labels to runs:** labels join to runs by (subject, run), where run is the sed2 run number in the release (`task-sed2_acq-rest_run-<n>`).
- **Format:** the authors' table is first converted to `subject, run, class`, with their class string kept verbatim.
- **Blind class mapping:** run `score_reports.py classes` first. It prints only the distinct class strings. `CLASSMAP.json` is then written from that list alone, without looking at subjects, runs or exponents, and committed before scoring. Rule:
  - any report of an experience (dreaming, thoughts, perceptions, with or without recalled content, including "experience without recall" / white dream) → `experience`;
  - a clear "nothing" report → `no_experience`;
  - unarousable, incoherent, or no reliable answer → `unarousable`;
  - "don't know whether anything was experienced", or any class string whose meaning the authors' paper or reply does not fix → `exclude` (listed, not scored).
- **Mechanical stops in code (no judgement):**
  - any class string missing from `CLASSMAP.json`;
  - any duplicate (subject, run) row;
  - any (subject, run) that is not a release sed2 file. This includes attempt numbers that do not match file run numbers ("not mappable"). sub-1037 is the exception: it is excluded from our extraction, so its rows count as unclean.
  If the authors later give an explicit mapping, it may be applied as an amendment only if it uses no exponent information.
- **Unclean runs:** labels for the 7 unclean runs and for sub-1037 are listed and not scored.

## Primary analysis (code: `experiments/transfer_5/score_reports.py score`)

1. **Stop check (kill test):** if fewer than 16 experience awakenings fall on clean runs, stop with "not testable". There is no further analysis and no reinterpretation.
2. Count k, the experience runs on the exponent's N3 side, out of n. Take the two-sided 95% Clopper-Pearson CI.
3. **Call:**
   - lower bound > 0.5 → **"N3-like despite report"**: the frozen sleep cutoff calls most report-confirmed experience under propofol N3-like;
   - upper bound < 0.5 → **"wake-like with report"**;
   - otherwise → **"inconclusive"**.

## Secondary (descriptive, not gating)

- The same count for the spectral baseline (LDA, exponent plus 6 bands, frozen in task #5).
- N3-side counts for `no_experience` and `unarousable`.
- Mann-Whitney on exponent values, experience vs unarousable, if there are at least 5 unarousable runs. This mirrors Casey et al. 2024's contrast. With these counts it is descriptive only.

## Planted/power gate (run before sealing: `score_reports.py gate`, output `reports_gate.json`; passed)

- **Pass rule:**
  - at a true N3-side rate of 0.5, the false "N3-like" rate is ≤ 0.05 at n = 16, 20 and 24. Observed: 0.011, 0.021, 0.011;
  - at a true rate of 0.80 and n = 24, "N3-like" is reached ≥ 80% of the time. Observed: 0.811.
- **Power is low at the rate we expect.** If reports were unrelated to the exponent, the experience runs would mirror all runs (30/44 = 0.68). The test then reaches "N3-like" only 31% of the time at n = 24 (20% at n = 16). Resampling the real 44 runs gives 14-29%. The likely outcome is "inconclusive", and we say so now.
- "Wake-like with report" is reachable only if the true rate is ≤ 0.3 (39% at n = 24).
- **Not independent:** the Clopper-Pearson interval treats runs as independent, but there are 1-3 runs per subject. Of the 15 subjects with two or more clean runs, 9 have all runs on one side. The false-call rates above are therefore optimistic. Disclosed, not corrected (Fable round 12).

## Prediction

"Inconclusive" or "N3-like despite report", with the point estimate above 0.5. A "wake-like with report" result would mean the frozen cutoff tracks reported experience under propofol better than its group-level behaviour suggests.

## Limits stated now

- The labels are the authors' interview classes. RASS −4 sed2 is the minute before the attempt, and we use only its last 30 s.
- The cutoff was fitted on a different montage and lab (Sleep-EDF Fpz-Cz/Pz-Oz, matched derivations here).
- The groups are small.
- Whatever the outcome, this is a calibration statement, not evidence about what the exponent measures in general.

## Pre-seal review

Fable round 12 found five must-fix items, all fixed before sealing: exposure counts, duplicate rows, a mechanical "not mappable" stop, blind class mapping, and subject-string parsing. A smoke test on synthetic labels exercised both the scoring path and the stop path; its output was deleted.

## Sealed files

- `experiments/transfer_5/score_reports.py`
- `experiments/transfer_5/make_runmap.py`
- `experiments/transfer_5/ds005620_runmap.json`
- `experiments/transfer_5/reports_gate.json`
- This prereg.
