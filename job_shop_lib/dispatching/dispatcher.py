"""Home of the Dispatcher class."""

from collections import deque

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
        filter_bad_choices:
            If True, the dispatcher will filter out operations that are
            sub-optimal choices from the available operations. An operation is
            sub-optimal if there is another operation that could be scheduled
            in the same machine that would finish before the start time of
            the sub-optimal operation.
        focus_on_current_time_machine:
            If True, the dispatcher will focus on the machine that is currently
            processing an operation. This is useful for dispatching operations
            in a way that is more similar to the way humans would do it.
    """

    def __init__(
        self,
        instance: JobShopInstance,
        filter_dominated_operations: bool = True,
        focus_on_current_time_machine: bool = False,
    ) -> None:
        """Initializes the object with the given instance.

        Args:
            instance:
                The instance of the job shop problem to be solved.
            filter_bad_choices:
                If True, the dispatcher will filter out operations that are
                sub-optimal choices from the available operations. An operation
                is sub-optimal if there is another operation that could be
                scheduled in the same machine that would finish before the
                start time of the sub-optimal operation.
        """

        self.instance = instance
        self.schedule = Schedule(self.instance)
        self._machine_next_available_time = [0] * self.instance.num_machines
        self._job_next_operation_index = [0] * self.instance.num_jobs
        self._job_next_available_time = [0] * self.instance.num_jobs
        self.filter_dominated_operations = filter_dominated_operations
        self.focus_on_current_time_machine = focus_on_current_time_machine

    @property
    def machine_next_available_time(self) -> list[int]:
        """Returns the next available time for each machine."""
        return self._machine_next_available_time

    @property
    def job_next_operation_index(self) -> list[int]:
        """Returns the index of the next operation to be scheduled for each
        job."""
        return self._job_next_operation_index

    @property
    def job_next_available_time(self) -> list[int]:
        """Returns the next available time for each job."""
        return self._job_next_available_time

    def create_schedule_from_raw_solution(
        self, raw_solution: list[list[Operation]]
    ) -> Schedule:
        """Creates a schedule from a raw solution.

        A raw solution is a list of lists of operations, where each list
        represents the order of operations for a machine.

        Args:
            instance:
                The instance of the job shop problem to be solved.
            raw_solution:
                A list of lists of operations, where each list represents the
                order of operations for a machine.

        Returns:
            A Schedule object representing the solution.
        """
        self.reset()
        raw_solution_deques = [
            deque(operations) for operations in raw_solution
        ]
        while not self.schedule.is_complete():
            for machine_id, operations in enumerate(raw_solution_deques):
                if not operations:
                    continue
                operation = operations[0]
                if self.is_operation_ready(operation):
                    self.dispatch(operation, machine_id)
                    operations.popleft()
        return self.schedule

    def reset(self) -> None:
        """Resets the dispatcher to its initial state."""
        self.schedule.reset()
        self._machine_next_available_time = [0] * self.instance.num_machines
        self._job_next_operation_index = [0] * self.instance.num_jobs
        self._job_next_available_time = [0] * self.instance.num_jobs

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

        start_time = self.start_time(operation, machine_id)

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

    def start_time(self, operation: Operation, machine_id: int) -> int:
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
        return self._min_start_time(available_operations)

    def _min_start_time(self, available_operations: list[Operation]) -> int:
        """Returns the minimum start time of the available operations."""
        if not available_operations:
            return self.schedule.makespan()
        min_start_time = float("inf")
        for op in available_operations:
            for machine_id in op.machines:
                start_time = self.start_time(op, machine_id)
                min_start_time = min(min_start_time, start_time)
        return int(min_start_time)

    def available_operations(self) -> list[Operation]:
        """Returns a list of available operations for processing, optionally
        filtering out operations known to be bad choices.

        This method first gathers all possible next operations from the jobs
        being processed. It then optionally filters these operations to exclude
        ones that are deemed inefficient or suboptimal choices.

        An operation is sub-optimal if there is another operation that could
        be scheduled in the same machine that would finish before the start
        time of the sub-optimal operation.

        Returns:
            A list of Operation objects that are available for scheduling.

        Raises:
            ValueError: If using the filter_bad_choices option and one of the
                available operations can be scheduled in more than one machine.
        """
        available_operations = self._available_operations()
        if self.focus_on_current_time_machine:
            available_operations = self._focus_on_current_time_machine(
                available_operations
            )
        if self.filter_dominated_operations:
            available_operations = self._filter_dominated_operations(
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

    def _filter_dominated_operations(
        self, available_operations: list[Operation]
    ) -> list[Operation]:
        end_times_per_machine = self._end_times_per_machine(
            available_operations
        )

        optimized_operations: list[Operation] = []
        for op in available_operations:
            if op.duration == 0:
                return [op]
            for machine_id in op.machines:
                start_time = self.start_time(op, machine_id)
                is_bad_choice = start_time >= end_times_per_machine[machine_id]
                if not is_bad_choice:
                    optimized_operations.append(op)
                    # Assumes adding to optimized if any machine is not a bad
                    # choice, and breaks to avoid adding the same operation
                    # multiple times.
                    break

        return optimized_operations

    def _focus_on_current_time_machine(
        self, available_operations: list[Operation]
    ) -> list[Operation]:
        working_machines = self._working_machines(available_operations)
        optimized_operations: list[Operation] = []
        for op in available_operations:
            for machine_id in op.machines:
                if working_machines[machine_id]:
                    optimized_operations.append(op)
                    break

        return optimized_operations

    def _end_times_per_machine(
        self, available_operations: list[Operation]
    ) -> list[int | float]:
        end_times_per_machine = [float("inf")] * self.instance.num_machines
        for op in available_operations:
            for machine_id in op.machines:
                start_time = self.start_time(op, machine_id)
                end_times_per_machine[machine_id] = min(
                    end_times_per_machine[machine_id], start_time + op.duration
                )
        return end_times_per_machine

    def _working_machines(
        self, available_operations: list[Operation]
    ) -> list[bool]:
        """Returns the machine ids of the machines that have at least one
        operation with the lowest start time (i.e. the start time)."""
        working_machines = [False] * self.instance.num_machines
        # We can't use the current_time directly because it will cause
        # an infinite loop.
        current_time = self._min_start_time(available_operations)
        for op in available_operations:
            for machine_id in op.machines:
                if self.start_time(op, machine_id) == current_time:
                    working_machines[machine_id] = True
        return working_machines

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
