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


def create_composite_pruning_strategy(
    pruning_strategies: list[PruningStrategy | str],
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
    pruning_strategy_functions = [
        pruning_strategy_factory(pruning_strategy)
        for pruning_strategy in pruning_strategies
    ]

    def composite_pruning_strategy(
        dispatcher: Dispatcher, operations: list[Operation]
    ) -> list[Operation]:
        pruned_operations = operations
        for pruning_strategy in pruning_strategy_functions:
            pruned_operations = pruning_strategy(dispatcher, pruned_operations)

        return pruned_operations

    return composite_pruning_strategy


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
