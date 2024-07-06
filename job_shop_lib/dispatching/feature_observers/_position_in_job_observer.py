"""Home of the `PositionInJobObserver` class."""

from job_shop_lib.dispatching import Dispatcher
from job_shop_lib import ScheduledOperation
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
)


class PositionInJobObserver(FeatureObserver):
    """Observer that adds a feature indicating the position of
    operations in their respective jobs.

    Positions are adjusted dynamically as operations are scheduled.
    """

    def __init__(self, dispatcher: Dispatcher, subscribe: bool = True):
        super().__init__(
            dispatcher,
            feature_types=[FeatureType.OPERATIONS],
            feature_size=1,
            subscribe=subscribe,
        )

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
