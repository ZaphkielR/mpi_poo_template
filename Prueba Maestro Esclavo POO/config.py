# Constantes globales del sistema.
# Centralizar estos valores aquí evita números mágicos dispersos en el código
# y facilita modificarlos si la arquitectura cambia (ej: múltiples masters).

# Rank MPI del proceso master. Por convención MPI, el rank 0 es el coordinador.
MASTER_RANK: int = 0