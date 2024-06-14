"""Home of the `GraphEnvironment` class."""

from dataclasses import dataclass, field
import enum
from typing import Any

from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureObserverType,
)


@dataclass(slots=True, frozen=True)
class FeatureObserverConfig:
    """Configuration for the feature observer.

    Attributes:
        type:
            Type of the feature observer.
        kwargs:
            Additional keyword arguments to pass to the feature observer
            constructor. It must not contain the `dispatcher` argument.
    """

    feature_observer_type: FeatureObserverType | str | type[FeatureObserver]
    kwargs: dict[str, Any] = field(default_factory=dict)


class ObservationSpaceKey(str, enum.Enum):
    """Enumeration of the keys for the observation space dictionary."""

    REMOVED_NODES = "removed_nodes"
    EDGE_LIST = "edge_list"
    OPERATIONS = "operations"
    JOBS = "jobs"
    MACHINES = "machines"
