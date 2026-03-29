"""
Lógica del proceso esclavo (worker/slave).

El slave es el proceso que ejecuta el trabajo real. Su comportamiento es simple:
1. Espera una tarea del master
2. Procesa la tarea
3. Devuelve el resultado al master
4. Repite hasta recibir señal de parada

El slave no conoce:
- Cuántas tareas hay en total
- Cuántos otros slaves existen
- El estado global del sistema

Esta ignorancia es intencional: el slave solo necesita recibir tareas
y devolver resultados. La coordinación es responsabilidad del master.
"""

from communication.communicator import Communicator
from communication.message import StopMessage, TaskMessage, ResultMessage
from random import randint
from time import sleep

class Slave:
    """
    Proceso worker que ejecuta tareas asignadas por el master.
    
    Attributes:
        _comm: Comunicador MPI para enviar/recibir mensajes
        _rank: Identificador único de este slave en el clúster
    """
    
    def __init__(self, comm: Communicator) -> None:
        """
        Inicializa el slave con su comunicador.
        
        Args:
            comm: Instancia del comunicador MPI compartida
        """
        # Referencia al comunicador para operaciones MPI
        self._comm = comm
        
        # Guarda el rank de este proceso
        # Útil para logs y depuración
        # No se usa para lógica de enrutamiento (el master lo maneja)
        self._rank = comm.get_rank()

    def run(self) -> None:
        """
        Ejecuta el ciclo de trabajo del slave.
        
        Bucle infinito que:
        1. Espera recibir un mensaje del master (bloqueante)
        2. Si es StopMessage: sale del bucle y termina
        3. Si es TaskMessage: procesa la tarea y devuelve el resultado
        
        El slave solo recibe mensajes del master (rank 0),
        por lo que source=0 en receive().
        """
        # Bucle principal: el slave espera tareas continuamente
        while True:
            """
            Bloquea hasta recibir un mensaje del master (rank 0).
            
            Esta es una recepción punto-a-punto específica:
            - Solo acepta mensajes del proceso con rank 0 (master)
            - Si no hay mensaje disponible, el proceso se bloquea
            """
            message = self._comm.receive(source=0)
            
            # Verifica el tipo de mensaje recibido
            
            # =====================================
            # Caso 1: Señal de terminación
            # =====================================
            if isinstance(message, StopMessage):
                """
                StopMessage indica que no hay más tareas disponibles.
                El master envía esto cuando la cola de tareas está vacía
                y quiere que este slave termine su ejecución.
                
                Acción: salir del bucle principal
                """
                break
            
            # =====================================
            # Caso 2: Nueva tarea
            # =====================================
            if isinstance(message, TaskMessage):
                """
                TaskMessage contiene:
                - task_id: identificador único de la tarea
                - payload: datos a procesar
                
                El slave debe:
                1. Procesar el payload
                2. Devolver el resultado al master
                """
                
                # Procesa la tarea: eleva el payload al cuadrado
                # NOTA: Esta es la lógica de negocio que debería
                # modificarse para otros tipos de procesamiento
                result = message.payload ** 2
                
                # Simulación de trabajo
                sleep(randint(1, 5))
                
                # Imprime un mensaje de progreso
                # Útil para visualizar qué slave procesó qué tarea
                print(f"Proceso {self._rank} terminó tarea {message.task_id} | Resultado: {result}")
                
                # Envía el resultado de vuelta al master
                # Incluye el task_id para que el master pueda
                # almacenar el resultado en la posición correcta
                self._comm.send(ResultMessage(message.task_id, result), dest=0)
                
                # El bucle se repite: el slave vuelve a esperar otra tarea
