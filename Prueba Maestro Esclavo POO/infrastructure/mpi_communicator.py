from mpi4py import MPI
from typing import Any

class MPICommunicator:
    def __init__(self) -> None:
        self._comm = MPI.COMM_WORLD

    def send(self, data: Any, dest: int) -> None:
        self._comm.send(data, dest=dest)

    def receive(self, source: int) -> Any:
        return self._comm.recv(source=source)
    
    def receive_any(self) -> tuple[Any, int]:
        status = MPI.Status()
        data = self._comm.recv(source=MPI.ANY_SOURCE, status=status)
        return data, status.Get_source()
    
    def get_rank(self) -> int:
        return self._comm.Get_rank()

    def get_size(self) -> int:
        return self._comm.Get_size()
