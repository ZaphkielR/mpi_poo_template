from mpi4py import MPI
import time
from random import randint

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

TAG_WORK = 1
TAG_RESULT = 2
TAG_EXIT = 3

# ======================================================
# MAESTRO
# ======================================================
if rank == 0:
    tareas = [10, 20, 30, 40, 50, 60, 70, 80, 90]  # puedes cambiar a cualquier tamaño
    print(f"[MAESTRO] Tareas iniciales: {tareas}")

    num_workers = size - 1
    tareas_enviadas = 0
    tareas_completadas = 0

    # --------------------------------------------------
    # ENVIAR PRIMERA OLA DE TAREAS
    # --------------------------------------------------
    for worker in range(1, size):
        if tareas:
            tarea = tareas.pop(0)
            print(f"[MAESTRO] Enviando {tarea} a worker {worker}")
            comm.send(tarea, dest=worker, tag=TAG_WORK)
            tareas_enviadas += 1
        else:
            # No hay trabajo → terminar inmediatamente
            comm.send(None, dest=worker, tag=TAG_EXIT)

    # --------------------------------------------------
    # LOOP PRINCIPAL (cola dinámica)
    # --------------------------------------------------
    while tareas_completadas < tareas_enviadas:
        status = MPI.Status()

        resultado = comm.recv(source=MPI.ANY_SOURCE,
                             tag=TAG_RESULT,
                             status=status)

        worker = status.Get_source()

        tareas_completadas += 1

        # Si quedan tareas → asignar inmediatamente
        if tareas:
            tarea = tareas.pop(0)
            print(f"[MAESTRO] Reasignando {tarea} a worker {worker}")
            comm.send(tarea, dest=worker, tag=TAG_WORK)
            tareas_enviadas += 1
        else:
            # No quedan tareas → terminar worker
            comm.send(None, dest=worker, tag=TAG_EXIT)

    print("[MAESTRO] Todo terminado")


# ======================================================
# WORKERS
# ======================================================
else:
    while True:
        status = MPI.Status()

        tarea = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
        tag = status.Get_tag()

        # --------------------------------------------------
        # SALIDA
        # --------------------------------------------------
        if tag == TAG_EXIT:
            break

        # --------------------------------------------------
        # PROCESAMIENTO
        # --------------------------------------------------

        resultado = tarea * 2
        time.sleep(randint(1, 5))
        print(f"[WORKER {rank}] Procesando {tarea} → {resultado}")

        comm.send(resultado, dest=0, tag=TAG_RESULT)