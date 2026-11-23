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

---

# Step 1 (AI2 kill test): trained stimulus-only controller vs planted visibility floor (run 2026-11-23)

**Verdict: VOID by the sealed rule.** The planted check failed: the planted agent TF showed the reversal in 0 of 4 cells (rule: at least 3). The trained stimulus-only agent T also showed it in 0 of 4 cells, but because the test is void that is not evidence either way.

- Sealed prereg: `docs/prereg/2026-11-21_self_model_kill_trained_control.md` (sha256 96a0b2f5..., 2026-11-21T07:44:08Z), script `kill_trained.py` (sha256 69a22e75...). The first attempt left a stale lock and no output (`runs/2026-11-23_stale_lock/NOTE.md`). The rerun used `run_kill_trained_ckpt.py`, which checks the sealed hash and runs the sealed code unchanged with per-job checkpoints. It took about one minute.
- Output: `kill_trained.json`, `kill_trained_ckpt.jsonl`, `kill_trained_run.log`.

## What happened (diagnosis, after the outcome)

All 32 trained agents (T and TF, every cell and seed) learned to **suppress at every distractor strength**. Disruption at strength 0 equals the suppression cost k in every run, and disruption rises monotonically to its maximum at s = 1 (reversal exactly 0 everywhere).

That is the reward-optimal policy in these cells. Suppressing pays whenever e * s^g > k. With g = 0.5 and k = 0.02 to 0.1, that holds for every s >= 0.05, so the best policy is to suppress (almost) always. The step 0 analysis already said an evidence-optimal controller cannot reverse; these cells make "always suppress" optimal outright.

The planted agent failed for a design reason, not a code bug. TF's floor hides the input below x = 0.3, but it does not stop the agent from acting. A blind agent whose best move is "suppress anyway" still suppresses. Step 0's fixed-floor controllers reversed because their floor blocked the **action** (no suppression below detection), not only the input.

## What this means

- The sealed question (does a trained stimulus-only agent reverse?) stays open. The test as designed could not have shown a reversal in either agent.
- Lesson for the agent study: a "visibility floor" must gate control, not just perception, or a cheap default action covers for it. Cells must also make suppression costly enough that blanket suppression is not optimal (k comparable to e * s^g at mid strengths).
- Next step, not started: a sealed amendment with an action-gated planted agent and cells where blanket suppression loses. Because T's behaviour in these four cells is now known, any amendment must use new cells.
