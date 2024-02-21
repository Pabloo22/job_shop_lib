"""Home of the Operation class."""

from typing import Optional


class Operation:
    """Stores machine and duration information for a job operation."""

    __slots__ = ("machines", "duration", "job_id", "position_in_job", "id")

    def __init__(
        self,
        machines: int | list[int],
        duration: int,
        job_id: Optional[int] = None,
        position_in_job: Optional[int] = None,
        operation_id: Optional[int] = None,
    ):
        self.machines = [machines] if isinstance(machines, int) else machines
        self.duration = duration
        self.job_id = job_id
        self.position_in_job = position_in_job
        self.id = operation_id

    @property
    def machine_id(self) -> int:
        """Returns the id of the machine and raises an error if there are
        multiple machines."""
        if len(self.machines) > 1:
            raise ValueError("Operation has multiple machines.")
        return self.machines[0]

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        machines = (
            self.machines[0] if len(self.machines) == 1 else self.machines
        )
        return (
            f"O(m={machines}, d={self.duration}, "
            f"j={self.job_id}, p={self.position_in_job})"
        )
