#!/bin/sh
# waits for the bifurcation SNR chain (5-model secondary) to exit, then calibrates, runs and summarises
while kill -0 "$(cat ../bifurcation_specificity/snr.pid)" 2>/dev/null; do sleep 60; done
echo "snr chain exited; TG starts $(date -u +%FT%TZ)"
nice -n 20 ../../.venv/bin/python -I tg_square.py calibrate && nice -n 20 ../../.venv/bin/python -I tg_square.py run && nice -n 20 ../../.venv/bin/python -I tg_square.py summary
echo "TG DONE $(date -u +%FT%TZ)"
