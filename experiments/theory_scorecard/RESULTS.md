# Theory × constraint scorecard (task #25, track B2)

**Verdict.** No theory explains more than 16 of the 58 in-scope constraints. IIT scores highest on the evidence-weighted total (119 of a possible 250), with GNWT close behind (115) and RPT third (101). The lead comes mostly from how many findings a theory's own authors have written about, not from successful risky predictions. No cell is marked "contradicts". Every clash we found is "strained": proponents keep an extra assumption that absorbs the problem.

Sixteen constraints are explained by no theory. They include two A-graded facts:
- postdiction (C36);
- covert awareness in about a quarter of unresponsive patients (C20): every theory is compatible with it, but none predicts it.

Six constraints get no "explains" or "compatible" mark from any theory: C19, C39, C50, C54, C56 and C57.

The best sealed-test targets are the constraints that split the theories:
- frontal vs posterior activity without report (C31, C32, C28, C11);
- ketamine dreams (C14);
- dream vs no-dream within one sleep stage (C17);
- the dissociation of wakefulness from awareness (C21).

Files:
- `scorecard.csv`: 649 cells, 11 theories × 59 constraints, with mark, proponent source, basis and note.
- `totals.csv`: per-theory counts and weighted totals.
- `gaps.csv`: constraints no theory explains.
- `splits.csv`: constraints that split the theories.
- `build_scorecard.py`: regenerates all four.

## How the marks were set

- **Explains:** a specific mechanism in the theory predicts the finding.
- **Compatible:** the finding does not conflict with the theory, but the theory does not predict it.
- **Silent:** the theory says nothing about it.
- **Strained:** the theory needs an extra assumption to fit.
- **Contradicts:** the finding conflicts with the theory.

Every non-silent cell names its basis:
- **Proponent (109 cells).** A paper by the theory's own authors, with DOI. Quotes are copied from the abstract or the open full text, which I read or searched in this task.
- **Our reading (154 non-silent cells).** No published position was found in the sources read. The cell says "no published position" and the note gives our reasoning. All 386 silent cells are also our reading.

Weighting:
- evidence grade: A = 3, B = 2, C = 1;
- mark points: explains +2, compatible +1, silent 0, strained −1, contradicts −2.

C59 (quantum decoherence) is a physics constraint on Orch-OR, not a fact about experience. It is left out of all totals and of the gap and split lists.

Theories scored:
1. GNWT.
2. IIT 4.0.
3. RPT.
4. HOT: Lau & Rosenthal, Brown-Lau-LeDoux, and Fleming's higher-order state space.
5. PP: predictive processing, active inference and the beast machine. Hohwy & Seth 2020 say PP is "not itself a theory of consciousness". It was scored as a framework, and that explains its many silent cells.
6. AST.
7. DIT.
8. Orch-OR.
9. Entropic brain / complexity.
10. TTC (temporo-spatial theory).
11. Brainstem affect theory (Solms; Merker). It was added as the "other with serious current backing", because it makes the clearest opposite prediction to the cortical theories.

## Per-theory totals (58 in-scope constraints, max weighted score 250)

| Theory | Explains | Compatible | Silent | Strained | Contradicts | Weighted score | Cells with proponent source |
|---|---|---|---|---|---|---|---|
| IIT 4.0 | 16 | 21 | 16 | 5 | 0 | 119 | 21 |
| GNWT | 13 | 27 | 12 | 6 | 0 | 115 | 28 |
| RPT | 8 | 28 | 20 | 2 | 0 | 101 | 12 |
| HOT | 5 | 22 | 26 | 5 | 0 | 69 | 8 |
| DIT | 4 | 19 | 34 | 1 | 0 | 69 | 12 |
| PP | 3 | 21 | 33 | 1 | 0 | 63 | 5 |
| AST | 4 | 8 | 46 | 0 | 0 | 40 | 6 |
| Brainstem affect | 3 | 10 | 44 | 1 | 0 | 35 | 6 |
| Entropic brain | 2 | 8 | 47 | 1 | 0 | 27 | 5 |
| TTC | 1 | 4 | 53 | 0 | 0 | 16 | 3 |
| Orch-OR | 2 | 0 | 55 | 1 | 0 | 5 | 2 |

