"""Contains factory functions for creating node feature encoders."""

from enum import Enum

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
    """Enumeration of the different feature observers."""

    IS_READY = "is_ready"
    EARLIEST_START_TIME = "earliest_start_time"
    DURATION = "duration"
    IS_SCHEDULED = "is_scheduled"
    POSITION_IN_JOB = "position_in_job"
    REMAINING_OPERATIONS = "remaining_operations"
    IS_COMPLETED = "is_completed"
    COMPOSITE = "composite"


# FeatureObserverConfig = DispatcherObserverConfig[
#     type[FeatureObserver] | FeatureObserverType | str
# ]
FeatureObserverConfig = (
    DispatcherObserverConfig[type[FeatureObserver]]
    | DispatcherObserverConfig[FeatureObserverType]
    | DispatcherObserverConfig[str]
)


def feature_observer_factory(
    feature_creator_type: (
        str
        | FeatureObserverType
        | type[FeatureObserver]
        | FeatureObserverConfig
    ),
    **kwargs,
) -> FeatureObserver:
    """Creates and returns a node feature creator based on the specified
    node feature creator type.

    Args:
        feature_creator_type:
            The type of node feature creator to create.
        **kwargs:
            Additional keyword arguments to pass to the node
            feature creator constructor.

    Returns:
        A node feature creator instance.
    """
    if isinstance(feature_creator_type, DispatcherObserverConfig):
        return feature_observer_factory(
            feature_creator_type.class_type,
            **feature_creator_type.kwargs,
            **kwargs,
        )
    # if the instance is of type type[FeatureObserver] we can just
    # call the object constructor with the keyword arguments
    if isinstance(feature_creator_type, type):
        return feature_creator_type(**kwargs)

    mapping: dict[FeatureObserverType, type[FeatureObserver]] = {
        FeatureObserverType.IS_READY: IsReadyObserver,
        FeatureObserverType.EARLIEST_START_TIME: EarliestStartTimeObserver,
        FeatureObserverType.DURATION: DurationObserver,
        FeatureObserverType.IS_SCHEDULED: IsScheduledObserver,
        FeatureObserverType.POSITION_IN_JOB: PositionInJobObserver,
        FeatureObserverType.REMAINING_OPERATIONS: RemainingOperationsObserver,
        FeatureObserverType.IS_COMPLETED: IsCompletedObserver,
    }
    feature_creator = mapping[feature_creator_type]  # type: ignore[index]
    return feature_creator(**kwargs)
