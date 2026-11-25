#!/bin/sh
# Latency-spread chain: shape -> ladder -> gate -> real (real analyses data only on GATE PASS). 4 workers, nice 20.
cd "$(dirname "$0")/../.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
P=".venv/bin/python -I experiments/latency_spread/latency_spread.py"
for step in shape ladder gate real; do
  echo "== $step $(date -u +%FT%TZ)"
  nice -n 20 $P $step || { echo "STEP FAILED $step"; exit 1; }
done
echo "CHAIN DONE $(date -u +%FT%TZ)"