How to read this:
- **These scores measure coverage, not truth.** A theory scores well when its authors have written about many findings. IIT and GNWT have the largest published literatures and lead for that reason too.
- **A narrow theory loses points here even if it is right about its own domain.** Examples are AST on attention, the entropic brain on psychedelics, and TTC on spontaneous activity.
- **"Explains" is often a retrodiction.** Several IIT "explains" cells rest on papers by IIT-aligned groups that were interpreted after the data came in (Siclari 2017, Rosanova 2018, Casali 2013). The same holds for GNWT (Del Cul 2009, van Vugt 2018). The scorecard does not separate prediction from retrodiction. Only COGITATE (C39) was a sealed test, and both theories it tested come out strained.
- **Zero "contradicts" is itself a finding.** Where a fact clashes with a theory, its proponents have published an auxiliary assumption. Examples:
  - HOT and prefrontal lesions: "redundancy" (Fleming 2020).
  - GNWT and the P3b: a move to the bifurcation marker (Sergent 2021).
  - IIT and COGITATE: no reply was read here.

  Theories this elastic cannot be ranked by the ledger alone. Sealed tests are needed.

## Gaps: constraints no theory explains (16)

| Id | Grade | Constraint (short) | What the theories manage |
|---|---|---|---|
| C20 | A | About 25% of unresponsive patients follow commands covertly | 10 of 11 compatible; none predicts who, or how many |
| C36 | A | Postdiction: later input changes what was experienced earlier | GNWT and PP compatible only; no published derivation |
| C06 | B | One hemisphere is enough | Compatible, trivially |
| C15 | B | Command-following under anaesthesia without recall | Compatible only |
| C18 | B | Sleep-onset imagery decodable from visual cortex | Compatible only |
| C19 | B | Lucid dreamers in REM answer questions in real time | All silent |
| C39 | B | COGITATE results | GNWT and IIT strained; the rest silent |
| C42 | B | Prominent delta in conscious people | IIT compatible; entropic brain strained |
| C44 | B | Local sleep in an awake brain | IIT compatible only |
| C51 | B | Prefrontal cholinergic stimulation reverses anaesthesia | IIT strained |
| C04 | C | One or two subjects after split brain | IIT strained |
| C30 | C | Awareness decodable from frontal fMRI without report or univariate response | Compatible only |
| C50 | C | Claustrum | All silent |
| C54 | C | Zolpidem awakens some patients | All silent |
| C56 | C | Gamma surge at cardiac arrest | All silent |
| C57 | C | Readiness potential vs reported intention | All silent |

**The 5 biggest shared gaps:**
1. **Time (C36, A).** Postdiction shows experience is settled after a delay of up to hundreds of ms, then dated earlier. No theory states its integration window or predicts which later inputs rewrite earlier content. C35 (onset at about 150-300 ms) is "explained" only by GNWT, and only as a latency, not as a window.
2. **Which unresponsive brains are conscious (C20, C21, A).** Every theory is compatible with covert awareness, but none predicts it from a measured brain property, except via PCI (an IIT-derived measure, C41) at the level of a threshold. C21 splits IIT and GNWT from the brainstem view.
3. **Large activity changes with consciousness intact (C42, C44, C45, C56).** Delta-rich conscious states, local sleep and psychedelic desynchronisation are explained only post hoc, and only by the entropic brain and PP for psychedelics. Delta-rich conscious states strain the entropic brain and are not addressed by the others. Any theory that uses a spectral or entropy signature inherits this gap. This matches the spectral-confound findings of tasks #12/#13 (Maschke 2025, r = 0.86).
4. **Disconnected but rich experience (C14, C15, C19).** Ketamine dreams, isolated-forearm responses and two-way communication with lucid REM dreamers show experience, and even connected cognition, while behaviour is absent. Only IIT has a mechanism-level account, and only for ketamine (wake-like PCI). No theory addresses real-time communication from REM.
5. **Neuromodulator paradoxes and small structures (C51, C54, C50).** Prefrontal cholinergic reversal, zolpidem awakenings and the claustrum have no theory-level account. Two of the three rest on weak evidence (grade C), so this gap matters less until they replicate.

