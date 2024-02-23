from typing import Optional

from job_shop_lib import ScheduledOperation, JobShopInstance


class Schedule:
    __slots__ = (
        "instance",
        "_schedule",
        "num_scheduled_operations",
        "metadata",
    )

    def __init__(
        self,
        instance: JobShopInstance,
        schedule: Optional[list[list[ScheduledOperation]]] = None,
        **metadata,
    ):
        if schedule is None:
            schedule = [[] for _ in range(instance.num_machines)]

        Schedule.check_schedule(schedule)

        self.instance = instance
        self._schedule = schedule
        self.num_scheduled_operations = sum(
            len(machine_schedule) for machine_schedule in self.schedule
        )
        self.metadata = metadata

    @property
    def schedule(self) -> list[list[ScheduledOperation]]:
        return self._schedule

    @schedule.setter
    def schedule(self, new_schedule: list[list[ScheduledOperation]]):
        Schedule.check_schedule(new_schedule)
        self._schedule = new_schedule
        self.num_scheduled_operations = sum(
            len(machine_schedule) for machine_schedule in self.schedule
        )

    def reset(self):
        self.schedule = [[] for _ in range(self.instance.num_machines)]

    def makespan(self) -> int:
        max_end_time = 0
        for machine_schedule in self.schedule:
            if machine_schedule:
                max_end_time = max(max_end_time, machine_schedule[-1].end_time)
        return max_end_time

    def is_complete(self) -> bool:
        return self.num_scheduled_operations == self.instance.num_operations

    def add(self, scheduled_operation: ScheduledOperation):
        self._check_start_time_of_new_operation(scheduled_operation)
        self.schedule[scheduled_operation.machine_id].append(
            scheduled_operation
        )
        self.num_scheduled_operations += 1

    def _check_start_time_of_new_operation(
        self,
        new_operation: ScheduledOperation,
    ):
        is_first_operation = not self.schedule[new_operation.machine_id]
        if is_first_operation:
            return

        last_operation = self.schedule[new_operation.machine_id][-1]
        self._check_start_time(new_operation, last_operation)

    @staticmethod
    def check_schedule(schedule: list[list[ScheduledOperation]]):
        for machine_id, scheduled_operations in enumerate(schedule):
            for i, scheduled_operation in enumerate(scheduled_operations):
                if scheduled_operation.machine_id != machine_id:
                    raise ValueError(
                        "The machine id of the scheduled operation "
                        f"({ScheduledOperation.machine_id}) does not match "
                        f"the machine id of the machine schedule ({machine_id}"
                        f"). Index of the operation: [{machine_id}][{i}]."
                    )

                if i == 0:
                    continue

                Schedule._check_start_time(
                    scheduled_operation, scheduled_operations[i - 1]
                )

    @staticmethod
    def _check_start_time(
        scheduled_operation: ScheduledOperation,
        previous_operation: ScheduledOperation,
    ):
        """Raises a ValueError if the start time of the new operation is before
        the end time of the last operation on the same machine."""

        if previous_operation.end_time <= scheduled_operation.start_time:
            return

        raise ValueError(
            "Operation cannot be scheduled before the last operation on "
            "the same machine: end time of last operation "
            f"({previous_operation.end_time}) > start time of new operation "
            f"({scheduled_operation.start_time})."
        )

    def __repr__(self) -> str:
        return str(self.schedule)
