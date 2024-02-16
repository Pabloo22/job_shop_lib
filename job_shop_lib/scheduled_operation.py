from job_shop_lib import Operation


class ScheduledOperation:

    __slots__ = ("operation", "start_time", "machine_id")

    def __init__(self, operation: Operation, start_time: int, machine_id: int):
        if machine_id not in operation.machines:
            raise ValueError(
                f"Operation cannot be scheduled on machine {machine_id}. "
                f"Valid machines are {operation.machines}."
            )

        self.operation = operation
        self.start_time = start_time
        self.machine_id = machine_id

    @property
    def end_time(self) -> int:
        return self.start_time + self.operation.duration
