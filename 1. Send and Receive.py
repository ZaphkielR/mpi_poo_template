from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    data = "Mensaje desde proceso 0"
    comm.send(data, dest=1, tag=11)
    print("Proceso 0 envió mensaje")

elif rank == 1:
    data = comm.recv(source=0, tag=11)
    print(f"Proceso 1 recibió: {data}")