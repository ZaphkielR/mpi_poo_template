from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

# Crear buffer
data = np.zeros(5, dtype='i')

if rank == 0:
    data = np.array([1, 2, 3, 4, 5], dtype='i')

# Broadcast a nivel bajo (más eficiente)
comm.Bcast(data, root=0)

print(f"Proceso {rank} tiene {data}")