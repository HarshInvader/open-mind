#!/bin/bash
# One gated job: realised-sample power first, then the sealed confirmatory analysis.
cd "$(dirname "$0")/../.."
.venv/bin/python -I experiments/t1_dream/power_realised.py > experiments/t1_dream/power_realised.log 2>&1 || exit 1
.venv/bin/python -I experiments/t1_dream/analysis.py > experiments/t1_dream/analysis.log 2>&1
