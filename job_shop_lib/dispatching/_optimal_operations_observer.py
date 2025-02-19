"""Home of the `OptimalOperationsObserver` class."""

from typing import List, Set, Dict
from job_shop_lib.dispatching import DispatcherObserver, Dispatcher
from job_shop_lib import Schedule, Operation, ScheduledOperation
from job_shop_lib.exceptions import ValidationError


class OptimalOperationsObserver(DispatcherObserver):
    """Observer that identifies which available operations are optimal based on
    a reference schedule.

    This observer compares the available operations at each step with a
    reference schedule to determine which operations would lead to the optimal
    solution. It can be used for training purposes or to analyze decision
    making in dispatching algorithms.

    Attributes:
        optimal_operations: Set of operations that are considered optimal
            based on the reference schedule.
        reference_schedule: The reference schedule used to determine optimal
            operations.
        _operation_to_scheduled: Dictionary mapping operations to their
            scheduled versions in the reference schedule.

    Args:
        dispatcher: The dispatcher instance to observe.
        reference_schedule: A complete schedule that represents the optimal
            or reference solution.
        subscribe: If True, automatically subscribes to the dispatcher.

    Raises:
        ValidationError: If the reference schedule is incomplete or if it
            doesn't match the dispatcher's instance.
    """

    _is_singleton = False

    def __init__(
        self,
        dispatcher: Dispatcher,
        reference_schedule: Schedule,
        *,
        subscribe: bool = True,
    ):
        super().__init__(dispatcher, subscribe=subscribe)

        if not reference_schedule.is_complete():
            raise ValidationError("Reference schedule must be complete.")

        if reference_schedule.instance != dispatcher.instance:
            raise ValidationError(
                "Reference schedule instance does not match dispatcher "
                "instance."
            )

        self.reference_schedule = reference_schedule
        self.optimal_available: Set[Operation] = set()
        self._operation_to_scheduled: Dict[Operation, ScheduledOperation] = {}
        self._machine_next_operation_index: List[int] = [0] * len(
            reference_schedule.schedule
        )

        self._build_operation_mapping()
        self._update_optimal_operations()

    def _build_operation_mapping(self) -> None:
        """Builds a mapping from operations to their scheduled versions in
        the reference schedule."""
        for machine_schedule in self.reference_schedule.schedule:
            for scheduled_op in machine_schedule:
                self._operation_to_scheduled[scheduled_op.operation] = (
                    scheduled_op
                )

    def _update_optimal_operations(self) -> None:
        """Updates the set of optimal operations based on current state.

        An operation is considered optimal if it is the next unscheduled
        operation in its machine's sequence according to the reference
        schedule.
        """
        self.optimal_available.clear()
        available_operations = self.dispatcher.available_operations()

        if not available_operations:
            return

        for operation in available_operations:
            scheduled_op = self._operation_to_scheduled[operation]
            machine_index = scheduled_op.machine_id
            next_index = self._machine_next_operation_index[machine_index]

            if (
                scheduled_op
                == self.reference_schedule.schedule[machine_index][next_index]
            ):
                self.optimal_available.add(operation)

    def update(self, scheduled_operation: ScheduledOperation) -> None:
        """Updates the optimal operations after an operation is scheduled.

        Args:
            scheduled_operation: The operation that was just scheduled.
        """
        self._machine_next_operation_index[scheduled_operation.machine_id] += 1
        self._update_optimal_operations()

    def reset(self) -> None:
        """Resets the observer to its initial state."""
        self._machine_next_operation_index = [0] * len(
            self.dispatcher.schedule.schedule
        )
        self.optimal_available.clear()
        self._update_optimal_operations()
