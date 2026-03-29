"""
Orquestador principal del clúster.

Esta clase es responsable de:
1. Inicializar el comunicador MPI
2. Determinar el rol de este proceso (master o slave) según su rank
3. Delegar la ejecución al componente correspondiente

El ClusterManager es el punto de entrada único para ejecutar el sistema.
Cada proceso MPI ejecuta este mismo código, pero se bifurca según su rol.
"""

from communication.communicator import Communicator
from core.master import Master
from core.slave import Slave
from config import MASTER_RANK


class ClusterManager:
    """
    Gestor del clúster que coordina la ejecución maestro-esclavo.
    
    Attributes:
        comm: Instancia del comunicador MPI compartida entre master y slave
        rank: Identificador único de este proceso en el clúster MPI
        data: Datos a procesar (solo relevante para el master)
    """
    
    def __init__(self, data: list) -> None:
        """
        Inicializa el gestor del clúster.
        
        Args:
            data: Lista de datos a procesar como tareas.
                  El master la usará para crear la cola de tareas.
        """
        # Inicializa el comunicador MPI
        # Este objeto encapsula todas las operaciones de comunicación
        # (send, receive, etc.) y es compartido por Master y Slave
        self.comm = Communicator()
        
        # Obtiene el rank (identificador) de este proceso en MPI
        # Rango válido: [0, size-1]
        # - rank 0: proceso maestro
        # - rank 1+: procesos esclavos
        self.rank = self.comm.get_rank()
        
        # Almacena los datos recibidos
        # Solo el master los usará para crear tareas
        # Los slaves ignoran este valor
        self.data = data

    def execute(self) -> None:
        """
        Ejecuta el flujo correspondiente según el rol del proceso.
        
        Esta es la bifurcación principal del patrón maestro-esclavo:
        - Si rank == 0: ejecuta la lógica del Master
        - Si rank > 0: ejecuta la lógica del Slave
        
        Importante: Todos los procesos llaman a este método,
        pero solo uno toma el camino del master.
        """
        # Verifica si este proceso es el master
        if self.rank == MASTER_RANK:
            # Proceso master: coordina tareas y recibe resultados
            Master(self.comm, self.data).run()
        else:
            # Proceso slave: ejecuta tareas asignadas por el master
            Slave(self.comm).run()
