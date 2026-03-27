from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    data = [i for i in range(size)]
else:
    data = None

# Distribuir datos
recv_data = comm.scatter(data, root=0)

# Procesamiento local
resultado = recv_data * 2

# Recolectar resultados
resultados = comm.gather(resultado, root=0)

if rank == 0:
    print("Resultados:", resultados)