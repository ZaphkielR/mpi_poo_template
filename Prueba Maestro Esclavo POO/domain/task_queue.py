from collections import deque

class TaskQueue:
    def __init__(self, data: list) -> None:
        self._queue: deque[tuple[int, object]] = deque(enumerate(data))

    def has_tasks(self) -> bool:
        return bool(self._queue)
    
    def get_next(self) -> tuple[int, object]:
        return self._queue.popleft()