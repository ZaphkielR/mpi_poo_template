"""
Definición de tipos de mensajes del protocolo de comunicación.

Este módulo define las estructuras de datos inmutables que se intercambian
entre el master y los slaves. Usamos dataclasses con frozen=True para
garantizar inmutabilidad, lo cual es importante porque:
    - Los mensajes se crean, se envían y se consumen
    - No deben modificarse en ningún punto del ciclo de vida
    - Previene errores por modificación accidental

Protocolo de comunicación:
    Master → Slave : TaskMessage   (hay trabajo para ti)
    Master → Slave : StopMessage    (puedes terminar)
    Slave  → Master : ResultMessage (aquí está mi resultado)
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TaskMessage:
    """
    Mensaje que el master envía a un slave para asignarle una tarea.
    
    Attributes:
        task_id: Identificador único de la tarea.
                Necesario para que el master pueda almacenar
                el resultado en la posición correcta de su lista.
        payload: Los datos que la tarea debe procesar.
                Es el elemento original de la lista de datos.
    """
    task_id: int
    payload: Any


@dataclass(frozen=True)
class ResultMessage:
    """
    Mensaje que un slave envía de vuelta al master con el resultado.
    
    Attributes:
        task_id: El mismo task_id recibido en el TaskMessage original.
                Permite al master asociar el resultado con su tarea.
        result: El resultado del procesamiento de la tarea.
                Es lo que retorna Task.execute() o la lógica de procesamiento.
    """
    task_id: int
    result: Any


@dataclass(frozen=True)
class StopMessage:
    """
    Señal de terminación que el master envía a un slave.
    
    Este mensaje no lleva datos útiles. Su mera recepción indica
    al slave que:
        - No hay más tareas disponibles en la cola
        - Debe salir de su bucle de procesamiento
        - Su trabajo en el clúster ha terminado
    
    Es la forma limpia de terminar la ejecución de los slaves,
    en contraste con forzarlos a terminar (que sería不正確).
    """
    pass
