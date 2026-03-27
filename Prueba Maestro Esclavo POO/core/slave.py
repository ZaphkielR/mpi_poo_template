# Lógica del nodo slave.
#
# El slave opera en un ciclo simple: espera una tarea del master,
# la ejecuta y devuelve el resultado. Repite hasta recibir StopMessage.
# No tiene conocimiento de otros slaves ni del estado global del sistema.

from domain.task import Task
from communication.communicator import Communicator
from communication.message import StopMessage, TaskMessage, ResultMessage

from time import sleep
from random import randint


class Slave:
    def __init__(self, comm: Communicator) -> None:
        self._comm = comm

        # El rank se guarda para identificar este proceso en los logs.
        # No se usa para lógica de enrutamiento (eso lo maneja el master).
        self._rank = comm.get_rank()

    def run(self) -> None:
        # Ciclo bloqueante: el slave espera pasivamente hasta recibir un mensaje.
        # Solo el master (rank 0) le envía mensajes, por eso source=0.
        while True:
            message = self._comm.receive(source=0)

            # El StopMessage es la señal de terminación limpia.
            # No hay respuesta: el slave simplemente sale del loop.
            if isinstance(message, StopMessage):
                break

            if isinstance(message, TaskMessage):
                # Se instancia Task con el payload recibido y se ejecuta.
                # Task es el único componente diseñado para ser reemplazado
                # cuando cambie la lógica de procesamiento.
                result = Task(message.payload).execute()

                # Simula latencia variable para demostrar el balanceo dinámico.
                # En producción, esta línea se elimina.
                sleep(randint(1, 5))

                print(f"Proceso {self._rank} terminó tarea {message.task_id} | Resultado: {result}")

                # Devuelve el resultado al master incluyendo el task_id
                # para que el master pueda almacenarlo en la posición correcta.
                self._comm.send(ResultMessage(message.task_id, result), dest=0)