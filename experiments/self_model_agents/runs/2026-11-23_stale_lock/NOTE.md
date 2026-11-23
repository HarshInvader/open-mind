# Stale lock record (2026-11-23)

The Mind compute lock was held by `self_model kill_trained 2026-11-21T07:44:08Z` with no live process. Searched the repo and /tmp for partial outputs or logs of that run: none exist (no kill_trained.json, no log). The script wrote output only at the end, so nothing from the first attempt survives and no outcome data was seen.

The coordinator authorised clearing the lock and rerunning the sealed test. Sealed files were checked unchanged before the rerun:
- docs/prereg/2026-11-21_self_model_kill_trained_control.md  sha256 96a0b2f5...
- experiments/self_model_agents/kill_trained.py  sha256 69a22e75...

The rerun uses `run_kill_trained_ckpt.py`, a wrapper that checks the sealed script's hash, executes its definitions unchanged, and runs the same 32 (cell, agent, seed) jobs with a checkpoint line after each. Each job seeds its own generator, so results do not depend on order or restarts.
