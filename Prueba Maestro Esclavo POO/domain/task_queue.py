"""
Cola de tareas pendientes para el patrón maestro-esclavo.

Gestiona el acceso ordenado a las tareas que el master debe distribuir
a los slaves. Implementa una cola FIFO (First In, First Out).

¿Por qué usar deque en lugar de list?
    - deque.popleft() es O(1) (tiempo constante)
    - list.pop(0) es O(n) porque desplaza todos los elementos
    
Para sistemas con muchas tareas, esta diferencia de rendimiento es significativa.
"""

from collections import deque


class TaskQueue:
    """
    Cola de tareas con acceso FIFO.
    
    Attributes:
        _queue: Cola interna que almacena tuplas (task_id, payload)
    """
    
    def __init__(self, data: list) -> None:
        """
        Inicializa la cola con los datos recibidos.
        
        Args:
            data: Lista de elementos que se convertirán en tareas.
                  Cada elemento será el payload de una tarea.
        
        Implementation:
            - Usa enumerate() para asignar un task_id único a cada elemento
            - El task_id permite al master mantener la correspondencia
              entre el dato original y su posición en la lista de resultados
        """
        # enumerate() crea tuplas (índice, elemento)
        # Ejemplo: [10, 20, 30] -> [(0, 10), (1, 20), (2, 30)]
        self._queue: deque[tuple[int, object]] = deque(enumerate(data))

    def has_tasks(self) -> bool:
        """
        Verifica si hay tareas pendientes en la cola.
        
        Returns:
            True si la cola no está vacía, False en caso contrario.
        
        Note:
            Un deque vacío es falsy en Python, por lo que bool()
            es suficiente sin necesidad de len() > 0.
        """
        return bool(self._queue)

    def get_next(self) -> tuple[int, object]:
        """
        Extrae y retorna la siguiente tarea de la cola.
        
        Returns:
            Tupla (task_id, payload) de la siguiente tarea.
            La tarea se REMUEVE de la cola.
        
        Raises:
            IndexError: Si se llama cuando la cola está vacía.
                      Quien llame debe verificar con has_tasks() primero.
        
        Performance:
            popleft() es O(1) gracias a la implementación de deque
            como cola de doble extremo.
        """
        # Extrae y retorna el elemento del frente de la cola
        # Este es el elemento más antiguo (FIFO)
        return self._queue.popleft()
