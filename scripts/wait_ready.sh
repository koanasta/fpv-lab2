#!/bin/bash

TIMEOUT=${1:-300}
DEADLINE=$(( $(date +%s) + TIMEOUT ))

echo "Waiting for the /ap/v1 services..."
while [ "$(date +%s)" -lt "$DEADLINE" ]; do
    if ros2 service list 2>/dev/null | grep -q "/ap/v1/prearm_check"; then
        break
    fi
    sleep 3
done

REQUIRED=3
STREAK=0

echo "Waiting for the vehicle to become armable..."
while [ "$(date +%s)" -lt "$DEADLINE" ]; do
    OUT=$(timeout 15 ros2 service call /ap/v1/prearm_check std_srvs/srv/Trigger 2>/dev/null)
    if echo "$OUT" | grep -q "success=True"; then
        STREAK=$((STREAK + 1))
        echo "  pre-arm passed ($STREAK/$REQUIRED)"
        if [ "$STREAK" -ge "$REQUIRED" ]; then
            echo "Vehicle is armable."
            exit 0
        fi
    else
        if [ "$STREAK" -gt 0 ]; then
            echo "  pre-arm flipped back to not armable, restarting the count"
        fi
        STREAK=0
    fi
    sleep 4
done

echo "ERROR: the vehicle did not become armable within ${TIMEOUT}s."
echo "Check the terminal running start_sim.sh for SITL or Gazebo errors."
exit 1
