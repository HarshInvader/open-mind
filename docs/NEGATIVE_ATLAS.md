# Negative atlas

Closed routes, each with the effect size the test could have caught. Empty until the first tests land.

## T1 settling-window theory: posterior OFF-period recency does not predict N2 dream reports (task #31, 2026-11-18)

- **Route closed:** "the time since the last posterior OFF-period before waking decides whether an N2 awakening yields experience", in its strong form (odds ratio of 2 or more per within-subject SD of log recency, beyond delta power, slow-wave count, sigma, beta, spectral exponent, clock time and awakening index).
- **Data:** DREAM Tononi Serial Awakenings (Wisconsin, 257-channel), 237 of 287 N2 awakenings (97 experience, 93 no experience, 47 without recall), 35 subjects. Sealed prereg `experiments/t1_dream/PREREG.md` (sha256 5272a976..., 2026-11-18T11:09:27Z).
- **Result:** recency coefficient 0.081 (90% CI -0.177 to 0.349; one-sided p 0.32). The CI lies inside ±0.693 (OR 2), so the sealed rule gives REFUTED. Timing beyond count: +0.015, p 0.45. Posterior minus frontal: -0.134, p 0.69. Without recall vs no experience: 0.037, p 0.40.
- **What it could catch:** at this sample the pipeline gave PASS in 70% of synthetic datasets with a true OR 2 effect and REFUTED in 88% with none (`power_realised.json`).
- **Not closed:** recency effects weaker than OR 2; true (intracranial) OFF-periods; T1's 250 ms hold time itself, which a 10 s window cannot test. The scalp OFF proxy (half-wave plus 25-45 Hz suppression) found no posterior OFF-period in 38-47% of windows.
- **Details:** `experiments/t1_dream/RESULTS.md`.

## LZ complexity adds nothing over the spectrum in sleep (mind-2, 2026-11-18)
Sleep-EDF, 45 subjects, subject-held-out. LZ adds no AUC over the exponent plus 6 band powers. Wake vs N3: +0.0004 [-0.0003, 0.0012], p = 0.19. REM vs N3: -0.0002, p = 0.16. Over the exponent alone, wake vs N3: +0.007, below the 0.01 mark. LZ fails the surrogate gate: 86% of phase-randomised wake surrogates are called awake, and 97% of its separation is spectral. Phase-normalised LZ carries no stage information (AUC 0.47-0.48). Detectable effect: P2 had 85% power at delta AUC 0.0005 (W vs N3). Caveat: the W vs N3 baseline is at ceiling (0.988-0.996). Propofol sets (ds005620, Chennu) are not yet run. Details: `experiments/lz_slope/RESULTS.md`, `experiments/surrogate_gate/RESULTS.md`.
