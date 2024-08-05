"""Home of the `PositionInJobObserver` class."""

from job_shop_lib import ScheduledOperation
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
)


class PositionInJobObserver(FeatureObserver):
    """Adds a feature indicating the position of
    operations in their respective jobs.

    Positions are adjusted dynamically as operations are scheduled. In other
    words, the position of an operation is the number of unscheduled operations
    that precede it in the job.

    It only supports the :meth:`~job_shop_lib.FeatureType.OPERATIONS` feature
    type.
    """

    _supported_feature_types = [FeatureType.OPERATIONS]

    def initialize_features(self):
        for operation in self.dispatcher.unscheduled_operations():
            self.features[FeatureType.OPERATIONS][
                operation.operation_id, 0
            ] = operation.position_in_job

    def update(self, scheduled_operation: ScheduledOperation):
        job = self.dispatcher.instance.jobs[scheduled_operation.job_id]
        for new_position_in_job, operation in enumerate(
            job[scheduled_operation.position_in_job + 1 :]
        ):
            self.features[FeatureType.OPERATIONS][
                operation.operation_id, 0
            ] = new_position_in_job
