#!/bin/sh
# Runs the sealed jitter_onset.py (resume: finished cell files are kept) with a heartbeat every 10 minutes.
cd "$(dirname "$0")"
PY=""
sig() { echo "SIGNAL $1 $(date -u +%FT%TZ) chain $$ py $PY" >> jitter_run.log; [ -n "$PY" ] && kill -"$1" "$PY" 2>/dev/null; exit 1; }
trap 'sig TERM' TERM
trap 'sig INT' INT
trap 'sig HUP' HUP
echo "START $(date -u +%FT%TZ) chain $$" >> jitter_run.log
nice -n 20 ../../.venv/bin/python -I jitter_onset.py run >> jitter_run.log 2>&1 &
PY=$!
echo "$PY" > jitter_run.pid
echo "PY $PY" >> jitter_run.log
while kill -0 "$PY" 2>/dev/null; do
  i=0
  while [ $i -lt 20 ] && kill -0 "$PY" 2>/dev/null; do sleep 30; i=$((i+1)); done
  kill -0 "$PY" 2>/dev/null && echo "HEARTBEAT $(date -u +%FT%TZ) cells_done $(ls out_jit/*.json 2>/dev/null | wc -l | tr -d ' ') load $(uptime | sed 's/.*averages*: //')" >> jitter_run.log
done
wait "$PY"; RC=$?
echo "RUN EXIT rc=$RC $(date -u +%FT%TZ)" >> jitter_run.log
[ "$RC" = 0 ] && nice -n 20 ../../.venv/bin/python -I jitter_onset.py summary >> jitter_run.log 2>&1 && echo "SUMMARY DONE $(date -u +%FT%TZ)" >> jitter_run.log
