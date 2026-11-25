# Pre-registration: is "tracks the psychometric curve" a specific test of an awareness correlate? (simulation)

Agent: Open Mind thread   Date: 2026-11-25   Script: `experiments/psych_criterion/criterion_sim.py`   Source: Fable round 16, item 3

- **Zero new bytes.** Simulation only. Each subject's report-block seen rate and trial count per SOA come from `experiments/cohen_fixed_soa/trial_counts.csv` (behaviour, 40 subjects; no EEG is read).
- **Hold:** this tests Cohen et al. 2024 directly. Results stay out of public posts and the site until the coordinator clears them.

## 0. The claim and prior art (texts in `datasets/local/r16_priorart/`)

- **Del Cul, Baillet & Dehaene 2007** call "tracks the seen-rate curve across SOA" and "differs between seen and unseen at a fixed SOA" two *independent* criteria. They test the first with one contrast (the 33→66 increase versus the flanking increases).
- **Cohen, Dembski, Ortego, Steinhibler & Pitts 2024** (Cereb Cortex, doi:10.1093/cercor/bhae415) pre-registered a four-part rule: "(i) little or no difference between the 17 and 33 ms SOAs, (ii) a significant difference between the 33 and 50 ms SOAs, (iii) a significant difference between the 50 and 67 ms SOAs, and (iv) little or no difference between the 67 and 83 ms SOAs". They state that "signals showing nonbifurcated (e.g. linear) patterns across SOAs can be ruled out".
  - **N2, no-report:** t(24) = 0.24, 4.49, 2.82 and 0.86 for the four parts.
  - **VAN, report:** t(24) = 4.48, 8.68 and 2.38, then a decrease (t = 2.18). On this basis the VAN was judged "neither linear nor bifurcated".
  - **Post hoc test:** a "linear and nonlinear regression on each individual participant's data", comparing the mean square error (MSE): nonlinear 0.70 vs linear 1.17, t(24) = 2.29, P = 0.026. The nonlinear model is not named.
- **Mixture identity:** the SOA mean is p(SOA)·μ_seen + (1 − p)·μ_unseen. Any signal with a seen/unseen difference and flat within-class means follows the seen-rate curve. Retter et al. 2020 state this to argue for all-or-none responses. No paper we found audits the criterion with it. (Search: all 13 papers citing Cohen 2024; about 500 citing Del Cul 2007, screened by title.)
- **Our own sealed result:** the VAN separates seen from unseen at fixed SOA 50 in held-out subjects (`experiments/cohen_fixed_soa/RESULTS.md`).

## 1. Design

- **Study:** 25 subjects, drawn with replacement from the 40-subject pool.
  - Per subject and SOA, the seen count is binomial(n, p), using that subject's real trial count n and seen rate p.
  - Trial noise SD is 1, so each SOA mean gets noise N(0, 1/√n).
  - Each effect has a per-subject gain, gamma with mean 1 and CV 0.5. There is one gain per subject across SOAs and no subject × SOA noise beyond trial noise. This is the case most favourable to parts (i) and (iv).
  - k = SOA index 0…4.
- **Cells:**