## Splits: constraints where at least one theory explains and another is strained

| Id | Grade | Explains | Strained | Sealed-test value |
|---|---|---|---|---|
| C31 | B | IIT, RPT | GNWT, HOT | High: no-report rivalry with frontal readout |
| C21 | A | GNWT, IIT | Brainstem affect | Medium: cortical vs brainstem source of experience |
| C05 | A | IIT | PP, Orch-OR (our reading) | Low: no proponent positions on the strained side |
| C08 | B | IIT, RPT, brainstem affect | HOT | Medium: lesion data are old and contested |
| C11 | B | IIT | GNWT, HOT | Medium: stimulation reports depend on what patients say |
| C14 | B | IIT | GNWT | **High: ketamine dissociation**, if independent data exist (task #19) |
| C17 | B | IIT | HOT | **High and runnable now:** posterior vs frontal markers of dream vs no-dream within one stage, on DREAM |
| C28 | B | IIT, RPT | GNWT | High: no-report P3b vs bifurcation marker |
| C32 | B | GNWT | IIT, RPT | High: the mirror image of C31 in macaques |
| C55 | C | Brainstem affect | GNWT, IIT, RPT, HOT, DIT | Low: evidence is behavioural and contested |

**Best targets for sealed tests:**
1. **Front vs back without report (C28, C31, C32, C11).** The theories make opposite predictions here, and the evidence itself is split: human fMRI says frontal activity follows report (C31), while macaque neurons say prefrontal cortex holds content (C32). A sealed no-report test is needed, with the decoding analysis fixed in advance in both regions. COGITATE experiment 2 or INTREPID may supply the data.
2. **Dream vs no-dream within one sleep stage (C17, C16).** This can be run on open data now: DREAM has 2,417 report-labelled awakenings (task #3). IIT predicts a posterior marker; HOT and GNWT predict a frontal contribution. Task #16 has already sealed IIT-posterior and GNWT-frontal predictions on DREAM N2. This scorecard adds a HOT-frontal arm as a candidate.
3. **Ketamine (C14).** IIT predicts a wake-like causal structure; GNWT is strained by frontoparietal disconnection. Blocked until an independent ketamine dataset with delayed report exists (task #19; the Milan cohort counts once).
4. **Wake without awareness (C21, C20).** Cortical theories against the brainstem view. Needs DoC data with outcome or command-following labels, which is not open (task #20).

## What was not checked

- Most proponent positions come from one or two papers per theory. A theory's authors may have answered a strained cell elsewhere. Each strained cell is open to correction by the theory's proponents, and the outreach queue could ask them.
- Paywalled full texts were not read. Only abstracts were read for Aru 2020, Brown, Lau & LeDoux 2019, Northoff (2017, 2022), Storm 2024 and Hameroff 2006 (no abstract; title only). Positions from these are thin.
- TTC and the brainstem affect theory were scored from 2-3 papers each, so their silent cells partly reflect our reading depth.
- No inter-rater check. A second agent should re-mark a random 20% of cells blind. This is posted as an M6 task.
- Orch-OR: only proponent claims on anaesthesia and EEG were found. Its silence on most of the ledger is real in the sources read.

## Files and cleanup

The full-text excerpts used for quotes are kept as `experiments/constraint_ledger/ft_*.log`. The full texts themselves (`raw_ft/`, under 1 MB, plain text) were deleted after use. No PDFs were downloaded.
