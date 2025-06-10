"""Contains classes and functions to solve the Job Shop Scheduling
Problem step-by-step.

.. autosummary::
    :nosignatures:

    Dispatcher
    DispatcherObserver
    HistoryObserver
    UnscheduledOperationsObserver
    OptimalOperationsObserver
    DispatcherObserverConfig
    ReadyOperationsFilter
    ReadyOperationsFilterType
    ready_operations_filter_factory
    filter_dominated_operations
    filter_non_immediate_machines
    filter_non_idle_machines
    filter_non_immediate_operations
    create_composite_operation_filter
    StartTimeCalculator
    no_setup_time_calculator
    get_machine_dependent_setup_time_calculator
    get_matrix_setup_time_calculator
    get_breakdown_calculator
    get_job_dependent_setup_calculator

Dispatching refers to the decision-making process of selecting which job
should be processed next on a particular machine when that machine becomes
available.
"""

from ._dispatcher import (
    Dispatcher,
    DispatcherObserver,
    StartTimeCalculator,
    no_setup_time_calculator,
)
from ._history_observer import (
    HistoryObserver,
)
from ._unscheduled_operations_observer import UnscheduledOperationsObserver
from ._optimal_operations_observer import OptimalOperationsObserver
from ._ready_operation_filters import (
    filter_dominated_operations,
    filter_non_immediate_machines,
    ReadyOperationsFilter,
    filter_non_idle_machines,
    filter_non_immediate_operations,
)
from ._start_time_calculators import (
    get_machine_dependent_setup_time_calculator,
    get_breakdown_calculator,
    get_job_dependent_setup_calculator,
    get_matrix_setup_time_calculator,
)
from ._dispatcher_observer_config import DispatcherObserverConfig
from ._factories import (
    ReadyOperationsFilterType,
    ready_operations_filter_factory,
    create_composite_operation_filter,
)


__all__ = [
    "Dispatcher",
    "DispatcherObserver",
    "StartTimeCalculator",
    "HistoryObserver",
    "UnscheduledOperationsObserver",
    "OptimalOperationsObserver",
    "DispatcherObserverConfig",
    "ReadyOperationsFilter",
    "ReadyOperationsFilterType",
    "ready_operations_filter_factory",
    "filter_dominated_operations",
    "filter_non_immediate_machines",
    "filter_non_idle_machines",
    "filter_non_immediate_operations",
    "create_composite_operation_filter",
    "no_setup_time_calculator",
    "get_machine_dependent_setup_time_calculator",
    "StartTimeCalculator",
    "get_matrix_setup_time_calculator",
    "get_breakdown_calculator",
    "get_job_dependent_setup_calculator",
]
