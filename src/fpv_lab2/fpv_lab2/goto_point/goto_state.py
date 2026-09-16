from enum import Enum, auto


class GotoState(Enum):
    GOING_TO_TARGET = auto()
    STOPPING = auto()
