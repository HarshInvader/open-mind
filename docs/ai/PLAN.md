# Can AI be conscious? (Open Mind sub-project, started 2026-11-21)

## Stance
We do not ask "is this model conscious?" directly. No test for that is validated. We follow the human-first rule argued by Chopra (2026, AAAI Symposium Series 8(1):241-247, doi:10.1609/aaaiss.v8i1.42549; page bot-blocked, abstract via search only, so unverified in detail) and by Thorat and Chopra (arXiv:2609.33366, read): a marker may be carried over to an AI system only once it has been validated in humans, and only for organisational features we have a reason to expect to carry over.

So the sub-project asks three narrower questions, each testable now:
1. **Do the markers being moved to AI survive in humans?** Many AI-consciousness indicators borrow human markers (complexity, PCI, ignition, workspace). Our human tests say some reduce to trivial signal properties.
2. **Do AI "consciousness signatures" survive the same controls?** Introspection and workspace findings in language models are new and mostly unreplicated. We apply our rules: planted answers, trivial-signal baselines, held-out items, publish either way.
3. **Can we build small systems where the answer is known, and check our methods recover it?** Agents with and without a learned self-model, ablated, scored against the human functional profile.

## What the field has shown (opened 2026-11-21)
- **Introspection by concept injection.** Lindsey (2026, arXiv:2601.01828, Anthropic): models sometimes detect and name a concept injected into their activations, about 20% at best, with 0 false positives in 100 controls for production models; "failures of introspection remain the norm". Macar, Yang, Wang, Wallich, Ameisen and Lindsey (arXiv:2603.21396, v5 Jun 2026): in Gemma3-27B, ablating the refusal direction raises detection from 10.8% to 63.8% (false positives 0% to 7.3%); code at github.com/safety-research/introspection-mechanisms. Hahami, Jain and Sinha (arXiv:2512.12411): Llama-3.1-8B tells injection strength (70%, chance 25%) far better than content; reports are "narrow and prompt-sensitive".
- **A workspace in language models.** Gurnee et al. (2026, arXiv:2607.15495, Anthropic): a "Jacobian lens" finds a subspace of verbalisable content in middle layers that holds on the order of tens of concepts and is widely read; within one forward pass, not recurrent; ignition-like competition unclear.
- **Ignition.** Rahbar (arXiv:2608.05160): a sigmoid-steepness "Ignition Index" from probe accuracy vs masking; about 23% of fits hit the parameter ceiling; no causal test; "not a measure of consciousness".
- **Indicator frameworks.** Chandaria et al. (arXiv:2609.35618, DeepMind and others): a five-level hierarchy plus a Bayesian network; LLM assessments range from below 0.01 to about 0.8 depending on credences, explicitly not an empirical probability.
- **Agents with self-models.** See `experiments/self_model_agents/PRIOR_ART.md` (Piefke et al. 2024 with Thorat; Liu et al. 2023; Phua 2025; Farrell, Ziman and Graziano arXiv:2411.00983).

Secondary summaries were used for parts of these long papers; numbers marked in the papers' own sections are the ones quoted.

## Tracks

| # | Track | Question | What is new (one sentence) | First kill test | Cost |
|---|---|---|---|---|---|
| AI1 | Transfer ledger | Which markers proposed for AI rest on human evidence that survived controls? | Nobody has scored AI-consciousness indicators against the human validation status of the marker they borrow. | Can each indicator be traced to a specific human marker at all? If fewer than 5 can, stop. | Desk work, days |
| AI2 | Self-model agents (board #43) | Does a learned attention model cause control, and does its ablation reproduce the human profile? | No agent study has made the agent's own attention less observable while the stimulus stays equally detectable, or tested a learned schema against all three profile entries. | Train the stimulus-only control alone: does it show the Tsushima reversal? Step 0 predicts no (optimal controllers never reverse); the independent reviewer predicts yes. | Laptop, hours per run |
| AI3 | Introspection or perturbation-sensing? | Does a model's "I notice an injected thought" reduce to sensing a generic disturbance (norm, entropy shift) rather than the content? | Our spectral-baseline logic, applied: a trivial-signal baseline for introspection reports. Prior-art check of 2603.21396 and 2512.12411 must come first; they may have done it. | On a small open model, do norm-matched random vectors trigger "detection" as often as concept vectors? | Laptop, a small open model |
| AI4 | Workspace and ignition audit | Do LLM workspace/ignition indices survive matched-difficulty and shuffled controls? | Later; depends on AI3 tooling. | Re-fit the Ignition Index with the ceiling removed. | Laptop |

## Rules
Same as the rest of Open Mind (`docs/AGENT_BRIEF.md`): prior art first, seal before looking, planted answer first, publish negatives with the smallest effect the test could catch. No claim that any system is or is not conscious. Model weights only from public, licensed sources.

## Order
AI1 and the AI2 kill test first (cheap). AI3 after its prior-art read. AI4 last.
