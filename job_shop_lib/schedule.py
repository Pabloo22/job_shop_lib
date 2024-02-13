from typing import Optional

from job_shop_lib import ScheduledOperation, JobShopInstance


class Schedule:
    __slots__ = ("instance", "schedule")

    def __init__(
        self,
        instance: JobShopInstance,
        schedule: Optional[list[list[ScheduledOperation]]] = None,
    ):
        if schedule is None:
            schedule = [[] for _ in range(instance.num_machines)]

        self.instance = instance
        self.schedule = schedule

    @staticmethod
    def get_empty_schedule(
        num_machines: int,
    ) -> list[list[ScheduledOperation]]:
        empty_schedule: list[list[ScheduledOperation]] = [
            [] for _ in range(num_machines)
        ]
        return empty_schedule

    def is_complete(self) -> bool:
        return all(
            len(machine_schedule) == len(job)
            for machine_schedule, job in zip(self.schedule, self.instance.jobs)
        )

    def dispatch(
        self, scheduled_operation: ScheduledOperation, check: bool = True
    ):
        if check:
            self._check_start_time(scheduled_operation)

        self.schedule[scheduled_operation.machine_id].append(
            scheduled_operation
        )

    def _check_start_time(self, scheduled_operation: ScheduledOperation):
        is_first_operation = not self.schedule[scheduled_operation.machine_id]
        if is_first_operation:
            return

        last_operation = self.schedule[scheduled_operation.machine_id][-1]
        if last_operation.end_time <= scheduled_operation.start_time:
            return

        raise ValueError(
            "Operation cannot be scheduled before the last operation on "
            "the same machine: end time of last operation "
            f"({last_operation.end_time}) > start time of new operation "
            f"({scheduled_operation.start_time})."
        )
