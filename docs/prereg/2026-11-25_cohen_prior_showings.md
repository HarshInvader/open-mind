# Pre-registration: does a stronger earlier showing of a face make that face easier to see later? (Cohen et al. 2024, behaviour only)

Agent: Open Mind thread   Date: 2026-11-25   Script: `experiments/cohen_fixed_soa/prior_showings.py`   Source: Fable round 15, item 3 (reframed after prior art)

- **Data:** `experiments/cohen_fixed_soa/trials.csv` only: event log and responses already on disk. Zero new bytes, no EEG.
- **Design facts (label-free, `out/prior_design.json`):**
  - 40 subjects, 5,079 target trials (median 128 per subject).
  - The two blocks share one timeline per subject; 18 subjects did the no-report block first.
  - On average a target face has 14.9 earlier showings.

## 0. Prior art and reframing

- **Searched (Europe PMC, Crossref):** repetition priming of detection, masked-face familiarity, old/new clarity or visibility, item-specific perceptual learning, serial dependence and b-CFS familiarity.
- **Established:**
  - Prior study improves identification of briefly flashed items and makes them seem clearer: Jacoby & Dallas 1981, *JEP:G* 110:306; Whittlesea, Jacoby & Girard 1990, *JML* 29:716.
  - Repeating a strongly masked stimulus within a trial increases awareness: Atas, Vermeiren & Cleeremans 2013, *Conscious Cogn*.
  - Visibility ratings rise with general practice, even on catch trials: Berger et al. 2026, *NoC*.
  - Expectation lowers threshold: Melloni 2011.
- **Not found:** an item-specific, randomised contrast of **strong vs weak earlier exposures** of the same item at a lag of minutes, with the number of exposures held fixed.
- **The question is therefore not "does repetition help".** It is whether the *strength* of earlier exposures matters beyond their number.
  - Strong exposures (SOA 67/83) are mostly visible; weak ones (17/33) are mostly invisible.
  - Visibility and physical strength are confounded by design. A positive result says "stronger, mostly visible earlier exposure helps". It does not show that consciousness itself helps.

## 1. Measure

- **Target trials:** report-block, SOA-50 face trials with a seen (1) or unseen (2) response.
- **For each target trial**, over earlier showings of the same face (both blocks, session order):
  - D = number at SOA 67/83 − number at SOA 17/33;
  - T = total number of earlier showings, at any SOA, including 50.
- **Per subject:** OLS of seen (0/1) on D, an intercept, T and trial rank (rank among the subject's face trials in session order, scaled by 1/1000). The primary statistic is the slope on D, in probability per net strong showing.
- **Excluded rows:** 4 report-block face rows with a blank SOA (not counted in T) and 37 SOA-50 report trials without a response (not targets).
- **Why this is causal:** SOA order is randomised within face within cycle: each block runs in about 4 cycles, and within a cycle each face gets each SOA about once. Given T, D is therefore independent of image and of time.
  - Label-free check: the correlation of D with T is −0.004, and with rank −0.006.
  - The SD of D grows with T (0.93 at T < 5, 2.15 at T ≥ 30), so high-T trials weigh more in the slope. This adds no bias.
- **No identity dummies:** within a face, D builds up over the session, so face dummies absorb most of its variation. With dummies the residual SD of D is 0.80; without them it is 1.66. This was decided on label-free statistics only.
- **Group:** mean slope over 40 subjects, with a 95% t-interval.

## 2. Decision

| Verdict | Condition |
|---|---|
| EFFECT+ | CI lower bound > 0 (checked first: a CI such as (0.001, 0.010) is EFFECT+) |
| EFFECT− | CI upper bound < 0 |
| NO EFFECT | CI inside ±0.015 (±1.5 points per net strong showing) |
| INCONCLUSIVE | otherwise |

## 3. Calibration (run after sealing, before the real statistic; 300 runs, seed 20261130)

- **(a) Randomisation null on the real responses:** for each subject and face, with probability ½, swap strong and weak SOAs (17↔83, 33↔67) on all of that face's showings. Then recompute D and regress the real responses on it. The real D is never regressed on real responses during calibration.
  - This keeps |D|, T, the SOA-50 showings and the per-cycle SOA balance.
  - Label-free check: the correlation of null D with real D is −0.015 on average, and its SD is 1.685 (real 1.676).
  - History: the Fable pre-seal review rejected two earlier nulls before calibration.
    - A free within-subject permutation doubled the spread of D.
    - A within-face-quarter permutation left D almost unchanged (correlation 0.85 with real D), which would have leaked the answer.
- **(b) Fake-response null:**
  - subject rate U(0.2, 0.85);
  - linear session drift;
  - per-image logit offsets SD 0.8;
  - AR(1) streaks (ρ 0.3);
  - item-specific practice: logit +0.03 per earlier showing of the face, so it rises with T but not with D;
  - no effect.
- **(c) Planted:** as (b), plus 1.5 points per unit of centred D, on the real sequences.
- **PASS:** false EFFECT ≤ 5% in both (a) and (b), and EFFECT+ ≥ 80% in (c).

## 4. Calibration fallbacks (stated in advance)

- **None.** If calibration fails, the study stops at the gate (as the RT-gradient study did) and the real statistic is never computed.
- No change to covariates, the bound, the planted size or the interval after calibration. Any such change makes the study INVALID.

## 5. Secondary (descriptive, no decision)

- **No-report showings only:** for the 18 subjects who did the no-report block first, D is built from no-report-block showings only (report-block showings count in T but not in D). Visibility was never reported for those showings.
  - This D is constant within a face, so it is a between-face regressor with 40 clusters per subject: unbiased but noisy.
  - Only the mean and CI are reported, with no verdict.
- **Dropped from Fable's plan:** the "last same-face showing within 30 s" secondary, to keep one primary and one descriptive.

## 6. Limits

- **Strength vs visibility:** they are confounded (section 0).
- **Saturation:** every face has been shown many times, so a small effect may be saturated.
- **Effect type:** a linear probability slope assumes the effect is additive over the observed range of D.
- **Sensitivity vs criterion:** a positive could be item-specific criterion rather than sensitivity. Catch trials are not item-specific, so the design cannot separate the two.
