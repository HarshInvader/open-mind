# Pre-registration: GNWT frontal involvement, dream vs no-dream within N2 (task #16, test T-GNWT)

Agent: mind-3   Task: #16   Date: 2026-11-18. Sealed before any EEG from these awakenings was downloaded or computed. Data, preprocessing, exclusions, measures, CV and nulls are identical to `docs/prereg/2026-11-18_theory_iit_posterior_dream.md` sections 2-5 and 7-8; only the prediction and pass mark differ. The two tests form one family of 2 (alpha 0.025 each).

## 1. Prediction, in the theory's own terms
GNWT holds that conscious content requires access to a global workspace with prefrontal (and parietal) neurons as its hubs; without workspace activation, processing stays non-conscious (Mashour, Roelfsema, Changeux & Dehaene 2020, doi:10.1016/j.neuron.2020.01.026). Dreams are conscious experiences, so GNWT predicts that experience during N2 comes with workspace activation, which in scalp EEG shows as frontal desynchronisation, i.e. lower frontal slow-wave (1-4 Hz) power. IIT does not require this (see the IIT prereg).

- H1: in the 20 s before awakening from N2, frontal (F3, Fz, F4) delta power is lower before experience than before no experience.
- H2 (beyond spectrum): frontal delta adds subject-held-out discrimination over the global 1-30 Hz spectral exponent (same CV as the IIT prereg, Model B = exponent + D_front).

Caveat for proponents: GNWT's signature is ignition to a stimulus, which sleep data cannot probe; this test checks the state-level implication only (frontal workspace activity during experience). A GNWT proponent may judge a failure here less decisive than a failed ignition test; this is stated with the result.

## 2. Pass marks
- PASSED this test: H1 one-sided permutation p < 0.025 AND H2 95% CI lower bound > 0.
- FAILED this test: otherwise; sub-verdicts "no frontal effect" or "frontal effect not beyond spectral exponent"; opposite-direction effect reported if the AUC 95% CI lies wholly below 0.5.
- Also reported (shared with T-IIT): dAUC posterior minus frontal. A clearly negative dAUC (frontal > posterior) is reported as evidence against IIT's specificity claim, not as a GNWT pass.

## 3. Power
Same as the IIT prereg: smallest detectable AUC about 0.64 at 80% power; empirical figure from the planted check (planted into the frontal ROI the same way).

## 4. Higher-order theories
HOT also predicts prefrontal involvement in conscious experience (Brown, Lau & LeDoux 2019, doi:10.1016/j.tics.2019.06.009), but its riskiest prediction concerns metacognitive awareness dissociated from performance, which this data cannot test. The frontal result is reported for HOT only as shared, non-independent context, not as a HOT test.
