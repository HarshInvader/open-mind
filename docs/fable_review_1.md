**Verdict**

T1 is not a new theory. It is a repackaging of four existing ideas joined by one fitted number, and its DREAM test is neither risky nor specific as drafted. A pass would barely move me, and a fail has a pre-built excuse. I verified six DOIs online (marked below); every other DOI in the repo is unchecked by me.

**1. Novelty**

- **Closest ancestor, and missing from T1's list:** Libet et al. 1979 (Brain, doi:10.1093/brain/102.1.193, verified). Libet proposed that experience waits for delayed "neuronal adequacy" and is then referred backwards in time to an early cortical time-marker. That is "minimum hold plus back-dating", 47 years earlier, with a different duration.
- **Discrete windows:** Herzog, Kammer & Scharnowski 2016 (doi:10.1371/journal.pbio.1002433, verified). Their model already has unconscious processing followed by conscious percepts at intervals of up to 400 ms.
- **Posterior locus and slow waves:** Siclari et al. 2017 (doi:10.1038/nn.4545, verified) and Siclari et al. 2018 (doi:10.1523/JNEUROSCI.0855-18.2018, verified). The 2018 paper already found fewer, smaller and shallower slow waves in central and posterior areas before dream reports than before no-experience reports.
- **The OFF-period gate:** Rosanova et al. 2018 (doi:10.1038/s41467-018-06871-1, verified), which is also where H comes from.
- **Unverified but relevant:** Lamme's recurrent processing theory (which `T1.md` itself calls closest), Zeki's microconsciousness and Dennett & Kinsbourne 1992. I did not check these.
- **What is actually new:** only the claim that one clock (H) governs sleep, anaesthesia, disorders of consciousness and perception, plus the timing-at-fixed-count test. `T1.md` section 6 already says roughly this, and it is right.

**2. Weaknesses**

- **H is fitted, and from the wrong level.** It comes from a TMS-evoked phase-locking duration and is applied to spontaneous local patches. The repo's own numbers give 248 ms at frontal sites too, which undercuts "posterior only".
- **The core terms are not measurable.** "Settled state", "patch" and "sensory-format" have no operational definition, and the substrate restriction is admitted to be a stipulation.
- **Sufficiency overreaches.** S1 implies an isolated posterior patch with a sustained state is conscious. Blindsight is not derived (admitted under C01).
- **The timing is unfalsifiable from the long side.** The reset rule added after critique lets any postdiction window longer than H be explained away.
- **Evidence already against it.** C51 (prefrontal but not parietal stimulation reverses anaesthesia), C09 (prefrontal lesions shift visibility), C04 (split brain), C55 (hydranencephaly), and NREM dreams reported amid plentiful slow waves.
- **The scoring does not support it.** All 20 "explains" are retrodictions. Under the harsh rule T1 scores 108/250, below both rivals.

**3. The DREAM Test**

It is not a fair risky test as written. The loopholes:

- **Recall versus experience:** unresolved, and excluding "without recall" removes the only contrast that addresses it. A published commentary on Siclari 2017 argues the serial-awakening contrast shows only activity preceding dream recall, not dreaming itself.
- **Frontal slow waves predict recall:** Siclari 2018 linked a subset of large, steep frontal slow waves with high-frequency increases to successful recall of content. This muddies H4.
- **Arousal:** sleep lightening before awakening predicts a pass under almost any theory. The AR covariate omits sigma power, time of night, cycle position and micro-arousals.
- **Not T1-specific:** H1 (recency) is largely a noisy restatement of delta power and wave count in the last seconds, which Siclari 2018 already reported.
- **The detector is not an OFF-period detector:** a median-amplitude threshold labels half of all half-waves as slow waves, with no high-frequency suppression check.
- **Window mismatch:** a 30 s window cannot test a 250 ms claim.
- **Lab effects:** reference, filtering, channel count and report method all differ by lab. One lab holds 55% of the data, so leave-one-lab-out has three folds, possibly two.
- **Multiple comparisons:** three tests at 0.025 each, uncorrected.
- **Asymmetric verdicts:** with 112 vs 77 and an AUC standard error near 0.04, REFUTED is almost unreachable. INCONCLUSIVE is the default outcome.
- **Prior exposure:** the DREAM paper's own EEG analyses already used Zhang & Wamsley 2019 and De Gennaro Young Adults. Task #16 may also have run delta tests on these awakenings.

Changes before sealing:

- Add last-5 s and last-10 s posterior delta power, last-10 s wave count, sigma power, time of night and awakening index to Model A.
- Require H2 or a count-matched timing test for PASS; H1 alone is not enough.
- Pre-state a posterior-minus-frontal recency difference test.
- Add "without recall" as a third class, with T1's prediction written down.
- Use one fixed ROI (P3, Pz, P4) and one re-reference across labs; report within-lab results too.
- Apply Holm correction across the family.
- Replace the single phase-randomised surrogate with 200 or more timing-only surrogates that keep wave shape.
- Define a smallest effect of interest and an equivalence test, so REFUTED is reachable.
- Declare the task #16 exposure, and delete the "scalp null counts less" caveat or label the test low-severity.

**4. Better Predictions**

- **Three-class test in DREAM:** T1 says "experience without recall" awakenings should look like experience on posterior recency; a recall account says they look like no-experience. This is the only cheap test that separates the two.
- **Tononi Serial Awakenings high-density set:** it is one of the six sets the DREAM paper used for EEG analysis. Run the posterior-minus-frontal contrast there, where local slow waves can be resolved.
- **Andrillon 2021 wake data (P3):** a posterior slow wave 50-150 ms after a brief stimulus should erase it and one after 250 ms should not. This is the sharpest test of H, but I did not confirm the data are public.

**5. Probabilities**

- **Formal PASS:** 20-30%. STRONG PASS: about 10%. REFUTED under current rules: under 5%. INCONCLUSIVE: 65-75%.
- **T1 broadly right as stated:** 3-7%.
- **Some posterior sustained-activity account with a bistability gate being part of the truth:** 25-35%, but that credit belongs to the prior work, not T1.