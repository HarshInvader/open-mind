> **DROPPED BEFORE SEALING (2026-11-25).** Never sealed or run, and no real-label dva was computed. The pre-seal review found the gate underpowered (per-subject Δdva SD about 0.015 under random labels; 0 of 400 simulated gates passed) and the EXPLAINED verdict not identifiable: a real stability difference also lowers the mean ERP, so injection "explains" a pure-stability world (S 0.62–0.82). Kept for the record; see docs/RESEARCH_STATE.md.

# Pre-registration: is "seen trials are more stable" (Schurger et al. 2015) explained by evoked amplitude?

Agent: Open Mind thread   Date: 2026-11-25   Script: `experiments/stability_specificity/stability.py`   Source: Fable round 16, item 5

- **Zero new bytes.** On-disk Cohen et al. 2024 SOA-50 report-block epochs, 38 eligible subjects, same preprocessing as the sealed fixed-SOA and latency studies.
- This tests Schurger et al.'s measure, not Cohen et al.'s claims.

## 0. The claim and prior art (texts in `datasets/local/r16_priorart/schurger/`)

- **Schurger, Sarigiannidis, Naccache, Sitt & Dehaene 2015** (PNAS, doi:10.1073/pnas.1418730112; full main text read; supplement not obtainable).
  - **Measure:** "dva = 1 − R̄", where R̄ = ‖Σ vᵢ/‖vᵢ‖‖ / n over the sensor vectors in "a 100-ms-wide sliding window over the entire array of 204 planar gradiometers". Each sample is normalised so that "only the angle… will determine the norm of their sum".
  - **Finding:** seen trials are more stable within trial (about 500–800 ms) and across trials.
  - **They flag the confound themselves:** "differences in the signal-to-noise ratio can produce artifactual differences in stability", and the relation to SNR is "highly nonlinear".
  - **Controls:** the L2 norm was not larger for seen trials; norm mean-matching; an SVD cross-check; a 7–13 Hz bandstop.
- **The gap.** A larger evoked response, or lower background power (alpha/beta suppression), raises SNR with an equal or lower norm. So the norm controls do not rule out SNR.
  - Of 170 citing papers screened, none tests this. Bachmann 2016 and a 2017 ASSC report raise related worries without a test.
  - Baria 2017 partly replicates the across-trial effect. Arazi 2019 shows that variability quenching in EEG/MEG largely reflects alpha–beta power.
- **Prior-art reviewer's throwaway simulation** (generic 63-channel pink noise, one fixed topography in both classes, not this code; disclosed): evoked amplitude ×1.5 lowered dva by 0.063 (z −43). Amplitude ×1.3 with noise ×0.9 lowered dva by 0.052 with a *lower* norm, which is their published pattern with no change in stability.
  - Because that zero-data result is already in hand, the decisive test here is the real-data injection.

## 1. Measure and data

