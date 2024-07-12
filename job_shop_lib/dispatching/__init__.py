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

from job_shop_lib.dispatching._dispatcher import Dispatcher, DispatcherObserver
from job_shop_lib.dispatching._history_observer import (
    HistoryObserver,
)
from job_shop_lib.dispatching._unscheduled_operations_observer import (
    UnscheduledOperationsObserver,
)
from job_shop_lib.dispatching._dispatching_rules import (
    shortest_processing_time_rule,
    first_come_first_served_rule,
    most_work_remaining_rule,
    most_operations_remaining_rule,
    random_operation_rule,
)
from job_shop_lib.dispatching._pruning_functions import (
    prune_dominated_operations,
    prune_non_immediate_machines,
    create_composite_pruning_function,
)
from job_shop_lib.dispatching._factories import (
    PruningFunction,
    DispatchingRule,
    MachineChooserType,
    dispatching_rule_factory,
    machine_chooser_factory,
    pruning_function_factory,
    composite_pruning_function_factory,
    DispatcherObserverConfig,
    MachineChooser,
)
from job_shop_lib.dispatching._dispatching_rule_solver import (
    DispatchingRuleSolver,
)


__all__ = [
    "dispatching_rule_factory",
    "machine_chooser_factory",
    "shortest_processing_time_rule",
    "first_come_first_served_rule",
    "most_work_remaining_rule",
    "most_operations_remaining_rule",
    "random_operation_rule",
    "DispatchingRule",
    "MachineChooserType",
    "Dispatcher",
    "DispatchingRuleSolver",
    "prune_dominated_operations",
    "prune_non_immediate_machines",
    "create_composite_pruning_function",
    "PruningFunction",
    "pruning_function_factory",
    "composite_pruning_function_factory",
    "DispatcherObserver",
    "HistoryObserver",
    "DispatcherObserverConfig",
    "MachineChooser",
    "UnscheduledOperationsObserver",
]
