from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    data = np.arange(10)
    counts = [1, 2, 3, 4]  # diferente tamaño por proceso
    displs = [0, 1, 3, 6]
else:
    data = None
    counts = None
    displs = None

# Broadcast de metadata
counts = comm.bcast(counts, root=0)
displs = comm.bcast(displs, root=0)

recvbuf = np.zeros(counts[rank], dtype='i')

comm.Scatterv([data, counts, displs, MPI.INT], recvbuf, root=0)

print(f"Proceso {rank} recibió {recvbuf}")