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

    def reset(self) -> None:
        self.schedule = Schedule(self.instance)
        self.machine_next_available_time = [0] * self.instance.num_machines
        self.job_next_operation_index = [0] * self.instance.num_jobs

    def step(self, operation: Operation, machine_id: int) -> None:
        if not self.is_operation_ready(operation):
            raise ValueError("Operation is not ready to be scheduled.")

        timestep = self.machine_next_available_time[machine_id]

        scheduled_operation = ScheduledOperation(
            operation, machine_id, timestep
        )
        self.schedule.dispatch(scheduled_operation)

        self.machine_next_available_time[machine_id] += operation.duration
        self.job_next_operation_index[operation.job_id] += 1

    def is_operation_ready(self, operation: Operation) -> bool:
        return (
            self.job_next_operation_index[operation.job_id]
            == operation.position_in_job
        )
