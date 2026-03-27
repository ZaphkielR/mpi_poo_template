from domain.task import Task
from communication.communicator import Communicator
from communication.message import StopMessage, TaskMessage, ResultMessage

from time import sleep
from random import randint

class Slave:
    def __init__(self, comm: Communicator) -> None:
        self._comm = comm
        self._rank = comm.get_rank()

    def run(self) -> None:
        while True:
            message = self._comm.receive(source=0)

            if isinstance(message, StopMessage):
                break

            if isinstance(message, TaskMessage):
                result = Task(message.payload).execute()
                sleep(randint(1, 5))

                print(f"Proceso {self._rank} terminó tarea {message.task_id}         Resultado: {result}")
                self._comm.send(ResultMessage(message.task_id, result), dest=0)