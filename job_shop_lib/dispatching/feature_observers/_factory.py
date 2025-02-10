"""Contains factory functions for creating :class:`FeatureObserver`s."""

from enum import Enum
from typing import Union, Type

from job_shop_lib.dispatching import DispatcherObserverConfig
from job_shop_lib.dispatching.feature_observers import (
    IsReadyObserver,
    EarliestStartTimeObserver,
    FeatureObserver,
    DurationObserver,
    IsScheduledObserver,
    PositionInJobObserver,
    RemainingOperationsObserver,
    IsCompletedObserver,
)


class FeatureObserverType(str, Enum):
    """Enumeration of the different feature observers.

    Each :class:`FeatureObserver` is associated with a string value that can be
    used to create the :class:`FeatureObserver` using the factory function.

    It does not include the :class:`CompositeFeatureObserver` class since this
    observer is often managed separately from the others. For example, a
    common use case is to create a list of feature observers and pass them to
    """

    IS_READY = "is_ready"
    EARLIEST_START_TIME = "earliest_start_time"
    DURATION = "duration"
    IS_SCHEDULED = "is_scheduled"
    POSITION_IN_JOB = "position_in_job"
    REMAINING_OPERATIONS = "remaining_operations"
    IS_COMPLETED = "is_completed"


# FeatureObserverConfig = DispatcherObserverConfig[
#     Type[FeatureObserver] | FeatureObserverType | str
# ]
FeatureObserverConfig = DispatcherObserverConfig[
    Union[Type[FeatureObserver], FeatureObserverType, str]
]


def feature_observer_factory(
    feature_observer_type: Union[
        str,
        FeatureObserverType,
        Type[FeatureObserver],
        FeatureObserverConfig
    ],
    **kwargs,
) -> FeatureObserver:
    """Creates and returns a :class:`FeatureObserver` based on the specified
    :class:`FeatureObserver` type.

    Args:
        feature_creator_type:
            The type of :class:`FeatureObserver` to create.
        **kwargs:
            Additional keyword arguments to pass to the
            :class:`FeatureObserver` constructor.

    Returns:
        A :class:`FeatureObserver` instance.
    """
    if isinstance(feature_observer_type, DispatcherObserverConfig):
        return feature_observer_factory(
            feature_observer_type.class_type,
            **feature_observer_type.kwargs,
            **kwargs,
        )
    # if the instance is of type Type[FeatureObserver] we can just
    # call the object constructor with the keyword arguments
    if isinstance(feature_observer_type, type):
        return feature_observer_type(**kwargs)

    mapping: dict[FeatureObserverType, Type[FeatureObserver]] = {
        FeatureObserverType.IS_READY: IsReadyObserver,
        FeatureObserverType.EARLIEST_START_TIME: EarliestStartTimeObserver,
        FeatureObserverType.DURATION: DurationObserver,
        FeatureObserverType.IS_SCHEDULED: IsScheduledObserver,
        FeatureObserverType.POSITION_IN_JOB: PositionInJobObserver,
        FeatureObserverType.REMAINING_OPERATIONS: RemainingOperationsObserver,
        FeatureObserverType.IS_COMPLETED: IsCompletedObserver,
    }
    feature_observer = mapping[feature_observer_type]  # type: ignore[index]
    return feature_observer(**kwargs)
