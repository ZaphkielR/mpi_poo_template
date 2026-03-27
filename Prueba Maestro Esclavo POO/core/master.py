# Lógica del nodo master.
#
# El master coordina la distribución de trabajo y la recolección de resultados.
# Implementa distribución dinámica: asigna una tarea por slave y solo envía
# la siguiente cuando ese slave reporta su resultado. Esto balancea la carga
# automáticamente cuando las tareas tienen tiempos de ejecución variables.

from domain.task_queue import TaskQueue
from communication.communicator import Communicator
from communication.message import TaskMessage, StopMessage, ResultMessage


class Master:
    def __init__(self, comm: Communicator, data: list) -> None:
        self._comm = comm

        # El tamaño total incluye al master, por eso los slaves van de 1 a size-1.
        self._size = comm.get_size()

        # La cola gestiona el orden y acceso a las tareas pendientes.
        self._queue = TaskQueue(data)

        # Lista preallocada para almacenar resultados en el índice de su task_id,
        # preservando la correspondencia entre dato original y resultado.
        self._results: list = [None] * len(data)

    def run(self) -> None:
        # Contador de slaves activos (que tienen una tarea asignada).
        # El master termina solo cuando todos los slaves han recibido StopMessage.
        active_slaves = 0

        # Fase de calentamiento: se carga un trabajo inicial a cada slave
        # para que todos comiencen a trabajar desde el arranque.
        for slave_rank in range(1, self._size):
            if self._queue.has_tasks():
                task_id, payload = self._queue.get_next()
                self._comm.send(TaskMessage(task_id, payload), slave_rank)
                active_slaves += 1

        # Loop principal: el master espera resultados de cualquier slave (bloqueante).
        # Cuando llega uno, guarda el resultado y decide si asignar otra tarea
        # o enviar la señal de parada a ese slave.
        while active_slaves > 0:
            # receive_any bloquea hasta que cualquier slave envíe un mensaje.
            # Retorna el mensaje y el rank del proceso que lo envió.
            message, source = self._comm.receive_any()

            if isinstance(message, ResultMessage):
                # Almacena el resultado en la posición correspondiente al task_id,
                # no al orden de llegada (que puede ser distinto por tiempos variables).
                self._results[message.task_id] = message.result

            if self._queue.has_tasks():
                # Hay más trabajo: reasigna inmediatamente al slave que acaba de responder.
                task_id, payload = self._queue.get_next()
                self._comm.send(TaskMessage(task_id, payload), source)
            else:
                # Cola vacía: le indica a este slave que puede terminar.
                # Cada slave recibe su propio StopMessage individualmente.
                self._comm.send(StopMessage(), source)
                active_slaves -= 1

        print("Resultados:", self._results)