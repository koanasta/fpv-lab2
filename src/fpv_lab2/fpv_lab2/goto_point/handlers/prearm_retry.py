"""Pre-arm check that tolerates a transient "not armable" answer.

Right after start-up the EKF solution is still settling, so ArduPilot can
answer "Vehicle is Armable" once and "Vehicle is Not Armable" a couple of
seconds later. The reference handler treats the first negative answer as a
fatal error. This handler retries for a while and only gives up if the
vehicle stays unarmable.
"""

import time
from functools import partial
from typing import TYPE_CHECKING

from std_srvs.srv import Trigger

from ...flight_test.flight_state import FlightState
from ...flight_test.handlers.handler import FlightStateHandler

if TYPE_CHECKING:
    from ..goto_point_node import GotoPointNode


class RetryingPrearmCheckHandler(FlightStateHandler):

    RETRY_DELAY = 3.0     # seconds between attempts
    MAX_WAIT = 180.0      # give up after this long

    def __init__(self):
        self._first_attempt_at = None
        self._next_attempt_at = 0.0

    def handle(self, node: "GotoPointNode") -> None:
        if node.request_in_progress:
            return

        now = time.monotonic()

        if self._first_attempt_at is None:
            self._first_attempt_at = now

        if now < self._next_attempt_at:
            return

        self.call_prearm_check(node)

    def call_prearm_check(self, node: "GotoPointNode") -> None:
        node.request_in_progress = True

        request = Trigger.Request()
        future = node.prearm_client.call_async(request)
        future.add_done_callback(partial(self.prearm_callback, node))

        node.get_logger().info("Running pre-arm check")

    def prearm_callback(self, node: "GotoPointNode", future) -> None:
        node.request_in_progress = False

        try:
            response = future.result()
        except Exception as error:
            node.fail(f"Pre-arm service failed: {error}")
            return

        if not response.success:
            waited = time.monotonic() - self._first_attempt_at

            if waited > self.MAX_WAIT:
                node.fail(f"Vehicle is not armable: {response.message}")
                return

            node.get_logger().info(
                f"Vehicle not armable yet ({response.message}), "
                f"retrying in {self.RETRY_DELAY:.0f} s "
                f"[{waited:.0f}/{self.MAX_WAIT:.0f} s]"
            )
            self._next_attempt_at = time.monotonic() + self.RETRY_DELAY
            return

        node.get_logger().info(f"Pre-arm check passed: {response.message}")
        node.state = FlightState.SETTING_GUIDED
