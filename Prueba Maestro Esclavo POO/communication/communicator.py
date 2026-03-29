"""
Capa de abstracción para comunicaciones MPI.

Esta clase encapsula todas las operaciones directas con la librería mpi4py,
proporcionando una interfaz más simple y consistente para el resto del código.

¿Por qué encapsular MPI?
    - Separa la lógica de negocio de la tecnología de comunicación
    - Facilita testing (se podría inyectar un comunicador mock)
    - Oculta los detalles de la API de mpi4py (que usa PascalCase)
    - Proporciona una API más limpia con snake_case

Operaciones disponibles:
    - send(): Envío punto-a-punto a un proceso específico
    - receive(): Recepción desde un proceso específico
    - receive_any(): Recepción desde cualquier proceso (ANY_SOURCE)
    - get_rank(): Obtener el rank de este proceso
    - get_size(): Obtener el número total de procesos
"""

from typing import Any


class Communicator:
    """
    Wrapper alrededor de mpi4py que simplifica la comunicación MPI.
    
    Attributes:
        _comm: Instancia del comunicador MPI de mpi4py
    """
    
    def __init__(self) -> None:
        """
        Inicializa el comunicador conectándose a COMM_WORLD.
        
        COMM_WORLD es el comunicador global de MPI que incluye todos los
        procesos lanzados por mpirun. Es el punto de entrada estándar
        para comunicación entre procesos.
        """
        from mpi4py import MPI
        # COMM_WORLD representa todos los procesos del comunicador global
        # Es el equivalente a MPI.COMM_WORLD en C/Fortran
        self._comm = MPI.COMM_WORLD

    def send(self, data: Any, dest: int) -> None:
        """
        Envía un mensaje a un proceso destino específico.
        
        Este es un envío síncrono (bloqueante): la función no retorna
        hasta que el mensaje es Copiado al buffer del sistema y está
        listo para ser recibido por el destino.
        
        Args:
            data: Objeto a enviar (debe ser serializable por pickle)
            dest: Rank del proceso destino (0, 1, 2, ...)
        
        Example:
            # Envía un mensaje al proceso con rank 2
            comm.send(mi_mensaje, dest=2)
        """
        self._comm.send(data, dest=dest)

    def receive(self, source: int) -> Any:
        """
        Recibe un mensaje desde un proceso específico.
        
        Esta es una recepción bloqueante: el proceso queda suspendido
        (en espera) hasta que llegue un mensaje del fuente especificado.
        
        Args:
            source: Rank del proceso fuente (0, 1, 2, ...)
                   Use MPI.ANY_SOURCE para recibir de cualquier proceso
        
        Returns:
            El objeto recibido desde el proceso fuente
        
        Example:
            # Espera un mensaje del master (rank 0)
            mensaje = comm.receive(source=0)
        """
        return self._comm.recv(source=source)

    def receive_any(self) -> tuple[Any, int]:
        """
        Recibe un mensaje desde cualquier proceso (ANY_SOURCE).
        
        Útil para el master que necesita recibir resultados de cualquier
        slave sin saber cuál terminará primero. Implementa el patrón
        "cualquier fuente" de MPI.
        
        Returns:
            Tupla (mensaje, rank_fuente)
            - mensaje: el objeto recibido
            - rank_fuente: el rank del proceso que envió el mensaje
        
        Example:
            mensaje, fuente = comm.receive_any()
            # fuente puede ser 1, 2, 3, etc. dependiendo de quién envió
        """
        from mpi4py import MPI
        
        # Status es un objeto que contiene metadatos del mensaje recibido
        status = MPI.Status()
        
        # Recibe desde cualquier fuente (MPI.ANY_SOURCE)
        # Pero captura el rank real del emisor en 'status'
        data = self._comm.recv(source=MPI.ANY_SOURCE, status=status)
        
        # Extrae el rank real del emisor desde el status
        source_rank = status.Get_source()
        
        return data, source_rank

    def get_rank(self) -> int:
        """
        Obtiene el rank (identificador) de este proceso en el comunicador.
        
        El rank es un entero único en el rango [0, size-1].
        Se usa para identificar este proceso en la comunicación.
        
        Returns:
            El rank de este proceso
        
        Example:
            Mi rank en el clúster: 3
        """
        return self._comm.Get_rank()

    def get_size(self) -> int:
        """
        Obtiene el número total de procesos en el comunicador.
        
        Equivale al argumento N de 'mpirun -n N'.
        
        Returns:
            Número total de procesos en el comunicador
        
        Example:
            # Si se ejecutó: mpirun -n 4 python main.py
            # get_size() retorna 4
        """
        return self._comm.Get_size()
