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
    """Base class for feature observers."""

    def __init__(
        self,
        dispatcher: Dispatcher,
        feature_types: list[FeatureType] | FeatureType | None = None,
        feature_size: dict[FeatureType, int] | int = 1,
        is_singleton: bool = True,
        subscribe: bool = True,
    ):
        feature_types = self.get_feature_types_list(feature_types)
        if isinstance(feature_size, int):
            feature_size = {
                feature_type: feature_size for feature_type in feature_types
            }
        super().__init__(dispatcher, is_singleton, subscribe)

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
        """Sets features to zero and calls to `initialize_features`."""
        self.set_features_to_zero()
        self.initialize_features()

    def set_features_to_zero(
        self, exclude: FeatureType | list[FeatureType] | None = None
    ):
        """Sets features to zero."""
        if exclude is None:
            exclude = []
        if isinstance(exclude, FeatureType):
            exclude = [exclude]

        for feature_type in self.features:
            if feature_type in exclude:
                continue
            self.features[feature_type][:] = 0.0

    @staticmethod
    def get_feature_types_list(
        feature_types: list[FeatureType] | FeatureType | None,
    ) -> list[FeatureType]:
        """Returns a list of feature types.

        Args:
            feature_types:
                A list of feature types or a single feature type. If `None`,
                all feature types are returned.
        """
        if isinstance(feature_types, FeatureType):
            feature_types = [feature_types]
        if feature_types is None:
            feature_types = list(FeatureType)
        return feature_types

    def __str__(self):
        out = [self.__class__.__name__, ":\n"]
        out.append("-" * len(out[0]))
        for feature_type, feature in self.features.items():
            out.append(f"\n{feature_type.value}:\n{feature}")
        return "".join(out)
