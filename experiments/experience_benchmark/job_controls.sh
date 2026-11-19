#!/bin/bash
# Wait for the shared thread compute lock, run the positive controls and the planted checks (no DREAM data), release.
#   experiments/experience_benchmark/job_controls.sh
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
L="$REPO/../open-citizen-science/.local/compute.lock"
until mkdir "$L" 2>/dev/null; do echo "$(date -u +%T) lock held by: $(cat $L/owner 2>/dev/null)"; /bin/sleep 60; done
echo "open-mind #42 positive controls + planted checks $(date -u +%FT%TZ)" > "$L/owner"
trap 'rm -rf "$L"; echo "$(date -u +%T) lock released"' EXIT
echo "$(date -u +%T) lock taken"
cd "$REPO" || exit 1
P=".venv/bin/python -I"
OMP_NUM_THREADS=1 board/run.sh $P experiments/experience_benchmark/positive_control.py all
OMP_NUM_THREADS=1 board/run.sh $P experiments/experience_benchmark/planted.py features
OMP_NUM_THREADS=1 board/run.sh $P experiments/experience_benchmark/planted.py evaluate
