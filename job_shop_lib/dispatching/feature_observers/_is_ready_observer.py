"""Home of the `IsReadyObserver` class."""

from typing import List

from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
)


class IsReadyObserver(FeatureObserver):
    """Feature creator that adds a binary feature indicating if the operation,
    machine or job is ready to be dispatched."""

    def initialize_features(self):
        self.set_features_to_zero()
        for feature_type, feature in self.features.items():
            feature_ids = self._get_ready_feature_ids(feature_type)
            feature[feature_ids, 0] = 1.0

    def _get_ready_feature_ids(self, feature_type: FeatureType) -> List[int]:
        if feature_type == FeatureType.OPERATIONS:
            return self._get_ready_operations()
        if feature_type == FeatureType.MACHINES:
            return self.dispatcher.available_machines()
        if feature_type == FeatureType.JOBS:
            return self.dispatcher.available_jobs()
        raise ValueError(f"Feature type {feature_type} is not supported.")

    def reset(self):
        self.initialize_features()

    def _get_ready_operations(self) -> List[int]:
        available_operations = self.dispatcher.available_operations()
        return [operation.operation_id for operation in available_operations]
