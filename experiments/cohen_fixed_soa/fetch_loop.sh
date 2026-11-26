#!/bin/sh
# Orchestration only (not sealed): rerun the sealed fetch until it exits 0, at most 15 attempts, 120 s apart.
# Each attempt resumes per subject. Run from experiments/cohen_fixed_soa/.
LOG=../../datasets/local/cohen2024_nr_fetch.out
i=1
while [ $i -le 15 ]; do
  echo "=== attempt $i $(date -u +%FT%TZ) ===" >> "$LOG"
  nice -n 20 ../../.venv/bin/python -I fetch_noreport.py fetch >> "$LOG" 2>&1 && { echo "=== fetch complete $(date -u +%FT%TZ) ===" >> "$LOG"; exit 0; }
  i=$((i+1)); sleep 120
done
echo "=== gave up after 15 attempts $(date -u +%FT%TZ) ===" >> "$LOG"; exit 1
