# Pre-registration: does the seen/unseen VAN difference need a report? Double difference with mask-only trials (Cohen et al. 2024, SOA 50 ms)

Agent: Open Mind thread   Date: 2026-11-25   Status: to be sealed before the gate and before any no-report value is looked at.

- **Supersedes the draft** `2026-11-24_cohen_noreport_study4.md` (design, simulations, byte options). That draft's questions, primary statistic and decision rule are kept; this file fixes the details, the gate and the fallbacks.
- **Builds on** the sealed fixed-SOA study (`2026-11-24_cohen_fixed_soa_killtest.md`): in report trials at SOA 50 the VAN (PO9/PO10 = channels 53/57, 140–200 ms) was −1.16 µV more negative on seen trials, in 22 of 24 held-out subjects.
- **Code:** `experiments/cohen_fixed_soa/fetch_noreport.py` (fetch), `experiments/cohen_fixed_soa/study4.py` (everything else).
- **Hold:** results built on Cohen data (OSF 6d5av) get no site page or post until a reply from the authors or 2026-12-08.

## 0. State of the data at sealing

- On disk before this prereg: the report-block face SOA-50 epochs (−100 to +600 ms; used in the sealed study).
- Being fetched while this was written (launched about 17:17Z on 2026-11-25), never opened before the seal: no-report face SOA-50 trials (all 5,144) and mask-only trials, 60 per subject per block (2,400 + 2,400), −100 to +300 ms, 250,588,800 bytes.
- Mask-only trials were picked label-free and before any data was read: the block's mask-only trials in time order, indices round(linspace(0, n−1, 60)).

## 1. Question and predictions

- In the no-report block there are no answers. Does the VAN on no-report face trials look like the report-block mix of seen and unseen trials (AWARE), or like unseen trials only (REPORT)?
- **AWARE:** the seen-like VAN appears without a report. The report-block difference does not depend on reporting.
- **REPORT:** the difference needs the report task.

## 2. Time-locking (checked on markers only)

- S150/S250 mark mask onset on mask-only trials: S153/S253 follows 50 samples (100 ms) later, as it follows the mask on face trials.
- On SOA-50 face trials the mask starts 25 samples (50 ms) after the face.
- Mask-only epochs are therefore locked 25 samples before S150/S250 (a virtual face onset). The mask is at +50 ms in all four cells.

## 3. Preprocessing (label-free; the sealed study's rules, applied identically to all four cells)

- Cells per subject: RF = report face SOA 50 with a seen/unseen answer; RM = report mask-only; NF = no-report face SOA 50; NM = no-report mask-only.
- RF epochs are cut to −100..+300 ms (200 samples) before filtering, so every cell is processed the same way.
- Then, in order:
  1. Zero-phase 4th-order Butterworth 30 Hz low-pass.
  2. Linked-mastoid re-reference (scalp − left mastoid / 2).
  3. Baseline −100..0 ms.
  4. Bad channels: median peak-to-peak more than 3 × the median over channels, computed over all of a subject's trials pooled across cells.
  5. Trial rejection: HEOG peak-to-peak > 50 µV, VEOG > 150 µV, any good scalp channel > 150 µV.
- Values per trial: the mean over the ROI's good channels and the window. VAN: channels 53/57, 140–200 ms. P1 control: channels 41–45 and 53–57, 100–140 ms.
- Note: the sealed study's rejection used −100..+600 ms epochs. Over the shorter epoch fewer trials will be rejected, and RF trial sets differ slightly from the sealed ones. This is accepted; all four cells are treated alike.

## 4. Eligibility and validity

- A subject is eligible if all of these hold:
  - both VAN channels are good;
  - at least half of the P1 ROI is good;
  - the mastoid is not flagged (the sealed rule);
  - at least 20 clean seen and 20 clean unseen RF trials;
  - at least 40 clean trials in each of NF, RM and NM.
- **INVALID** if fewer than 30 subjects are eligible.
- **INVALID** if the alignment check fails. This is the sealed label-free criterion applied to NF trials, all subjects that have at least one clean NF trial (the number skipped is recorded): grand occipital response onset (> 1 µV) in 60–120 ms, positive peak in 100–160 ms, and a 100–160 ms mean > 0 across subjects with p < .01.

## 5. Primary statistic and decision

- Per subject:
  - DD_s = (mean NF − mean NM) − (mean RF − mean RM), VAN window.
  - π_s = the share of seen answers among clean RF trials.
  - Δ̂_s = mean VAN of seen RF trials − mean VAN of unseen RF trials.
- DD_norm = mean(DD_s) / −mean(π_s Δ̂_s).
  - Under REPORT, the no-report face trials are all unseen-like, so DD_s = −π_s Δ_s and DD_norm = 1.
  - Under AWARE, DD_norm = 0. A half-size effect gives 0.5.
- **Interval:** a percentile bootstrap over subjects (10,000 resamples, numerator and denominator resampled together, seed 20261125 + 1). The interval is 95% (2.5/97.5), or 99% if fallback F2 is in force.
- **Decision:**
  - **INVALID** if the lower bound of the bootstrap interval for −mean(π Δ̂) is ≤ 0 (no clear report-block seen–unseen VAN difference to scale by), or if any bound is non-finite.
  - **REPORT-like** if the lower bound of DD_norm > 0.5.
  - **AWARE-like** if the upper bound < 0.5.
  - Otherwise **INCONCLUSIVE**.
