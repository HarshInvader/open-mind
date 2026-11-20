# Self-model agents: prior art and what is new (2026-11-20)

Goal: build agents that learn a model of their own attention (and confidence), ablate it, and check whether the ablation reproduces the human "functional profile" of Thorat and Chopra (arXiv:2609.33366, doi:10.48550/arXiv.2609.33366, full text read). This is item 4 of their research agenda, tested against item 5.

## Closest work (opened 2026-11-20)

1. **Piefke, Doerig, Kietzmann, Thorat (2024),** "Computational characterization of the role of an attention schema in controlling visuospatial attention", CogSci 2024, https://arxiv.org/abs/2402.01056 (v1 full text read). A PPO agent catches a ball in a noisy grid with an attention window that removes noise. An extra 3x3 "resource" the agent controls comes to carry its attention location (decoding 61%, chance 1.6%). Removing it collapses catching (reward 1.73 to -0.89 at p = 0.5). Not tested: distractors, confidence, binding. Their stated next step is an unstructured resource. Sushrut Thorat is also the first author of the functional-profile paper.
2. **Wilterson and Graziano (2021),** PNAS 118(33) e2102421118, https://www.pnas.org/doi/10.1073/pnas.2102421118. Blocked (HTTP 403), so only second-hand: a DQN with a hard-wired schema (a copy of the attention window) needed for control (as described in item 1). Marked unverified.
3. **Liu, Bolotta, Zhu, Bengio, Dumas (2023),** "Attention Schema in Neural Agents", https://arxiv.org/abs/2305.17375. Multi-agent PPO; a GRU "internal control" that predicts and masks attention gives the best reward, by a margin the authors call marginal. No distractor, confidence or binding tests.
4. **Phua (2025),** "Can We Test Consciousness Theories on AI? Ablations, Markers, and Robustness", https://arxiv.org/abs/2512.19155 (first third read verbatim, rest from a summary, so numbers unverified). A behaviour-cloned MiniGrid agent with a self-model trained on its own correctness: lesioning it drops type-2 AUROC 0.92 to 0.50 while accuracy stays 88.5% vs 88.2%, a "synthetic blindsight". No attention model; confidence supervised with correctness labels.

## What is new versus them (one sentence)

No agent study has checked an ablated, learned (not hard-wired, not correctness-supervised) self-model against all three entries of the human functional profile at once: the Tsushima reversal in attentional control, blindsight-like loss of confidence calibration at matched accuracy, and binding that survives without it; nor asked whether one module comes to carry both attention state and reliability.

## Kill test before any agent is trained

Is the Tsushima reversal even diagnostic of a self-model? If any detection-gated controller produces it, reproducing it in an agent shows nothing about attention schemas. Sealed in `docs/prereg/2026-11-20_self_model_kill_reversal.md`.
