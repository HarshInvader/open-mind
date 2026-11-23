# Pre-registration: does awareness add metacognition beyond a single-evidence observer? (Rausch 2016 data, 2026-11-23)

## Question
Thorat & Chopra (2026, arXiv:2609.33366) list "knowing when you are right at matched first-order performance" as a functional marker of awareness. The evidence for it rests mainly on one blindsight patient (Persaud et al. 2011, GY). We test it in healthy observers:

> At a fixed stimulus contrast, does confidence track accuracy better on high-visibility trials than a single-evidence observer predicts?

**Why the null matters.** If confidence and visibility are both noisy read-outs of the same evidence sample, then splitting trials by visibility restricts the range of that evidence. That alone makes "seen" trials show higher confidence-accuracy sensitivity, with no special role for awareness. In our synthetic gate, the null observer showed a seen-minus-unseen AUROC2 gap of about +0.048. The test is therefore the excess over that null, not the raw gap.

## Prior art (opened)
- **Jachs et al. 2015** (10.1037/xhp0000026, abstract) and **Mei et al. 2019** (bioRxiv 607069, readme): awareness affects type-2 sensitivity much less than type-1. These are the Soto-lab datasets, so they are excluded as already analysed for this question.
- **Rausch & Zehetleitner 2016** (10.3389/fpsyg.2016.00591, full text): compares meta-d_a of the visibility and confidence scales by contrast. It does not test confidence sensitivity split by visibility, so this question is not answered there.
- **Fable novelty read (2026-11-23):** incremental but useful. No accuracy-matched seen-vs-unseen test against a single-evidence null was found.

## Data
- **Source:** Confidence Database (Rahnev et al. 2020, OSF s46pr), file `data_Rausch_2016.csv` (https://osf.io/download/zy43r/).
- **Design:** 20 participants; low-contrast grating orientation; continuous confidence and visibility (-12 to 12) on every trial, with rating order counterbalanced (ScaleOrder).
- **Exclusions:**
  - training trials (Training == 1);
  - contrast 0, which has no correct answer;
  - rows that fail to parse, have non-finite values, or have Accuracy outside {0, 1}.
- **Before sealing**, only the column header and the readme were seen. No trial values were looked at.

## Model and statistic (`experiments/metacog_awareness/run_rausch.py`, hashed with this file)
- **Preprocessing:** confidence and visibility are z-scored within subject.
- **Primary statistic:** a logistic regression of accuracy on z(conf), z(vis), z(conf)×z(vis), contrast dummies and subject dummies. The statistic is the coefficient on z(conf)×z(vis).
- **Single-evidence null** (refitted to these data):
  - evidence e ~ N(d/2, 1), with d estimated per subject × contrast from accuracy;
  - visibility = |e| + gamma·d + sv·N(0,1);
  - confidence = |e| + sc·N(0,1);
  - (sc, sv, gamma) fitted by simulated method of moments on four statistics: the within-cell correlations conf-accuracy, vis-accuracy and conf-vis, and the within-subject vis-contrast correlation.
- **Marginal matching:** simulated confidence and visibility are mapped by rank onto each subject's own observed rating values, so the null reproduces every subject's floors, ceilings and ties.
- **Null distribution:** 1000 simulated datasets at the fitted parameters, using the real trial design.
- **Outputs:**
  - one-sided p (share of null ≥ observed) and the coefficient excess;
  - the interpretable effect size (AUROC computed with tie-averaged ranks): AUROC2 gap excess per subject = (AUROC2 of confidence in the high-visibility half minus the low-visibility half, within subject × contrast, averaged), minus the null mean gap. Its 95% CI comes from a 2000-sample subject bootstrap.

## Gate (passed before sealing; `power_gate.py`, `power_gate.json`)
The test was run on synthetic data with the same design, n = 20 and 63 trials per contrast. The planted effect was confidence noise that grows on low-visibility trials, scaled to an AUROC2 excess of 0.05.

| Condition | Rejection rate | Target |
|---|---|---|
| Correctly specified null | 0.05 | ≤ 0.05 |
| Heavy-tailed (t3) misspecified null | 0.04 | — |
| Planted effect | 1.00 | ≥ 0.80 |

The analysis script also gave the expected verdicts on one synthetic null file ("refutes") and one planted file ("supports").

**Gate 2** (after Fable's pre-seal review; `gate2.py`, `gate2.json`) runs the exact analysis code with 200 null simulations per dataset, 60 datasets per condition, including bounded, floored and tied ratings. Conditions:
- null;
- t3 null;
- floored null (visibility censored at each subject's 35% quantile, confidence at 15%, on the -12..12 scale, rounded to 0.1);
- floored planted, full and half size.

Pass requires, in every null condition, "supports" ≤ 0.05 and void ≤ 0.10; and "supports" ≥ 0.80 for the floored planted condition.

**Gate 2 results (passed):**

| Condition | Supports | Refutes | Void | Mean excess |
|---|---|---|---|---|
| Null | 0.017 | 0.37 | 0 | 0.003 |
| t3 null | 0.017 | 0.43 | 0 | 0.000 |
| Floored null | 0.017 | 0.32 | 0 | 0.002 |
| Floored planted (excess ~0.05) | 0.98 | 0 | 0.017 | 0.063 |
| Floored planted, half size (~0.03) | 0.42 | 0.03 | 0 | 0.031 |

**Disclosed:** the first gate-2 attempt was stopped after 12 datasets. The null fit was not moving (sc stuck at its start value 1.000; 2 of 12 nulls void), because scipy's Nelder-Mead takes a 0.00025 first step from a zero start coordinate and the rank-mapped loss is step-shaped. Fix: an explicit initial simplex with 0.3 steps. Gate 2 was then rerun from scratch, giving the table above. Fable's final pre-seal check (2026-11-23) found moment z centred near 0 in all nulls (largest |z| 2.46).

**What this power means:** at a true excess of 0.03, "supports" fires only 42% of the time, and a true null yields "refutes" only 32-43% of the time. **Inconclusive is the most likely outcome**, and it will be reported as such.

## Decision rule (primary, all subjects)
- **Void:**
  - fewer than 15 subjects with a computable gap; or
  - the fitted null misfits, meaning any of the four moments lies more than 3 null SDs from the observed value.
- **Supports** (rejects the single-evidence null; consistent with awareness-linked metacognition): p < 0.05 and AUROC2 gap excess ≥ 0.03. This means only that this one null is rejected.
- **Refutes** (no awareness-linked metacognition beyond a single-evidence observer at this effect size): the upper 95% CI bound of the AUROC2 gap excess is below 0.03.
- **Inconclusive:** anything else.
- **Void is terminal.** If the null misfits on the real data, we will not refit or change the null without a new, separately sealed pre-registration. (A real effect can itself push moment z up; the planted maximum was 3.28.)

## Secondary (reported, not gating)
- The same analysis, run separately for each rating order (ScaleOrder), as a check on order effects. ScaleOrder is asserted to be constant within each subject.
- The same analysis without the lowest contrast (2.2%), where accuracy is near chance.
- Dropped-row counts (training, contrast 0, unparsable) are printed and saved.

## Prediction
Inconclusive or refutes. The excess is small, in line with Jachs 2015.

## Limits stated in advance
- **One lab and n = 20.**
- **"Single-evidence" is one specific null.** A different shared-evidence model (for example, confidence that also reads visibility, as in Rausch's later WEV models, which we have not checked) could change the null.
- **Visibility and confidence are reports by the same person**, so shared response style is not fully removed.
- **This is not blindsight.** These are healthy observers near threshold, not a lesioned field.
