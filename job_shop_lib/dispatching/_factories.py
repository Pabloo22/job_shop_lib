"""Contains factory functions for creating ready operations filters.

The factory functions create and return the appropriate functions based on the
specified names or enums.
"""

from typing import Union
from enum import Enum
from collections.abc import Iterable

from job_shop_lib import Operation
from job_shop_lib.exceptions import ValidationError

from job_shop_lib.dispatching import (
    Dispatcher,
    filter_dominated_operations,
    filter_non_immediate_machines,
    filter_non_idle_machines,
    filter_non_immediate_operations,
    ReadyOperationsFilter,
)


class ReadyOperationsFilterType(str, Enum):
    """Enumeration of ready operations filter types.

    A filter function is used by the
    :class:`~job_shop_lib.dispatching.Dispatcher` class to reduce the
    amount of available operations to choose from.
    """

    DOMINATED_OPERATIONS = "dominated_operations"
    NON_IMMEDIATE_MACHINES = "non_immediate_machines"
    NON_IDLE_MACHINES = "non_idle_machines"
    NON_IMMEDIATE_OPERATIONS = "non_immediate_operations"


def create_composite_operation_filter(
    ready_operations_filters: Iterable[
        Union[ReadyOperationsFilter, str, ReadyOperationsFilterType]
    ],
) -> ReadyOperationsFilter:
    """Creates and returns a :class:`ReadyOperationsFilter` function by
    combining multiple filter strategies.

    The composite filter function applies multiple filter strategies
    iteratively in the order they are specified in the list.

    Args:
        ready_operations_filters:
            A list of filter strategies to be used.
            Supported values are 'dominated_operations' and
            'non_immediate_machines' or any Callable that takes a
            :class:`~job_shop_lib.dispatching.Dispatcher` instance and a list
            of :class:`~job_shop_lib.Operation` instances as input
            and returns a list of :class:`~job_shop_lib.Operation` instances.

    Returns:
        A function that takes a :class:`~job_shop_lib.dispatching.Dispatcher`
        instance and a list of :class:`~job_shop_lib.Operation`
        instances as input and returns a list of
        :class:`~job_shop_lib.Operation` instances based on
        the specified list of filter strategies.

    Raises:
        ValidationError: If any of the filter strategies in the list are not
            recognized or are not supported.
    """

    filter_functions = [
        ready_operations_filter_factory(name)
        for name in ready_operations_filters
    ]

    def composite_pruning_function(
        dispatcher: Dispatcher, operations: list[Operation]
    ) -> list[Operation]:
        pruned_operations = operations
        for pruning_function in filter_functions:
            pruned_operations = pruning_function(dispatcher, pruned_operations)

        return pruned_operations

    return composite_pruning_function


def ready_operations_filter_factory(
    filter_name: Union[str, ReadyOperationsFilterType, ReadyOperationsFilter]
) -> ReadyOperationsFilter:
    """Creates and returns a filter function based on the specified
    filter strategy name.

    The filter function filters operations based on certain criteria such as
    dominated operations, immediate machine operations, etc.

    Args:
        filter_name:
            The name of the filter function to be used. Supported
            values are 'dominated_operations' and
            'immediate_machine_operations'.

    Returns:
        A function that takes a :class:`~job_shop_lib.dispatching.Dispatcher`
        instance and a list of :class:`~job_shop_lib.Operation`
        instances as input and returns a list of
        :class:`~job_shop_lib.Operation` instances based on
        the specified filter function.

    Raises:
        ValidationError: If the ``filter_name`` argument is not recognized or
            is not supported.
    """
    if callable(filter_name):
        return filter_name

    filtering_strategies = {
        ReadyOperationsFilterType.DOMINATED_OPERATIONS: (
            filter_dominated_operations
        ),
        ReadyOperationsFilterType.NON_IMMEDIATE_MACHINES: (
            filter_non_immediate_machines
        ),
        ReadyOperationsFilterType.NON_IDLE_MACHINES: filter_non_idle_machines,
        ReadyOperationsFilterType.NON_IMMEDIATE_OPERATIONS: (
            filter_non_immediate_operations
        ),
    }

    if filter_name not in filtering_strategies:
        raise ValidationError(
            f"Unsupported filter function '{filter_name}'. "
            f"Supported values are {', '.join(filtering_strategies.keys())}."
        )

    return filtering_strategies[filter_name]  # type: ignore[index]
