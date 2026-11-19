#!/bin/bash
# Wait for the shared thread compute lock, run the NE job through board/run.sh, release the lock.
L=/Users/harsha/Desktop/Personal/open-citizen-science/.local/compute.lock
until mkdir "$L" 2>/dev/null; do echo "$(date -u +%T) lock held by: $(cat $L/owner 2>/dev/null)"; /bin/sleep 60; done
echo "open-mind nonequilibrium extract+analysis $(date -u +%FT%TZ)" > "$L/owner"
trap 'rm -rf "$L"; echo "$(date -u +%T) lock released"' EXIT
echo "$(date -u +%T) lock taken"
cd /Users/harsha/Desktop/Personal/open-mind && board/run.sh experiments/nonequilibrium/${1:-job.sh}
