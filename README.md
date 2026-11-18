# Open Mind: find the most accurate theory of human consciousness, in the open

**Goal: by the end of 2027, the most accurate theory of human consciousness we can find or build.** Current theories may all be wrong, so the project does three things:
- tests each existing theory's riskiest predictions on open data;
- keeps a public **constraint ledger**: the established facts any true theory must explain;
- builds its own theory where every existing one fails.

"Most accurate" is checkable. It means the theory explains more of the ledger than any rival, and predicts held-out and future data better than its rivals.

This does not explain why experience exists at all (the hard problem). A theory that predicts exactly which brain activity comes with experience is the part that can be checked. We say so on every page.

**Honest odds.** The middle two are the lead's estimates for the widened goal. The benchmark and winning-theory odds are from `docs/fable_plan.md`.
- A public constraint ledger with every major theory scored against it: 70-80%.
- A theory of our own, sealed with risky predictions, that explains more of the ledger than any rival: 25-35%.
- A theory, ours or anyone's, that beats its rivals on held-out data: under 5%.
- A red-teamed benchmark of which published measures survive the spectral confound: 50-60%.

**What would raise the odds:**
- An open TMS-EEG dataset across sleep, anaesthesia and patients.
- Open, pooled dream-report data from serial awakenings.
- COGITATE experiment 2 or INTREPID data released after our hash date.

## What counts as cracked (root milestone R)

All of these must hold:

1. **Frozen.** One measure plus a decision rule from a named theory, ours or another. Code and thresholds are SHA-256 hashed before any held-out data is opened. No per-dataset tuning.
2. **State, zero-shot.** Conscious vs unconscious on at least 4 held-out datasets from at least 3 families (sleep, anaesthesia, disorders of consciousness). Pooled AUC ≥ 0.90, and ≥ 0.80 in every dataset.
3. **Dissociations.** Correct where behaviour misleads:
   - ketamine (unresponsive, but experience is reported afterwards);
   - REM dreaming;
   - dream vs no-dream awakenings within one sleep stage.

   Ground truth is the report given afterwards, not behaviour.
4. **Beats baselines.** It beats spectral slope, band power and an arousal classifier by a pre-registered margin.
5. **Beats rivals.** It scores better than at least two rival theories' measures, frozen the same way, on a pre-registered log score.
6. **Prospective.** It passes on at least one dataset published after the hash date, or run by an outside lab.
7. **Red team.** An independent team fails to break it.

Our own bench can refute a measure but cannot confirm one alone.

## The claim ladder

| Level | Claim | Field today |
|---|---|---|
| L0 | Signal: reproducible, differs between states beyond nulls | Done |
| L1 | State: separates clearly conscious from clearly unconscious when behaviour agrees | Solid |
| L2 | Dissociation: tracks experience when behaviour disagrees, after spectral controls | Partial (PCI best; spontaneous-EEG measures in doubt) |
| L3 | Content: predicts what is experienced, with report and task confounds controlled | Contested (COGITATE mixed) |
| L4 | Theory: one theory's pre-registered predictions beat the rivals across L1-L3 | Empty |

## Theories on the scoreboard

The theories are IIT 4.0, global neuronal workspace, recurrent processing, higher-order theories, predictive processing / active inference, attention schema, dendritic integration, and criticality / entropic brain. Each theory's riskiest predictions, and what COGITATE found, are in `docs/fable_plan.md` §3 and on the site's scoreboard.

## How the work is done (same rules as Open Indus)

1. **Seal it before you look.** Write the prediction, test and pass mark in `docs/prereg/`, and append the SHA-256 to `docs/prereg/HASHES.txt` before any result is seen.
2. **Held-out by subject and lab.** Split by subject, never by epoch. Data from the same lab counts as a near-copy.
3. **Planted answer first.** A measure must recover an injected effect of known size, fail on phase-randomised surrogates, and rank known-Φ toy networks correctly before it is run on brain data.
4. **Red team.** Every positive result goes to an agent that did not produce it.
5. **Publish either way.** Each negative states the effect size the test could have caught (`docs/NEGATIVE_ATLAS.md`).

Work is done by AI agents with a human lead on one shared task board (`board/README.md`). Everything runs on one laptop.

## Layout

- `docs/AGENT_BRIEF.md`: rules of evidence.
- `docs/fable_plan.md`: the founding plan.
- `docs/prereg/`: sealed pre-registrations.
- `board/`: the task board.
- `experiments/<area>/`: code, `RESULTS.md` and `results.json`.
- `data/`: public datasets, fetched by script, never committed.
- `site/`: the public site (`python3 site/build.py`).
