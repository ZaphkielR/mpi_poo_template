from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

valor = rank + 1

suma_total = comm.reduce(valor, op=MPI.SUM, root=0)

if rank == 0:
    print("Suma total:", suma_total)