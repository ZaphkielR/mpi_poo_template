# Punto de entrada del programa.
#
# Cuando se ejecuta con `mpirun -n N python main.py`, MPI lanza N copias
# de este script en paralelo. Cada proceso ejecuta exactamente el mismo código
# desde aquí, pero ClusterManager los diferencia por su rank.

from core.cluster_manager import ClusterManager

if __name__ == "__main__":
    # Datos de entrada: cada elemento se convierte en el payload de una tarea.
    # En este caso, 25 enteros que los slaves elevarán al cuadrado.
    data = list(range(25))

    manager = ClusterManager(data)
    manager.execute()  # Todos los procesos llaman esto; internamente se bifurcan por rol.