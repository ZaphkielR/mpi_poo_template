"""
Lógica del proceso maestro (master).

El master es el proceso coordinator del sistema. Su responsabilidad principal
es distribuir tareas a los slaves y recopilar los resultados.

Patrón de distribución:
    - Distribución dinámica (work-stealing): el master envía una tarea a cada
      slave y, cuando un slave completa su trabajo, le envía otra tarea si hay
      disponibles. Esto balancea la carga automáticamente.
    
Flujo de ejecución:
    1. Fase de calentamiento: envía una tarea inicial a cada slave
    2. Loop principal: espera resultados y asigna nuevas tareas
    3. Finalización: envía señal de StopMessage a cada slave

El master usa receive_any() para esperar resultados de cualquier slave,
lo que permite responder inmediatamente al slave que termine primero.
"""

from domain.task_queue import TaskQueue
from communication.communicator import Communicator
from communication.message import TaskMessage, StopMessage, ResultMessage


class Master:
    """
    Coordinator del sistema distribuido.
    
    Attributes:
        _comm: Comunicador MPI para enviar/recibir mensajes
        _size: Número total de procesos en el clúster (incluye al master)
        _queue: Cola de tareas pendientes por procesar
        _results: Lista de resultados indexada por task_id
    """
    
    def __init__(self, comm: Communicator, data: list) -> None:
        """
        Inicializa el master con los datos a procesar.
        
        Args:
            comm: Instancia del comunicador MPI
            data: Lista de datos que se convertirán en tareas
        """
        # Referencia al comunicador para operaciones MPI
        self._comm = comm
        
        # Obtiene el número total de procesos
        # Si hay 4 procesos (mpirun -n 4), size = 4
        # Los slaves tienen rank 1, 2, 3 (size-1 slaves)
        self._size = comm.get_size()
        
        # Crea la cola de tareas a partir de los datos
        # Cada elemento de data se convierte en una tarea con task_id
        self._queue = TaskQueue(data)
        
        # Pre-aloca la lista de resultados con el tamaño correcto
        # Se indexa por task_id para mantener correspondencia dato-resultado
        # [None, None, None, ..., None] con longitud = len(data)
        self._results: list = [None] * len(data)

    def run(self) -> None:
        """
        Ejecuta el ciclo de coordinación del master.
        
        Algoritmo:
        1. ENVÍO INICIAL: Envía una tarea a cada slave (fase de calentamiento)
        2. LOOP: Espera resultados y asigna nuevas tareas o indica parada
        3. TERMINACIÓN: Todos los slaves recibieron StopMessage
        """
        # Contador de slaves que actualmente tienen una tarea asignada
        # El master espera este número de respuestas antes de terminar
        active_slaves = 0
        
        # =========================================================================
        # FASE 1: Envío inicial de tareas (calentamiento / warm-up)
        # =========================================================================
        # Envía una tarea a cada slave para que todos empiecen a trabajar
        # Itera desde rank 1 hasta size-1 (todos los slaves)
        for slave_rank in range(1, self._size):
            # Solo envía si hay tareas disponibles en la cola
            if self._queue.has_tasks():
                # Extrae la siguiente tarea (task_id, payload)
                task_id, payload = self._queue.get_next()
                
                # Envía TaskMessage al slave con el rank especificado
                self._comm.send(TaskMessage(task_id, payload), slave_rank)
                
                # Incrementa el contador de slaves activos
                active_slaves += 1
        
        # =========================================================================
        # FASE 2: Loop principal - distribución dinámica
        # =========================================================================
        # El master espera resultados de cualquier slave y responde
        # inmediatamente enviando otra tarea o la señal de parada
        while active_slaves > 0:
            """
            Bloquea hasta recibir un mensaje de cualquier slave.
            
            receive_any() retorna:
                - message: el mensaje recibido (puede ser ResultMessage)
                - source: el rank del proceso que envió el mensaje
            """
            message, source = self._comm.receive_any()
            
            # Verifica si el mensaje recibido es un resultado
            if isinstance(message, ResultMessage):
                # Almacena el resultado en la posición对应的task_id
                # Esto preserva la correspondencia dato original -> resultado
                self._results[message.task_id] = message.result
            
            # Decide qué hacer con el slave que respondió:
            if self._queue.has_tasks():
                # Hay más tareas pendientes: envía otra tarea al slave
                task_id, payload = self._queue.get_next()
                self._comm.send(TaskMessage(task_id, payload), source)
                # El slave sigue activo (active_slaves no cambia)
            else:
                # No hay más tareas: indica al slave que puede terminar
                self._comm.send(StopMessage(), source)
                # Este slave ya no está activo
                active_slaves -= 1
        
        # =========================================================================
        # FASE 3: Finalización
        # =========================================================================
        # Todos los slaves recibieron StopMessage
        # Imprime los resultados collectedos
        print("Resultados:", self._results)
