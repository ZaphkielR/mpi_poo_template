# Protocolo (interfaz) del comunicador.
#
# Define el contrato que debe cumplir cualquier implementación de comunicación
# entre procesos. Al usar Protocol en lugar de una clase base abstracta, se
# obtiene compatibilidad estructural (duck typing): cualquier clase que implemente
# estos métodos es válida, sin necesidad de heredar de Communicator.
#
# Esto facilita crear implementaciones alternativas (ej: en memoria para tests)
# sin modificar el código que las consume.

from typing import Any, Protocol, runtime_checkable


@runtime_checkable  # Permite usar isinstance(obj, Communicator) en tiempo de ejecución si es necesario.
class Communicator(Protocol):
    def send(self, data: Any, dest: int) -> None:
        # Envía un objeto a un proceso destino identificado por su rank.
        ...

    def receive(self, source: int) -> Any:
        # Bloquea hasta recibir un mensaje del proceso con el rank indicado.
        ...

    def receive_any(self) -> tuple[Any, int]:
        # Bloquea hasta recibir un mensaje de cualquier proceso.
        # Retorna el mensaje y el rank del proceso que lo envió.
        ...

    def get_rank(self) -> int:
        # Retorna el rank de este proceso en el clúster (0, 1, 2, ...).
        ...

    def get_size(self) -> int:
        # Retorna el número total de procesos en el clúster.
        ...