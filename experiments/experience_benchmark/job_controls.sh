#!/bin/bash
# Positive controls and planted checks (no DREAM data) under Open Mind's own compute lock.
#   experiments/experience_benchmark/job_controls.sh
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
L="$REPO/../open-citizen-science/.local/compute.lock.mind"
until mkdir "$L" 2>/dev/null; do echo "$(date -u +%T) mind lock held by: $(cat $L/owner 2>/dev/null)"; /bin/sleep 60; done
echo "mind #42 positive controls + planted checks $(date -u +%FT%TZ)" > "$L/owner"
trap 'rm -rf "$L"; echo "$(date -u +%T) mind lock released"' EXIT
echo "$(date -u +%T) mind lock taken"
cd "$REPO" || exit 1
memfree() { memory_pressure | tail -1 | grep -o '[0-9]*' | tail -1; }
for step in "positive_control.py all" "planted.py features" "planted.py evaluate"; do
  until [ "$(memfree)" -ge 20 ]; do echo "$(date -u +%T) free memory $(memfree)% < 20%; waiting"; /bin/sleep 60; done
  echo "$(date -u +%T) step $step"
  OMP_NUM_THREADS=1 taskpolicy -b nice -n 20 .venv/bin/python -I experiments/experience_benchmark/$step || exit 1
done
