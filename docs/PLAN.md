# Open Mind: research plan

**Aim for 2027:** the most accurate theory of human consciousness we can find or build, judged by how much of the constraint ledger it explains and how well its sealed predictions do on data it never saw. All current theories may be wrong, so building our own theory is part of the plan, not an afterthought. **Aim for the next months:** the red-teamed benchmark (Fable puts it at 50-60%), which shows which published measures survive once the EEG spectrum is controlled.

The work runs in waves. The lead reviews each wave: what to drop, what to escalate, what to try next. Fable is used sparingly, at most once per night, for a second opinion on the overall direction. Its one review is saved as `docs/fable_review_N.md`.

## The question tree

Every approach answers one of these:

1. **Is there a "level of consciousness" signal beyond the spectrum?** If no measure beats the 1-40 Hz spectral exponent zero-shot, the level-measure programme is in trouble, and the plan moves to content (L3) and dissociations.
2. **Does any measure get the dissociations right?** These are ketamine, REM, and dream vs no-dream awakenings. This is L2, and the decisive rung.
3. **Do the theories' signature predictions survive analytic flexibility?** This is the COGITATE multiverse.
4. **Do the theory-derived measures measure what the theory says?** Examples: Φ proxies on networks of known Φ, and ignition detectors on simulated ignition.

## Approach portfolio

| # | Approach | Question | Decisive outcome | Kill criterion | Wave |
|---|---|---|---|---|---|
| A1 | Dataset audit plus ground-truth grading | all | at least 4 qualifying datasets across 3 families | under 3 families: rescope R to sleep plus anaesthesia | 1 |
| A2 | Leak-proof splits plus test ledger | all | a dry run catches a planted leak | (tooling) | 1 |
| A3 | Surrogate gate (phase-randomised, spectrum-matched) | 1 | each measure passes or fails | a measure that calls surrogates conscious is barred | 1-2 |
| A4 | LZ vs spectral exponent on Sleep-EDF | 1 | ΔAUC of LZ over the slope, with a permutation CI | ΔAUC CI includes 0 at stated power: LZ goes to the atlas | 1-2 |
| A5 | Φ proxies on networks of known Φ (PyPhi) | 4 | rank correlation with true Φ | ρ < 0.5 under EEG-like noise: proxy barred from brain data | 1-2 |
| A6 | Zero-shot transfer of 8-10 measures across families | 1 | AUC ≥ 0.80 in every family | none passes: write the "no universal level measure" result | 2 |
| A7 | Dream vs no-dream within stage (ds005620, DREAM) | 2 | held-out AUC above chance with a CI | null at stated power | 2 |
| A8 | Ketamine and REM classification by every measure | 2 | each measure's call vs the report | (descriptive; feeds the scoreboard) | 2 |
| A9 | Simulated ignition (neural-mass model) and detector recovery | 4 | the detector separates ignition on/off at COGITATE-like SNR | if it cannot, COGITATE ignition claims are underpowered | 2-3 |
| A10 | Reproduce COGITATE iEEG decoding | 3 | match the published numbers | document the mismatch | 3 |
| A11 | Sealed multiverse on COGITATE (offset ignition, posterior synchrony) | 3 | the share of variants supporting each theory | (reported whole) | 3 |
| A12 | Resting EEG → PCI (Maschke 2024) out of sample | 1-2 | prediction holds on new subjects | fails: PCI stays TMS-only | 3 |
| A13 | Red team every positive | all | survives or drops one ladder level | (always) | every wave |
| A14 | Prediction registry for COGITATE exp 2 / INTREPID | 3-4 | hashed before release | (prospective) | 2-3 |

## Testing the theories directly, and our own

The scoreboard should hold our own results, not only the literature's. Two tracks:

**T. Each theory's own prediction on open data.** For every theory on the scoreboard, encode at least one prediction that the theory's proponents would accept as risky and that open data can test. Seal it, run it on held-out data, and record pass or fail on the scoreboard as *our* result. Examples:
- IIT: posterior complexity or integration should track experience when frontal activity does not (dreaming vs no-dream; ketamine).
- GNWT: a frontal "ignition" signature should be absent in experience without report and present at both onset and offset of a percept.
- HOT: prefrontal signals should track confidence or awareness separately from performance.
- Predictive processing: mismatch responses should change with conscious state in a specific direction.
- Entropic brain: complexity should rise under psychedelics beyond what the spectrum explains.

