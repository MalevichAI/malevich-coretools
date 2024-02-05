from enum import Enum


class AppStatus(Enum):
    RUN = "run"
    WAIT = "wait"
    COMPLETE = "complete"   # = stop, not deleted
    FAIL = "fail"           # = stop, not deleted
    PAUSE = "pause"
    PAUSING = "pausing"
    STOP = "stop"           # deleted


class TaskStatus(Enum):
    COMPLETE = "complete"
    FAIL = "fail"
