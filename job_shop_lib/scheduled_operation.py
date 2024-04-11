"""Home of the `ScheduledOperation` class."""

from job_shop_lib import Operation


class ScheduledOperation:
    """Data structure to store a scheduled operation.

    Attributes:
        operation:
            The `Operation` object that is scheduled.
        start_time:
            The time at which the operation is scheduled to start.
        machine_id:
            The id of the machine on which the operation is scheduled.
    """

    __slots__ = ("operation", "start_time", "_machine_id")

    def __init__(self, operation: Operation, start_time: int, machine_id: int):
        """Initializes the object with the given operation, start time, and
        machine id.

        Args:
            operation:
                The `Operation` object that is scheduled.
            start_time:
                The time at which the operation is scheduled to start.
            machine_id:
                The id of the machine on which the operation is scheduled.

        Raises:
            ValueError:
                If the machine_id is not valid for the operation.
        """
        self.operation = operation
        self.start_time = start_time
        self._machine_id = machine_id
        self.machine_id = machine_id  # Validate machine_id

    @property
    def machine_id(self) -> int:
        """Returns the id of the machine on which the operation has been
        scheduled."""
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
    def job_id(self) -> int:
        """Returns the id of the job that the operation belongs to.

        Raises:
            ValueError: If the operation has no job_id.
        """

        if self.operation.job_id is None:
            raise ValueError("Operation has no job_id.")
        return self.operation.job_id

    @property
    def position(self) -> int:
        """Returns the position (starting at zero) of the operation in the job.

        Raises:
            ValueError: If the operation has no position_in_job.
        """
        if self.operation.position_in_job is None:
            raise ValueError("Operation has no position.")
        return self.operation.position_in_job

    @property
    def end_time(self) -> int:
        """Returns the time at which the operation is scheduled to end."""
        return self.start_time + self.operation.duration

    def __repr__(self) -> str:
        return (
            f"S-Op(operation={self.operation}, "
            f"start_time={self.start_time}, machine_id={self.machine_id})"
        )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, ScheduledOperation):
            return False
        return (
            self.operation is value.operation
            and self.start_time == value.start_time
            and self.machine_id == value.machine_id
        )
