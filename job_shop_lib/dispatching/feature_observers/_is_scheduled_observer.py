"""Home of the `IsScheduledObserver` class."""

from job_shop_lib import ScheduledOperation
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
)


class IsScheduledObserver(FeatureObserver):
    """Updates features based on scheduling operations.

    This observer tracks which operations have been scheduled and updates
    feature matrices accordingly.

    It updates a feature in the
    :meth:`FeatureType.OPERATIONS` matrix to indicate that an operation has
    been scheduled.

    Additionally, it counts the number of uncompleted but
    scheduled operations for each machine and job, updating the respective
    :meth:`FeatureType.MACHINES` and :meth:`FeatureType.JOBS` feature matrices.
    """

    def update(self, scheduled_operation: ScheduledOperation):
        if FeatureType.OPERATIONS in self.features:
            self.features[FeatureType.OPERATIONS][
                scheduled_operation.operation.operation_id, 0
            ] = 1.0

        ongoing_operations = self.dispatcher.ongoing_operations()
        self.set_features_to_zero(exclude=FeatureType.OPERATIONS)
        for scheduled_op in ongoing_operations:
            if FeatureType.MACHINES in self.features:
                machine_id = scheduled_op.machine_id
                self.features[FeatureType.MACHINES][machine_id, 0] += 1.0
            if FeatureType.JOBS in self.features:
                self.features[FeatureType.JOBS][scheduled_op.job_id, 0] += 1.0
