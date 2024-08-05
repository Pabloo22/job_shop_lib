"""Home of the `DurationObserver` class."""

import numpy as np

from job_shop_lib import ScheduledOperation
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
)


class DurationObserver(FeatureObserver):
    """Measures the remaining duration of operations, machines, and jobs.

    The duration of an :class:`~job_shop_lib.Operation` is:
        - if the operation has not been scheduled, it is the duration of the
          operation.
        - if the operation has been scheduled, it is the remaining duration of
          the operation.
        - if the operation has been completed, it is the last duration of the
          operation that has been computed. The duration must be set to 0
          manually if needed. We do not update the duration of completed
          operations to save computation time.

    The duration of a machine or job is the sum of the durations of the
    unscheduled operations that belong to the machine or job.

    Args:
        dispatcher:
            The :class:`~job_shop_lib.dispatching.Dispatcher` to observe.
        subscribe:
            If ``True``, the observer is subscribed to the dispatcher upon
            initialization. Otherwise, the observer must be subscribed later
            or manually updated.
        feature_types:
            A list of :class:`FeatureType` or a single :class:`FeatureType`
            that specifies the types of features to observe. They must be a
            subset of the class attribute :attr:`supported_feature_types`.
            If ``None``, all supported feature types are tracked.
    """

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
        duration_matrix = self.dispatcher.instance.durations_matrix_array
        operation_durations = np.array(duration_matrix).reshape(-1, 1)
        # Drop the NaN values
        operation_durations = operation_durations[
            ~np.isnan(operation_durations)
        ].reshape(-1, 1)
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
        machine_id = scheduled_operation.machine_id
        op_duration = scheduled_operation.operation.duration
        self.features[FeatureType.MACHINES][machine_id, 0] -= op_duration

    def _update_job_durations(self, scheduled_operation: ScheduledOperation):
        operation_duration = scheduled_operation.operation.duration
        job_id = scheduled_operation.job_id
        self.features[FeatureType.JOBS][job_id, 0] -= operation_duration
