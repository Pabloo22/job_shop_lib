"""Home of the `RemainingOperationsObserver` class."""

from job_shop_lib import ScheduledOperation
from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
)


class RemainingOperationsObserver(FeatureObserver):
    """Adds a feature indicating the number of remaining operations for each
    job and machine.

    It does not support FeatureType.OPERATIONS.
    """

    def __init__(
        self,
        dispatcher: Dispatcher,
        feature_types: list[FeatureType] | FeatureType | None = None,
        subscribe: bool = True,
    ):
        if feature_types is None:
            feature_types = [FeatureType.MACHINES, FeatureType.JOBS]

        if (
            feature_types == FeatureType.OPERATIONS
            or FeatureType.OPERATIONS in feature_types
        ):
            raise ValueError("FeatureType.OPERATIONS is not supported.")
        super().__init__(
            dispatcher,
            feature_types=feature_types,
            feature_size=1,
            subscribe=subscribe,
        )

    def initialize_features(self):
        for operation in self.dispatcher.unscheduled_operations():
            if FeatureType.JOBS in self.features:
                self.features[FeatureType.JOBS][operation.job_id, 0] += 1
            if FeatureType.MACHINES in self.features:
                self.features[FeatureType.MACHINES][
                    operation.machine_id, 0
                ] += 1

    def update(self, scheduled_operation: ScheduledOperation):
        if FeatureType.JOBS in self.features:
            job_id = scheduled_operation.job_id
            self.features[FeatureType.JOBS][job_id, 0] -= 1
        if FeatureType.MACHINES in self.features:
            machine_id = scheduled_operation.machine_id
            self.features[FeatureType.MACHINES][machine_id, 0] -= 1
