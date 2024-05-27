"""Home of the `IsReadyObserver` class."""

from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
)


class IsReadyObserver(FeatureObserver):
    """Feature creator that adds a binary feature indicating if the operation
    is ready to be dispatched."""

    def __init__(
        self,
        dispatcher: Dispatcher,
        feature_types: list[FeatureType] | FeatureType | None = None,
        subscribe: bool = True,
    ):
        super().__init__(
            dispatcher, feature_types, feature_size=1, subscribe=subscribe
        )

    def initialize_features(self):
        self.set_features_to_zero()
        for feature_type, feature in self.features.items():
            node_ids = self._get_ready_nodes(feature_type)
            feature[node_ids, 0] = 1.0

    def _get_ready_nodes(self, feature_type: FeatureType) -> list[int]:
        mapping = {
            FeatureType.OPERATIONS: self._get_ready_operation_nodes,
            FeatureType.MACHINES: self.dispatcher.available_machines,
            FeatureType.JOBS: self.dispatcher.available_jobs,
        }
        return mapping[feature_type]()

    def _get_ready_operation_nodes(self) -> list[int]:
        available_operations = self.dispatcher.available_operations()
        return [operation.operation_id for operation in available_operations]
