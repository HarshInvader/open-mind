# Is a temporal-generalisation "square" specific to a sustained code? (simulation)

**Verdict: SQUARE NOT SPECIFIC ONLY AT LARGE JITTER (75 ms).**
- **Secondary: CPL UNINFORMATIVE.** The proposed coupling test cannot separate the cases (see below).
- **Run:** sealed 2026-11-25T06:37:56Z (31e01cc), after a Fable pre-seal review whose throwaway peeks are disclosed in the prereg. Run once.
- **Validity:** every validity condition passed.
  - All 10 calibrated cells hit the target (mean diagonal AUC 0.58 ± 0.004), and every run median was within 0.01.
  - SUS was "square" in 40/40 studies (median SQ 0.94).
  - NULL was "square" in 0/40.

- **Prereg:** `docs/prereg/2026-11-25_tg_square_specificity.md`.
- **Script:** `tg_square.py`.
- **Outputs:** `out/calibration.json`, `out/<cell>.json` and `out/summary.json`.
- **Setup:** 40 simulated 20-subject studies per cell, all through Hutchinson et al.'s pipeline: causal 0.1 Hz high-pass, −100 to 0 ms baseline, 250 Hz, LDA TG.

## Results

| Cell | Ground truth | Amp | Median SQ | Median SPAN (ms) | "Square" (SQ ≥ 0.80 and SPAN ≥ 150) | CPL median | CPL > 0 sig. | CPL < 0 sig. |
|---|---|---|---|---|---|---|---|---|
| SUS | sustained 200–400 ms | 1.48 | 0.94 | 224 | **40/40** | +0.028 | 35% | 3% |
| SUS_j60 | sustained, onset SD 60 ms | 1.87 | 0.98 | 308 | 40/40 | −0.065 | 0% | **78%** |
| NULL | no signal | 0 | (noise) | 0 | 0/40 | −0.003 | 0% | 3% |
| **CH4_s0** | chain of four 50 ms codes, no jitter | 1.39 | 0.26 | 104 | 0/40 | −0.011 | 3% | 18% |
| **CH4_s25** | same, jitter SD 25 ms | 1.99 | 0.44 | 160 | 0/40 | −0.037 | 3% | 43% |
| **CH4_s50** | same, jitter SD 50 ms | 2.84 | 0.69 | 264 | 0/40 | −0.093 | 0% | 90% |
| **CH4_s75** | same, jitter SD 75 ms | 3.60 | 0.85 | 340 | **40/40** | −0.103 | 0% | 93% |
| J1_s0 (descr.) | one 50 ms code, no jitter | 4.56 | 0.31 | 88 | 0/40 | −0.007 | 8% | 13% |
| J1_s25 (descr.) | jitter SD 25 ms | 5.78 | 0.56 | 144 | 0/40 | −0.154 | 0% | 100% |
| J1_s50 (descr.) | jitter SD 50 ms | 8.26 | 0.90 | 224 | **40/40** | −0.456 | 0% | 100% |
| J1_s75 (descr.) | jitter SD 75 ms | 11.79 | 0.98 | 288 | **40/40** | −0.499 | 0% | 100% |

Each cell's run-median diagonal AUC was 0.575–0.586. In NULL, SQ is undefined or noisy: 23/40 studies were NaN because the diagonal mean was ≤ 0.

## What it means

- **Chain of distinct brief codes (primary).**
  - At matched decodability, a chain of four 50 ms codes, none of them sustained, makes a square only when trial-to-trial latency jitter reaches about 75 ms SD.
  - At 50 ms the matrix is visibly widened (SQ 0.69, SPAN 264 ms) but falls below the fixed square bar in every study.
  - So for this alternative, Hutchinson et al.'s reading survives up to moderate jitter. It fails only if their real single-trial latency spread is near 75 ms.
- **One brief code (descriptive; their own stated alternative, "variability in the latency of evoked responses").**
  - A single 50 ms code with 50 ms latency jitter gives a full square: SQ 0.90 and SPAN 224 ms, in 40/40 studies. That matches their example of a 200 ms decoder generalising over about 180–400 ms.
  - This follows arithmetically from the rank-1 structure (King & Dehaene 2014). But it means their verbal dismissal ("off-diagonal decoding started early and lasted long") does not rule this alternative out. A square of that size is exactly what it predicts at 50 ms jitter.
- **The proposed coupling test (CPL) does not work as designed.**
  - A sustained code with 60 ms onset jitter gives *negative* coupling in 78% of studies, the same sign as jittered brief codes.
  - A sustained code with little jitter is positive in only 35%.
  - Onset jitter therefore confounds the sign. CPL cannot tell "sustained but jittered" from "brief and jittered", so it is not a usable discriminator in this form.

## Limits

- Random mixing rather than a lead field; codes orthogonal in latent space, which is the hardest case for a square.
- The jitter grid is not anchored to measured single-trial latency spreads in their datasets. The answer depends on that spread: about 75 ms for a chain, about 50 ms for a single code.
- One decodability (mean diagonal AUC 0.58 over 200–400 ms); seen versus unseen modelled as signal versus none.
- The filter and baseline ablation (van Driel 2021) was not run.
- Results are properties of the method under simulation, not claims about their data.
