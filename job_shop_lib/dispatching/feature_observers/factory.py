"""Contains factory functions for creating node feature encoders."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_observers import (
    IsReadyObserver,
    EarliestStartTimeObserver,
    FeatureObserver,
    DurationObserver,
    IsScheduledObserver,
    PositionInJobObserver,
    RemainingOperationsObserver,
    IsCompletedObserver,
    CompositeFeatureObserver,
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


@dataclass(slots=True, frozen=True)
class FeatureObserverConfig:
    """Configuration for initializing a feature observer.

    Useful for specifying the type of the feature observer and additional
    keyword arguments to pass to the feature observer constructor while
    not containing the `dispatcher` argument.

    Attributes:
        type:
            Type of the feature observer.
        kwargs:
            Additional keyword arguments to pass to the feature observer
            constructor. It must not contain the `dispatcher` argument.
    """

    feature_observer_type: FeatureObserverType | str | type[FeatureObserver]
    kwargs: dict[str, Any] = field(default_factory=dict)


def feature_observer_factory(
    node_feature_creator_type: (
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
        node_feature_creator_type:
            The type of node feature creator to create.
        **kwargs:
            Additional keyword arguments to pass to the node
            feature creator constructor.

    Returns:
        A node feature creator instance.
    """
    if isinstance(node_feature_creator_type, FeatureObserverConfig):
        return feature_observer_factory(
            node_feature_creator_type.feature_observer_type,
            **node_feature_creator_type.kwargs,
            **kwargs,
        )
    # if the instance is of type type[FeatureObserver] we can just
    # call the object constructor with the keyword arguments
    if isinstance(node_feature_creator_type, type):
        return node_feature_creator_type(**kwargs)

    mapping: dict[FeatureObserverType, type[FeatureObserver]] = {
        FeatureObserverType.IS_READY: IsReadyObserver,
        FeatureObserverType.EARLIEST_START_TIME: EarliestStartTimeObserver,
        FeatureObserverType.DURATION: DurationObserver,
        FeatureObserverType.IS_SCHEDULED: IsScheduledObserver,
        FeatureObserverType.POSITION_IN_JOB: PositionInJobObserver,
        FeatureObserverType.REMAINING_OPERATIONS: RemainingOperationsObserver,
        FeatureObserverType.IS_COMPLETED: IsCompletedObserver,
    }
    feature_creator = mapping[node_feature_creator_type]  # type: ignore[index]
    return feature_creator(**kwargs)


def initialize_composite_observer(
    dispatcher: Dispatcher,
    feature_observer_configs: list[FeatureObserverConfig],
    subscribe: bool = True,
) -> CompositeFeatureObserver:
    """Creates the composite feature observer.

    Args:
        dispatcher:
            The dispatcher used to create the feature observers.
        feature_observer_configs:
            The list of feature observer configuration objects.
        subscribe:
            Whether to subscribe the CompositeFeatureObserver to the
            dispatcher.
    """
    observers = [
        feature_observer_factory(observer_config, dispatcher=dispatcher)
        for observer_config in feature_observer_configs
    ]
    composite_observer = CompositeFeatureObserver(
        dispatcher, observers, subscribe=subscribe
    )
    return composite_observer
