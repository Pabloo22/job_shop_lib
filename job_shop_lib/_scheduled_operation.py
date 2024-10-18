"""Home of the `ScheduledOperation` class."""

from job_shop_lib import Operation
from job_shop_lib.exceptions import ValidationError


class ScheduledOperation:
    """Data structure to store a scheduled operation.

    Args:
        operation:
            The :class:`Operation` object that is scheduled.
        start_time:
            The time at which the operation is scheduled to start.
        machine_id:
            The id of the machine on which the operation is scheduled.

    Raises:
        ValidationError:
            If the given machine_id is not in the list of valid machines
            for the operation.
    """

    __slots__ = {
        "operation": "The :class:`Operation` object that is scheduled.",
        "start_time": "The time at which the operation is scheduled to start.",
        "_machine_id": (
            "The id of the machine on which the operation is scheduled."
        ),
    }

    def __init__(self, operation: Operation, start_time: int, machine_id: int):
        self.operation: Operation = operation
        self.start_time: int = start_time
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
            raise ValidationError(
                f"Operation cannot be scheduled on machine {value}. "
                f"Valid machines are {self.operation.machines}."
            )
        self._machine_id = value

    @property
    def job_id(self) -> int:
        """Returns the id of the job that the operation belongs to."""
        return self.operation.job_id

    @property
    def position_in_job(self) -> int:
        """Returns the position (starting at zero) of the operation in the
        job."""
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
            self.operation == value.operation
            and self.start_time == value.start_time
            and self.machine_id == value.machine_id
        )
