#!/bin/bash
# Task 3: run the reference example (take off, hover, land).
# The simulation must already be running (./start_sim.sh).

set -e
cd "$(dirname "$0")"
source ./setup_env.sh

./wait_ready.sh 300

LOG=$HOME/fpv_labs/logs/flight_test_$(date +%Y%m%d_%H%M%S).log
mkdir -p "$(dirname "$LOG")"
echo "Log file: $LOG"

ros2 run fpv_lab2 flight_test 2>&1 | tee "$LOG"
