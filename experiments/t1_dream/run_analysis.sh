#!/bin/bash
# One gated job: realised-sample power first, then the sealed confirmatory analysis.
cd "$(dirname "$0")/../.."
# (realised-sample power already done: power_realised.json)
.venv/bin/python -I experiments/t1_dream/analysis.py > experiments/t1_dream/analysis.log 2>&1
