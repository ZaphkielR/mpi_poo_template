class Task:
    def __init__(self, data: int) -> None:
        self.data = data

    def execute(self) -> int:
        return self.data ** 2