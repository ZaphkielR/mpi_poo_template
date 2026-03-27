# Unidad de trabajo ejecutada por cada slave.
#
# Este es el único componente diseñado explícitamente para ser reemplazado.
# Cuando cambie la lógica de procesamiento, solo este archivo debe modificarse;
# el sistema de comunicación, la cola y la coordinación master-slave permanecen igual.
#
# Interfaz esperada por el sistema:
#   - __init__(self, data): recibe el payload enviado por el master.
#   - execute(self) -> Any: realiza el procesamiento y retorna el resultado.


class Task:
    def __init__(self, data: int) -> None:
        self.data = data

    def execute(self) -> int:
        # Tarea temporal de ejemplo: eleva el dato al cuadrado.
        # Reemplazar este método con la lógica real del problema.
        return self.data ** 2