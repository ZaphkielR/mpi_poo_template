# Prueba Maestro-Esclavo POO con MPI

Implementación de un sistema distribuido usando el patrón **maestro-esclavo** (master-slave) con **MPI** y programación orientada a objetos en Python.

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Estructura de Archivos](#estructura-de-archivos)
4. [Componentes del Sistema](#componentes-del-sistema)
5. [Protocolo de Comunicación](#protocolo-de-comunicación)
6. [Ejecución del Programa](#ejecución-del-programa)
7. [Ejemplo de Salida](#ejemplo-de-salida)
8. [Personalización](#personalización)

---

## Descripción General

Este proyecto implementa un sistema distribuido de procesamiento paralelo donde:

- **1 proceso master** coordina la distribución de tareas
- **N-1 procesos slaves** ejecutan el trabajo real
- La comunicación se realiza mediante la librería **mpi4py**

El sistema usa **distribución dinámica de tareas**: el master envía una tarea a cada slave y, cuando un slave completa su trabajo, le envía otra tarea si hay disponibles. Esto permite balancear la carga automáticamente.

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                         mpirun -n 4                              │
│                                                                 │
│  ┌─────────────┐    ┌─────────────────────────────────────┐   │
│  │  rank 0    │    │  rank 1    rank 2    rank 3         │   │
│  │  (Master)  │    │  (Slave)   (Slave)   (Slave)         │   │
│  └─────────────┘    └─────────────────────────────────────┘   │
│         │                    │      │      │                    │
│         │                    │      │      │                    │
│         │  TaskMessage       │      │      │                    │
│         │  ───────────────► │      │      │                    │
│         │                    │      │      │                    │
│         │  ResultMessage    │      │      │                    │
│         │  ◄─────────────── │      │      │                    │
│         │                    │      │      │                    │
│         │              TaskMessage                         │
│         │  ──────────────────────────────────────────────►  │
│         │                    │      │      │                    │
│         │                    │      │      │                    │
│         │              ResultMessage                        │
│         │  ◄────────────────────────────────────────────── │
│         │                    │      │      │                    │
│         │                    │      │      │                    │
│         │                    ▼      ▼      ▼                  │
│         │               (Procesamiento paralelo)              │
│         │                    │      │      │                    │
│         │                    │      │      │                    │
│         │              StopMessage (cuando termina)           │
│         └────────────────►│      │      │                    │
│                           └──────┴──────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
Prueba Maestro Esclavo POO/
├── main.py                    # Punto de entrada del programa
├── config.py                  # Configuración global (MASTER_RANK)
├── Readme.md                  # Este archivo
├── core/                      # Lógica principal
│   ├── cluster_manager.py    # Orquestador: bifurca master/slave
│   ├── master.py              # Lógica del proceso maestro
│   └── slave.py               # Lógica del proceso esclavo
├── communication/             # Capa de comunicación
│   ├── communicator.py        # Wrapper de mpi4py
│   └── message.py             # Definición de tipos de mensaje
└── domain/                    # Lógica de negocio
    └── task_queue.py          # Cola de tareas FIFO
```

---

## Componentes del Sistema

### 1. main.py
**Punto de entrada.** Cuando MPI lanza el programa, todos los procesos ejecutan este código. El `ClusterManager` detecta el rol de cada proceso según su rank.

### 2. config.py
Contiene la constante `MASTER_RANK = 0`, que define cuál proceso es el maestro.

### 3. core/cluster_manager.py
**Orquestador del sistema.** Su responsabilidad es:
- Inicializar el comunicador MPI
- Determinar si este proceso es master (rank 0) o slave (rank > 0)
- Delegar la ejecución al componente correspondiente

### 4. core/master.py
**Coordinador del sistema distribuido.** Responsibilities:
- Crear la cola de tareas desde los datos de entrada
- Distribuir tareas a los slaves (fase de calentamiento)
- Recibir resultados de cualquier slave (`receive_any`)
- Reasignar tareas o enviar señal de parada
- Recopilar y mostrar resultados finales

**Algoritmo del master:**
```
1. Enviar una tarea a cada slave (warm-up)
2. Mientras haya slaves activos:
   a. Esperar resultado de cualquier slave
   b. Guardar el resultado
   c. Si hay más tareas → enviar nueva tarea al slave
   d. Si no hay más → enviar StopMessage al slave
3. Imprimir resultados
```

### 5. core/slave.py
**Worker del sistema.** Su comportamiento es simple:
- Esperar mensaje del master (bloqueante)
- Si es TaskMessage → procesar y devolver resultado
- Si es StopMessage → terminar

### 6. communication/communicator.py
**Capa de abstracción MPI.** Encapsula todas las operaciones de mpi4py:
- `send(data, dest)`: Enviar a un proceso específico
- `receive(source)`: Recibir de un proceso específico
- `receive_any()`: Recibir de cualquier proceso (retorna mensaje + rank)
- `get_rank()`: Obtener el rank de este proceso
- `get_size()`: Obtener el número total de procesos

### 7. communication/message.py
**Definición de mensajes.** Tres tipos:
- **TaskMessage**: Master → Slave (hay trabajo)
- **ResultMessage**: Slave → Master (aquí está el resultado)
- **StopMessage**: Master → Slave (puedes terminar)

### 8. domain/task_queue.py
**Cola FIFO de tareas.** Implementada con `deque` para eficiencia O(1) en extracción.

---

## Protocolo de Comunicación

El protocolo de comunicación sigue este flujo:

```
┌─────────────────────────────────────────────────────────────────┐
│                    MASTER                          SLAVE        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────── TaskMessage(tid, payload) ─────────┐   │
│   │                                                      │   │
│   │  task_id: identificador único de la tarea            │   │
│   │  payload: dato a procesar (ej: 5, 10, 15...)          │   │
│   ▼                                                      ▼   │
│                                                                 │
│                                                      Procesa:
│                                                      payload**2
│                                                      │
│   ┌──────────────────── ResultMessage(tid, result) ◄───┐     │
│   │                                                      │     │
│   │  task_id: mismo ID recibido                         │     │
│   │  result: resultado del procesamiento                │     │
│   ▼                                                      ▼     │
│                                                                 │
│   [Repite el ciclo hasta que la cola esté vacía]              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│   ┌─────────────────── StopMessage() ───────────────────┐     │
│   │  (Señal de terminación - no lleva datos)            │     │
│   ▼                                                      ▼     │
│                                                                 │
│   [Slave sale del bucle y termina]                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Ejecución del Programa

### Requisitos
- Python 3.x
- mpi4py (`pip install mpi4py`)
- OpenMPI o similar instalado en el sistema

### Comando de ejecución

```bash
mpirun -n <num_procesos> python main.py
```

Ejemplos:

```bash
# 2 procesos (1 master + 1 slave)
mpirun -n 2 python main.py

# 4 procesos (1 master + 3 slaves)
mpirun -n 4 python main.py

# 6 procesos (1 master + 5 slaves)
mpirun -n 6 python main.py
```

---

## Ejemplo de Salida

```bash
$ mpirun -n 4 python main.py
Proceso 1 terminó tarea 0 | Resultado: 0
Proceso 2 terminó tarea 1 | Resultado: 1
Proceso 2 terminó tarea 3 | Resultado: 9
Proceso 2 terminó tarea 6 | Resultado: 36
Proceso 3 terminó tarea 2 | Resultado: 4
Proceso 3 terminó tarea 5 | Resultado: 25
Proceso 1 terminó tarea 4 | Resultado: 16
Proceso 3 terminó tarea 8 | Resultado: 64
Proceso 1 terminó tarea 9 | Resultado: 81
Proceso 2 terminó tarea 10 | Resultado: 100
Proceso 3 terminó tarea 11 | Resultado: 121
Proceso 1 terminó tarea 12 | Resultado: 144
Proceso 2 terminó tarea 13 | Resultado: 169
Proceso 3 terminó tarea 14 | Resultado: 196
Proceso 1 terminó tarea 15 | Resultado: 225
Proceso 2 terminó tarea 16 | Resultado: 256
Proceso 3 terminó tarea 17 | Resultado: 289
Proceso 1 terminó tarea 18 | Resultado: 324
Proceso 2 terminó tarea 19 | Resultado: 361
Proceso 3 terminó tarea 20 | Resultado: 400
Proceso 1 terminó tarea 21 | Resultado: 441
Proceso 2 terminó tarea 22 | Resultado: 484
Proceso 3 terminó tarea 23 | Resultado: 529
Proceso 1 terminó tarea 24 | Resultado: 576
Resultados: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225, 256, 289, 324, 361, 400, 441, 484, 529, 576]
```

---

## Personalización

### Cambiar la lógica de procesamiento

Para modificar qué hacen los slaves, edita `core/slave.py`:

```python
# En el método run(), línea ~18:
# Antes:
result = message.payload ** 2

# Después (ejemplo: raíz cuadrada):
import math
result = math.sqrt(message.payload)

# O ejemplo: multiplicar por 3:
result = message.payload * 3
```

### Cambiar los datos de entrada

Edita `main.py` para modificar los datos iniciales:

```python
# Datos de entrada
data = list(range(25))      # [0, 1, 2, ..., 24]

# O usa otros datos:
data = [10, 20, 30, 40, 50]
data = ["a", "b", "c", "d"]
```

### Agregar más información al mensaje

Si necesitas enviar datos adicionales, modifica `communication/message.py`:

```python
@dataclass(frozen=True)
class TaskMessage:
    task_id: int
    payload: Any
    prioridad: int = 0  # Nuevo campo con valor por defecto
```

---

## Notas Técnicas

- **Blocking vs Non-blocking**: Este ejemplo usa operaciones bloqueantes (`send`/`recv`) para simplicidad. Para mejor rendimiento, se podrían usar `Isend`/`Irecv` con `Wait`.
- **Serialización**: mpi4py usa `pickle` para serializar objetos. Asegúrate de que tus datos sean serializables.
- **Orden de llegada**: Los resultados pueden llegar en cualquier orden debido a la naturaleza asíncrona del procesamiento. El `task_id` permite mantener la correspondencia correcta.
