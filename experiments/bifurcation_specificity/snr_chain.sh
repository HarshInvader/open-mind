#!/bin/sh
# SNR-timing simulation (prereg 2026-11-25_bifurcation_snr_timing.md): primary 3-model run, then 5-model secondary, then summary
nice -n 20 ../../.venv/bin/python -I snr_timing.py run3 && nice -n 20 ../../.venv/bin/python -I snr_timing.py summary
nice -n 20 ../../.venv/bin/python -I snr_timing.py run5 && nice -n 20 ../../.venv/bin/python -I snr_timing.py summary
echo "SNR DONE $(date -u +%FT%TZ)"
