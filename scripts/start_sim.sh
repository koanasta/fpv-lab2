#!/bin/bash
# Start the whole simulation environment in one command:
# Gazebo (maze world) + ArduPilot SITL + micro-ROS DDS agent + RViz.
#
# ArduPilot SITL writes its working files (eeprom.bin, mav.tlog, logs,
# terrain) into the current directory, so the run directory is used.

set -e
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"

"$SCRIPTS/stop_sim.sh"

source "$SCRIPTS/setup_env.sh"

RUN_DIR=$HOME/fpv_labs/run
mkdir -p "$RUN_DIR"
cd "$RUN_DIR"

echo "Starting Gazebo + ArduPilot SITL + ROS 2 ..."
echo "Working directory: $RUN_DIR"
echo "Leave this terminal open. Use Ctrl+C or ./stop_sim.sh to stop."

exec ros2 launch ardupilot_gz_bringup iris_maze.launch.py "$@"