| Cell | Mean at an SOA | Strength (median part-(ii) t) | Role |
|---|---|---|---|
| NULL | 0 | — | false positives |
| AW_t | B·g·(seen share) | t ∈ {3, 4.49, 6, 7.5} | **primary:** pure awareness signal (mixture identity) across strengths |
| LIN | B·g′·k | 4.49 | linear stimulus signal |
| SAT | B·g′·min(k, 2)/2 | 4.49 | sensory, rises to 50 ms then flat (P1-like) |
| SIG | B·g′·(group seen rate) | 4.49 | sensory sigmoid with the psychometric shape, no awareness |
| MIX_r | AW_4.49 + r·B·g′·k, r ∈ {0.05, 0.1, 0.15, 0.2, 0.3, 0.5} | not equated | awareness plus a linear stimulus slope |
| AWSAT_c | AW_4.49 + c·B·g′·min(k, 2)/2, c ∈ {0.25, 0.5, 1} | not equated | awareness plus a saturating stimulus term (closer to the report VAN's shape) |

- **Calibration:**
  - For each AW_t, LIN, SAT and SIG, B is set by bisection on log B in [0.001, 10], up to 30 steps, so that the median part-(ii) t over 400 calibration studies hits its target within ± 0.15. The calibration seed stream is separate from the run.
  - MIX and AWSAT use AW_4.49's B.
- **Studies:** 1,000 per cell. Seed 20261206.

## 2. Tests (per study)

- **RULE** (paired t, two-sided, α = .05, df 24):
  - parts (i) and (iv) need p ≥ .05;
  - parts (ii) and (iii) need p < .05 with an increase.
  - A study passes when all four hold.
- **MSE test:** per subject, linear and nonlinear fits to the 5 SOA means; a paired t across subjects (linear MSE − nonlinear MSE); "nonlinear" if p < .05 with the nonlinear MSE lower.
  - Their model and their MSE definition are not stated, so there are four variants: nonlinear = 4-parameter logistic (best of 18 starts) or quadratic, × MSE = uncorrected SSE/5 or df-corrected SSE/(5 − parameters).

## 3. Decision

| Verdict | Condition |
|---|---|
| INVALID | AW_4.49, LIN, SAT or SIG misses calibration tolerance |
| RULE PASSES PURE AWARENESS SIGNALS AT EVERY TESTED STRENGTH | every calibrated AW_t passes in ≥ 50% of studies |
| RULE REJECTS A PURE AWARENESS SIGNAL AT STRENGTH t = X | some calibrated AW_t passes in < 50%; X is the smallest such t |

- An AW_t other than 4.49 that misses tolerance is reported as unreachable and left out.
- **Why this is the primary test:** parts (i) and (iv) accept a null, so whether a signal that is pure awareness by construction passes depends on its strength. The seen rate still rises from 67 to 83 ms (group 0.87 → 0.94) and from 17 to 33 ms (0.01 → 0.04). If a strong pure-awareness signal fails, then "fails the rule" is not evidence against an awareness correlate. Cohen's P3b in report failed part (iv), and the P3b is strong.
- **MSE verdict per variant:** NON-SPECIFIC if LIN is called "nonlinear" in ≥ 50% of studies, else SPECIFIC TO LINEAR TRUTH. The NULL cell's "nonlinear" rate is reported beside it.
- **Descriptive (no verdict):**
  - the smallest r at which MIX passes in < 50% (the reviewer's hand estimate before the run was 0.15–0.2);
  - the AWSAT pass rates;
  - the SIG and SAT pass rates;
  - per cell: the share meeting each part, the median t per part, the MSE "nonlinear" rates and median t per variant, and logistic fit failures.

## 4. Fallbacks and disclosures (stated before calibration)

- **A required cell misses calibration:** INVALID. There is no re-tuning, and the grids and tolerance stay unchanged.
- **Logistic fit failures:** a subject whose fit fails at every start is dropped from that study's logistic MSE tests. If ≥ 3 subjects fail, those variants count as "not nonlinear".
- **Compute:** at most 4 workers, nice 20.
- **Re-seal disclosure:**
  - A first version was sealed at 11:40:06Z (hashes a2ad5b60…, bdd127b8…) and **never run**: no calibration and no study.
  - A pre-run review then found its two verdicts fixed by design. (a) Its VAN-like ratio r = 0.5 came from the VAN's 17→33 t, which part (i) re-tests, so "RULE EXCLUDES" only restated a published t. (b) The uncorrected-MSE test with a nested model can never favour linear, so "NON-SPECIFIC" was arithmetic, and with a df correction it flips.
  - Changes: the primary outcome became the pure-awareness strength sweep; r = 0.5 was dropped as a verdict; AWSAT cells were added; the MSE test now has four variants; the calibration seed tag changed (it overlapped one run stream).
- **Other disclosures:**
  - The prior-art reviewer ran a throwaway simulation (not this code: linear truth, 25 subjects, 4-parameter logistic). The uncorrected MSE test called "nonlinear" in 100% of runs, and the four-part rule passed linear truth in 0–5%.
  - The pre-run reviewer computed deterministic expectations, with no studies run. Uncorrected MSE t on line-plus-noise vectors is about 4.8 (logistic) and 3.5 (quadratic); df-corrected, about −2.1 and 0.2. AW's noise-free part-(ii) ceiling is t ≈ 8.27, and the part-(iv) ceiling is about 4.9.
  - The author's pilot timed one study (0.56 s), ran unit checks on hand-made vectors, and printed the group seen rates (0.010, 0.038, 0.523, 0.873, 0.942). No pass rates were printed.
- Any other change after sealing makes the study INVALID.

## 5. What a result would and would not mean

- **RULE REJECTS A PURE AWARENESS SIGNAL AT t = X:**
  - **Means:** a signal that is by construction nothing but the seen/unseen mixture fails the rule once its strength reaches X, so failing the rule is not evidence against an awareness correlate at that strength.
  - **Does not mean:** that any signal Cohen et al. dismissed is an awareness correlate.
- **RULE PASSES … AT EVERY TESTED STRENGTH:** the rule is not too strict for pure-mixture signals up to t = 7.5. Its dismissals then rest on stimulus-driven variance (see MIX, AWSAT), which the mixture identity says is a separate question.
- **MSE variants:** if only the uncorrected variants are NON-SPECIFIC, their t = 2.29 is uninformative under that reading, and its meaning depends on a definition the paper does not give (to be asked of the authors).
- **Limits:**
  - Their nonlinear model is unknown.
  - Gamma gains and Gaussian noise are assumed, with no subject × SOA noise.
  - Report-block seen rates stand in for no-report awareness.
  - This is a statement about the rule under simulation, not about the N2's, P3b's or VAN's actual role.
