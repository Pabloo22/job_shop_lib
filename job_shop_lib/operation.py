"""Home of the Operation class."""

from typing import Optional


class Operation:
    """Stores machine and duration information for a job operation."""

    __slots__ = ("machines", "duration", "_job_id", "_position_in_job", "_id")

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
        self._job_id = job_id
        self._position_in_job = position_in_job
        self._id = operation_id

    @property
    def machine_id(self) -> int:
        """Returns the id of the machine and raises an error if there are
        multiple machines."""
        if len(self.machines) > 1:
            raise ValueError("Operation has multiple machines.")
        return self.machines[0]

    @property
    def job_id(self) -> int:
        """Returns the id of the job."""
        if self._job_id is None:
            raise ValueError("Operation has no job_id.")
        return self._job_id

    @job_id.setter
    def job_id(self, value: int) -> None:
        self._job_id = value

    @property
    def position_in_job(self) -> int:
        """Returns the position of the operation in the job."""
        if self._position_in_job is None:
            raise ValueError("Operation has no position_in_job.")
        return self._position_in_job

    @position_in_job.setter
    def position_in_job(self, value: int) -> None:
        self._position_in_job = value

    @property
    def id(self) -> int:
        """Returns the id of the operation."""
        if self._id is None:
            raise ValueError("Operation has no id.")
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value

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
