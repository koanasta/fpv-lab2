"""Additional flight states used by the student algorithm.

The base FlightState enum from the reference project is not modified.
These states are stored in the same handler map next to the base ones,
because a Python dict can hold keys of different enum types.
"""

from enum import Enum, auto


class GotoState(Enum):
    GOING_TO_TARGET = auto()
    STOPPING = auto()
