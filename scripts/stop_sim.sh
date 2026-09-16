#!/bin/bash

PATTERNS="gz sim|ruby.*gz|arducopter|micro_ros_agent|MicroXRCEAgent|rviz2|mavproxy|parameter_bridge|robot_state_publisher|ros_gz_sim"
PORTS="5760 5501 2019 9002 14550 14551"

echo "Stopping simulation processes..."
pkill -f "$PATTERNS" 2>/dev/null

for i in $(seq 1 10); do
    pgrep -f "$PATTERNS" >/dev/null 2>&1 || break
    sleep 1
done

if pgrep -f "$PATTERNS" >/dev/null 2>&1; then
    echo "Some processes ignored SIGTERM, sending SIGKILL..."
    pkill -9 -f "$PATTERNS" 2>/dev/null
    sleep 2
fi

echo "Waiting for ports to be released..."
for i in $(seq 1 30); do
    BUSY=""
    for P in $PORTS; do
        if ss -lntu 2>/dev/null | grep -qE "[:.]$P\b"; then
            BUSY="$BUSY $P"
        fi
    done
    if [ -z "$BUSY" ]; then
        echo "All simulation processes stopped, ports are free."
        exit 0
    fi
    sleep 1
done

echo "WARNING: these ports are still busy:$BUSY"
echo "Processes still running:"
pgrep -fa "$PATTERNS"
exit 1
