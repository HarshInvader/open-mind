# Pre-registration: does a trained stimulus-only controller show the Tsushima reversal? (AI2 kill test, 2026-11-21)

Why: the independent reviewer expects any agent that suppresses only after detecting a distractor to show the reversal automatically. Step 0 (`experiments/self_model_agents/RESULTS.md`) predicts the opposite for a controller trained close to optimal. This decides whether entry (1) of the profile can be used as a diagnostic at all.

Script: `experiments/self_model_agents/kill_trained.py` (hashed with this file). Simulation only.

## Task (one-step)
Distractor strength s uniform on {0, 0.05, ..., 1}. The agent sees x = s + N(0, sigma) and chooses suppress (cost k) or not. Attention is captured with probability s^g; captured and unsuppressed costs 1; suppression removes a fraction e. Reward = -loss.

## Agents
- **T (trained stimulus-only):** MLP 1-16-16-1, sigmoid suppress probability, REINFORCE with a mean baseline, Adam lr 0.01, 1500 updates of 4096 trials. Evaluated greedily (suppress if p > 0.5) on 20,000 trials per strength.
- **TF (planted, trained with a visibility floor):** same, but its input is set to 0 whenever x < 0.3, so weak distractors are invisible to it.

## Cells and seeds
Four cells (e, g, sigma, k): (0.95, 0.5, 0.1, 0.02), (0.95, 1, 0.1, 0.02), (0.8, 0.5, 0.3, 0.1), (0.95, 0.5, 0.3, 0.1); the fixed-floor controllers reversed in all four in step 0. Four seeds each.

## Metric
Reversal = max_s D(s) - D(1); "shows" if > 0.05 with the peak at s < 0.9. A cell counts as showing if at least 3 of 4 seeds show.

## Planted check (test void if it fails)
TF must show the reversal in at least 3 of the 4 cells.

## Decision rule
- **T shows the reversal in 0 or 1 cells:** step 0 holds for a trained agent. The reversal is a signature of a visibility floor, not of detection-gated control as such, and it stays usable as a diagnostic for capacity-limited gating.
- **T shows it in 2 or more cells:** the reviewer is right; drop the reversal as a diagnostic and build the agent study only on the observability manipulation.

## Prediction
T shows it in 0 cells.
