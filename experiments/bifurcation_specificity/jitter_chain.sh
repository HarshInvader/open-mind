#!/bin/sh
# Runs the sealed jitter_onset.py (resume: finished cell files are kept) with a heartbeat line every 10 minutes.
cd "$(dirname "$0")"
echo "START $(date -u +%FT%TZ) pid $$" >> jitter_run.log
nice -n 20 ../../.venv/bin/python -I jitter_onset.py run >> jitter_run.log 2>&1 &
PY=$!
echo "$PY" > jitter_run.pid
while kill -0 "$PY" 2>/dev/null; do
  sleep 600
  kill -0 "$PY" 2>/dev/null && echo "HEARTBEAT $(date -u +%FT%TZ) cells_done $(ls out_jit/*.json 2>/dev/null | wc -l | tr -d ' ') load $(uptime | sed 's/.*averages*: //')" >> jitter_run.log
done
wait "$PY"; RC=$?
echo "RUN EXIT rc=$RC $(date -u +%FT%TZ)" >> jitter_run.log
[ "$RC" = 0 ] && nice -n 20 ../../.venv/bin/python -I jitter_onset.py summary >> jitter_run.log 2>&1 && echo "SUMMARY DONE $(date -u +%FT%TZ)" >> jitter_run.log
