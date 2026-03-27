# Tipos de mensajes intercambiados entre master y slaves.
#
# Cada mensaje es un dataclass inmutable (frozen=True) que representa
# un evento puntual en el protocolo de comunicación. La inmutabilidad
# es intencional: los mensajes se crean, se envían y se consumen;
# no deben modificarse en ningún punto del ciclo de vida.
#
# Protocolo de mensajes:
#   Master → Slave : TaskMessage  (hay trabajo para ti)
#   Master → Slave : StopMessage  (puedes terminar)
#   Slave  → Master: ResultMessage (aquí está mi resultado)

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TaskMessage:
    # Identifica la tarea de forma única dentro de la cola.
    # El slave lo reenvía en ResultMessage para que el master
    # almacene el resultado en la posición correcta.
    task_id: int

    # El dato que la tarea debe procesar.
    # Es el elemento original de la lista `data` pasada al ClusterManager.
    payload: Any


@dataclass(frozen=True)
class ResultMessage:
    # Mismo task_id recibido en TaskMessage, necesario para
    # que el master asocie el resultado con su posición original.
    task_id: int

    # El valor retornado por Task.execute().
    result: Any


@dataclass(frozen=True)
class StopMessage:
    # Señal de terminación. No lleva datos: su mera recepción
    # indica al slave que no habrá más tareas y puede finalizar.
    pass