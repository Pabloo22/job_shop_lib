"""Home of the Dispatcher class."""

from enum import Enum
from typing import Callable
from collections import deque

from job_shop_lib import (
    JobShopInstance,
    Schedule,
    ScheduledOperation,
    Operation,
)


class PruningMethod(str, Enum):
    """Enumeration of pruning strategies."""

    DOMINATED_OPERATIONS = "dominated_operations"
    NON_IMMEDIATE_MACHINES = "non_immediate_machines"


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
        pruning_pipeline:
            The pipeline of pruning methods to be used to filter out
            operations from the list of available operations.
    """

    __slots__ = (
        "instance",
        "schedule",
        "_machine_next_available_time",
        "_job_next_operation_index",
        "_job_next_available_time",
        "_pruning_pipeline",
    )

    def __init__(
        self,
        instance: JobShopInstance,
        pruning_methods: list[str] | None = None,
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

        if pruning_methods is None:
            pruning_methods = [PruningMethod.DOMINATED_OPERATIONS]

        self._pruning_pipeline = self.create_composite_pruning_pipeline(
            pruning_methods
        )

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
        dispatcher = cls(instance, pruning_methods=[])
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
        available_operations = self._pruning_pipeline(available_operations)
        return available_operations

    def _available_operations(self) -> list[Operation]:
        available_operations = []
        for job_id, next_position in enumerate(self.job_next_operation_index):
            if next_position == len(self.instance.jobs[job_id]):
                continue
            operation = self.instance.jobs[job_id][next_position]
            available_operations.append(operation)
        return available_operations

    def prune_dominated_operations(
        self, operations: list[Operation]
    ) -> list[Operation]:
        """Filters out all the operations that are dominated.

        An operation is dominated if there is another operation that ends
        before it starts on the same machine.
        """

        min_machine_end_times = self._get_min_machine_end_times(operations)

        non_dominated_operations: list[Operation] = []
        for operation in operations:
            # One benchmark instance has an operation with duration 0
            if operation.duration == 0:
                return [operation]
            for machine_id in operation.machines:
                start_time = self.start_time(operation, machine_id)
                is_dominated = start_time >= min_machine_end_times[machine_id]
                if not is_dominated:
                    non_dominated_operations.append(operation)
                    break

        return non_dominated_operations

    def prune_non_immediate_machines(
        self, operations: list[Operation]
    ) -> list[Operation]:
        """Filters out all the operations associated with machines which
        earliest operation is not the current time."""

        is_immediate_machine = self._get_immediate_machines(operations)
        non_dominated_operations: list[Operation] = []
        for operation in operations:
            if any(
                is_immediate_machine[machine_id]
                for machine_id in operation.machines
            ):
                non_dominated_operations.append(operation)

        return non_dominated_operations

    def _get_min_machine_end_times(
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

    def _get_immediate_machines(
        self, available_operations: list[Operation]
    ) -> list[bool]:
        """Returns the machine ids of the machines that have at least one
        operation with the lowest start time (i.e. the start time)."""
        working_machines = [False] * self.instance.num_machines
        # We can't use the current_time directly because it will cause
        # an infinite loop.
        current_time = self.min_start_time(available_operations)
        for operation in available_operations:
            for machine_id in operation.machines:
                if self.start_time(operation, machine_id) == current_time:
                    working_machines[machine_id] = True
        return working_machines

    def create_composite_pruning_pipeline(
        self,
        pruning_strategies: list[PruningMethod | str],
    ) -> Callable[[list[Operation]], list[Operation]]:
        """Creates and returns a composite pruning strategy function based on
        the specified list of pruning strategies.

        The composite pruning strategy function filters out operations based on
        the specified list of pruning strategies.

        Args:
            pruning_strategies:
                A list of pruning strategies to be used. Supported values are
                'dominated_operations' and 'non_immediate_machines'.

        Returns:
            A function that takes a Dispatcher instance and a list of Operation
            instances as input and returns a list of Operation instances based
            on the specified list of pruning strategies.

        Raises:
            ValueError: If any of the pruning strategies in the list are not
                recognized or are not supported.
        """
        pruning_strategy_functions = [
            self.pruning_strategy_factory(pruning_strategy)
            for pruning_strategy in pruning_strategies
        ]

        def composite_pruning_strategy(
            operations: list[Operation],
        ) -> list[Operation]:
            pruned_operations = operations
            for pruning_strategy in pruning_strategy_functions:
                pruned_operations = pruning_strategy(pruned_operations)

            return pruned_operations

        return composite_pruning_strategy

    def pruning_strategy_factory(
        self,
        pruning_strategy: str | PruningMethod,
    ) -> Callable[[list[Operation]], list[Operation]]:
        """Creates and returns a pruning strategy function based on the
        specified pruning strategy name.

        The pruning strategy function filters out operations based on certain
        criteria such as dominated operations, non-immediate machines, etc.

        Args:
            pruning_strategy:
                The name of the pruning strategy to be used. Supported values
                are 'dominated_operations' and 'non_immediate_machines'.

        Returns:
            A function that takes a Dispatcher instance and a list of
            `Operation` instances as input and returns a list of `Operation`
            instances based on the specified pruning strategy.

        Raises:
            ValueError: If the pruning_strategy argument is not recognized or
                is not supported.
        """
        pruning_strategies = {
            PruningMethod.DOMINATED_OPERATIONS: (
                self.prune_dominated_operations
            ),
            PruningMethod.NON_IMMEDIATE_MACHINES: (
                self.prune_non_immediate_machines
            ),
        }

        if pruning_strategy not in pruning_strategies:
            raise ValueError(
                f"Unsupported pruning strategy '{pruning_strategy}'. "
                f"Supported values are {', '.join(pruning_strategies.keys())}."
            )

        return pruning_strategies[pruning_strategy]  # type: ignore[index]
