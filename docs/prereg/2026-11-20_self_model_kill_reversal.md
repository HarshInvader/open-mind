# Pre-registration: is the Tsushima reversal diagnostic of an attention model? (kill test, 2026-11-20)

Simulation only. No real data. Script: `experiments/self_model_agents/kill_reversal.py` (hashed with this file).

## Model
- Distractor strength s on a grid 0, 0.05, ..., 1. Capture is stochastic: attention is captured with probability s; if captured and not suppressed, target performance loses 1; suppression removes a fraction e = 0.9 of that loss; suppressing costs k whether or not capture happens.
- Controllers, each with one noisy signal and a threshold rule (suppress if signal > theta). Theta is chosen to minimise expected loss under a uniform prior on s (grid search, 401 values).
  - **N (none):** never suppresses.
  - **S (stimulus detector):** signal x ~ N(s, sigma).
  - **A1 (attention model, binary):** reads its own attention state after capture onset: z ~ N(1[captured], sigma).
  - **A2 (attention model, graded):** reads a capture-onset signal whose size grows with s: z ~ N(s * 1[captured], sigma).
- Grid: sigma in {0.1, 0.2, 0.3, 0.5}, k in {0.02, 0.05, 0.1, 0.2}. Disruption D(s) is the expected loss, computed exactly (normal CDF), not sampled.

## Reversal metric
reversal = max_s D(s) - D(1). A controller "shows the reversal" in a cell if reversal > 0.05 and the peak is at s < 0.9.

## Planted checks (must pass or the test is void)
- P1: N must show no reversal in any cell (D(s) = s is monotonic).
- P2: a hand-coded step controller (suppress iff s >= 0.3, no noise) must show the reversal in every cell where k < 0.3.

## Decision rule
- The reversal is **diagnostic of an attention model** only if there are cells where A1 or A2 shows it and S does not, or the reverse, in at least 4 of the 16 cells.
- Otherwise it is **not diagnostic**: any agent study must not use the reversal on its own as evidence for a self-model, and must instead use a signature that separates S from A (for example, changing how observable the agent's own attention is while keeping the stimulus equally detectable).

## Prediction (written before running)
S and A2 show the reversal in the same cells. A1 never does, because its signal does not depend on s, so D(s) is linear in s. Verdict expected: not diagnostic. The reversal tells you control is gated by a signal that grows with distractor strength, not whether that signal is about the stimulus or about one's own attention.
