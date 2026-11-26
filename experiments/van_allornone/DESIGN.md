# Round 19 #1: is an unseen face's VAN the same as mask-only? (design draft, not sealed)

Status: draft, 2026-11-26. This must be sealed before item 4's `gate` or `run` reads report mask-only (RM) VAN values.
Item 4's `prep` is label-free and prints counts only, so it may run first. Study 1 then reads `out/s4_prep.npz`.
Cohen hold: nothing public before 2026-12-08.

## 1. Question
In Cohen et al. 2024 at SOA 50 (report block), is the visual awareness negativity (VAN) all-or-none or graded?
- All-or-none: an unseen face's VAN equals the mask-only baseline.
- Graded: an unseen face's VAN lies part of the way to a seen face's.

This bears on two theories:
- **Recurrent processing (RPT):** the VAN marks awareness.
- **Global workspace (GNWT):** early stages are graded and preconscious; only later activity is all-or-none.

It also bears on reading our own sealed VAN PASS (seen − unseen at fixed SOA) as an awareness marker.

Statistic: R = (miss − CR) / (hit − CR), from VAN window means.
- **Hit:** face shown, reported seen.
- **Miss:** face shown, reported unseen.
- **CR:** report mask-only trial. Item 4's prep does not keep mask-only responses. False alarms are 69 of 6,126 (1.1%), so using all mask-only trials moves R by at most about 0.01. This is stated in advance and not corrected.

## 2. Rival explanations and what each predicts for R
Behaviour, from `trials.csv` (report block): mask-only false alarms are 1.13%, so the criterion is c = 2.28. SOA-50 hits are 52.5%.
Predictions are derived in `predictions.py` (to be added; the numbers below are from the same code run inline on 2026-11-26).

| Rival | R predicted |
|---|---|
| A. All-or-none, lapses λ (aware trials reported unseen) | 0.02 (λ = 0.02), 0.06 (λ = 0.05), 0.12 (λ = 0.10) |
| B. Graded signal, report = threshold on the VAN's own variable (β = 1), signal SD σs | 0.49 (σs = 1), 0.40 (1.25), 0.32 (1.5), 0.19 (2.0) |
| B'. Graded, VAN carries only a share β of the decision variance | higher: β = 0.5 gives 0.50–0.71; β = 0.2 gives 0.77–0.87 |
| C. All-or-none awareness plus stimulus-driven residue (an unseen face still evokes an N170-like response in the window) | R > 0, of any size |
| D. Artefact: mask-only epochs misaligned (virtual onset 25 samples before the mask) | the P1 check also gives miss = CR, or a shifted mask P1 |

Fable's round 19 note gave 0.49 as a floor for B. That holds only at σs = 1 and β = 1. Unequal variance lowers it: detection z-ROC slopes of about 0.8 give σs of about 1.25.

## 3. Where the rivals disagree, and the decision rule (draft)
- **R is decisive in one direction only.** A small R rejects B with σs ≤ 1.5, and B'. A large R cannot separate B from C.
- **Primary call (bootstrap over subjects, 95% CI):**
  - Upper bound < 0.20: **ALL-OR-NONE-COMPATIBLE**. A is supported, and graded with σs ≤ 1.5 is rejected. An upper bound of 0.20 sits above A at λ ≤ 0.10, and the threshold should sit above A. σs = 2 is not rejected, and that is stated.
  - Lower bound > 0.20: **NOT ALL-OR-NONE AT THE VAN**. This is either B or C; §4 separates them.
  - Otherwise: **INCONCLUSIVE**.
  - Open for review: whether 0.20 or 0.25 is the right cut.
- **Separating B from C: shape test.** Under B, every trial class reads one latent variable. So the miss − CR waveform at the VAN electrodes over 100–300 ms must be a scaled copy of the hit − miss waveform. Under C, the miss − CR difference is stimulus-driven: earlier (P1/N1) with a different time course.
  - Statistic: the correlation between the two subject-averaged difference waveforms, against a split-half reliability ceiling.
  - Needs per-sample waveforms, not window means. That means a small sealed re-cut using item 4's exact preprocessing rules (draft).

## 4. Independent checks (each states why it tracks its target)
- **P1 (100–140 ms), miss > CR.** A face was physically shown on miss trials, so early visual cortex should respond more than to the mask alone. If P1 miss = CR, the alignment or the cells are wrong (D), and the study is INVALID.
- **Hit − miss VAN must reproduce the sealed VAN PASS sign.** These are the same RF trials, so this is a consistency check, not new evidence.
- **The P3b check is dropped.** Mask-only epochs end at +300 ms, and fetching more would mean a new download under the hold.

