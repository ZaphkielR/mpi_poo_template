from mpi4py import MPI

comm = MPI.COMM_WORLD   # Comunicador global
rank = comm.Get_rank()  # ID del proceso
size = comm.Get_size()  # Total de procesos

print(f"Hola desde proceso {rank} de {size}")

# mpirun -np <NUM_PROCESOS> python3 <ARCHIVO_PYTHON>