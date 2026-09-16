#!/usr/bin/env python3

import rclpy

from ..flight_test.flight_state import FlightState
from .goto_point_node import GotoPointNode


def main(args=None):
    rclpy.init(args=args)

    node = GotoPointNode()

    try:
        while (
            rclpy.ok()
            and node.state != FlightState.FINISHED
            and node.state != FlightState.ERROR
        ):
            rclpy.spin_once(node, timeout_sec=0.2)

        if node.final_error is not None:
            node.get_logger().info(
                f"Flight finished, position error {node.final_error:.3f} m"
            )

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
