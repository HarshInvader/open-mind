#!/bin/sh
# Open Mind compute: at most 4 workers in total, nice 20 (no -b; coordinator decision 2026-11-25).
# Sealed scripts are not edited: WORKERS is overridden at import. Results do not depend on worker count
# (fixed per-study seeds); finished cells are kept by each script's resume rule.
# The design gate was stopped after DMAX 2 by coordinator decision (see RESULTS.md); it is not run here.
PY="../../.venv/bin/python -I"
cd bifurcation_specificity
nice -n 20 $PY -c "import sys; sys.path.insert(0,'.'); import snr_timing as S; S.WORKERS=4; S.run5(); S.summary()" >> snr_run.log 2>&1
echo "SNR DONE $(date -u +%FT%TZ)" >> snr_run.log
cd ../tg_square_specificity && echo "snr exited; TG starts $(date -u +%FT%TZ)" >> tg_run.log
nice -n 20 $PY -c "import sys; sys.path.insert(0,'.'); import tg_square as T; T.WORKERS=4; T.calibrate(); T.run(); T.summary()" >> tg_run.log 2>&1
echo "TG DONE $(date -u +%FT%TZ)" >> tg_run.log
