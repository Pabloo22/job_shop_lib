"""Dispatching rules for the job shop scheduling problem.

This module contains functions that implement different dispatching rules for
the job shop scheduling problem. A dispatching rule determines the order in
which operations are selected for execution based on certain criteria such as
shortest processing time, first come first served, etc.
"""

import random

from job_shop_lib import Dispatcher, Operation


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


def most_operations_remaining_rule(dispatcher: Dispatcher) -> Operation:
    """Dispatches the operation which job has the most remaining operations."""
    job_remaining_operations = [0] * dispatcher.instance.num_jobs
    for operation in dispatcher.uncompleted_operations():
        job_remaining_operations[operation.job_id] += 1

    return max(
        dispatcher.available_operations(),
        key=lambda operation: job_remaining_operations[operation.job_id],
    )


def random_operation_rule(dispatcher: Dispatcher) -> Operation:
    """Dispatches a random operation."""
    return random.choice(dispatcher.available_operations())
