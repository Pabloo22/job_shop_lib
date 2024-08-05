"""Home of the `RemainingOperationsObserver` class."""

from job_shop_lib import ScheduledOperation
from job_shop_lib.dispatching import UnscheduledOperationsObserver
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
)


class RemainingOperationsObserver(FeatureObserver):
    """Adds a feature indicating the number of remaining operations for each
    job and machine.

    It does not support :meth:`FeatureType.OPERATIONS`.
    """

    _supported_feature_types = [FeatureType.MACHINES, FeatureType.JOBS]

    def initialize_features(self):
        unscheduled_ops_observer = self.dispatcher.create_or_get_observer(
            UnscheduledOperationsObserver
        )
        for operation in unscheduled_ops_observer.unscheduled_operations:
            if FeatureType.JOBS in self.features:
                self.features[FeatureType.JOBS][operation.job_id, 0] += 1
            if FeatureType.MACHINES in self.features:
                self.features[FeatureType.MACHINES][operation.machines, 0] += 1

    def update(self, scheduled_operation: ScheduledOperation):
        if FeatureType.JOBS in self.features:
            job_id = scheduled_operation.job_id
            self.features[FeatureType.JOBS][job_id, 0] -= 1
        if FeatureType.MACHINES in self.features:
            machine_id = scheduled_operation.machine_id
            self.features[FeatureType.MACHINES][machine_id, 0] -= 1
