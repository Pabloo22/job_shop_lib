from typing import NamedTuple

from job_shop_lib import Operation


class ScheduledOperation(NamedTuple):
    """Stores information about the scheduled operation."""

    operation: Operation
    start_time: int
    machine_id: int

    @property
    def end_time(self) -> int:
        return self.start_time + self.operation.duration
