from typing import Callable

from job_shop_lib import JobShopInstance, Dispatcher, Schedule, Operation


def dispatching_rule_solver(
    instance: JobShopInstance,
    dispatching_rule: Callable[[Dispatcher], Operation],
    machine_chooser: Callable[
        [Dispatcher, Operation], int
    ] = lambda _, o: o.machines[0],
) -> Schedule:
    dispatcher = Dispatcher(instance)

    while not dispatcher.schedule.is_complete():
        selected_operation = dispatching_rule(dispatcher)
        machine_id = machine_chooser(dispatcher, selected_operation)
        dispatcher.dispatch(selected_operation, machine_id)

    return dispatcher.schedule


def shortest_processing_time(dispatcher: Dispatcher) -> Operation:
    """Dispatches the operation with the shortest duration."""
    return min(
        dispatcher.available_operations(),
        key=lambda operation: operation.duration,
    )


def first_come_first_served(dispatcher: Dispatcher) -> Operation:
    """Dispatches the operation with the lowest id."""
    return min(
        dispatcher.available_operations(),
        key=lambda operation: operation.id,
    )


def most_work_remaining(dispatcher: Dispatcher) -> Operation:
    """Dispatches the operation which job has the most remaining work."""
    job_remaining_work = [0] * dispatcher.instance.num_jobs
    for operation in dispatcher.uncompleted_operations():
        job_remaining_work[operation.job_id] += operation.duration

    return max(
        dispatcher.available_operations(),
        key=lambda operation: job_remaining_work[operation.job_id],
    )
