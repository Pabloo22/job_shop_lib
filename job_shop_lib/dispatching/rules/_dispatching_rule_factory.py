"""Contains factory functions for creating dispatching rules, machine choosers,
and pruning functions for the job shop scheduling problem.

The factory functions create and return the appropriate functions based on the
specified names or enums.
"""

from typing import Dict, Union

from enum import Enum
from collections.abc import Callable

from job_shop_lib import Operation
from job_shop_lib.exceptions import ValidationError
from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.rules import (
    shortest_processing_time_rule,
    first_come_first_served_rule,
    most_operations_remaining_rule,
    random_operation_rule,
    most_work_remaining_rule,
)


class DispatchingRuleType(str, Enum):
    """Enumeration of dispatching rules for the job shop scheduling problem."""

    SHORTEST_PROCESSING_TIME = "shortest_processing_time"
    FIRST_COME_FIRST_SERVED = "first_come_first_served"
    MOST_WORK_REMAINING = "most_work_remaining"
    MOST_OPERATIONS_REMAINING = "most_operations_remaining"
    RANDOM = "random"


def dispatching_rule_factory(
    dispatching_rule: Union[str, DispatchingRuleType,]
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
        ValidationError:
            If the dispatching_rule argument is not recognized or it is
            not supported.
    """
    dispatching_rules: Dict[
        DispatchingRuleType,
        Callable[[Dispatcher], Operation],
    ] = {
        DispatchingRuleType.SHORTEST_PROCESSING_TIME: (
            shortest_processing_time_rule
        ),
        DispatchingRuleType.FIRST_COME_FIRST_SERVED: (
            first_come_first_served_rule
        ),
        DispatchingRuleType.MOST_WORK_REMAINING: most_work_remaining_rule,
        DispatchingRuleType.MOST_OPERATIONS_REMAINING: (
            most_operations_remaining_rule
        ),
        DispatchingRuleType.RANDOM: random_operation_rule,
    }

    dispatching_rule = dispatching_rule.lower()
    if dispatching_rule not in dispatching_rules:
        raise ValidationError(
            f"Dispatching rule {dispatching_rule} not recognized. Available "
            f"dispatching rules: {', '.join(dispatching_rules)}."
        )

    return dispatching_rules[dispatching_rule]  # type: ignore[index]
