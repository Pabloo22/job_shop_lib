class Operation:
    __slots__ = ("machines", "duration")

    def __init__(self, machines: int | list[int], duration: int):
        self.machines = [machines] if isinstance(machines, int) else machines
        self.duration = duration

    @property
    def machine_id(self) -> int:
        if len(self.machines) > 1:
            raise ValueError("Operation has multiple machines.")
        return self.machines[0]
