#!/bin/bash
# Wait for the shared thread compute lock, run the label-blind extraction (Rome first), release the lock.
#   experiments/experience_benchmark/job_extract.sh
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
L="$REPO/../open-citizen-science/.local/compute.lock"
until mkdir "$L" 2>/dev/null; do echo "$(date -u +%T) lock held by: $(cat $L/owner 2>/dev/null)"; /bin/sleep 60; done
echo "open-mind #42 label-blind extraction (Rome first) $(date -u +%FT%TZ)" > "$L/owner"
trap 'rm -rf "$L"; echo "$(date -u +%T) lock released"' EXIT
echo "$(date -u +%T) lock taken"
cd "$REPO" && OMP_NUM_THREADS=1 board/run.sh .venv/bin/python -I experiments/experience_benchmark/extract.py Rome LODE DATA1 Aamodt Set19 Zhang Tononi
