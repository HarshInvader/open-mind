# Pre-registration: does weak two-state data look "unimodal" under the bifurcation test? (simulation)

Agent: Open Mind thread   Date: 2026-11-25   Script: `experiments/bifurcation_specificity/snr_timing.py`   Source: Fable round 16, item 1

- **Zero data.** Simulation only, reusing the sealed `audit.py` and `extended.py` unchanged.
- **Builds on:** the bifurcation audit (NOT SPECIFIC) and the extended model set (FIX WORKS). Both used one signal size, which was a stated limit.

## 0. The claim and prior art

- **Sergent et al. 2021** (*Nat Commun* 12:1149, PMC7895979) state the timing of the model comparison:
  - "a first period between 0 and 250 ms after stimulus onset where the unimodal model showed the highest probability";
  - then Model 3 above 95% from about 250 to 700 ms;
  - then "a last period between 700 and 900 ms where the unimodal model seemed most favored again".
- **Their discussion reads the early period as a finding:** early sensory processing "followed a non-linear increase in magnitude … but … the underlying dynamics were unimodal". It is the core of "early graded, late all-or-none" (GNWT).
- **Why this is a question:** decoding at the strongest SNR became significant only from about 100 ms. The early and late periods are when the stimulus signal is weakest. Two overlapping states are hard to tell from one state when their separation is small: mixture detection depends on separation (Bauer & Curran 2003; general mixture-power results). If weak two-state data also make the unimodal model win, the early "unimodal" period is what a two-state brain would show too.
- **Prior art checked:** among the 122 works citing Sergent 2021 (screened for the audit) and a Europe PMC search on bifurcation with power, SNR or simulation, none tests this. Klatzmann 2025 models ignition mechanistically; it is not a critique.

## 1. Design

- **Generator:** their Model 3 shape (`B_bifurcation`):
  - two states with a shared noise SD;
  - P(high) logistic in level, zero at level 0;
  - high-state mean scaled by DMAX.
- **Signal grid:** DMAX ∈ {0.25, 0.5, 0.75, 1.0, 1.5, 2.0} noise SDs. The max-level separation (level 5 vs level 0, label-free property of the generator) gives AUC 0.570, 0.636, 0.699, 0.755, 0.848 and 0.912.
- **Comparison cell:** `M2_unimodal` (their Model 2B shape) on the same grid. It shows what a graded brain gives.
- **Design otherwise as sealed:** 20 subjects, 150 trials per level, 6 levels, 5-fold block CV, their inits, fminsearch defaults, spm_BMS.
- **Studies:** 100 per cell, seed 20261202.
- **Primary analysis:** their 3-model comparison (0, 2B, 3). For each study:
  - the model with the highest protected exceedance (their "highest probability" wording);
  - whether Model 3 or 2B exceeds 0.95.
- **Secondary (descriptive):** the 5-model comparison (adding J and T) on `B_bifurcation` only, run as a separate set of 100 studies per grid point (different seeds). The verdict uses the 3-model run only.
- **Shares:** every share is over all 100 studies. A study with a non-finite log-evidence counts for no model, and the number of such studies is reported.

## 2. Decision (B_bifurcation, 3-model comparison)

The verdicts describe the method. They are not claims about Sergent's data.

| Verdict | Condition |
|---|---|
| INVALID | At DMAX 2.0, Model 3 has the top pxp in < 80% of studies. That would contradict the sealed audit, where Model 3 was called in 100%. |
| SEES WEAK TWO-STATE SIGNALS | Model 3 has the top pxp in ≥ 80% of studies at every grid point with max-level AUC ≥ 0.60 (DMAX ≥ 0.5). A "unimodal" win at any decodable signal size is then evidence against two states, and this idea is dead. |
| BLIND ZONE REACHES AUC 0.70 | Model 2B alone has the top pxp in > 50% of studies at some grid point with AUC ≥ 0.69 (DMAX ≥ 0.75; exact AUC 0.697 there). A clearly decodable two-state signal then reads as "unimodal". |
| NEITHER CONDITION MET | otherwise. Includes points where Model 0 (null) dominates, which reproduces their baseline period, not their early period. |

- **Checked in this order:** INVALID first, then SEES WEAK TWO-STATE SIGNALS, then BLIND ZONE.
- **Reported in every case:**
  - the table of shares per grid point (Model 3, 2B and 0 top; call rates; non-finite);
  - the same for the M2_unimodal cell;
  - the smallest grid AUC where Model 3 is top in ≥ 80%;
  - per-study pxp (kept in the output files).
- **Reading against Sergent's data:**
  - Their early-window AUCs are only in their Fig. 2 and its source-data file, which we have not fetched. Fetching that small spreadsheet is a later decision, not part of this run.
  - Our AUC is computed on the generator's window values. Theirs is per time sample after a 10 Hz low-pass, so a window-mean AUC would differ somewhat from their plotted curve.
  - Decoding is significant only from about 100 ms, so 0–100 ms carries no signal and should not be read against the grid.

## 3. Calibration fallbacks (stated in advance)

- **None.** The INVALID row above is the validity check.
- **Resume:** finished cells are kept, with the same seeds.
- Any other change after sealing makes the run INVALID.

## 4. Limits

- **Separation-scaled signals only:** a weak signal here means two states that are close together. A weak signal can also come from low occupancy: states fully separated, but few trials in the high state. At the same AUC that case is much more mixture-like. A BLIND ZONE verdict is therefore an existence proof for separation-scaled signals. It does not show that every weak two-state signal reads as unimodal. This matters most for 700–900 ms.
- **One shape:** the generator's two states keep a fixed mean ratio across levels. In real data the early signal may differ in shape as well as in size.
- **Not a claim about their data:** an UNINFORMATIVE verdict says the early "unimodal" period does not, on its own, show unimodal dynamics. It does not show that early dynamics are two-state.
- **The 700–900 ms period** has the same logic, and the same boundary applies to it.
- **Neutrality:** results are stated as properties of the method under simulation.
