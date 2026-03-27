from core.cluster_manager import ClusterManager

if __name__ == "__main__":
    data = list(range(25))
    manager = ClusterManager(data)
    manager.execute()