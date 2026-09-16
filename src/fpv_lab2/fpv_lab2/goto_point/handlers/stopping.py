"""Damp the residual horizontal speed, record the result, then land."""

import math
import time
from typing import TYPE_CHECKING

from ...flight_test.flight_state import FlightState
from ...flight_test.handlers.handler import FlightStateHandler

if TYPE_CHECKING:
    from ..goto_point_node import GotoPointNode


class StoppingHandler(FlightStateHandler):

    SETTLE_TIMEOUT = 5.0   # seconds
    SPEED_EPSILON = 0.15   # m/s

    def handle(self, node: "GotoPointNode") -> None:
        node.stop_horizontal_motion()

        if node.stop_started_at is None:
            node.stop_started_at = time.monotonic()

        twist = node.odometry.twist.twist if node.odometry is not None else None
        speed = math.hypot(twist.linear.x, twist.linear.y) if twist else 0.0

        elapsed = time.monotonic() - node.stop_started_at

        if speed > self.SPEED_EPSILON and elapsed < self.SETTLE_TIMEOUT:
            return

        position = node.current_position()

        if position is not None and node.target_position is not None:
            error = math.hypot(
                position[0] - node.target_position[0],
                position[1] - node.target_position[1],
            )

            node.final_position = position
            node.final_error = error

            node.get_logger().info("----- RESULT -----")
            node.get_logger().info(
                f"Start position:  x={node.start_position[0]:.3f} "
                f"y={node.start_position[1]:.3f}"
            )
            node.get_logger().info(
                f"Target position: x={node.target_position[0]:.3f} "
                f"y={node.target_position[1]:.3f}"
            )
            node.get_logger().info(
                f"Actual position: x={position[0]:.3f} "
                f"y={position[1]:.3f} z={position[2]:.3f}"
            )
            node.get_logger().info(f"Position error:  e={error:.3f} m")
            node.get_logger().info("------------------")

        node.get_logger().info("Horizontal motion stopped, starting landing")
        node.state = FlightState.LANDING
