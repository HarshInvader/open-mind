# Self-model agents, step 0: is the Tsushima reversal a usable signature? (2026-11-20)

**Verdict: the sealed rule was not met, but the test still settles what the agent study can use.** Controllers that use their evidence optimally never showed the reversal: 0 of 108 cells in the sealed run (and 0 of 48 in the void first run). Controllers with a fixed access floor showed it in 13 (stimulus signal) and 11 (attention-state signal) of 36 cells, short of the sealed 18. They showed it only when strong distractors were almost fully suppressed (e >= 0.8) and capture rose steeply at low strength (g <= 1). In every cell, the stimulus-signal and attention-state-signal versions behaved nearly the same.

Two consequences for the agent study:
1. The reversal cannot tell a self-model from a stimulus detector. Any claim that an agent's attention schema is shown by it would be empty. A test has to change how observable the agent's own attention is while keeping the stimulus equally detectable.
2. A reward-optimal agent should not show the reversal at all. If a trained agent shows it, something is withholding control below an optimal threshold: a capacity limit or an all-or-none gate. That makes the reversal a probe of gating, not of the content of the gate.

## What was sealed
- First run: `docs/prereg/2026-11-20_self_model_kill_reversal.md` + `kill_reversal.py`. **Void:** my planted check P2 was wrong on paper (the step controller cannot reverse when k >= 0.1). I saw the main outcome (all optimised controllers flat) before writing the amendment, so that outcome is exploratory.
- Amendment 1: `docs/prereg/2026-11-20_self_model_kill_reversal_amendment1.md` + `kill_reversal_a1.py`, sealed before its run, on a fresh 36-cell grid. Planted checks passed (P1: no-control never reverses; P2: step controller reverses in all 16 cells its formula says it should).

## Numbers (amendment run, `kill_reversal_a1.json`)

| Controller | Cells with reversal (of 36) | Largest reversal |
|---|---|---|
| S, optimised stimulus detector | 0 | 0.000 |
| A1, optimised binary attention model | 0 | 0.000 |
| A2, optimised graded attention model | 0 | 0.000 |
| F, stimulus signal, fixed floor 0.3 | 13 | 0.313 |
| FA, attention-state signal, fixed floor 0.3 | 11 | 0.311 |

Why optimised controllers cannot reverse (noiseless case): they suppress once e * p(s) > k, so peak disruption is about k / e, while disruption at full strength is (1 - e) + k. A reversal needs k > e, and then suppression never pays.

## Limits
- A toy expected-loss model, not a trained agent. One distractor, one suppression action, normal noise, uniform prior on strength.
- "Optimal" here means optimal for this loss. Real brains and trained agents face other costs (speed, capacity), which is exactly what the next step tests.
- Tsushima et al. (2006, doi:10.1126/science.1133197) already argued that weak signals escape control because they are not noticed. This test adds that an evidence-optimal controller would not behave that way, and that the effect does not identify what the gate reads from.

## Next step (not started)
Train small agents with and without a capacity-limited, learned self-model on a task with graded distractors, a confidence wager and a feature-location binding probe. Seal: the reversal appears only with the bottleneck; ablating the self-model abolishes control and calibration at matched accuracy but leaves binding intact. Independent novelty read first, per the prior-art rule. Prior art: `PRIOR_ART.md`.
