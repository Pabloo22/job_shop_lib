"""Home of the Operation class."""


class Operation:
    """Stores machine and duration information for a job operation."""

    __slots__ = ("machines", "duration")

    def __init__(self, machines: int | list[int], duration: int):
        self.machines = [machines] if isinstance(machines, int) else machines
        self.duration = duration

    @property
    def machine_id(self) -> int:
        """Returns the id of the machine and raises an error if there are
        multiple machines."""
        if len(self.machines) > 1:
            raise ValueError("Operation has multiple machines.")
        return self.machines[0]

    def get_id(self, job_id: int, position: int) -> str:
        """Returns the id of the operation."""
        return f"J{job_id}M{self.machine_id}P{position}"

    @staticmethod
    def get_job_id_from_id(op_id: str) -> int:
        """Returns the job id from the operation id."""
        return int(op_id.split("M")[0][1:])

    @staticmethod
    def get_machine_id_from_id(op_id: str) -> int:
        """Returns the machine id from the operation id."""
        return int(op_id.split("M")[1][0])

    @staticmethod
    def get_position_from_id(op_id: str) -> int:
        """Returns the position from the operation id."""
        return int(op_id.split("P")[1])
