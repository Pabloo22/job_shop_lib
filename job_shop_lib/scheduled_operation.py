from job_shop_lib import Operation


class ScheduledOperation:

    __slots__ = ("operation", "start_time", "_machine_id")

    def __init__(self, operation: Operation, start_time: int, machine_id: int):
        self.operation = operation
        self.start_time = start_time
        self._machine_id = machine_id

    @property
    def machine_id(self) -> int:
        return self._machine_id

    @machine_id.setter
    def machine_id(self, value: int):
        if value not in self.operation.machines:
            raise ValueError(
                f"Operation cannot be scheduled on machine {value}. "
                f"Valid machines are {self.operation.machines}."
            )
        self._machine_id = value

    @property
    def end_time(self) -> int:
        return self.start_time + self.operation.duration
