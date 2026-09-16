from ...flight_test.flight_state import FlightState
from ...flight_test.handlers import HANDLERS as BASE_HANDLERS
from ..goto_state import GotoState
from .going_to_target import GoingToTargetHandler
from .stabilizing import StabilizingHandler
from .stopping import StoppingHandler

# The base handlers are reused as-is; only the hovering step is replaced
# and two new states are added.
GOTO_HANDLERS = {
    **BASE_HANDLERS,
    FlightState.HOVERING: StabilizingHandler(),
    GotoState.GOING_TO_TARGET: GoingToTargetHandler(),
    GotoState.STOPPING: StoppingHandler(),
}
