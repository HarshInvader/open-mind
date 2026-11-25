#!/bin/sh
# waits for the extended run (pid in ext_resume.pid) to exit, then runs the design gate
while kill -0 "$(cat ext_resume.pid)" 2>/dev/null; do sleep 30; done
echo "extended run exited; gate starts $(date -u +%FT%TZ)"
nice -n 20 ../../.venv/bin/python -I gate_design.py run && nice -n 20 ../../.venv/bin/python -I gate_design.py summary
echo "GATE DONE $(date -u +%FT%TZ)"
