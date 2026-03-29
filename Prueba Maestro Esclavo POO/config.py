"""
Archivo de configuración centralizada del sistema.

Contiene constantes globales que definen el comportamiento del clúster MPI.
Centralizar estos valores evita números mágicos dispersos en el código
y facilita cambios futuros en la configuración.
"""

# Rank (identificador) del proceso maestro en el comunicador MPI.
# 
# Por convención en MPI, el proceso con rank 0 es tradicionalmente el coordinator.
# Este valor se usa en ClusterManager para determinar qué proceso
# ejecutará la lógica del master y cuáles ejecutarán la lógica del slave.
#
# En un sistema con N procesos:
#   - rank 0: proceso maestro (Master)
#   - rank 1 a N-1: procesos esclavos (Slave)
#
# Ejemplo con mpirun -n 4:
#   - rank 0: Master
#   - rank 1: Slave
#   - rank 2: Slave
#   - rank 3: Slave
MASTER_RANK: int = 0
