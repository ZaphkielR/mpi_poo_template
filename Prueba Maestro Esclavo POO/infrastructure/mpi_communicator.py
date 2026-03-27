# Implementación del comunicador usando mpi4py.
#
# Encapsula toda la interacción directa con la librería MPI en un único lugar.
# El resto del sistema (Master, Slave, ClusterManager) no importa mpi4py directamente,
# lo que aísla la dependencia y facilita reemplazar o extender el transporte
# sin modificar la lógica de negocio.
#
# La API de mpi4py usa PascalCase (Get_rank, COMM_WORLD), mientras que
# este wrapper expone snake_case para mantener consistencia con el estilo Python.

from mpi4py import MPI
from typing import Any


class MPICommunicator:
    def __init__(self) -> None:
        # COMM_WORLD es el comunicador global de MPI que incluye todos los procesos
        # lanzados por mpirun. Es el punto de entrada estándar para comunicación colectiva.
        self._comm = MPI.COMM_WORLD

    def send(self, data: Any, dest: int) -> None:
        # Envío punto a punto bloqueante: espera hasta que el mensaje
        # sea recibido por el buffer del sistema antes de continuar.
        self._comm.send(data, dest=dest)

    def receive(self, source: int) -> Any:
        # Recepción bloqueante desde un proceso específico.
        # El proceso queda suspendido hasta que llegue el mensaje.
        return self._comm.recv(source=source)

    def receive_any(self) -> tuple[Any, int]:
        # Recepción bloqueante desde cualquier proceso (ANY_SOURCE).
        # Status captura metadatos del mensaje, incluyendo el rank del emisor,
        # que se necesita para saber a qué slave responder.
        status = MPI.Status()
        data = self._comm.recv(source=MPI.ANY_SOURCE, status=status)
        return data, status.Get_source()

    def get_rank(self) -> int:
        # Rank de este proceso: entero único en el rango [0, size-1].
        return self._comm.Get_rank()

    def get_size(self) -> int:
        # Número total de procesos en el comunicador (el N de `mpirun -n N`).
        return self._comm.Get_size()