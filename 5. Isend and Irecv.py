from mpi4py import MPI
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    data = "Mensaje asincrónico"

    # Envío NO bloqueante
    req = comm.Isend([data, MPI.CHAR], dest=1, tag=0)

    print("Proceso 0 sigue ejecutando mientras envía...")
    time.sleep(2)

    # Esperar a que termine el envío
    req.Wait()
    print("Proceso 0 terminó envío")

elif rank == 1:
    data = bytearray(50)

    # Recepción NO bloqueante
    req = comm.Irecv([data, MPI.CHAR], source=0, tag=0)

    print("Proceso 1 puede hacer otras cosas mientras espera...")
    time.sleep(1)

    req.Wait()
    print("Proceso 1 recibió:", data.decode().strip("\x00"))