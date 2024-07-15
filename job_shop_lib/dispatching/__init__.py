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
from ._pruning_functions import (
    prune_dominated_operations,
    prune_non_immediate_machines,
    create_composite_pruning_function,
)
from ._factories import (
    PruningFunction,
    pruning_function_factory,
    composite_pruning_function_factory,
    DispatcherObserverConfig,
)


__all__ = [
    "Dispatcher",
    "prune_dominated_operations",
    "prune_non_immediate_machines",
    "create_composite_pruning_function",
    "PruningFunction",
    "pruning_function_factory",
    "composite_pruning_function_factory",
    "DispatcherObserver",
    "HistoryObserver",
    "DispatcherObserverConfig",
    "UnscheduledOperationsObserver",
]
