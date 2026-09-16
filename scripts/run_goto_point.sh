#!/bin/bash
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
