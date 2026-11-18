#!/bin/bash
# One gated job for tasks #8 and #4 (run via board/run.sh). Resumable: skips finished steps.
set -e
cd "$(dirname "$0")/../.."
P=".venv/bin/python -I"
free=$(df -m /System/Volumes/Data | awk 'NR==2{print $4}')
if [ "$free" -lt 1000 ]; then echo "DISK_LOW ${free}MB, not running"; exit 3; fi
[ -f experiments/surrogate_gate/results_gate.json ] || $P experiments/surrogate_gate/gate.py real > experiments/surrogate_gate/gate_real.log 2>&1
[ -f experiments/lz_slope/planted1.json ] || $P experiments/lz_slope/analyse.py planted1 > experiments/lz_slope/planted1.log 2>&1
# raw epochs are only needed for P1: delete them as soon as it is done
[ -f experiments/lz_slope/planted1.json ] && rm -rf experiments/lz_slope/raw
[ -f experiments/lz_slope/planted2.json ] || $P experiments/lz_slope/analyse.py planted2 > experiments/lz_slope/planted2.log 2>&1
[ -f experiments/lz_slope/results.json ] || $P experiments/lz_slope/analyse.py main > experiments/lz_slope/main.log 2>&1
echo ALL_DONE
