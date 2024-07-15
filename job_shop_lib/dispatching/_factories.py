"""Contains factory functions for creating dispatching rules, machine choosers,
and pruning functions for the job shop scheduling problem.

The factory functions create and return the appropriate functions based on the
specified names or enums.
"""

from enum import Enum
from typing import TypeVar, Generic, Any
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from job_shop_lib import Operation
from job_shop_lib.exceptions import ValidationError
from job_shop_lib.dispatching import (
    Dispatcher,
    prune_dominated_operations,
    prune_non_immediate_machines,
    create_composite_pruning_function,
)


class PruningFunction(str, Enum):
    """Enumeration of pruning functions.

    A pruning function is used by the `Dispatcher` class to reduce the
    amount of available operations to choose from.
    """

    DOMINATED_OPERATIONS = "dominated_operations"
    NON_IMMEDIATE_MACHINES = "non_immediate_machines"


# Disable pylint's false positive
# pylint: disable=invalid-name
T = TypeVar("T")


@dataclass(slots=True, frozen=True)
class DispatcherObserverConfig(Generic[T]):
    """Configuration for initializing any type of class.

    Useful for specifying the type of the
    :class:`~job_shop_lib.dispatching.DispatcherObserver` and additional
    keyword arguments to pass to the dispatcher observer constructor while
    not containing the ``dispatcher`` argument.

    Attributes:
        class_type:
            Type of the class to be initialized. It can be the class type, an
            enum value, or a string. This is useful for the creation of
            DispatcherObserver instances from the factory functions.
        kwargs:
            Keyword arguments needed to initialize the class. It must not
            contain the ``dispatcher`` argument.
    """

    # We use the type hint T, instead of ObserverType, to allow for string or
    # specific Enum values to be passed as the type argument. For example:
    # FeatureObserverConfig = DispatcherObserverConfig[
    #     type[FeatureObserver] | FeatureObserverType | str
    # ]
    # This allows for the creation of a FeatureObserver instance
    # from the factory function.
    class_type: T
    kwargs: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if "dispatcher" in self.kwargs:
            raise ValidationError(
                "The 'dispatcher' argument should not be included in the "
                "kwargs attribute."
            )


def composite_pruning_function_factory(
    pruning_function_names: Sequence[str | PruningFunction],
) -> Callable[[Dispatcher, list[Operation]], list[Operation]]:
    """Creates and returns a composite pruning function based on the
    specified list of pruning strategies.

    The composite pruning function filters out operations based on
    the specified list of pruning strategies.

    Args:
        pruning_functions:
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

    pruning_functions = [
        pruning_function_factory(name) for name in pruning_function_names
    ]
    return create_composite_pruning_function(pruning_functions)


def pruning_function_factory(
    pruning_function_name: str | PruningFunction,
) -> Callable[[Dispatcher, list[Operation]], list[Operation]]:
    """Creates and returns a pruning function based on the specified
    pruning strategy name.

    The pruning function filters out operations based on certain
    criteria such as dominated operations, non-immediate machines, etc.

    Args:
        pruning_function:
            The name of the pruning function to be used. Supported values are
            'dominated_operations' and 'non_immediate_machines'.

    Returns:
        A function that takes a Dispatcher instance and a list of Operation
        instances as input and returns a list of Operation instances based on
        the specified pruning function.

    Raises:
        ValueError: If the pruning_function argument is not recognized or is
            not supported.
    """
    pruning_strategies = {
        PruningFunction.DOMINATED_OPERATIONS: prune_dominated_operations,
        PruningFunction.NON_IMMEDIATE_MACHINES: prune_non_immediate_machines,
    }

    if pruning_function_name not in pruning_strategies:
        raise ValidationError(
            f"Unsupported pruning function '{pruning_function_name}'. "
            f"Supported values are {', '.join(pruning_strategies.keys())}."
        )

    return pruning_strategies[pruning_function_name]  # type: ignore[index]
