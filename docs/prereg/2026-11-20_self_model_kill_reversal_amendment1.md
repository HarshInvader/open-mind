# Amendment 1 to the reversal kill test (2026-11-20, after the first run)

## What happened
The first run (`kill_reversal.json`) is **void**: planted check P2 failed. My P2 was wrong on paper: the step controller's disruption at s = 1 is (1 - e) + k = 0.1 + k, and its peak is 0.25, so its reversal is 0.15 - k, which is not above 0.05 for k >= 0.1. I also saw the main outcome before writing this amendment: every optimised controller (S, A1, A2) showed zero reversal in all 16 cells. So the question below is new, and the first-run outcome is recorded as exploratory only.

## Why the first run came out flat (worked out after seeing it)
For a noiseless controller that minimises expected loss, the best rule suppresses whenever e * p(s) > k. Its peak disruption is therefore about k / e, and its disruption at s = 1 is (1 - e) + k. A reversal needs k / e > (1 - e) + k, which reduces to k > e, and then it never suppresses. So an expected-loss-optimal controller cannot show the Tsushima reversal; noise only blurs this. The reversal needs control to be withheld below a threshold higher than the optimum: a fixed access floor.

## New sealed question
Across a fresh grid, do optimised controllers rarely show the reversal while fixed-floor controllers usually do?
- Grid: e in {0.7, 0.8, 0.95}; capture p(s) = s^g with g in {0.5, 1, 2}; sigma in {0.1, 0.3}; k in {0.02, 0.1}. 36 cells. Same reversal metric (reversal > 0.05, peak at s < 0.9).
- Optimised controllers: S, A1, A2 as before, theta chosen by grid search.
- Fixed-floor controllers: F (stimulus signal, theta fixed at 0.3) and FA (graded attention signal, theta fixed at 0.3).
- Planted checks: P1 as before (N never reverses). P2 corrected: a noiseless step controller at 0.3 must show the reversal in every cell where its formula gives p(0.25) - ((1 - e) + k) > 0.05.

## Decision rule
- **Supported** if each optimised controller shows the reversal in at most 10% of cells (<= 3 of 36) and F and FA each show it in at least 50% (>= 18 of 36).
- **Not supported** otherwise; then the reversal cannot be used to separate gating types in the agent study.

## What it would mean
If supported, the reversal is a signature of thresholded (all-or-none-like) access gating control, not of whether the gating signal is about the stimulus or about the agent's own attention. For the agent study, it predicts that a trained agent shows the reversal only if its route to control passes through a low-capacity, thresholded self-model.
