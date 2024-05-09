"""Home of the `DurationObserver` class."""

import numpy as np

from job_shop_lib.dispatching import Dispatcher
from job_shop_lib import ScheduledOperation
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
)


class DurationObserver(FeatureObserver):
    """Observer that adds a feature indicating the duration of operations,
    and the cumulative duration of upcoming operations for jobs and
    machines."""

    def __init__(
        self,
        dispatcher: Dispatcher,
        feature_types: list[FeatureType] | FeatureType | None = None,
    ):
        super().__init__(dispatcher, feature_types, feature_size=1)

    def initialize_features(self):
        mapping = {
            FeatureType.OPERATIONS: self._initialize_operation_durations,
            FeatureType.MACHINES: self._initialize_machine_durations,
            FeatureType.JOBS: self._initialize_job_durations,
        }
        for feature_type in self.features:
            mapping[feature_type]()

    def update(self, scheduled_operation: ScheduledOperation):
        mapping = {
            FeatureType.OPERATIONS: self._update_operation_durations,
            FeatureType.MACHINES: self._update_machine_durations,
            FeatureType.JOBS: self._update_job_durations,
        }
        for feature_type in self.features:
            mapping[feature_type](scheduled_operation)

    def _initialize_operation_durations(self):
        duration_matrix = self.dispatcher.instance.durations_matrix
        operation_durations = np.array(duration_matrix).reshape(-1, 1)
        self.features[FeatureType.OPERATIONS] = operation_durations

    def _initialize_machine_durations(self):
        machine_durations = self.dispatcher.instance.machine_loads
        for machine_id, machine_load in enumerate(machine_durations):
            self.features[FeatureType.MACHINES][machine_id, 0] = machine_load

    def _initialize_job_durations(self):
        job_durations = self.dispatcher.instance.job_durations
        for job_id, job_duration in enumerate(job_durations):
            self.features[FeatureType.JOBS][job_id, 0] = job_duration

    def _update_operation_durations(
        self, scheduled_operation: ScheduledOperation
    ):
        operation_id = scheduled_operation.operation.operation_id
        self.features[FeatureType.OPERATIONS][operation_id, 0] = (
            self.dispatcher.remaining_duration(scheduled_operation)
        )

    def _update_machine_durations(
        self, scheduled_operation: ScheduledOperation
    ):
        operation_id = scheduled_operation.operation.operation_id
        operation_duration = self.features[FeatureType.OPERATIONS][
            operation_id, 0
        ]
        self.features[FeatureType.MACHINES][
            scheduled_operation.machine_id, 0
        ] -= operation_duration

    def _update_job_durations(self, scheduled_operation: ScheduledOperation):
        operation_id = scheduled_operation.operation.operation_id
        operation_duration = self.features[FeatureType.OPERATIONS][
            operation_id, 0
        ]
        job_id = scheduled_operation.job_id
        self.features[FeatureType.JOBS][job_id, 0] -= operation_duration
