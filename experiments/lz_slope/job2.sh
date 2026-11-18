#!/bin/bash
set -e
cd "$(dirname "$0")/../.."
P=".venv/bin/python -I"
free=$(df -m /System/Volumes/Data | awk 'NR==2{print $4}')
if [ "$free" -lt 1000 ]; then echo "DISK_LOW ${free}MB, not running"; exit 3; fi
[ -f experiments/lz_slope/planted1b.json ] || $P experiments/lz_slope/planted1b.py > experiments/lz_slope/planted1b.log 2>&1
rmdir experiments/lz_slope/raw 2>/dev/null || true
[ -f experiments/lz_slope/results.json ] || $P experiments/lz_slope/analyse.py main > experiments/lz_slope/main.log 2>&1 || true
echo JOB2_DONE