- **Data:** each subject's kept trials (as in `cohen_killtest.preprocess`: 30 Hz low-pass, linked mastoids, baseline −100–0 ms, the authors' rejection thresholds, bad-channel rule), good scalp channels, then **average reference**. Seen = answer 1, unseen = answer 2.
- **dva (primary, within-trial):** for each trial and each window, 1 − ‖mean over samples of v_t/‖v_t‖‖. This is averaged over trials, then over the two windows **300–400 and 400–500 ms** (the P3b window of our sealed studies, fixed in advance; the epoch ends at 598 ms, so Schurger's 500–800 ms window is not available).
- **dva (secondary, across-trial):** the same formula on each trial's window-mean vector.
- **Descriptive time course:** 100 ms windows centred every 20 ms from 0 to 540 ms.
- **Split-half scoring, per subject, 20 random splits × 2 directions:**
  - The seen-minus-unseen ERP d (all channels and samples) comes from half A.
  - Half B's seen and unseen trials are cut to equal counts and scored.
  - The injected trials are half B's unseen trials + d.
  - No trial is scored with an ERP it contributed to.
- **Secondary injection (+noise):** half B's unseen residuals are scaled by the half-A ratio of seen to unseen broadband residual SD, before adding the unseen mean and d.

## 2. Gate (synthetic, label-free; runs first)

- **Noise:** each subject's kept trials minus their grand mean (labels unused). Pseudo-labels are drawn at random, at the real seen count.
- **Planted topography:** the label-free grand-average 300–500 ms topography (centred, max |value| = 1), on a Gaussian time course (peak 400 ms, SD 80 ms).
- **Worlds:**
  - **AMP world:** the same topography in both classes, peak 3.5 µV in pseudo-seen and 1.5 µV in pseudo-unseen. The difference is pure amplitude, and the pattern is equally stable.
  - **STAB world:** pseudo-unseen trials carry the pattern rotating within each trial toward a random orthogonal direction (random-walk angle, step SD 0.10 rad per sample, angle 0 at 400 ms). Pseudo-seen trials carry the fixed pattern, scaled so that both class means are equal. The difference is pure stability, with equal ERPs.
- **GATE PASS needs:**
  - seen more stable (one-sided t > t_crit, df 37) in both worlds;
  - an explained share (section 3) with 95% CI lower bound ≥ 0.8 in AMP;
  - an explained-share CI upper bound ≤ 0.5 in STAB.
- Otherwise the verdict is **METHOD BLIND**, and the real labels are not analysed.
- **Amplitudes:** 3.5/1.5 µV and 2.5 µV are set near the real P3b-ROI seen-minus-unseen peak (3.6 µV), which the latency study's sealed shape step reported. The planted topography is not ROI-scaled, so the match is rough.

## 3. Real data (only after GATE PASS)

- **Δobs** = dva(unseen) − dva(seen) per subject (> 0: seen more stable). **Replication:** group one-sided t > t_crit (df 37).
- **Explained share** S = 1 − mean(dva(injected) − dva(seen)) ÷ mean(Δobs) (group ratio of means). 95% CI from 5,000 bootstrap resamples of subjects.

| Verdict | Condition (in order) |
|---|---|
| NO REPLICATION | Δobs not significantly > 0. S is still reported as descriptive. |
| STABILITY DIFFERENCE EXPLAINED BY EVOKED AMPLITUDE | S CI lower ≥ 0.8 |
| STABILITY DIFFERENCE NOT EXPLAINED BY EVOKED AMPLITUDE | S CI upper ≤ 0.5 |
| PARTLY EXPLAINED | otherwise |

- **Reported in every case:**
  - S with the +noise injection;
  - across-trial dva and its S;
  - the injected-minus-seen dva and its t;
  - the time course;
  - per-subject values and trial counts.

## 4. Fallbacks and disclosures (stated before any real-label dva)

- **Gate fails:** METHOD BLIND. There is no change to worlds, amplitudes, windows or thresholds.
- **A ratio's denominator is 0:** that bootstrap draw is NaN. More than 5% NaN makes the verdict UNRESOLVED.
- **Compute:** at most 4 workers, nice 20.
- **Pre-seal runs:**
  - The author's pilot timed one subject with permuted labels (0.8 s) and printed timing only.
  - A mechanics check ran `plant` and the scoring for one subject in each gate world and printed only array shapes, the pseudo-seen count, finiteness and timing.
- Any other change after sealing makes the study INVALID.

## 5. What a result would and would not mean

- **EXPLAINED:** in these data, the seen-trial stability advantage is what a larger evoked response gives a fixed-pattern measure. "More stable" adds nothing beyond "larger evoked response" here.
- **NOT EXPLAINED:** some of the stability difference survives an exact amplitude match, which is evidence for a genuine pattern-stability difference.
- **Limits:**
  - EEG (59 channels, average reference) rather than 204 gradiometers.
  - Masked faces in the report block, at 300–500 ms rather than 500–800 ms.
  - Injection matches the mean evoked response, not trial-to-trial amplitude variability.
  - The +noise variant rescales broadband power only, not alpha/beta specifically.
  - This says nothing about their patient result.
