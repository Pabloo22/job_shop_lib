from job_shop_lib import (
    JobShopInstance,
    Schedule,
    ScheduledOperation,
    Operation,
)


class Dispatcher:

    def __init__(self, instance: JobShopInstance) -> None:
        self.instance = instance
        self.schedule = Schedule(self.instance)
        self.machine_next_available_time = [0] * self.instance.num_machines
        self.job_next_operation_index = [0] * self.instance.num_jobs
        self.job_next_available_time = [0] * self.instance.num_jobs

    def reset(self) -> None:
        self.schedule = Schedule(self.instance)
        self.machine_next_available_time = [0] * self.instance.num_machines
        self.job_next_operation_index = [0] * self.instance.num_jobs

    def step(self, operation: Operation, machine_id: int) -> None:
        if not self.is_operation_ready(operation):
            raise ValueError("Operation is not ready to be scheduled.")

        start_time = self.compute_start_time(operation, machine_id)

        scheduled_operation = ScheduledOperation(
            operation, start_time, machine_id
        )
        self.schedule.add(scheduled_operation)

        self.machine_next_available_time[machine_id] = (
            start_time + operation.duration
        )
        self.job_next_operation_index[operation.job_id] += 1
        self.job_next_available_time[operation.job_id] = (
            start_time + operation.duration
        )

    def is_operation_ready(self, operation: Operation) -> bool:
        return (
            self.job_next_operation_index[operation.job_id]
            == operation.position_in_job
        )

    def compute_start_time(self, operation: Operation, machine_id: int) -> int:
        return max(
            self.machine_next_available_time[machine_id],
            self.job_next_available_time[operation.job_id],
        )
