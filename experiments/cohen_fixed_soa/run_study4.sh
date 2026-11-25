#!/bin/sh
# Item 4, one launch: prep -> align -> gate -> (gate99 only if the gate FAILED; fallback F2) -> run.
# Orchestration only; every step is the sealed study4.py command (prereg docs/prereg/2026-11-25_cohen_noreport_dd.md §8).
# Usage (from experiments/cohen_fixed_soa/):  sh run_study4.sh FETCH_PID
#   FETCH_PID = the fetch's python pid; refuses to start while it is alive (F1: prep runs once, after the fetch exited).
set -u
PY="nice -n 20 ../../.venv/bin/python -I"
if [ $# -ne 1 ]; then echo "usage: sh run_study4.sh FETCH_PID"; exit 2; fi
if kill -0 "$1" 2>/dev/null; then echo "fetch pid $1 still alive: not starting"; exit 2; fi
date -u +"start %Y-%m-%dT%H:%M:%SZ"
$PY study4.py prep || { echo "prep failed: stop"; exit 1; }
$PY study4.py align || { echo "align crashed: stop"; exit 1; }      # FAIL is recorded in s4_align.json; run makes it INVALID
$PY study4.py gate
gs=$?
if [ $gs -eq 0 ] && [ -f out/s4_gate.json ] && grep -q '"PASS": false' out/s4_gate.json; then
  echo "gate FAILED: fallback F2 (gate99, once)"
  $PY study4.py gate99 || { echo "gate99 crashed: stop"; exit 1; }
elif [ $gs -ne 0 ] && [ -f out/s4_gate.json ]; then
  echo "gate crashed after writing s4_gate.json: stop"; exit 1
fi                                   # gate exits non-zero without s4_gate.json only when < 30 eligible -> run records INVALID
$PY study4.py run
date -u +"end %Y-%m-%dT%H:%M:%SZ"
