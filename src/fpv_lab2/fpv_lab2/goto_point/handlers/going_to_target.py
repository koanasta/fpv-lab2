"""Proportional guidance towards the target point with slowdown."""

from typing import TYPE_CHECKING

from ...flight_test.handlers.handler import FlightStateHandler
from ..goto_state import GotoState

if TYPE_CHECKING:
    from ..goto_point_node import GotoPointNode


class GoingToTargetHandler(FlightStateHandler):

    LOG_PERIOD = 5  # print progress every N control cycles

    def __init__(self):
        self._tick = 0

    def handle(self, node: "GotoPointNode") -> None:
        if node.disarmed_unexpectedly():
            node.fail("Drone disarmed unexpectedly during flight")
            return

        position = node.current_position()
        distance = node.distance_to_target()

        if position is None or distance is None:
            return

        # Target reached: stop the horizontal motion.
        if distance <= node.tolerance:
            node.stop_horizontal_motion()

            node.get_logger().info(
                f"Target reached, distance {distance:.3f} m "
                f"(tolerance {node.tolerance:.2f} m)"
            )
            node.state = GotoState.STOPPING
            return

        dx = node.target_position[0] - position[0]
        dy = node.target_position[1] - position[1]

        # Slow down proportionally inside the slowdown radius so that the
        # drone does not overshoot the point.
        speed = node.max_speed * min(1.0, distance / node.slowdown_radius)
        speed = max(speed, node.min_speed)

        node.send_velocity(speed * dx / distance, speed * dy / distance)

        self._tick += 1
        if self._tick % self.LOG_PERIOD == 0:
            node.get_logger().info(
                f"x={position[0]:.2f} y={position[1]:.2f} z={position[2]:.2f} "
                f"| distance {distance:.2f} m | speed {speed:.2f} m/s"
            )
