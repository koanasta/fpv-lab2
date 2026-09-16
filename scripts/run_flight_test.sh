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

# use_sim_time is required here. The node timer runs on the wall clock, while
# ArduPilot publishes /ap/v1/status every 100 ms of SIMULATION time. With a
# real-time factor around 0.25 that is ~400 ms of wall time, so the hovering
# handler of the reference example read a stale armed=False and aborted with
# "Drone disarmed unexpectedly". Running the node on simulation time keeps the
# control loop and the status topic on the same clock. The reference code
# itself is not modified.
ros2 run fpv_lab2 flight_test --ros-args -p use_sim_time:=true 2>&1 | tee "$LOG"
