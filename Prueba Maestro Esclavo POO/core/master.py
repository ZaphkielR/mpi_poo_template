from domain.task_queue import TaskQueue
from communication.communicator import Communicator
from communication.message import TaskMessage, StopMessage, ResultMessage

class Master:
    def __init__(self, comm: Communicator, data: list) -> None:
        self._comm = comm
        self._size = comm.get_size()
        self._queue = TaskQueue(data)
        self._results: list = [None] * len(data)

    def run(self) -> None:
        active_slaves = 0

        # Enviar tareas iniciales
        for slave_rank in range(1, self._size):
            if self._queue.has_tasks():
                task_id, payload = self._queue.get_next()
                self._comm.send(TaskMessage(task_id, payload), slave_rank)
                active_slaves += 1

        # Loop principal
        while active_slaves > 0:
            message, source = self._comm.receive_any()

            if isinstance(message, ResultMessage):
                self._results[message.task_id] = message.result

            if self._queue.has_tasks():
                task_id, payload = self._queue.get_next()
                self._comm.send(TaskMessage(task_id, payload), source)
            else:
                self._comm.send(StopMessage(), source)
                active_slaves -= 1

        print("Resultados:", self._results)