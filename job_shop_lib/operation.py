"""Home of the Operation class."""

from typing import Optional


class Operation:
    """Stores machine and duration information for a job operation."""

    __slots__ = ("machines", "duration", "job_id", "position")

    def __init__(
        self,
        machines: int | list[int],
        duration: int,
        job_id: Optional[int] = None,
        position: Optional[int] = None,
    ):
        self.machines = [machines] if isinstance(machines, int) else machines
        self.duration = duration
        self.job_id = job_id
        self.position = position

    @property
    def machine_id(self) -> int:
        """Returns the id of the machine and raises an error if there are
        multiple machines."""
        if len(self.machines) > 1:
            raise ValueError("Operation has multiple machines.")
        return self.machines[0]

    @property
    def operation_id(self) -> str:
        """Returns the id of the operation."""
        if self.job_id is None or self.position is None:
            raise ValueError("Operation has no job_id or position.")
        return f"J{self.job_id}M{self.machine_id}P{self.position}"

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

    def __repr__(self) -> str:
        machines = (
            self.machines[0] if len(self.machines) == 1 else self.machines
        )
        return (
            f"O(m={machines}, d={self.duration}, "
            f"j={self.job_id}, p={self.position})"
        )
