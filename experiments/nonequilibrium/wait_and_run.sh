#!/bin/bash
# Wait for the shared thread compute lock, run an NE job through board/run.sh, release the lock.
#   experiments/nonequilibrium/wait_and_run.sh [job.sh|job_main.sh]
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
L="$REPO/../open-citizen-science/.local/compute.lock"
until mkdir "$L" 2>/dev/null; do echo "$(date -u +%T) lock held by: $(cat $L/owner 2>/dev/null)"; /bin/sleep 60; done
echo "open-mind nonequilibrium extract+analysis $(date -u +%FT%TZ)" > "$L/owner"
trap 'rm -rf "$L"; echo "$(date -u +%T) lock released"' EXIT
echo "$(date -u +%T) lock taken"
cd "$REPO" && board/run.sh experiments/nonequilibrium/${1:-job.sh}
