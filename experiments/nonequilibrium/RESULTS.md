# Non-equilibrium (time-irreversibility) EEG measures vs the spectrum: results

Task #41. Agent: mind-ne. Pre-registration: `docs/prereg/2026-11-18_nonequilibrium_vs_spectrum.md`, sealed 2026-11-18T21:51:44Z. Amendment 1 (a 64-channel file) was sealed at 23:29:05Z. Amendment 2 (a gate bug fix, with disclosure) was sealed at 2026-11-19T01:05:26Z.

## Verdict

- **H-NE-HO (our higher-order variant): NOT SUPPORTED.** No contrast met the three counting conditions. `tra_x` is real and spectrum-free: in wake vs N3 it separates the states (held-out AUC 0.70) and passes the surrogate gate (share kept 0.01). But it adds nothing over the exponent plus band powers (ΔAUC +0.0005, Holm p 0.55). It does not separate REM (dreaming) from N3 at all (AUC 0.50).
- **H-NE-2 (published second-order form): does not replicate on scalp EEG.** Single-measure held-out AUC was 0.43 to 0.56 in all four contrasts, against the 0.70 mark. It adds nothing beyond the spectrum. In Chennu, phase surrogates separate the states better than the real signal does (share kept 5.9). This fits the prediction that the measure is cross-spectral, though the gate share is unstable when real AUC is near 0.5.
- **Reading.** Time asymmetry in waveform shape tracks being awake (wake vs N3), not being conscious (REM ≈ N3). So it behaves like an arousal or waveform marker, such as alpha/mu shape, eye movements or muscle, not a consciousness marker. The deeper-sounding "arrow of time" measures add nothing here that the spectrum lacks.

## Numbers

Held-out = 5-fold subject-held-out logistic regression. Δ = AUC(baseline + measure) − AUC(baseline), where baseline = 1-40 Hz exponent + 6 relative band powers. p = within-subject Freedman-Lane permutation, 1000. CI = 1000-resample subject bootstrap. Holm is over the 8 primary tests.

| Contrast | Subjects | Baseline AUC | `tra_x` alone | `tra_x` Δ [95% CI], Holm p | `tra_x` gate share | `ne2` alone | `ne2` Δ, Holm p |
|---|---|---|---|---|---|---|---|
| Sleep-EDF W vs N3 | 60 | 0.996 | 0.701 | +0.0005 [−0.0000, 0.0012], 0.55 | 0.01 (pass) | 0.482 | −0.0002, 1.0 |
| Sleep-EDF REM vs N3 | 60 | 0.990 | 0.496 | +0.0005 [−0.0004, 0.0015], 0.55 | n/a (AUC ≈ 0.5) | 0.464 | −0.0002, 1.0 |
| Chennu baseline vs moderate propofol | 20 | 0.838 | 0.634 | +0.002 [−0.014, 0.017], 1.0 | 0.07 (pass) | 0.560 | −0.032, 1.0 |
| ds005620 awake vs sed2 | 15 | 0.990 | 0.429 (reversed) | 0.000 [−0.002, 0.002], 1.0 | n/a | 0.431 | −0.0006, 1.0 |

Secondary measures, uncorrected:
- `ptir_x`: W vs N3 single AUC 0.63, Δ 0.0000, p 0.011 (the CI spans zero); Chennu single AUC 0.65, Δ −0.001.
- `tra_xi` (IAAFT excess) follows `tra_x`, with Δ ≤ 0.002 everywhere.
- LZ again adds ≤ 0.006 everywhere.

## Power (P2) and what the test could catch

P2 passed its false-positive check (FPR ≤ 0.1 at d = 0 in every contrast). Power at a planted effect of d = 0.2:
- Sleep-EDF: 80% (W vs N3) and 50% (REM vs N3), with mean Δ 0.0002 to 0.0003. Both reached 100% at d = 0.4.
- Chennu: 10% at d = 0.4.
- ds005620: 0% at d = 0.4.

So the sleep contrasts could catch tiny increments. The two propofol contrasts are underpowered: 20 and 15 subjects, with baselines at 0.84 and 0.99. Their null results do not close the route for propofol. This was stated in Amendment 2 before any NE outcome was seen.

## Planted checks

P1 synthetic checks passed (`planted.json`):
- a Gaussian process gives no `tra_x`;
- planted asymmetry is recovered monotonically (0.117 at full strength), and its phase surrogate drops to 0.0004;
- one-way Gaussian coupling gives `ne2` 62× the symmetric value, which surrogates keep (they are second-order), while `tra_x` stays at 0.

## Not checked or not computed

- **Arousal-adjusted secondary (`tra_x` over spectrum + EMG + EOG): not computed.** 194 of 8372 Sleep-EDF epochs have no EMG value, and the sealed code skips the test if any are missing. Because `tra_x` added nothing even without arousal covariates, this cannot change the verdict.
- **Gate for `tra_xi`: not computed.** That measure was stored only on real rows; see Amendment 2.
- **Sleep-EDF `ne2` is one channel pair (Fpz-Cz × Pz-Oz).** The published work uses source-level or high-density data and model-based estimators (OU fits). Our `ne2` is the model-free time-shifted correlation form (Camassa 2024). A failed replication here is about scalp EEG with these estimators, not about the theory as such.
- **ds005620:** 20 subjects extracted; 15 had at least 2 clean epochs in each class. None were unreadable, and no file was skipped after Amendment 1.

## Hypotheses table

| ID | Prediction | Result |
|---|---|---|
| H-NE-HO | `tra_x` higher in conscious-side state, adds ≥ 0.01 AUC over spectrum, passes gate, in ≥ 3/4 contrasts | NOT SUPPORTED (0/4) |
| H-NE-2 replicate | `ne2` held-out AUC ≥ 0.70, conscious side higher | No (0/4; AUC 0.43-0.56) |
| H-NE-2 adds | `ne2` Holm p < 0.05, ΔAUC ≥ 0.01 | No (0/4) |
| H-NE-2 gate (predicted fail) | share kept > 0.5 | Fails in all 4. Chennu 5.9, ds005620 0.97; the two Sleep-EDF shares are undefined because real AUC ≈ 0.5 |

Files: `results.json`, `planted.json`, `planted2.json`, `ledger_rows.csv`, `run.log`.