## 5. Kill test (before sealing; does not touch RM values)
- Take the real RF hit and miss VAN values from s4_prep. Draw synthetic RM from the RF-unseen trial SD at real per-subject RM counts (about 60, fewer after rejection), with the CR mean planted at R = 0 and at R = 0.4.
- Required: a 95% CI half-width of R ≤ 0.12, and correct calls in ≥ 80% of runs at both plants. Otherwise drop the study before sealing.
- Problem: s4_prep does not exist until item 4's `prep` runs (after the fetch exits). Until then, the kill test can use the report-face epochs already on disk (`cohen2024_epochs`), with the sealed preprocessing re-applied to RF only.

## 6. Likely artefacts if a surprise appears
- **R ≈ 0 from wrong time-locking of mask-only trials:** P1 check, plus a label-free mask-P1 latency match between RM and RF.
- **R > 1 or < 0 with a large CI:** a near-zero denominator in some subjects. Use the group ratio of means, never the mean of per-subject ratios.
- **Rejection rates differ between RF and RM (blinks around the mask):** report both.

## 7. Prior art (to read before sealing)
On disk:
- Sergent 2021 Fig 3C (`datasets/local/r16_priorart/sergent2021.txt`);
- Fisch 2009;
- Cohen 2024.

Not yet opened:
- Koivisto & Grassini 2016 (unverified);
- Lamy 2009 (unverified);
- any study that tested an unseen-versus-absent VAN in masking (to search).

The novelty sentence is written after reading.

## 8. Kill test results (2026-11-26, pre-seal; no mask-only value read)
`killtest.py`: 39 eligible subjects; median 59 synthetic mask-only trials per subject after rejection; 200 runs × 2,000 bootstraps.
Outputs are in `out/killtest_*.json`. The pre-stated criteria were a median 95% half-width ≤ 0.12 on the R scale and ≥ 80% correct calls at both plants.

| Version | Mask-only trials | Cut | R = 0: correct, wrong | R = 0.4: correct, wrong | Half-width at R = 0, R = 0.4 | Verdict |
|---|---|---|---|---|---|---|
| 1: ratio bootstrap | 60 | 0.20 | 69.5%, 0% | 96.5%, 0% | 0.19, 0.10 | FAIL |
| 2: linear contrast | 60 | 0.20 | 69.5%, 0% | 96.5%, 0% | 0.19, 0.10 | FAIL |
| 2 | 150 | 0.20 | 72.5%, 0% | 99.5%, 0% | 0.16, 0.09 | FAIL |
| 2 | 60 | 0.25 | 87%, 0% | 83%, 0% | 0.19, 0.10 | FAIL (half-width) |
| 2 | 150 | 0.25 | 85.5%, 0% | 93.5%, 0% | 0.16, 0.09 | FAIL (half-width) |

- **Version 2's first run was a bug.** The VAN is a negativity, so the contrast's sign was flipped and every call was mirrored. The signs are now fixed in the awareness direction set by the sealed VAN PASS. After the fix, version 2 gives the same results as version 1.
- **More mask-only trials help little.** Most of the noise is in the miss and hit means, which cannot be increased.
- **A cut of 0.25 passes the call-rate criteria but not the half-width.** It would also call a graded signal with σs = 2 (R ≈ 0.19) all-or-none-compatible.
- **Decision pending.** Fable's review will decide whether to drop the study, re-cut it, or redesign it. As written, the study fails its kill test.

## 9. Decision: DROPPED before sealing (2026-11-26)
- **Kill test:** failed its pre-stated criteria (§5, §8). §5 already said "otherwise drop the study before sealing". The cut is not moved and the half-width criterion is not removed.
- **Fable review:** agreed, and added four reasons:
  - The planted R was the same in every subject, so real between-subject spread would make the half-width wider still.
  - A trial-distribution (mixture vs graded) likelihood reduces to the means. Report-face trials only, 39 subjects: hit − miss −1.55 µV (between-subject SD 1.27), single-trial SD 4.08 µV, hit/miss variance ratio 0.995. Mixture variance adds 1–4%, against a standard error of about 3%.
  - The VAN electrodes and window (PO9/PO10, 140–200 ms) are N170 territory. Stimulus residue (rival C) is therefore the expected outcome, and only R ≈ 0 would be informative, which is where power is worst.
  - The waveform-shape test is underpowered and not diagnostic.
- **Fixed now, before item 4 reads any mask-only value:** item 4's output lets miss − CR be computed. If R is ever reported, it is a description only: point estimate and 95% CI, with no call, no claim and no cut chosen afterwards. This file is hashed in `docs/prereg/HASHES.txt` to fix that rule.
- **Next:** round 19 #2 (ds006171). The primary test is a second-lab, no-mask replication of seen vs unseen at matched contrast. R is secondary, under unchanged kill-test criteria plus a plant at 0.25–0.32. If R's kill test fails, R is reported as an estimate only.
