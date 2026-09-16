"""ROS 2 node that flies the drone to an individually assigned point.

The node reuses FlightTestNode from the reference project without
modifying it: take-off, arming and landing logic stay exactly the same.
Only the hovering phase is replaced by horizontal navigation towards
the target point.

Target point (Appendix 2 of the lab manual):
    x_target = x0 - delta_x
    y_target = y0 - delta_y
where (x0, y0) is the position actually measured at start-up.
"""

import math

from geometry_msgs.msg import TwistStamped

from ..flight_test.flight_test_node import FlightTestNode
from .handlers import GOTO_HANDLERS


class GotoPointNode(FlightTestNode):

    def __init__(self):
        super().__init__()

        # Use the extended handler map instead of the base one.
        self._handlers = GOTO_HANDLERS

        self.declare_parameter("delta_x", 0.0)
        self.declare_parameter("delta_y", 0.0)
        self.declare_parameter("takeoff_altitude", 2.0)
        self.declare_parameter("tolerance", 0.25)
        self.declare_parameter("max_speed", 1.5)
        self.declare_parameter("min_speed", 0.15)
        self.declare_parameter("slowdown_radius", 2.5)
        self.declare_parameter("stabilize_duration", 5.0)
        # Appendix 2 of the manual defines the target as x0 - delta_x.
        # Measured against the real maze.sdf, that direction runs into
        # Wall_9 (x = -1 m) for all 56 variants, while the manual states
        # that no route crosses a wall. The axis of the manual is therefore
        # opposite to the x axis of /odometry, so the offset is applied with
        # this sign. Set it to -1.0 to follow the manual literally.
        self.declare_parameter("axis_direction", 1.0)

        self.axis_direction = self.get_parameter("axis_direction").value
        self.delta_x = self.get_parameter("delta_x").value * self.axis_direction
        self.delta_y = self.get_parameter("delta_y").value * self.axis_direction
        self.tolerance = self.get_parameter("tolerance").value
        self.max_speed = self.get_parameter("max_speed").value
        self.min_speed = self.get_parameter("min_speed").value
        self.slowdown_radius = self.get_parameter("slowdown_radius").value
        self.stabilize_duration = self.get_parameter("stabilize_duration").value

        # Override the take-off altitude of the base class per instance.
        self.TAKEOFF_ALTITUDE = self.get_parameter("takeoff_altitude").value

        # HOVER_DURATION of the base class is reused as the stabilisation
        # time before navigation starts.
        self.HOVER_DURATION = self.stabilize_duration

        # /ap/v1/status is published at a lower rate than the control loop,
        # so right after arming it can still report armed=False. Treat a
        # false reading as a real disarm only after the drone was actually
        # seen armed at least once.
        self.seen_armed = False

        self.start_position = None
        self.target_position = None
        self.altitude_reached_at = None
        self.stop_started_at = None
        self.final_position = None
        self.final_error = None

        self.cmd_vel_publisher = self.create_publisher(
            TwistStamped,
            "/ap/v1/cmd_vel",
            10,
        )

        self.get_logger().info(
            f"Target offset applied: dx={self.delta_x:+.2f} m, "
            f"dy={self.delta_y:+.2f} m (axis_direction={self.axis_direction:+.0f})"
        )

    def status_callback(self, message):
        super().status_callback(message)

        if message.armed:
            self.seen_armed = True

    def disarmed_unexpectedly(self):
        """True only if the drone was armed before and is not armed now."""
        if self.status is None:
            return False

        return self.seen_armed and not self.status.armed

    def odometry_callback(self, message):
        """Remember the very first measured position as the start point."""
        super().odometry_callback(message)

        if self.start_position is None:
            x0 = message.pose.pose.position.x
            y0 = message.pose.pose.position.y

            self.start_position = (x0, y0)
            # delta_x / delta_y already carry the sign of axis_direction
            self.target_position = (x0 + self.delta_x, y0 + self.delta_y)

            self.get_logger().info(
                f"Start position:  x0={x0:.3f} m, y0={y0:.3f} m"
            )
            self.get_logger().info(
                f"Target position: x={self.target_position[0]:.3f} m, "
                f"y={self.target_position[1]:.3f} m"
            )

    def current_position(self):
        if self.odometry is None:
            return None

        position = self.odometry.pose.pose.position
        return (position.x, position.y, position.z)

    def distance_to_target(self):
        """Horizontal distance to the target point, or None if unknown."""
        position = self.current_position()

        if position is None or self.target_position is None:
            return None

        dx = self.target_position[0] - position[0]
        dy = self.target_position[1] - position[1]

        return math.hypot(dx, dy)

    def send_velocity(self, vx, vy):
        """Publish a horizontal velocity command in the ENU map frame.

        For frame_id "map" ArduPilot reads twist.linear.x as the East
        component and twist.linear.y as the North component.
        """
        message = TwistStamped()
        message.header.stamp = self.get_clock().now().to_msg()
        message.header.frame_id = "map"
        message.twist.linear.x = float(vx)
        message.twist.linear.y = float(vy)
        message.twist.linear.z = 0.0
        message.twist.angular.z = 0.0

        self.cmd_vel_publisher.publish(message)

    def stop_horizontal_motion(self):
        self.send_velocity(0.0, 0.0)
