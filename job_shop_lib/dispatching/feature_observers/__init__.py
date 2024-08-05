"""Contains :class:`FeatureObserver` classes for observing features of the
dispatcher.

.. autosummary::
    :nosignatures:

    FeatureObserver
    FeatureType
    CompositeFeatureObserver
    EarliestStartTimeObserver
    IsReadyObserver
    DurationObserver
    IsScheduledObserver
    PositionInJobObserver
    RemainingOperationsObserver
    IsCompletedObserver
    FeatureObserverType
    feature_observer_factory
    FeatureObserverConfig

A :class:`~job_shop_lib.dispatching.feature_observers.FeatureObserver` is a
a subclass of :class:`~job_shop_lib.dispatching.DispatcherObserver` that
observes features related to operations, machines, or jobs in the dispatcher.

Attributes are stored in numpy arrays with a shape of (``num_entities``,
``feature_size``), where ``num_entities`` is the number of entities being
observed (e.g., operations, machines, or jobs) and ``feature_size`` is the
number of values being observed for each entity.

The advantage of using arrays is that they can be easily updated in a
vectorized manner, which is more efficient than updating each attribute
individually. Furthermore, machine learning models can be trained on these
arrays to predict the best dispatching decisions.
"""

from ._feature_observer import FeatureObserver, FeatureType
from ._earliest_start_time_observer import EarliestStartTimeObserver
from ._is_ready_observer import IsReadyObserver
from ._duration_observer import DurationObserver
from ._is_scheduled_observer import IsScheduledObserver
from ._position_in_job_observer import PositionInJobObserver
from ._remaining_operations_observer import RemainingOperationsObserver
from ._is_completed_observer import IsCompletedObserver
from ._factory import (
    FeatureObserverType,
    feature_observer_factory,
    FeatureObserverConfig,
)
from ._composite_feature_observer import CompositeFeatureObserver


__all__ = [
    "FeatureObserver",
    "FeatureType",
    "CompositeFeatureObserver",
    "EarliestStartTimeObserver",
    "IsReadyObserver",
    "DurationObserver",
    "IsScheduledObserver",
    "PositionInJobObserver",
    "RemainingOperationsObserver",
    "IsCompletedObserver",
    "FeatureObserverType",
    "feature_observer_factory",
    "FeatureObserverConfig",
]
