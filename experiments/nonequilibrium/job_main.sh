#!/bin/bash
set -e
cd "$(dirname "$0")/../.."
.venv/bin/python -I experiments/nonequilibrium/ne_analyse.py main
