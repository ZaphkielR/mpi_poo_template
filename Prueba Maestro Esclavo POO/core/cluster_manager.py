# Orquestador del clúster.
#
# Responsabilidad única: determinar el rol de este proceso (master o slave)
# según su rank MPI y delegar la ejecución al objeto correspondiente.
# No contiene lógica de negocio ni de comunicación directa.

from infrastructure.mpi_communicator import MPICommunicator
from core.master import Master
from core.slave import Slave
from config import MASTER_RANK


class ClusterManager:
    def __init__(self, data: list) -> None:
        # El comunicador encapsula toda interacción con MPI.
        # Se instancia aquí para que tanto Master como Slave compartan
        # el mismo objeto de comunicación configurado.
        self.comm = MPICommunicator()

        # El rank identifica a este proceso dentro del clúster (0, 1, 2, ...).
        # Es único por proceso y constante durante toda la ejecución.
        self.rank = self.comm.get_rank()

        # Los datos solo son relevantes para el master, que construirá
        # la cola de tareas a partir de ellos. Los slaves los ignoran.
        self.data = data

    def execute(self) -> None:
        # Todos los procesos llegan aquí, pero solo uno toma el camino del master.
        # Esta bifurcación es el núcleo del patrón master-slave con MPI.
        if self.rank == MASTER_RANK:
            Master(self.comm, self.data).run()
        else:
            Slave(self.comm).run()