"""Contains functions to prune (filter) operations.

This functions are used by the `Dispatcher` class to reduce the
amount of available operations to choose from.
"""

from typing import List, Set
from collections.abc import Callable

from job_shop_lib import Operation
from job_shop_lib.dispatching import Dispatcher


ReadyOperationsFilter = Callable[
    [Dispatcher, List[Operation]], List[Operation]
]


def filter_non_idle_machines(
    dispatcher: Dispatcher, operations: List[Operation]
) -> List[Operation]:
    """Filters out all the operations associated with non-idle machines.

    A machine is considered idle if there are no ongoing operations
    currently scheduled on it. This filter removes operations that are
    associated with machines that are busy (i.e., have at least one
    uncompleted operation).

    Utilizes :meth:``Dispatcher.ongoing_operations()`` to determine machine
    statuses.

    Args:
        dispatcher: The dispatcher object.
        operations: The list of operations to filter.

    Returns:
        The list of operations that are associated with idle machines.
    """
    current_time = dispatcher.min_start_time(operations)
    non_idle_machines = _get_non_idle_machines(dispatcher, current_time)

    # Filter operations to keep those that are associated with at least one
    # idle machine
    filtered_operations: List[Operation] = []
    for operation in operations:
        if all(
            machine_id in non_idle_machines
            for machine_id in operation.machines
        ):
            continue
        filtered_operations.append(operation)

    return filtered_operations


def _get_non_idle_machines(
    dispatcher: Dispatcher, current_time: int
) -> Set[int]:
    """Returns the set of machine ids that are currently busy (i.e., have at
    least one uncompleted operation)."""

    non_idle_machines = set()
    for machine_schedule in dispatcher.schedule.schedule:
        for scheduled_operation in reversed(machine_schedule):
            is_completed = scheduled_operation.end_time <= current_time
            if is_completed:
                break
            non_idle_machines.add(scheduled_operation.machine_id)

    return non_idle_machines


def filter_non_immediate_operations(
    dispatcher: Dispatcher, operations: List[Operation]
) -> List[Operation]:
    """Filters out all the operations that can't start immediately.

    An operation can start immediately if its earliest start time is the
    current time.

    The current time is determined by the minimum start time of the
    operations.

    Args:
        dispatcher: The dispatcher object.
        operations: The list of operations to filter.
    """

    min_start_time = dispatcher.min_start_time(operations)
    immediate_operations: List[Operation] = []
    for operation in operations:
        start_time = dispatcher.earliest_start_time(operation)
        if start_time == min_start_time:
            immediate_operations.append(operation)

    return immediate_operations


def filter_dominated_operations(
    dispatcher: Dispatcher, operations: List[Operation]
) -> List[Operation]:
    """Filters out all the operations that are dominated.
    An operation is dominated if there is another operation that ends before
    it starts on the same machine.
    """

    min_machine_end_times = _get_min_machine_end_times(dispatcher, operations)

    non_dominated_operations: List[Operation] = []
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


def filter_non_immediate_machines(
    dispatcher: Dispatcher, operations: List[Operation]
) -> List[Operation]:
    """Filters out all the operations associated with machines which earliest
    operation is not the current time."""

    is_immediate_machine = _get_immediate_machines(dispatcher, operations)
    non_dominated_operations: List[Operation] = []
    for operation in operations:
        if any(
            is_immediate_machine[machine_id]
            for machine_id in operation.machines
        ):
            non_dominated_operations.append(operation)

    return non_dominated_operations


def _get_min_machine_end_times(
    dispatcher: Dispatcher, available_operations: List[Operation]
) -> List[float]:
    end_times_per_machine = [float("inf")] * dispatcher.instance.num_machines
    for op in available_operations:
        for machine_id in op.machines:
            start_time = dispatcher.start_time(op, machine_id)
            end_times_per_machine[machine_id] = min(
                end_times_per_machine[machine_id], start_time + op.duration
            )
    return end_times_per_machine


def _get_immediate_machines(
    self: Dispatcher, available_operations: List[Operation]
) -> List[bool]:
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
