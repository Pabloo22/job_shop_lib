"""Contains functions to prune (filter) operations.

This functions are used by the `Dispatcher` class to reduce the
amount of available operations to choose from.
"""

from collections.abc import Callable, Iterable

from job_shop_lib import Operation
from job_shop_lib.dispatching import Dispatcher


def create_composite_pruning_function(
    pruning_functions: Iterable[
        Callable[[Dispatcher, list[Operation]], list[Operation]]
    ],
) -> Callable[[Dispatcher, list[Operation]], list[Operation]]:
    """Creates and returns a composite pruning strategy function based on the
    specified list of pruning strategies.
    The composite pruning strategy function filters out operations based on
    the specified list of pruning strategies.
    Args:
        pruning_strategies:
            A list of pruning strategies to be used. Supported values are
            'dominated_operations' and 'non_immediate_machines'.
    Returns:
        A function that takes a Dispatcher instance and a list of Operation
        instances as input and returns a list of Operation instances based on
        the specified list of pruning strategies.
    Raises:
        ValueError: If any of the pruning strategies in the list are not
            recognized or are not supported.
    """

    def composite_pruning_function(
        dispatcher: Dispatcher, operations: list[Operation]
    ) -> list[Operation]:
        pruned_operations = operations
        for pruning_function in pruning_functions:
            pruned_operations = pruning_function(dispatcher, pruned_operations)

        return pruned_operations

    return composite_pruning_function


def prune_dominated_operations(
    dispatcher: Dispatcher, operations: list[Operation]
) -> list[Operation]:
    """Filters out all the operations that are dominated.
    An operation is dominated if there is another operation that ends before
    it starts on the same machine.
    """

    min_machine_end_times = _get_min_machine_end_times(dispatcher, operations)

    non_dominated_operations: list[Operation] = []
    for operation in operations:
        # One benchmark instance has an operation with duration 0
        if operation.duration == 0:
            return [operation]
        for machine_id in operation.machines:
            start_time = dispatcher.start_time(operation, machine_id)
            is_dominated = start_time >= min_machine_end_times[machine_id]
            if not is_dominated:
                non_dominated_operations.append(operation)
                break

    return non_dominated_operations


def prune_non_immediate_machines(
    dispatcher: Dispatcher, operations: list[Operation]
) -> list[Operation]:
    """Filters out all the operations associated with machines which earliest
    operation is not the current time."""

    is_immediate_machine = _get_immediate_machines(dispatcher, operations)
    non_dominated_operations: list[Operation] = []
    for operation in operations:
        if any(
            is_immediate_machine[machine_id]
            for machine_id in operation.machines
        ):
            non_dominated_operations.append(operation)

    return non_dominated_operations


def _get_min_machine_end_times(
    dispatcher: Dispatcher, available_operations: list[Operation]
) -> list[int | float]:
    end_times_per_machine = [float("inf")] * dispatcher.instance.num_machines
    for op in available_operations:
        for machine_id in op.machines:
            start_time = dispatcher.start_time(op, machine_id)
            end_times_per_machine[machine_id] = min(
                end_times_per_machine[machine_id], start_time + op.duration
            )
    return end_times_per_machine


def _get_immediate_machines(
    self: Dispatcher, available_operations: list[Operation]
) -> list[bool]:
    """Returns the machine ids of the machines that have at least one
    operation with the lowest start time (i.e. the start time)."""
    working_machines = [False] * self.instance.num_machines
    # We can't use the current_time directly because it will cause
    # an infinite loop.
    current_time = self.min_start_time(available_operations)
    for op in available_operations:
        for machine_id in op.machines:
            if self.start_time(op, machine_id) == current_time:
                working_machines[machine_id] = True
    return working_machines
