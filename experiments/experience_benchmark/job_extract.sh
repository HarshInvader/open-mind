#!/bin/bash
# Label-blind extraction under Open Mind's own compute lock (owner 2026-11-19: projects run in parallel).
#   experiments/experience_benchmark/job_extract.sh
# One lab per chunk; before each chunk, wait while free memory is under 20%. extract.py resumes from its log.
# Background priority; extract.py uses 2 worker processes (Mind cap: 3).
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
L="$REPO/../open-citizen-science/.local/compute.lock.mind"
until mkdir "$L" 2>/dev/null; do echo "$(date -u +%T) mind lock held by: $(cat $L/owner 2>/dev/null)"; /bin/sleep 60; done
echo "mind #42 label-blind extraction (amendment 4, Rome first) $(date -u +%FT%TZ)" > "$L/owner"
trap 'rm -rf "$L"; echo "$(date -u +%T) mind lock released"' EXIT
echo "$(date -u +%T) mind lock taken"
cd "$REPO" || exit 1
memfree() { memory_pressure | tail -1 | grep -o '[0-9]*' | tail -1; }
for lab in Rome LODE DATA1 Aamodt Set19 Zhang Tononi; do
  until [ "$(memfree)" -ge 20 ]; do echo "$(date -u +%T) free memory $(memfree)% < 20%; waiting"; /bin/sleep 60; done
  echo "$(date -u +%T) chunk $lab (free memory $(memfree)%)"
  OMP_NUM_THREADS=1 taskpolicy -b nice -n 20 .venv/bin/python -I experiments/experience_benchmark/extract.py "$lab" || exit 1
done
echo "$(date -u +%T) extraction finished"
