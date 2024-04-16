"""Contains a factory function for creating pruning strategy functions from
string names or enumeration values."""

from enum import Enum

from typing import Callable

from job_shop_lib import Operation
from job_shop_lib.dispatching import (
    Dispatcher,
    prune_dominated_operations,
    prune_non_immediate_machines,
)


class PruningStrategy(str, Enum):
    """Enumeration of pruning strategies."""

    DOMINATED_OPERATIONS = "dominated_operations"
    NON_IMMEDIATE_MACHINES = "non_immediate_machines"


def pruning_strategy_factory(
    pruning_strategy: str | PruningStrategy,
) -> Callable[[Dispatcher, list[Operation]], list[Operation]]:
    """Creates and returns a pruning strategy function based on the specified
    pruning strategy name.

    The pruning strategy function filters out operations based on certain
    criteria such as dominated operations, non-immediate machines, etc.

    Args:
        pruning_strategy:
            The name of the pruning strategy to be used. Supported values are
            'dominated_operations' and 'non_immediate_machines'.

    Returns:
        A function that takes a Dispatcher instance and a list of Operation
        instances as input and returns a list of Operation instances based on
        the specified pruning strategy.

    Raises:
        ValueError: If the pruning_strategy argument is not recognized or is
            not supported.
    """
    pruning_strategies = {
        PruningStrategy.DOMINATED_OPERATIONS: prune_dominated_operations,
        PruningStrategy.NON_IMMEDIATE_MACHINES: prune_non_immediate_machines,
    }

    if pruning_strategy not in pruning_strategies:
        raise ValueError(
            f"Unsupported pruning strategy '{pruning_strategy}'. "
            f"Supported values are {', '.join(pruning_strategies.keys())}."
        )

    return pruning_strategies[pruning_strategy]  # type: ignore[index]
