from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

valor = rank + 1

# Operación máxima
max_val = comm.reduce(valor, op=MPI.MAX, root=0)

if rank == 0:
    print("Máximo:", max_val)

total = comm.allreduce(valor, op=MPI.SUM)
print(f"Proceso {rank} ve suma total: {total}")
