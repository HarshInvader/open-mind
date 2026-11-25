# Is "tracks the psychometric curve" a specific test of an awareness correlate? RESULTS (simulation)

**No site page or post** until the Cohen correspondence resolves (coordinator, 2026-11-25). Committed to the repo with the coordinator's clearance.

Prereg: `docs/prereg/2026-11-25_psych_criterion_sim.md`.
- **Seal 1:** 2026-11-25T11:40:06Z (prereg a2ad5b60…, script bdd127b8…). Never run: no calibration, no study. The pre-run review found both of its verdicts fixed by design.
- **Seal 2 (run):** 2026-11-25T11:44:42Z (prereg 0152c3e5…, script 471a7917…). Run 11:45–12:40Z, 17 cells × 1,000 studies, 25 subjects each, real report-block seen rates, 4 workers, nice 20. All 7 calibrated cells hit target (median part-(ii) t within 0.05).

## Sealed verdicts

- **Rule: RULE REJECTS A PURE AWARENESS SIGNAL AT STRENGTH t = 3.0.**
- **MSE test, by variant:**

| Variant | Verdict |
|---|---|
| logistic, uncorrected | SPECIFIC TO LINEAR TRUTH — **an artefact of the fit-failure fallback, see below** |
| logistic, df-corrected | SPECIFIC TO LINEAR TRUTH |
| quadratic, uncorrected | NON-SPECIFIC |
| quadratic, df-corrected | SPECIFIC TO LINEAR TRUTH |

## The rule: a pure awareness signal passes at most ~75% of the time, and less when weak or strong

| Cell | Pass | (i) n.s. | (ii) sig ↑ | (iii) sig ↑ | (iv) n.s. | median t (i–iv) |
|---|---|---|---|---|---|---|
| AW t=3.0 | **0.33** | 0.95 | 0.78 | 0.53 | 0.93 | 0.2, 2.8, 2.2, 0.4 |
| AW t=4.49 (N2 strength) | 0.75 | 0.94 | 0.98 | 0.90 | 0.89 | 0.3, 4.4, 3.4, 0.7 |
| AW t=6.0 | 0.74 | 0.92 | 1.00 | 1.00 | 0.81 | 0.5, 6.0, 4.9, 1.1 |
| AW t=7.5 | **0.41** | 0.86 | 1.00 | 1.00 | 0.48 | 1.0, 7.5, 6.9, 2.1 |
| SIG (sensory, psychometric shape, no awareness) | 0.75 | 0.95 | 0.99 | 0.88 | 0.89 | 0.3, 4.3, 3.4, 0.6 |
| LIN | 0.00 | 0.01 | 0.99 | 0.99 | 0.01 | 4.6, 4.4, 4.4, 4.5 |
| SAT (P1-like) | 0.00 | 0.01 | 0.99 | 0.02 | 0.95 | 4.5, 4.5, 0.0, 0.0 |
| NULL | 0.00 | 0.96 | 0.03 | 0.03 | 0.95 | — |

- **Weak end (t = 3):** the failure is power. Part (iii) reaches significance in only 53% of studies, because the seen rate rises less from 50 to 67 ms (0.52 → 0.87) than from 33 to 50 (0.04 → 0.52). The sealed verdict fires here, but the reason is low power, not strictness.
- **Strong end (t = 7.5):** the failure is strictness. Part (iv) "no difference 67 vs 83" fails in 52% of studies, because the seen rate still rises there (0.87 → 0.94) and a strong signal detects it.
- **Plain reading:** even a signal that is nothing but awareness by construction fails the rule in a quarter or more of studies at every strength tested. Failing the rule is weak evidence against an awareness correlate.
- **Specificity:** the rule cleanly rejects linear and saturating sensory signals (0%). It passes a purely sensory signal shaped like the psychometric curve exactly as often as awareness (0.75 vs 0.75), as the mixture identity predicts.

## Stimulus slopes (descriptive)

| Cell | Pass |
|---|---|
| MIX r = 0.05 | 0.66 |
| MIX r = 0.1 | **0.48** |
| MIX r = 0.15 | 0.22 |
| MIX r = 0.2 | 0.11 |
| MIX r = 0.3 | 0.01 |
| MIX r = 0.5 | 0.00 |
| AWSAT c = 0.25 | 0.55 |
| AWSAT c = 0.5 | 0.16 |
| AWSAT c = 1.0 | 0.00 |

- A real awareness step plus a linear stimulus slope of **one tenth** of it already halves the pass rate. The same holds for a saturating stimulus term of half the awareness step: the signal is mostly "ruled out".
- So the rule rejects any awareness-carrying signal that also grows measurably with stimulus strength. The VAN's report-block profile (t 4.48, 8.68, 2.38, −2.18) is of that kind.

## The MSE test

| Cell | logistic uncorrected | logistic df-corr | quadratic uncorrected | quadratic df-corr |
|---|---|---|---|---|
| NULL (pure noise) | **1.00** | 0.00 | **1.00** | 0.01 |
| LIN | 0.47 (0.99 among valid) | 0.00 | **1.00** | 0.01 |
| AW t=4.49 | 0.99 | 0.01 | 1.00 | 0.00 |
| AW t=7.5 | 1.00 | 0.98 | 0.99 | 0.00 |

- **Uncorrected MSE (either model): pure noise is called "nonlinear" in 100% of studies.** Under that reading, their t = 2.29 says nothing about nonlinearity.
- **The sealed "SPECIFIC" for uncorrected logistic is an artefact:**
  - On LIN, 528 of 1,000 studies had ≥ 3 subjects whose logistic fit failed on a noisy straight line, and the pre-stated fallback counts those studies as "not nonlinear".
  - Among the 472 valid studies, 99.2% called "nonlinear". The fallback was written for rare optimiser failures and did not anticipate this.
  - This is reported as sealed, with the reason.
- **df-corrected MSE:** specific, but nearly blind. A pure awareness signal at N2 strength is called "nonlinear" in only 1% (logistic) or 0% (quadratic) of studies.
  - So their significant t = 2.29 fits the uncorrected reading, under which it is uninformative, much better than the corrected one.
  - Which reading they used is a question for the authors.

## What this does and does not mean

- **Means:** under Cohen et al.'s pre-registered rule and N = 25, "fails the four-part rule" is weak evidence against an awareness correlate:
  - a pure-mixture signal fails in 25–67% of studies;
  - a signal with a small stimulus slope added fails most of the time.
  - The rule also cannot tell awareness from a sensory nonlinearity shaped like the psychometric curve.
- **Does not mean:** that the VAN, P3b or N2 is or is not an awareness correlate. The question is the criterion, not the signals.
- **Limits:** their nonlinear model and MSE definition are unknown; gamma gains with no subject × SOA noise (the case most favourable to the rule passing); report seen rates stand in for no-report awareness.