- **P1 control:** the same DD statistic in the P1 window, scaled by the VAN denominator, always with a 95% interval (also under F2). If the interval excludes 0, the verdict is flagged (an early stimulus or state difference between the blocks). The flag qualifies the verdict; it does not change it.
- **Descriptive only:**
  - mean NF − NM;
  - mean RF − RM;
  - the mask-only block offset (NM − RM).
- The P3b window cannot be measured: the epochs end at 300 ms.

## 6. Gate: planted-proportion calibration on real trials (run after sealing, before `run`)

- **Inputs:** report-block trials only (RF with answers, RM). No NF or NM value is read.
- **Each run, per eligible subject:**
  1. Split RF at random into halves A and B, stratified by answer. Split RM into halves A and B.
  2. Half A is the pseudo report block. Its labels give π and Δ̂.
  3. Half B builds the pseudo no-report block. Draw |B| face trials with replacement, with a planted seen share q; each trial comes from B's seen pool or B's unseen pool.
  4. Pseudo NM = RM half B.
  5. Add a block offset β ~ N(0, 1 µV) to both pseudo no-report cells.
  6. Add a face-only mismatch ~ N(0, τ_int) to the pseudo NF mean.
- **Worlds:**
  - AWARE: q = B's seen share; expect DD_norm 0.
  - HALF: q = half of that; expect 0.5.
  - REPORT: q = 0; expect 1.
  - SHUFFLED: the AWARE world with half A's labels permuted, so Δ̂ ≈ 0.
- Each world is run at τ_int ∈ {0.3, 0.6} µV: 200 runs per world, 2,000 bootstrap resamples per run, seed 20261125.
- **PASS needs all of the following, at both τ_int:**
  - AWARE world called REPORT-like in ≤ 5% of runs;
  - REPORT world called AWARE-like in ≤ 5%;
  - HALF world called AWARE-like ≤ 10% and REPORT-like ≤ 10%;
  - SHUFFLED world called AWARE-like or REPORT-like in ≤ 5% in total (INVALID or INCONCLUSIVE are the right answers there).
- **Also reported, not gated:** the AWARE world with a fixed face-only block shift δ ∈ {−0.4, −0.2, +0.2, +0.4} µV added to the pseudo NF mean. These show how large an awareness-independent face-specific block difference must be to produce a false REPORT-like or AWARE-like call. The INVALID rate per world is reported next to power.
- **Power is reported, not gated.** Each pseudo block has about half the trials of the real ones, so gate power is a lower bound on the real design's power. A synthetic smoke test of this code (40 runs) gave 0.18–0.33 correct calls with no wrong calls. The draft's full-size simulation gave about 0.6.

## 7. Fallbacks (stated before calibration; any other change after the gate makes the result INVALID)

| Event | Fallback |
|---|---|
| F1: the fetch leaves gaps (failed requests, a subject missing) | `prep` runs once, after the fetch process has exited, on what is on disk. Eligibility (§4) decides. No re-fetch and no second `prep` (the script refuses; the gate stores the sha256 of `s4_prep.npz` and `run` checks it). |
| F2: the gate FAILS | `run` refuses until `gate99` has run. Run `gate99` once: the same gate with 99% intervals and seed 20261125 + 2. If it passes, `run` uses 99% intervals. If it fails, the study stops: "the design cannot separate AWARE from REPORT on these data", and `run` records INVALID. |
| F3: the gate passes with power < 0.5 | No change. INCONCLUSIVE is the likely outcome, and it is reported as such. |
| F4: alignment fails, or fewer than 30 subjects are eligible | INVALID, recorded by `run` (with fewer than 30 eligible the gate is not run). No change of criterion. |
| F6: `run` has written `s4_result.json` | It is final; the script refuses a second `run`. |
| F5: the denominator interval includes 0 | INVALID (§5). |

## 8. Commands

| Step | Command (in `experiments/cohen_fixed_soa/`) | Needs the seal |
|---|---|---|
| Fetch | `python -I fetch_noreport.py fetch` | no (data only) |
| Preprocess | `python -I study4.py prep`, once, after the fetch has exited | no (label-free; prints counts and rejection rates only) |
| Alignment | `python -I study4.py align` | yes (prints PASS and timings only) |
| Gate | `python -I study4.py gate` (then `gate99` only under F2) | yes |
| Result | `python -I study4.py run` | yes |

- Before the seal, `prep` may be dry-run on the subjects fetched so far, into a scratch directory that is then deleted, to check that the code runs. It prints counts only. No NF or NM value is printed before `run`.

## 9. What it cannot say

- **No answers in the no-report block.** "AWARE-like" means the no-report VAN matches the report-block mix. It does not prove those faces were seen.
- **Seeing may differ between blocks** (task and attention differ). DD measures that as well as any effect of reporting.
- **Mask-only trials are an imperfect reference.** The block offset must be shared between face and mask-only trials. τ_int models random, subject-level departures from this. It does not model a systematic face-specific block difference: for example, faces are task-relevant only in the report block. With mean π Δ̂ near 0.75 µV, a shift of about 0.38 µV moves a true AWARE world to DD_norm 0.5. So REPORT-like cannot be told apart from an awareness-independent face-specific shift of that size, in the predicted direction. The δ worlds in §6 show the size.
