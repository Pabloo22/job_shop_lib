"""A Feature Extractor computes features from a graph and a dispatcher."""

from abc import abstractmethod

import enum

import numpy as np
from job_shop_lib import ScheduledOperation
from job_shop_lib.dispatching import Dispatcher, DispatcherObserver


class FeatureType(str, enum.Enum):
    """Types of features that can be extracted from a graph."""

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

    @abstractmethod
    def initialize_features(self):
        """Creates the features for the nodes in the graph."""

    def update(self, scheduled_operation: ScheduledOperation):
        """Updates the features of the nodes in the graph."""
        self.initialize_features()

    def reset(self):
        """Resets the node features to their initial values."""
        self.initialize_features()
