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
        self.schedule.reset()
        self.machine_next_available_time = [0] * self.instance.num_machines
        self.job_next_operation_index = [0] * self.instance.num_jobs
        self.job_next_available_time = [0] * self.instance.num_jobs

    def dispatch(self, operation: Operation, machine_id: int) -> None:
        if not self.is_operation_ready(operation):
            raise ValueError("Operation is not ready to be scheduled.")

        start_time = self.compute_start_time(operation, machine_id)

        scheduled_operation = ScheduledOperation(
            operation, start_time, machine_id
        )
        self.schedule.add(scheduled_operation)
        self._update_tracking_attributes(scheduled_operation)

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

    def _update_tracking_attributes(
        self, scheduled_operation: ScheduledOperation
    ) -> None:
        # Variables defined here to make the lines shorter
        job_id = scheduled_operation.job_id
        machine_id = scheduled_operation.machine_id
        end_time = scheduled_operation.end_time

        self.machine_next_available_time[machine_id] = end_time
        self.job_next_operation_index[job_id] += 1
        self.job_next_available_time[job_id] = end_time

    def available_operations(self) -> list[Operation]:
        available_operations = []
        for job_id, next_position in enumerate(self.job_next_operation_index):
            if next_position == len(self.instance.jobs[job_id]):
                continue
            operation = self.instance.jobs[job_id][next_position]
            available_operations.append(operation)
        return available_operations

    def uncompleted_operations(self) -> list[Operation]:
        uncompleted_operations = []
        for job_id, next_position in enumerate(self.job_next_operation_index):
            operations = self.instance.jobs[job_id][next_position:]
            uncompleted_operations.extend(operations)
        return uncompleted_operations
