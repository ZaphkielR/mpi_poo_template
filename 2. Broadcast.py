from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    data = 100
else:
    data = None

data = comm.bcast(data, root=0)

print(f"Proceso {rank} recibió: {data}")