from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

requests = []

if rank == 0:
    for i in range(1, 4):
        req = comm.Isend(i, dest=i, tag=0)
        requests.append(req)

elif rank in [1, 2, 3]:
    req = comm.Irecv(source=0, tag=0)
    requests.append(req)

# Esperar todas las operaciones
MPI.Request.Waitall(requests)

print(f"Proceso {rank} completó operaciones")