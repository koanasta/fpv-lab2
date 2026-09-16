#!/bin/bash
# Task 4: fly to the individually assigned point and land.
# The simulation must already be running (./start_sim.sh).
#
# Usage:  ./run_goto_point.sh <delta_x> <delta_y> [axis_direction]
# Example (variant 13):  ./run_goto_point.sh 4.0 0.2
#
# axis_direction defaults to 1 (target = start + delta). Pass -1 to follow
# the formula of Appendix 2 literally (target = start - delta) - in the real
# maze.sdf that direction runs into a wall, see DEPLOY.md.

set -e
cd "$(dirname "$0")"
source ./setup_env.sh

DX=${1:?delta_x is required, see Appendix 2 of the lab manual}
DY=${2:?delta_y is required, see Appendix 2 of the lab manual}
DIR=${3:-1.0}

./wait_ready.sh 300

LOG=$HOME/fpv_labs/logs/goto_point_$(date +%Y%m%d_%H%M%S).log
mkdir -p "$(dirname "$LOG")"

echo "delta_x=$DX  delta_y=$DY  axis_direction=$DIR"
echo "Log file: $LOG"

ros2 run fpv_lab2 goto_point --ros-args \
    -p delta_x:=$DX \
    -p delta_y:=$DY \
    -p axis_direction:=$DIR 2>&1 | tee "$LOG"
