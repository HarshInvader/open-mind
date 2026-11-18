# Pre-registration: phi_proxy_recovery

Agent: mind-1   Task: #9   Date: 2026-11-18

Sealed together with the code that runs it: `experiments/phi_proxy/phi_lib.py`, `run.py`, `analyze.py`. No outcome (true φ or any proxy value on the grid below) has been computed when this is sealed. The planted-answer checks in `planted.py` test the code on separate, hand-built inputs and are not part of the outcome.

## 1. Question and hypotheses

Do published Φ proxies, computed from time series alone, rank small networks by their exact IIT 4.0 integrated information? A proxy that cannot do this on toy systems with known φ gets barred from brain data (README rule 3, plan section 6).

- H1 (per proxy): Spearman ρ between proxy and true φ is positive and large under EEG-like observation (condition C1).
- H2 (per proxy): proxy separates structurally zero-φ networks (feedforward, disconnected) from high-φ recurrent networks.
- H3 (per proxy): proxy ranks networks better than two non-integration baselines.

No direction is predicted for which proxy wins.

## 2. Data

Synthetic only; ground truth = synthetic. 75 networks of N = 5 binary units with kinetic-Ising updates: P(x_i(t+1)=1) = sigmoid(2β(Σ_j W_ji s_j + h_i)), s = 2x − 1, h_i ~ N(0, 0.3).
- Families (15 networks each): FF (random DAG, edge probability 0.6), DISC (recurrent modules {0,1} and {2,3,4}, no edges between them), DENSE (off-diagonal edge probability 0.8), SPARSE (probability 0.4 plus one directed cycle through all nodes), RING (directed ring with weights ±(1 to 1.2), plus 20% random extra edges of weight N(0, 0.3)).
- β ∈ {0.3, 0.6, 1, 2, 4}, 3 networks per family × β. Seed `np.random.default_rng([2026, k])`.
- Truth: φ_s of the whole 5-unit system (PyPhi 2.0.0rc4, `analyze(..., compute="sia")`, default formalism IIT_4_0_2026), averaged over states weighted by the exact stationary distribution; states with stationary weight < 1e-3 are skipped and weights renormalised. FF and DISC are structurally zero; this is verified in `planted.py`.
- Each network is simulated for T = 20,000 steps after 500 burn-in steps.

## 3. Observation models

- **C0, clean (secondary):** the binary unit states themselves.
- **C1, EEG-like (primary):** leaky integration y_t = 0.6 y_{t−1} + s_t; volume-conduction mixing to 5 sensors with Gaussian falloff (σ = 1 unit spacing); z-score; add pink (1/f) plus about 10% white noise at SNR 1 (equal power); decimate by 2 (no anti-alias filter). T = 10,000 samples.
- For LZc and plug-in φ, C1 sensors are binarised at each channel's median.

## 4. Measures

Proxies (six, the confirmatory family):
1. `phi_wms`: Barrett & Seth (2011) whole-minus-sum Φ_E, Gaussian, τ = 1, at the bipartition that minimises Φ/min(|A|, |B|).
2. `causal_density`: mean conditional Granger causality over all 20 ordered pairs, VAR order 2.
3. `integration`: Gaussian total correlation (zero lag).
4. `tse_complexity`: Tononi-Sporns-Edelman neural complexity, Gaussian, all subsets.
5. `lzc`: multichannel LZ76 (time-major concatenation of the binary matrix), divided by the mean of 3 time-shuffled copies.
6. `phi_plugin`: IIT 4.0 φ_s from an empirical TPM (lag 1, Laplace +1 smoothing; unobserved states 0.5; full connectivity), weighted by empirical state frequency (states < 1e-3 skipped).

Baselines (no integration in them): `base_local_pred` = sum of single-channel lag-1 Gaussian MI; `base_mean_corr` = mean |zero-lag correlation| between channels.

## 5. Split

Not applicable: no fitting. Every network is scored once. The unit of analysis is the network (n = 75).

## 6. Statistics

- Spearman ρ(proxy, true φ) over all 75 networks; 95% CI from 2,000 bootstrap resamples of networks; one-sided permutation p (5,000 shuffles of truth) in C1, Holm-corrected over the 6 proxies.
- AUC: structurally zero networks (FF + DISC, 30) vs recurrent networks in the top half of true φ among recurrent networks (≥ median).
- Baseline comparison: ρ_proxy − ρ_best-baseline, where the best baseline is the one with the higher ρ in that condition; 95% paired bootstrap CI.
- Descriptive: ρ within recurrent networks only; mean truth and proxies per β.

## 7. Pass marks (per proxy, condition C1)

A proxy PASSES, and may be used on brain data, only if all four hold:
1. ρ ≥ 0.6;
2. bootstrap 95% CI lower bound of ρ > 0.3;
3. AUC ≥ 0.8;
4. the paired bootstrap 95% CI of ρ_proxy − ρ_best-baseline lies above 0.

Anything else FAILS and is barred, with C0 reported to show whether the failure is in the proxy or in the observation model. If a baseline itself reaches ρ ≥ 0.6, that is reported as a finding: the "known φ" ranking is then recoverable without integration.

## 8. Planted-answer checks (must pass before the run counts)

`planted.py`: Gaussian lagged MI matches the analytic AR(1) value; Granger recovers a planted one-way coupling; Φ_E ≈ 0 for independent channels and > 0 for coupled ones; integration and TSE ≈ 0 for independent channels; LZc ≈ 1 for iid and ≪ 1 for periodic data; PyPhi gives φ_s = 0 in every state for FF and DISC and > 0 for a dense network; plug-in φ is within 25% of truth on 100k clean steps; simulated state frequencies match the stationary distribution (TV < 0.02).

## 9. Power

With n = 75 networks, a one-sided permutation test at α = 0.05/6 (Holm worst case) has 80% power for ρ ≈ 0.40. The pass mark (ρ ≥ 0.6, lower CI > 0.3) is stricter than significance. A proxy with true ρ = 0.6 has a bootstrap CI half-width of about 0.15 at this n.

## What this cannot show

Passing ranks toy 5-unit binary networks; it does not show a proxy tracks φ in brains with about 10^10 units. Failing is the informative direction: a proxy that cannot rank 5-unit networks has no claim to measure φ.

## Amendment 1 (2026-11-18, lead), sealed before any recurrent network was scored
The run stopped at network 14 (the first outside the feedforward family): `phi_wms` crashed because every bipartition gave NaN (a unit that never changes state makes the Gaussian mutual information undefined). At that point only feedforward networks (true Φ = 0 by construction) had been scored, and no proxy-versus-truth number had been computed.
- `phi_wms` now returns NaN when undefined instead of crashing. No defined value changes.
- In `analyze.py`, an undefined value of any measure is scored as the median of that measure's defined values (neutral: it neither helps nor hurts rank agreement much).
- A proxy undefined on more than 10% of networks fails its pass mark regardless of its other numbers, since it could not be trusted on brain data. Each proxy's count of undefined networks is reported.
- Pass marks, grid, seeds and everything else are unchanged.
