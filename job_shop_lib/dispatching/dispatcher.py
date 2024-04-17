"""Home of the `Dispatcher` class."""

from __future__ import annotations

from collections.abc import Callable
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
        pruning_function:
            The pipeline of pruning methods to be used to filter out
            operations from the list of available operations.
    """

    __slots__ = (
        "instance",
        "schedule",
        "_machine_next_available_time",
        "_job_next_operation_index",
        "_job_next_available_time",
        "pruning_function",
    )

    def __init__(
        self,
        instance: JobShopInstance,
        pruning_function: (
            Callable[[Dispatcher, list[Operation]], list[Operation]] | None
        ) = None,
    ) -> None:
        """Initializes the object with the given instance.

        Args:
            instance:
                The instance of the job shop problem to be solved.
            pruning_strategies:
                A list of pruning strategies to be used to filter out
                operations from the list of available operations. Supported
                values are 'dominated_operations' and 'non_immediate_machines'.
                Defaults to [PruningStrategy.DOMINATED_OPERATIONS]. To disable
                pruning, pass an empty list.
        """

        self.instance = instance
        self.schedule = Schedule(self.instance)
        self._machine_next_available_time = [0] * self.instance.num_machines
        self._job_next_operation_index = [0] * self.instance.num_jobs
        self._job_next_available_time = [0] * self.instance.num_jobs
        self.pruning_function = pruning_function

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

    @classmethod
    def create_schedule_from_raw_solution(
        cls, instance: JobShopInstance, raw_solution: list[list[Operation]]
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
        dispatcher = cls(instance)
        dispatcher.reset()
        raw_solution_deques = [
            deque(operations) for operations in raw_solution
        ]
        while not dispatcher.schedule.is_complete():
            for machine_id, operations in enumerate(raw_solution_deques):
                if not operations:
                    continue
                operation = operations[0]
                if dispatcher.is_operation_ready(operation):
                    dispatcher.dispatch(operation, machine_id)
                    operations.popleft()
        return dispatcher.schedule

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
        return self.min_start_time(available_operations)

    def min_start_time(self, operations: list[Operation]) -> int:
        """Returns the minimum start time of the available operations."""
        if not operations:
            return self.schedule.makespan()
        min_start_time = float("inf")
        for op in operations:
            for machine_id in op.machines:
                start_time = self.start_time(op, machine_id)
                min_start_time = min(min_start_time, start_time)
        return int(min_start_time)

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
        if self.pruning_function is not None:
            available_operations = self.pruning_function(
                self, available_operations
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
