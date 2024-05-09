"""Home of the `FeatureObserver` class and `FeatureType` enum."""

import enum

import numpy as np
from job_shop_lib import ScheduledOperation
from job_shop_lib.dispatching import Dispatcher, DispatcherObserver


class FeatureType(str, enum.Enum):
    """Types of features that can be extracted."""

    OPERATIONS = "operations"
    MACHINES = "machines"
    JOBS = "jobs"


class FeatureObserver(DispatcherObserver):
    """Base class for node feature extractors."""

    def __init__(
        self,
        dispatcher: Dispatcher,
        feature_types: list[FeatureType] | FeatureType | None = None,
        feature_size: dict[FeatureType, int] | int = 1,
    ):
        if isinstance(feature_types, FeatureType):
            feature_types = [feature_types]
        if feature_types is None:
            feature_types = list(FeatureType)
        if isinstance(feature_size, int):
            feature_size = {
                feature_type: feature_size for feature_type in feature_types
            }
        super().__init__(dispatcher)

        number_of_entities = {
            FeatureType.OPERATIONS: dispatcher.instance.num_operations,
            FeatureType.MACHINES: dispatcher.instance.num_machines,
            FeatureType.JOBS: dispatcher.instance.num_jobs,
        }
        self.feature_dimensions = {
            feature_type: (
                number_of_entities[feature_type],
                feature_size[feature_type],
            )
            for feature_type in feature_types
        }
        self.features = {
            feature_type: np.zeros(
                self.feature_dimensions[feature_type],
                dtype=np.float32,
            )
            for feature_type in feature_types
        }
        self.initialize_features()

    def initialize_features(self):
        """Initializes the features based on the current state of the
        dispatcher."""

    def update(self, scheduled_operation: ScheduledOperation):
        """Updates the features based on the scheduled operation.

        By default, this method just calls `initialize_features`.

        Args:
            scheduled_operation:
                The operation that has been scheduled.
        """
        self.initialize_features()

    def reset(self):
        """Sets features to zero and calls to `initialize_features`.

        This method should not be overridden by subclasses.
        """
        self.set_features_to_zero()
        self.initialize_features()

    def set_features_to_zero(self):
        """Sets features to zero."""
        for feature_type in self.features:
            self.features[feature_type][:] = 0.0

    def __str__(self):
        out = [self.__class__.__name__, ":\n"]
        out.append("-" * len(out[0]))
        for feature_type, feature in self.features.items():
            out.append(f"\n{feature_type.value}:\n{feature}")
        return "".join(out)
