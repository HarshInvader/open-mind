# Constraint ledger (task #24, track B1)

**Verdict.** The ledger has 59 constraints: 19 graded A, 30 graded B and 10 graded C. Every source is a DOI that was resolved on Crossref in this task or by the research sweep. For 46 of the 59 rows I also read the abstract or open full text of at least one source, or the research sweep had. Eleven DOIs I recalled from memory were wrong. All eleven were caught by the title check and corrected, so no constraint was dropped. The ledger is `ledger.csv`.

What the ledger says, in short:
- **Strongest facts (A):** blindsight; content-specific loss after posterior lesions; posterior stimulation that evokes matched experiences; anaesthetics with different targets that all remove consciousness; dreams reported from both REM and NREM; covert command-following in about a quarter of unresponsive patients; the masking threshold; the attentional blink; inattentional blindness; the partial-report advantage; seen vs unseen diverging at about 150-300 ms; postdiction; cortical bistability in unconscious states; brainstem and paramedian thalamic lesions causing coma.
- **Honest weak spots:** the ketamine dissociation rests on one cohort of 18 people (C14). The no-report and P3b results come mostly from one research line (C28). PCI comes from one consortium, and there is no open TMS-EEG data to re-test it (C41). The claustrum evidence is one stimulation case plus one correlational lesion study (C50, grade C). The split-brain "one or two subjects" question is open (C04, grade C). The finding that prefrontal TMS impairs metacognition failed to replicate (C27).
- **Large activity changes with consciousness intact:** prominent delta in awake, conscious people (C42); local sleep in awake animals (C44); lower oscillatory power and fMRI activity under psychedelics while experience intensifies (C45); hemispherectomy (C06); a gamma surge in dying rats (C56, grade C, experience unknown).

## Grading rule

- **A:** replicated across labs and methods.
- **B:** solid but limited: one lab, one method, animals only, or a small n.
- **C:** suggestive or contested, including findings with a failed replication.

I graded down whenever the evidence came from one cohort or one lab, even when the paper is famous.

## Counts by category

| Category | n | Rows |
|---|---|---|
| lesion | 9 | C01, C03-C09, C52 |
| pharmacology | 7 | C12-C15, C45, C46, C58 |
| no-report | 6 | C28-C32, C38 |
| state | 6 | C40-C44, C56 |
| subcortical | 6 | C47-C51, C55 |
| psychophysics | 5 | C22-C26 |
| sleep | 4 | C16-C19 |
| timing | 4 | C35-C37, C57 |
| clinical | 3 | C20, C21, C54 |
| content | 3 | C33, C34, C39 |
| stimulation | 2 | C10, C11 |
| attention, metacognition, self, physics | 1 each | C02, C27, C53, C59 |

## Required items: where they are

| Required by the task | Row(s) |
|---|---|
| Blindsight | C01, C02 |
| Split brain | C03, C04 |
| Cerebellum | C05 |
| Posterior vs prefrontal lesions | C07, C08, C09; stimulation C10, C11 |
| Anaesthetics with different targets; ketamine dreams | C12, C13, C14, C15 |
| REM vs NREM dream reports; dreaming in NREM | C16, C17, C18, C19 |
| Covert awareness (Owen 2006, Bodien 2024) | C20, C21 |
| Masking, attentional blink, inattentional blindness | C22-C26 |
| No-report paradigms and the P3b | C28-C32, C38 |
| Absence seizures | C43 |
| Slow waves and bistability | C40, C44 |
| PCI thresholds | C41 |
| Psychedelics | C45, C46 |
| Thalamus and claustrum | C48, C49, C50 (claustrum graded C), C51 |
| Timing and postdiction | C35, C36, C37, C57 |
| Binocular rivalry and decoding | C31, C32, C33, C18 |
| COGITATE | C39 |
| Large activity changes with consciousness intact | C06, C42, C44, C45, C56 |

## How sources were checked