Theories already strained by COGITATE are re-tested too, because a different dataset can strain or rescue them.

**H. Our own hypotheses.** Any agent may propose a new hypothesis when the data suggest one. A hypothesis counts only if:
1. it is written down with the result that would refute it, and hashed before testing;
2. it is formed on development data and tested on held-out subjects or a different dataset;
3. it beats the spectral baseline and the best rival theory's measure;
4. it passes a planted-answer check and then a red team.

Hypotheses that fail go in the negative atlas like everything else. Leads worth trying, all of them untested:
- direction of information flow (posterior → frontal vs frontal → posterior) as a state marker independent of spectral slope;
- whether dream reports track posterior activity that the spectrum does not explain;
- whether measures from different theories agree on the hard cases. Where they disagree is where the theories can be told apart.

| # | Approach | Decisive outcome | Wave |
|---|---|---|---|
| A15 | One sealed open-data test per theory | pass or fail per theory, recorded as our result on the scoreboard | 2-3 |
| A16 | Our own hypotheses (H track) | a hashed hypothesis that beats baselines and rivals on held-out data, or a logged failure | 2-3 |
| A17 | Theory disagreement map | the cases (ketamine, REM, psychedelics, sedation levels) where theory-derived measures disagree most, which become the next sealed tests | 2 |

## Building the most accurate theory (track B)

Testing theories only tells us which ones fail. To get a better theory we need the facts any true theory must explain, a fair score for every theory against them, and then a theory built to cover what the others miss.

| # | Approach | Decisive outcome | Wave |
|---|---|---|---|
| B1 | **Constraint ledger.** Every robust finding a true theory must explain: blindsight, split brain, cerebellum vs cortex, posterior vs frontal lesions, anaesthetics with different mechanisms, ketamine and REM dreaming, covert awareness, masking and inattentional blindness, no-report results, slow-wave sleep, psychedelics, seizures, and so on. Each is graded by evidence strength and backed by DOIs. | 40+ graded constraints, each source-checked | 2 |
| B2 | **Theory × constraint scorecard.** Each of about 10 theories is marked explains / compatible / silent / contradicts on every constraint, quoting the proponents' own stated position. | where every theory fails at once: the gaps a new theory must fill | 2 |
| B3 | **Data-driven ingredients.** On held-out subjects and labs (DREAM, 2,417 report-labelled awakenings), find which signals predict reported experience beyond spectral baselines. Each found signal is an ingredient a theory must explain. | signals that survive held-out tests, or a logged null | 2-3 |
| B4 | **Our theory.** Draft one or more explicit theories that cover the ledger better than the rivals. Each states mechanism, necessary and sufficient conditions, and at least 3 risky predictions no rival makes, and is sealed by hash. Rival agents argue against each draft. | a sealed theory (or theories) that outscores rivals on the ledger, scored blind | 3 |
| B5 | **Test our theory like the others.** Run the sealed predictions on held-out data, and on future data when released (COGITATE exp 2, INTREPID). Red team. | pass or fail, recorded on the scoreboard | 3+ |

Rules for our own theory: it is scored by agents who did not write it; it may not be revised after its predictions are opened without a new hash and a new test; and a failed theory goes in the negative atlas like any other.

## Order and risk

Foundations come first, because every later number depends on them: A1, A2 and A3 gate everything. A4 and A5 are cheap and decisive, so they run in wave 1. Dissociations (A7, A8) depend on the audit finding report-graded data; if it finds none, that is the headline finding of wave 1. The COGITATE work (A10, A11) is costly on this laptop, so it runs on iEEG subsets only.

## What each morning review contains

- what landed, with verdict, numbers and path;
- what moved on the ladder or the scoreboard, and what was closed (added to the negative atlas);
- which citations were verified or struck;
- the lead's review: what to stop, what to escalate, the next wave;
- decisions only the human lead can make (data access requests, outreach drafts).
