"""
=========================================================
PLANTILLA BASE MPI EN PYTHON (mpi4py)
Autor: [Tu nombre]
Descripción: Estructura estándar para programas MPI
=========================================================
"""

# ======================================================
# IMPORTS
# ======================================================
from mpi4py import MPI
import sys

# ======================================================
# INICIALIZACIÓN MPI
# ======================================================
comm = MPI.COMM_WORLD      # Comunicador global
rank = comm.Get_rank()     # ID del proceso
size = comm.Get_size()     # Número total de procesos

# ======================================================
# CONFIGURACIÓN / PARÁMETROS
# ======================================================
def configurar():
    """
    Definir parámetros globales del programa.
    Solo el proceso root suele inicializar datos.
    """
    if rank == 0:
        data = list(range(size))
    else:
        data = None
    return data

# ======================================================
# DISTRIBUCIÓN DE DATOS
# ======================================================
def distribuir_datos(data):
    """
    Distribuye datos entre procesos.
    """
    return comm.scatter(data, root=0)

# ======================================================
# COMPUTACIÓN LOCAL
# ======================================================
def computar(dato_local):
    """
    Lógica principal que ejecuta cada proceso.
    """
    resultado = dato_local ** 2
    return resultado

# ======================================================
# RECOLECCIÓN DE RESULTADOS
# ======================================================
def recolectar(resultados_locales):
    """
    Recolecta resultados en el proceso root.
    """
    return comm.gather(resultados_locales, root=0)

# ======================================================
# FUNCIÓN PRINCIPAL
# ======================================================
def main():
    data = configurar()
    
    dato_local = distribuir_datos(data)
    
    resultado_local = computar(dato_local)
    
    resultados = recolectar(resultado_local)
    
    if rank == 0:
        print("Resultados finales:", resultados)

# ======================================================
# ENTRY POINT
# ======================================================
if __name__ == "__main__":
    main()