"""Home of the `IsScheduledObserver` class."""

from job_shop_lib import ScheduledOperation
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
)


class IsScheduledObserver(FeatureObserver):
    """Observer that updates features based on scheduling operations.

    This observer tracks which operations have been scheduled and updates
    feature matrices accordingly. It updates a feature in the
    `FeatureType.OPERATIONS` matrix to indicate that an operation has been
    scheduled. Additionally, it counts the number of uncompleted but
    scheduled operations for each machine and job, updating the respective
    `FeatureType.MACHINES` and `FeatureType.JOBS` feature matrices.
    """

    def update(self, scheduled_operation: ScheduledOperation):
        if FeatureType.OPERATIONS in self.features:
            self.features[FeatureType.OPERATIONS][
                scheduled_operation.operation.operation_id, 0
            ] = 1.0

        uncompleted_operations = set(self.dispatcher.uncompleted_operations())
        scheduled_operations = set(self.dispatcher.scheduled_operations())
        uncompleted_and_scheduled_operations = (
            uncompleted_operations & scheduled_operations
        )
        for operation in uncompleted_and_scheduled_operations:
            if FeatureType.MACHINES in self.features:
                machine_id = operation.machine_id
                self.features[FeatureType.MACHINES][machine_id, 0] += 1.0
            if FeatureType.JOBS in self.features:
                self.features[FeatureType.JOBS][operation.job_id, 0] += 1.0
