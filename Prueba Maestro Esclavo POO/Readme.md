# Arquitectura Master-Slave con MPI y Cola de Tareas

Sistema de procesamiento paralelo distribuido usando MPI (Message Passing Interface) con Python. Implementa el patrón **Master-Slave** con una cola de tareas dinámica: el nodo master distribuye trabajo a los nodos slave a medida que estos van terminando, garantizando un uso eficiente de todos los procesos disponibles.

---

## Requisitos

- Python 3.10+
- `mpi4py`
- `openmpi` o equivalente instalado en el sistema

```bash
pip install mpi4py
```

---

## Ejecución

```bash
mpirun -n <número_de_procesos> python main.py
```

Ejemplo con 4 procesos (1 master + 3 slaves):

```bash
mpirun -n 4 python main.py
```

> El número mínimo de procesos es **2** (1 master + al menos 1 slave). Con 1 solo proceso, no hay slaves y el master nunca recibe resultados, quedando en espera indefinida.

---

## Estructura del Proyecto

```
.
├── main.py                         # Punto de entrada
├── config.py                       # Constantes globales
├── core/
│   ├── cluster_manager.py          # Orquestador: decide si el proceso es master o slave
│   ├── master.py                   # Lógica del nodo master
│   └── slave.py                    # Lógica del nodo slave
├── domain/
│   ├── task.py                     # Unidad de trabajo (reemplazable)
│   └── task_queue.py               # Cola de tareas pendientes
├── infrastructure/
│   └── mpi_communicator.py         # Wrapper sobre mpi4py
└── communication/
    ├── communicator.py             # Protocolo (interfaz) del comunicador
    └── message.py                  # Tipos de mensajes entre procesos
```

---

## Cómo Funciona

### El Modelo Master-Slave

Cuando se ejecuta con `mpirun -n N`, MPI lanza **N procesos idénticos** del mismo script. Cada proceso recibe un **rank** (número entero único desde 0 hasta N-1). El `ClusterManager` usa ese rank para decidir qué rol cumple cada proceso:

- **Rank 0 → Master**: distribuye tareas y recolecta resultados.
- **Rank 1..N-1 → Slaves**: reciben tareas, las ejecutan y devuelven el resultado.

```
mpirun -n 4 python main.py
  ├── Proceso rank 0  →  Master
  ├── Proceso rank 1  →  Slave
  ├── Proceso rank 2  →  Slave
  └── Proceso rank 3  →  Slave
```

### Flujo de Comunicación

El master implementa una estrategia de **distribución dinámica**: en lugar de repartir todas las tareas al inicio (lo que desbalancearía la carga si algunas tareas tardan más), envía una tarea a la vez por slave y solo asigna la siguiente cuando ese slave reporta su resultado.

```
Master                          Slave 1              Slave 2
  │                                │                    │
  ├──── TaskMessage(0, dato) ────►│                    │
  ├──── TaskMessage(1, dato) ─────────────────────────►│
  │                                │ (procesando)       │ (procesando)
  │◄─── ResultMessage(0, res) ────┤                    │
  ├──── TaskMessage(2, dato) ────►│                    │
  │◄─── ResultMessage(1, res) ─────────────────────────┤
  │                                │                    │ (cola vacía)
  ├──── StopMessage() ─────────────────────────────────►│
  │◄─── ResultMessage(2, res) ────┤
  │                                │ (cola vacía)
  ├──── StopMessage() ────────────►│
  │
  └── Imprime resultados
```

### Protocolo de Parada

El master no envía un broadcast de parada. En cambio, envía un `StopMessage` **individualmente** a cada slave una vez que la cola se ha vaciado y ese slave reporta un resultado. Esto evita condiciones de carrera y mantiene la sincronización simple.

---

## Decisiones de Diseño

### ¿Por qué `Protocol` en lugar de clase base abstracta?

`communication/communicator.py` define `Communicator` como un `Protocol` de Python. Esto permite **duck typing estructural**: cualquier clase que implemente los métodos requeridos es compatible automáticamente, sin necesidad de heredar de `Communicator`. Los beneficios son:

- `MPICommunicator` no depende de `Communicator` en tiempo de ejecución.
- Es fácil crear comunicadores alternativos para testing sin tocar la jerarquía de clases.
- El type checker (mypy, Pylance) sigue recomendando métodos y detectando errores.

### ¿Por qué `deque` en `TaskQueue`?

`list.pop(0)` es O(n) porque desplaza todos los elementos. `collections.deque.popleft()` es O(1). Para colas con muchas tareas, la diferencia es significativa.

### ¿Por qué mensajes `frozen=True`?

Los mensajes (`TaskMessage`, `ResultMessage`, `StopMessage`) son objetos de comunicación: se crean, se envían y se consumen. No deben mutar. `frozen=True` en `@dataclass` los hace inmutables, lo que previene bugs difíciles de rastrear y comunica la intención claramente.

### ¿Por qué separar `domain/` de `communication/`?

- `domain/` contiene la lógica de negocio: qué es una tarea y cómo se procesa. Es lo que **más cambia** entre proyectos.
- `communication/` contiene la infraestructura de mensajería: cómo se comunican los procesos. Es lo que **menos cambia**.

Esta separación permite reemplazar `Task` con cualquier otra lógica sin tocar el sistema de mensajes, y viceversa.

### ¿Por qué `MPICommunicator` envuelve `mpi4py`?

Para aislar la dependencia de MPI en un solo lugar. Si en el futuro se quiere:
- Testear sin MPI (usando un comunicador en memoria).
- Cambiar la librería de comunicación.
- Agregar logging o métricas a los envíos.

...solo se modifica o reemplaza `MPICommunicator`, sin tocar `Master`, `Slave` ni la lógica de dominio.

---

## Reemplazar la Tarea

`domain/task.py` es la única parte diseñada para ser reemplazada. La interfaz esperada es simple:

```python
class Task:
    def __init__(self, data: <tipo>) -> None:
        self.data = data

    def execute(self) -> <tipo_resultado>:
        # tu lógica aquí
        ...
```

El payload que recibe `Task` es el mismo objeto que se puso en la lista `data` en `main.py`. El resultado de `execute()` es lo que el master almacena en `self._results`.