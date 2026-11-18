#!/bin/bash
# One gated job: planted checks first, then the sealed main run (resumable).
cd "$(dirname "$0")/../.."
.venv/bin/python -I experiments/phi_proxy/planted.py > experiments/phi_proxy/planted.log 2>&1
grep -q "ALL PASS" experiments/phi_proxy/planted.log || { echo "planted failed"; exit 1; }
.venv/bin/python -I experiments/phi_proxy/run.py >> experiments/phi_proxy/run.log 2>&1
