"""Home of the `EarliestStartTimeObserver` class."""

from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_extraction import (
    FeatureObserver,
    FeatureType,
)


class EarliestStartTimeObserver(FeatureObserver):
    """Observer that adds a feature indicating the earliest start time of
    each operation, machine, and job in the graph."""

    def __init__(
        self,
        dispatcher: Dispatcher,
        feature_types: list[FeatureType] | FeatureType | None = None,
    ):
        super().__init__(dispatcher, feature_types, feature_size=1)

    def initialize_features(self):
        """Updates the features based on the current state of the
        dispatcher."""
        mapping = {
            FeatureType.OPERATIONS: self._update_operation_features,
            FeatureType.MACHINES: self._update_machine_features,
            FeatureType.JOBS: self._update_job_features,
        }
        for feature_type in self.features:
            mapping[feature_type]()

    def _update_operation_features(self):
        for operation in self.dispatcher.unscheduled_operations():
            start_time = self.dispatcher.earliest_start_time(operation)
            adjusted_start_time = start_time - self.dispatcher.current_time()
            self.features[FeatureType.OPERATIONS][
                operation.operation_id, 0
            ] = adjusted_start_time

    def _update_machine_features(self):
        for machine_id, start_time in enumerate(
            self.dispatcher.machine_next_available_time
        ):
            self.features[FeatureType.MACHINES][machine_id, 0] = (
                start_time - self.dispatcher.current_time()
            )

    def _update_job_features(self):
        for job_id, start_time in enumerate(
            self.dispatcher.job_next_available_time
        ):
            self.features[FeatureType.JOBS][job_id, 0] = (
                start_time - self.dispatcher.current_time()
            )
