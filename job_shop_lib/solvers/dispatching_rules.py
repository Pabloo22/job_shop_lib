from typing import Callable
import random

from job_shop_lib import Dispatcher, Operation


def dispatching_rule_factory(
    dispatching_rule: str,
) -> Callable[[Dispatcher], Operation]:
    dispatching_rules = {
        "shortest_processing_time": shortest_processing_time_rule,
        "first_come_first_served": first_come_first_served_rule,
        "most_work_remaining": most_work_remaining_rule,
        "spt": shortest_processing_time_rule,
        "fcfs": first_come_first_served_rule,
        "mwkr": most_work_remaining_rule,
        "random": random_operation_rule,
    }

    dispatching_rule = dispatching_rule.lower()
    if dispatching_rule not in dispatching_rules:
        raise ValueError(
            f"Dispatching rule {dispatching_rule} not recognized. Available "
            f"dispatching rules: {', '.join(dispatching_rules)}."
        )

    return dispatching_rules[dispatching_rule]


def machine_chooser_factory(
    machine_chooser: str,
) -> Callable[[Dispatcher, Operation], int]:
    machine_choosers = {
        "first": lambda _, operation: operation.machines[0],
        "random": lambda _, operation: random.choice(operation.machines),
    }

    machine_chooser = machine_chooser.lower()
    if machine_chooser not in machine_choosers:
        raise ValueError(
            f"Machine chooser {machine_chooser} not recognized. Available "
            f"machine choosers: {', '.join(machine_choosers)}."
        )

    return machine_choosers[machine_chooser]


def shortest_processing_time_rule(dispatcher: Dispatcher) -> Operation:
    """Dispatches the operation with the shortest duration."""
    return min(
        dispatcher.available_operations(),
        key=lambda operation: operation.duration,
    )


def first_come_first_served_rule(dispatcher: Dispatcher) -> Operation:
    """Dispatches the operation with the lowest position in job."""
    return min(
        dispatcher.available_operations(),
        key=lambda operation: operation.position_in_job,
    )


def most_work_remaining_rule(dispatcher: Dispatcher) -> Operation:
    """Dispatches the operation which job has the most remaining work."""
    job_remaining_work = [0] * dispatcher.instance.num_jobs
    for operation in dispatcher.uncompleted_operations():
        job_remaining_work[operation.job_id] += operation.duration

    return max(
        dispatcher.available_operations(),
        key=lambda operation: job_remaining_work[operation.job_id],
    )


def random_operation_rule(dispatcher: Dispatcher) -> Operation:
    """Dispatches a random operation."""
    return random.choice(dispatcher.available_operations())
