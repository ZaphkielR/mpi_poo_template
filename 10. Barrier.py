from mpi4py import MPI
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

print(f"Proceso {rank} antes de barrier")

time.sleep(rank)

comm.Barrier()

print(f"Proceso {rank} después de barrier")