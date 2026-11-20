# Amendment 5 to the experience benchmark pre-registration: the Michalak check becomes mandatory

Amends the pre-registration (de1f44ce…) and amendments 1-4. Written 2026-11-20 after an independent prior-art review (coordinator, Fable) and the owner's "prior art first" rule. **No DREAM label has been joined to any EEG feature.** No Michalak experience label (`Recall`) has been read. To build and test the reader I read only: the file's structure, variable names, category names, Stage counts (1 = 10, 2 = 1,024, 3 = 41 awakenings), and Delta values without labels (for the electrode-mapping check). The scoring was tested on random and planted fake labels only.

Changes to the DREAM analysis prompted by the same review are separate (amendment 6, to be sealed before unblinding).

## 1. Why

The closest work leaves one question open: within a person, at a fixed sleep stage, does the ordinary spectrum predict a report of experience?
- Wong et al. 2025 (the DREAM paper) folded over epochs.
- Selte et al. 2026 pooled N2 and N3 at one site.
- Michalak et al. 2026 did not report an experience vs no-experience AUC.

The Michalak data (1,024 N2 awakenings, an independent lab, more N2 awakenings than all of Tier 1) can answer that question without touching DREAM. It is the strongest cheap kill test, so it runs first and decides the framing.

## 2. Change from amendment 3 §3

- **Mandatory.** The check is no longer optional, and it runs now, before DREAM is unblinded. A reader that uses scipy only was built and is sealed with this amendment: `experiments/experience_benchmark/michalak_check.py`.
- **Values are already log power.** The authors' code labels Delta and Gamma as log(µV²) and defines Ratio = Gamma − Delta. So the sealed "log10(gamma/delta)" is computed as the ROI mean of (Gamma − Delta). This ranks awakenings the same way for any log base. ROI averages are means of log values.
- **Three scores instead of one:**
  - ratio, the primary score: one-sided, higher with experience;
  - posterior gamma, higher with experience: two-sided;
  - posterior delta, lower with experience: two-sided.
- **Statistic, as sealed in amendment 3:**
  - the within-subject pair AUC;
  - 5,000 within-subject permutations;
  - 5,000 subject bootstrap draws within each of the two studies (wp1, wp2).
  - The subject key is (Study, Subj).
- **Added, descriptive only:** a pooled AUC that is between-subject and not centred, with a subject-bootstrap CI. It shows how much of any pooled figure comes from differences between people.
- **Reader checks.** The script stops if any of these fails:
  - the object ids of the 256 tables;
  - the variable names;
  - Subj, Study, Stage and Recall being identical across the 256 channel tables;
  - a label-free electrode-mapping check: each ROI channel's Delta must correlate more with its nearest neighbour than with the farthest channel, in a majority of ROI channels.

  The dry run passed all of them, with 13 of 13 on the mapping check. The ROI electrodes are L16L, R10E, Z15Z, L19L, R5H, Z18L, R18Z, Z17R, L20Z, R19R, Z19L, R20Z and Z19Z.

## 3. Reading (fixed now)

| Reading | Condition | Consequence |
|---|---|---|
| NULL_SETTLED | every within-subject 95% CI (ratio, gamma, delta) lies inside [0.43, 0.57] | Outside DREAM, the within-person spectral null at a fixed stage is settled. Pooled figures like Selte's 0.80 most likely come from stage or between-person differences. DREAM's own contribution narrows to bounding the complexity markers, which is atlas material unless amendment 1's A1/A2 marks are met. |
| LIVE | any within-subject AUC ≥ 0.60 with a lower 95% bound > 0.50 | The benchmark question is live. DREAM tests whether this transfers across labs, and whether markers add anything beyond it. |
| OTHER | anything else | Reported as it falls. A small effect is not called null. |

The result is reported whatever it is. It is outside every Holm family and outside A1, A2 and R1-R5.
