"""Wait until the drone reaches the take-off altitude and settles.

Important: no velocity command may be published here. In GUIDED mode a
command on /ap/v1/cmd_vel overrides the running TAKEOFF command, and the
drone never leaves the ground.
"""

import time
from typing import TYPE_CHECKING

from ...flight_test.handlers.handler import FlightStateHandler
from ..goto_state import GotoState

if TYPE_CHECKING:
    from ..goto_point_node import GotoPointNode


class StabilizingHandler(FlightStateHandler):

    ALTITUDE_FRACTION = 0.9   # share of the target altitude counted as reached
    TAKEOFF_TIMEOUT = 60.0    # seconds

    def handle(self, node: "GotoPointNode") -> None:
        if node.disarmed_unexpectedly():
            node.fail("Drone disarmed unexpectedly during flight")
            return

        position = node.current_position()

        if position is None:
            return

        altitude = position[2]
        elapsed = time.monotonic() - node.hover_started_at

        required = node.TAKEOFF_ALTITUDE * self.ALTITUDE_FRACTION

        if altitude < required:
            if elapsed > self.TAKEOFF_TIMEOUT:
                node.fail(
                    f"Take-off timed out, altitude {altitude:.2f} m "
                    f"instead of {node.TAKEOFF_ALTITUDE:.2f} m"
                )
            return

        if node.altitude_reached_at is None:
            node.altitude_reached_at = time.monotonic()
            node.get_logger().info(
                f"Take-off altitude reached: {altitude:.2f} m"
            )
            return

        # Hold the position for a short while so the drone settles.
        if time.monotonic() - node.altitude_reached_at < node.stabilize_duration:
            return

        if node.target_position is None:
            node.fail("No odometry received, target point is unknown")
            return

        node.get_logger().info(
            "Hover stabilised, starting flight to the target point"
        )
        node.state = GotoState.GOING_TO_TARGET
