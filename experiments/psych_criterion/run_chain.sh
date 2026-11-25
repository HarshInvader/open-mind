#!/bin/sh
# Psychometric-criterion simulation: calibrate -> run. 4 workers, nice 20.
cd "$(dirname "$0")/../.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
for step in calibrate run; do
  echo "== $step $(date -u +%FT%TZ)"
  nice -n 20 .venv/bin/python -I experiments/psych_criterion/criterion_sim.py $step || { echo "STEP FAILED $step"; exit 1; }
done
echo "CHAIN DONE $(date -u +%FT%TZ)"
