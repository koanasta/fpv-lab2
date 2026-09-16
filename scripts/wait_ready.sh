#!/bin/bash
# Wait until ArduPilot SITL is fully up and the vehicle passes the pre-arm
# check. After a fresh start the EKF needs time to converge on the GPS
# solution; until then pre-arm answers "Vehicle is Not Armable" and the
# flight node stops with an error.
# Source setup_env.sh before calling this script.

TIMEOUT=${1:-300}
DEADLINE=$(( $(date +%s) + TIMEOUT ))

echo "Waiting for the /ap/v1 services..."
while [ "$(date +%s)" -lt "$DEADLINE" ]; do
    if ros2 service list 2>/dev/null | grep -q "/ap/v1/prearm_check"; then
        break
    fi
    sleep 3
done

echo "Waiting for the vehicle to become armable..."
while [ "$(date +%s)" -lt "$DEADLINE" ]; do
    OUT=$(timeout 15 ros2 service call /ap/v1/prearm_check std_srvs/srv/Trigger 2>/dev/null)
    if echo "$OUT" | grep -q "success=True"; then
        echo "Vehicle is armable."
        exit 0
    fi
    sleep 5
done

echo "ERROR: the vehicle did not become armable within ${TIMEOUT}s."
echo "Check the terminal running start_sim.sh for SITL or Gazebo errors."
exit 1
