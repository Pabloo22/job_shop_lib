"""Home of the `PositionInJobObserver` class."""

from job_shop_lib.dispatching import Dispatcher
from job_shop_lib import ScheduledOperation
from job_shop_lib.dispatching.feature_extraction import (
    FeatureObserver,
    FeatureType,
)


class PositionInJobObserver(FeatureObserver):
    """Observer that adds a feature indicating the position of
    operations in their respective jobs.

    Positions are adjusted dynamically as operations are scheduled.
    """

    def __init__(self, dispatcher: Dispatcher):
        super().__init__(
            dispatcher, feature_types=[FeatureType.OPERATIONS], feature_size=1
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


if __name__ == "__main__":
    example_list = [0, 1, 2, 3, 4]
    for i, item in enumerate(example_list[0 + 1 :]):
        print(f"{i = }, {item = }")
