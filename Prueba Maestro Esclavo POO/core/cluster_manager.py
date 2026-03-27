from infrastructure.mpi_communicator import MPICommunicator
from core.master import Master
from core.slave import Slave
from config import MASTER_RANK

class ClusterManager:
    def __init__(self, data):
        self.comm = MPICommunicator()
        self.rank = self.comm.get_rank()
        self.data = data

    def execute(self):
        
        if self.rank == MASTER_RANK:
            Master(self.comm, self.data).run()
        else:
            Slave(self.comm).run()