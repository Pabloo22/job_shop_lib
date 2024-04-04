"""Home of the Dispatcher class."""

from job_shop_lib import (
    JobShopInstance,
    Schedule,
    ScheduledOperation,
    Operation,
)


class Dispatcher:
    """Handles the logic of scheduling operations on machines.

    This class allow us to just define the order in which operations are
    sequenced and the machines in which they are processed. It is then
    responsible for scheduling the operations on the machines and keeping
    track of the next available time for each machine and job.

    Attributes:
        instance:
            The instance of the job shop problem to be scheduled.
        schedule:
            The schedule of operations on machines.
        machine_next_available_time:
            The next available time for each machine.
        job_next_operation_index:
            The index of the next operation to be scheduled for each job.
        job_next_available_time:
            The next available time for each job.
    """

    def __init__(self, instance: JobShopInstance) -> None:
        """Initializes the object with the given instance.

        Args:
            instance: The instance of the job shop problem to be scheduled.
        """
        self.instance = instance
        self.schedule = Schedule(self.instance)
        self.machine_next_available_time = [0] * self.instance.num_machines
        self.job_next_operation_index = [0] * self.instance.num_jobs
        self.job_next_available_time = [0] * self.instance.num_jobs

    def reset(self) -> None:
        """Resets the dispatcher to its initial state."""
        self.schedule.reset()
        self.machine_next_available_time = [0] * self.instance.num_machines
        self.job_next_operation_index = [0] * self.instance.num_jobs
        self.job_next_available_time = [0] * self.instance.num_jobs

    def dispatch(self, operation: Operation, machine_id: int) -> None:
        """Schedules the given operation on the given machine.

        The start time of the operation is computed based on the next
        available time for the machine and the next available time for the
        job to which the operation belongs. The operation is then scheduled
        on the machine and the tracking attributes are updated.
        Args:
            operation:
                The operation to be scheduled.
            machine_id:
                The id of the machine on which the operation is to be
                scheduled.

        Raises:
            ValueError: If the operation is not ready to be scheduled.
        """

        if not self.is_operation_ready(operation):
            raise ValueError("Operation is not ready to be scheduled.")

        start_time = self.compute_start_time(operation, machine_id)

        scheduled_operation = ScheduledOperation(
            operation, start_time, machine_id
        )
        self.schedule.add(scheduled_operation)
        self._update_tracking_attributes(scheduled_operation)

    def is_operation_ready(self, operation: Operation) -> bool:
        """Returns True if the given operation is ready to be scheduled.

        An operation is ready to be scheduled if it is the next operation
        to be scheduled for its job.

        Args:
            operation:
                The operation to be checked.
        """
        return (
            self.job_next_operation_index[operation.job_id]
            == operation.position_in_job
        )

    def compute_start_time(self, operation: Operation, machine_id: int) -> int:
        """Computes the start time for the given operation on the given
        machine.

        The start time is the maximum of the next available time for the
        machine and the next available time for the job to which the
        operation belongs.

        Args:
            operation:
                The operation to be scheduled.
            machine_id:
                The id of the machine on which the operation is to be
                scheduled.
        """
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

    def current_time(self) -> int:
        """Returns the current time of the schedule.

        The current time is the minimum start time of the available
        operations.
        """
        available_operations = self.available_operations()
        if not available_operations:
            return self.schedule.makespan()
        current_time = float("inf")
        for operation in available_operations:
            for machine_id in operation.machines:
                start_time = self.compute_start_time(operation, machine_id)
                current_time = min(current_time, start_time)
        return int(current_time)

    def available_operations(
        self, filter_bad_choices: bool = True
    ) -> list[Operation]:
        """Returns a list of available operations for processing, optionally
        filtering out operations known to be bad choices.

        This method first gathers all possible next operations from the jobs
        being processed. It then optionally filters these operations to exclude
        ones that are deemed inefficient or suboptimal choices.

        An operation is sub-optimal if there is another operation that could
        be scheduled in the same machine that would finish before the start
        time of the sub-optimal operation.

        Args:
            filter_bad_choices (bool):
                If True, the method filters out operations if there is another
                operation that could be scheduled in the same machine that
                would finish before the start time of the sub-optimal
                operation.
                If False, no filtering is applied, and all next possible
                operations are returned.

        Returns:
            A list of Operation objects that are available for scheduling.

        Raises:
            ValueError: If using the filter_bad_choices option and one of the
                available operations can be scheduled in more than one machine.
        """
        available_operations = self._available_operations()
        if filter_bad_choices:
            available_operations = self._filter_bad_choices(
                available_operations
            )
        return available_operations

    def _available_operations(self) -> list[Operation]:
        available_operations = []
        for job_id, next_position in enumerate(self.job_next_operation_index):
            if next_position == len(self.instance.jobs[job_id]):
                continue
            operation = self.instance.jobs[job_id][next_position]
            available_operations.append(operation)
        return available_operations

    def _filter_bad_choices(
        self, available_operations: list[Operation]
    ) -> list[Operation]:
        end_times_per_machine = [float("inf")] * self.instance.num_machines
        for op in available_operations:
            start_time = self.compute_start_time(op, op.machine_id)
            end_times_per_machine[op.machine_id] = min(
                end_times_per_machine[op.machine_id], start_time + op.duration
            )

        optimized_operations: list[Operation] = []

        for op in available_operations:
            start_time = self.compute_start_time(op, op.machine_id)
            is_bad_choice = end_times_per_machine[op.machine_id] <= start_time
            if not is_bad_choice:
                optimized_operations.append(op)
                end_times_per_machine[op.machine_id] = start_time + op.duration

        return optimized_operations

    def uncompleted_operations(self) -> list[Operation]:
        """Returns the list of operations that have not been scheduled.

        An operation is uncompleted if it has not been scheduled yet.

        It is more efficient than checking all operations in the instance.
        """

        uncompleted_operations = []
        for job_id, next_position in enumerate(self.job_next_operation_index):
            operations = self.instance.jobs[job_id][next_position:]
            uncompleted_operations.extend(operations)
        return uncompleted_operations
