from job_shop_lib import Operation
from job_shop_lib.dispatching import Dispatcher


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

    min_machine_end_times = _get_min_machine_end_times(dispatcher, operations)

    non_dominated_operations: list[Operation] = []
    for operation in operations:
        if operation.duration == 0:
            return [operation]
        for machine_id in operation.machines:
            start_time = dispatcher.start_time(operation, machine_id)
            is_dominated = start_time > min_machine_end_times[machine_id]
            if not is_dominated:
                non_dominated_operations.append(operation)
                break

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
