from typing import Optional

from job_shop_lib import ScheduledOperation, JobShopInstance


class Schedule:
    __slots__ = ("instance", "schedule", "check", "metadata")

    def __init__(
        self,
        instance: JobShopInstance,
        schedule: Optional[list[list[ScheduledOperation]]] = None,
        check: bool = True,
        **metadata,
    ):
        if schedule is None:
            schedule = [[] for _ in range(instance.num_machines)]

        if check:
            self._check_initialization(schedule)

        self.instance = instance
        self.schedule = schedule
        self.check = check
        self.metadata = metadata

    @staticmethod
    def get_empty_schedule(
        num_machines: int,
    ) -> list[list[ScheduledOperation]]:
        empty_schedule: list[list[ScheduledOperation]] = [
            [] for _ in range(num_machines)
        ]
        return empty_schedule

    def is_complete(self) -> bool:
        num_scheduled_operations = sum(
            len(machine_schedule) for machine_schedule in self.schedule
        )
        return num_scheduled_operations == self.instance.num_operations

    def is_empty(self) -> bool:
        return all(not machine_schedule for machine_schedule in self.schedule)

    def dispatch(self, scheduled_operation: ScheduledOperation):
        if self.check:
            self._check_start_time_of_new_operation(scheduled_operation)

        self.schedule[scheduled_operation.machine_id].append(
            scheduled_operation
        )

    def _check_start_time_of_new_operation(
        self,
        new_operation: ScheduledOperation,
    ):
        is_first_operation = not self.schedule[new_operation.machine_id]
        if is_first_operation:
            return

        last_operation = self.schedule[new_operation.machine_id][-1]
        self._check_start_time(new_operation, last_operation)

    def _check_initialization(self, schedule: list[list[ScheduledOperation]]):
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

                self._check_start_time(
                    scheduled_operation, scheduled_operations[i - 1]
                )

    def _check_start_time(
        self,
        scheduled_operation: ScheduledOperation,
        previous_operation: ScheduledOperation,
    ):

        if previous_operation.end_time <= scheduled_operation.start_time:
            return

        raise ValueError(
            "Operation cannot be scheduled before the last operation on "
            "the same machine: end time of last operation "
            f"({previous_operation.end_time}) > start time of new operation "
            f"({scheduled_operation.start_time})."
        )
