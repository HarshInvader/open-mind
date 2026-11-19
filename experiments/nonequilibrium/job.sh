#!/bin/bash
# NE test, all steps resumable. Run: board/run.sh experiments/nonequilibrium/job.sh
set -e
cd "$(dirname "$0")/../.."
P=".venv/bin/python -I"
$P experiments/nonequilibrium/extract.py ds005620
$P experiments/nonequilibrium/extract.py chennu
$P experiments/nonequilibrium/ne_analyse.py power
$P experiments/nonequilibrium/ne_analyse.py main