- `crossref_check.py` resolved every DOI on Crossref and logged title, first author, year and venue to `crossref.jsonl` (140 lookups, including the theory papers for #25).
- `epmc_abstract.py` printed Europe PMC abstracts. I read them for every number that appears in the ledger.
- `epmc_fulltext_grep.py` searched open full text (Europe PMC or PMC) for theory positions. It was used in #25.
- The `checked` column of `ledger.csv` records what was read for each row:
  - `abs`: abstract read;
  - `ft`: full text searched;
  - `xref`: Crossref record only;
  - `sweep`: verified in `experiments/research_sweep/RESULTS.md` or `experiments/findings_page/SOURCES.md`.
- 13 rows rest on Crossref records only (C02, C07, C12, C22, C23, C25, C26, C33, C34, C36, C37, C48, C57). For those, the claim is the paper's main, title-level finding. No number in them was taken from memory.

## DOIs corrected or dropped

All eleven wrong DOIs were caught by the title check, then replaced with the right DOI:

| Paper | Wrong DOI (from memory) | Correct DOI |
|---|---|---|
| Schmid 2010, blindsight and LGN | 10.1038/nature09139 | 10.1038/nature09179 |
| Nielsen 2000, NREM mentation | 10.1017/S0140525X00003976 (Hobson's paper) | 10.1017/s0140525x0000399x |
| Blumenfeld 2012, epilepsy | 10.1016/S1474-4422(12)70153-9 | 10.1016/s1474-4422(12)70188-6 |
| Logothetis & Schall 1989 | 10.1126/science.2762826 (404) | 10.1126/science.2772635 |
| Winawer & Parvizi 2016 | 10.1016/j.neuron.2016.11.022 | 10.1016/j.neuron.2016.11.008 |
| Melloni 2011 | 10.1523/JNEUROSCI.4402-10.2011 (404) | 10.1523/jneurosci.4570-10.2011 |
| Kentridge 1999 | 10.1098/rspb.1999.0855 | 10.1098/rspb.1999.0850 |
| Whyte & Myers 2009 | 10.1097/PHM.0b013e3181a0e2c2 (404) | 10.1097/phm.0b013e3181a0e3a0 |
| Lee 2013, ketamine/propofol/sevoflurane | 10.1097/ALN.0b013e3182a8ec8c (different Lee 2013 paper) | 10.1097/aln.0b013e31829103f5 |
| Yu 2014, cerebellar agenesis | 10.1093/brain/awv117 | 10.1093/brain/awu239 |
| Chau 2015, claustrum lesions | 10.1016/j.concog.2015.07.002 | 10.1016/j.concog.2015.06.017 |

Not used, because I could not confirm them:
- the exact width of the attentional blink window (written as the standard description and flagged in C24);
- the number of participants in Horikawa 2013;
- whether hydranencephaly cases keep residual cortex;
- a DOI for Carhart-Harris & Friston's REBUS paper (not looked up);
- Libet's timing numbers.

## What was not checked

- Full texts of most ledger sources. Claims stay at the level of the abstract or title.
- Whether each A-graded effect has a formal multi-lab replication. A grades rest on the known literature plus the cited reviews.
- Independent replications of PCI outside the Milan consortium.
- Animal-to-human transfer for C13, C44, C49, C51 and C58. All are graded B or C for that reason.
- No PDFs were downloaded. `raw_ft/` holds plain-text full texts (under 1 MB) used for #25; they are deleted at the end of #25.

## Hypotheses this suggests (not tested)

| # | Pattern | Why it matters |
|---|---|---|
| H1 | Every A-graded "level" fact (C12, C40, C47, C48) involves loss of large-scale cortical responsiveness to input, but C42 and C45 show the EEG signatures used to measure it are not reliable | A theory should be stated in terms of causal responsiveness, not spectral shape |
| H2 | The content facts (C07, C10, C33) are posterior, and the access/report facts (C09, C28, C31) are frontal | A two-part theory (posterior content, frontal access) may cover more of the ledger than any single-locus theory |
| H3 | Postdiction (C36) and the 150-300 ms onset (C35) together imply that experience is assigned after a delay, then time-stamped earlier | Any theory needs an explicit temporal integration window |
