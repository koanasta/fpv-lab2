from ...flight_test.flight_state import FlightState
from ...flight_test.handlers import HANDLERS as BASE_HANDLERS
from ..goto_state import GotoState
from .going_to_target import GoingToTargetHandler
from .prearm_retry import RetryingPrearmCheckHandler
from .stabilizing import StabilizingHandler
from .stopping import StoppingHandler

GOTO_HANDLERS = {
    **BASE_HANDLERS,
    FlightState.PREARM_CHECK: RetryingPrearmCheckHandler(),
    FlightState.HOVERING: StabilizingHandler(),
    GotoState.GOING_TO_TARGET: GoingToTargetHandler(),
    GotoState.STOPPING: StoppingHandler(),
}
