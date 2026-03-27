from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class TaskMessage:
    task_id: int
    payload: Any

@dataclass(frozen=True)
class ResultMessage:
    task_id: int
    result: Any

@dataclass(frozen=True)
class StopMessage:
    pass