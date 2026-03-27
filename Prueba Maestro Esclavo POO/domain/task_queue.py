# Cola de tareas pendientes.
#
# Gestiona el acceso ordenado a las tareas que el master debe distribuir.
# Usa deque internamente porque es la estructura correcta para este patrón:
# se consume siempre por el frente (FIFO) y deque.popleft() es O(1),
# mientras que list.pop(0) desplaza todos los elementos restantes (O(n)).

from collections import deque


class TaskQueue:
    def __init__(self, data: list) -> None:
        # enumerate asigna un índice único (task_id) a cada elemento.
        # Ese task_id viaja con la tarea y permite al master guardar
        # el resultado en la posición correcta de self._results.
        self._queue: deque[tuple[int, object]] = deque(enumerate(data))

    def has_tasks(self) -> bool:
        # deque vacío es falsy en Python, por lo que bool() es suficiente.
        return bool(self._queue)

    def get_next(self) -> tuple[int, object]:
        # Extrae y retorna el siguiente (task_id, payload) de la cola.
        # popleft() es O(1) a diferencia de list.pop(0) que es O(n).
        return self._queue.popleft()