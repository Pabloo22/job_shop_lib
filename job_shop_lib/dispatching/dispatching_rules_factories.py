from enum import Enum

from typing import Callable
import random

from job_shop_lib import Operation
from job_shop_lib.dispatching import (
    shortest_processing_time_rule,
    first_come_first_served_rule,
    most_work_remaining_rule,
    most_operations_remaining_rule,
    random_operation_rule,
    Dispatcher,
)

# DispatchingRule = Callable[[Dispatcher], Operation]
# MachineChooser = Callable[[Dispatcher, Operation], int]


class DispatchingRule(str, Enum):
    """Enumeration of dispatching rules for the job shop scheduling problem."""

    SHORTEST_PROCESSING_TIME = "shortest_processing_time"
    FIRST_COME_FIRST_SERVED = "first_come_first_served"
    MOST_WORK_REMAINING = "most_work_remaining"
    MOST_OPERATIONS_REMAINING = "most_operations_remaining"
    RANDOM = "random"


class MachineChooser(str, Enum):
    """Enumeration of machine chooser strategies for the job shop scheduling"""

    FIRST = "first"
    RANDOM = "random"


def dispatching_rule_factory(
    dispatching_rule: str | DispatchingRule,
) -> Callable[[Dispatcher], Operation]:
    """Creates and returns a dispatching rule function based on the specified
    dispatching rule name.

    The dispatching rule function determines the order in which operations are
    selected for execution based on certain criteria such as shortest
    processing time, first come first served, etc.

    Args:
        dispatching_rule: The name of the dispatching rule to be used.
            Supported values are 'shortest_processing_time',
            'first_come_first_served', 'most_work_remaining',
            and 'random'.

    Returns:
        A function that takes a Dispatcher instance as input and returns an
        Operation based on the specified dispatching rule.

    Raises:
        ValueError: If the dispatching_rule argument is not recognized or is
            not supported.
    """
    dispatching_rules = {
        DispatchingRule.SHORTEST_PROCESSING_TIME: (
            shortest_processing_time_rule
        ),
        DispatchingRule.FIRST_COME_FIRST_SERVED: first_come_first_served_rule,
        DispatchingRule.MOST_WORK_REMAINING: most_work_remaining_rule,
        DispatchingRule.MOST_OPERATIONS_REMAINING: (
            most_operations_remaining_rule
        ),
        DispatchingRule.RANDOM: random_operation_rule,
    }

    dispatching_rule = dispatching_rule.lower()
    if dispatching_rule not in dispatching_rules:
        raise ValueError(
            f"Dispatching rule {dispatching_rule} not recognized. Available "
            f"dispatching rules: {', '.join(dispatching_rules)}."
        )

    return dispatching_rules[dispatching_rule]  # type: ignore[index]


def machine_chooser_factory(
    machine_chooser: str,
) -> Callable[[Dispatcher, Operation], int]:
    """Creates and returns a machine chooser function based on the specified
    machine chooser strategy name.

    The machine chooser function determines which machine an operation should
    be assigned to for execution. The selection can be based on different
    strategies such as choosing the first available machine or selecting a
    machine randomly.

    Args:
        machine_chooser (str): The name of the machine chooser strategy to be
            used. Supported values are 'first' and 'random'.

    Returns:
        A function that takes a Dispatcher instance and an Operation as input
        and returns the index of the selected machine based on the specified
        machine chooser strategy.

    Raises:
        ValueError: If the machine_chooser argument is not recognized or is
            not supported.
    """
    machine_choosers: dict[str, Callable[[Dispatcher, Operation], int]] = {
        MachineChooser.FIRST: lambda _, operation: operation.machines[0],
        MachineChooser.RANDOM: lambda _, operation: random.choice(
            operation.machines
        ),
    }

    machine_chooser = machine_chooser.lower()
    if machine_chooser not in machine_choosers:
        raise ValueError(
            f"Machine chooser {machine_chooser} not recognized. Available "
            f"machine choosers: {', '.join(machine_choosers)}."
        )

    return machine_choosers[machine_chooser]