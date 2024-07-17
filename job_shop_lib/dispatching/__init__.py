"""Contains classes and functions to solve the Job Shop Scheduling
Problem step-by-step.

.. autosummary::

        Dispatcher
        DispatcherObserver
        HistoryObserver
        DispatchingRule
        MachineChooser
        DispatchingRuleSolver
        PruningFunction
        DispatcherObserverConfig

Dispatching refers to the decision-making process of selecting which job
should be processed next on a particular machine when that machine becomes
available.
"""

from ._dispatcher import Dispatcher, DispatcherObserver
from ._history_observer import (
    HistoryObserver,
)
from ._unscheduled_operations_observer import (
    UnscheduledOperationsObserver,
)
from ._ready_operation_filters import (
    filter_dominated_operations,
    filter_non_immediate_machines,
    ReadyOperationsFilter,
)
from ._dispatcher_observer_config import DispatcherObserverConfig
from ._factories import (
    ReadyOperationsFilterType,
    ready_operations_filter_factory,
    create_composite_operation_filter,
)


__all__ = [
    "Dispatcher",
    "filter_dominated_operations",
    "filter_non_immediate_machines",
    "create_composite_operation_filter",
    "ReadyOperationsFilterType",
    "ready_operations_filter_factory",
    "DispatcherObserver",
    "HistoryObserver",
    "DispatcherObserverConfig",
    "UnscheduledOperationsObserver",
    "ReadyOperationsFilter",
]
