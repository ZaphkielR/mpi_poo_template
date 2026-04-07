"""
Punto de entrada del programa maestro-esclavo con MPI.

Este script es el punto de inicio de la aplicación. Cuando se ejecuta con 
mpirun (ej: mpiexec -n 4 python main.py), MPI crea múltiples procesos que 
ejecutan este mismo código en paralelo.

Ejecución:
    mpiexec -n <num_procesos> python main.py
    
    - <num_procesos> debe ser >= 2 (1 master + al menos 1 slave)
    - El proceso con rank 0 será el master
    - Los procesos con rank 1, 2, 3, ... serán los slaves
"""

from core.cluster_manager import ClusterManager


if __name__ == "__main__":
    """
    Bloque de entrada principal.
    
    Este bloque solo se ejecuta cuando el script se lanza directamente,
    no cuando se importa como módulo. Es el punto de inicio padrão
    en aplicaciones Python.
    
    En MPI, todos los procesos (master y slaves) ejecutan este código,
    pero el ClusterManager se encarga de diferenciarlos por su rank.
    """
    
    # Datos de entrada: lista de 25 enteros (0 a 24)
    # Cada entero será el payload de una tarea que el slave procesará
    # En este ejemplo, los slaves elevarán cada número al cuadrado
    data = list(range(25))
    
    # Instancia del gestor del clúster
    # ClusterManager detectará si este proceso es master o slave
    # según su rank en MPI y ejecutará la lógica correspondiente
    manager = ClusterManager(data)
    
    # Inicia la ejecución
    # - Si es master: coordina distribución de tareas y recibe resultados
    # - Si es slave: espera tareas, las procesa y devuelve resultados
    manager.execute()
