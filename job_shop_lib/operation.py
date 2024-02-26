"""Home of the Operation class."""

from __future__ import annotations

from typing import Optional


class Operation:
    """Stores machine and duration information for a job operation.

    Note:
    To increase performance, some solvers such as the CP-SAT solver use
    only integers to represent operation's attributes. Should a problem
    involve operations with non-integer durations, it would be necessary to
    multiply all durations by a sufficiently large integer so that every
    duration is an integer.
    """

    __slots__ = (
        "machines",
        "duration",
        "_job_id",
        "_position_in_job",
        "_operation_id",
    )

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
        self._operation_id = operation_id

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
    def operation_id(self) -> int:
        """Returns the id of the operation."""
        if self._operation_id is None:
            raise ValueError("Operation has no id.")
        return self._operation_id

    @operation_id.setter
    def operation_id(self, value: int) -> None:
        self._operation_id = value

    def __hash__(self) -> int:
        return hash(self.operation_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Operation):
            return NotImplemented
        return self.operation_id == other.operation_id

    def __repr__(self) -> str:
        machines = (
            self.machines[0] if len(self.machines) == 1 else self.machines
        )
        return (
            f"O(m={machines}, d={self.duration}, "
            f"j={self.job_id}, p={self.position_in_job})"
        )
