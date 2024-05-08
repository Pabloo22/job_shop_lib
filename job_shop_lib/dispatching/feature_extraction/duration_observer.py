"""Home of the `DurationObserver` class."""

import numpy as np

from job_shop_lib.dispatching import Dispatcher
from job_shop_lib import ScheduledOperation
from job_shop_lib.dispatching.feature_extraction import (
    FeatureObserver,
    FeatureType,
)


class DurationObserver(FeatureObserver):
    """Observer that adds a feature indicating the duration of operations,
    and the cumulative duration of upcoming operations for job and machine
    nodes."""

    def __init__(
        self,
        dispatcher: Dispatcher,
        feature_types: list[FeatureType] | FeatureType | None = None,
    ):
        super().__init__(dispatcher, feature_types, feature_size=1)

    def initialize_features(self):
        """Initializes or resets the duration features for all nodes."""
        mapping = {
            FeatureType.OPERATIONS: self._initialize_operation_durations,
            FeatureType.MACHINES: self._initialize_machine_durations,
            FeatureType.JOBS: self._initialize_job_durations,
        }
        for feature_type in self.features:
            mapping[feature_type]()

    def update(self, scheduled_operation: ScheduledOperation):
        """Updates the duration features of the nodes in the graph."""
        mapping = {
            FeatureType.OPERATIONS: self._update_operation_durations,
            FeatureType.MACHINES: self._update_machine_durations,
            FeatureType.JOBS: self._update_job_durations,
        }
        for feature_type in self.features:
            mapping[feature_type](scheduled_operation)

    def _initialize_operation_durations(self):
        """Sets the duration of each operation node."""
        duration_matrix = self.dispatcher.instance.durations_matrix
        operation_durations = np.array(duration_matrix).reshape(-1, 1)
        self.features[FeatureType.OPERATIONS] = operation_durations

    def _initialize_machine_durations(self):
        """Sets the cumulative duration of upcoming operations for each
        machine node."""
        machine_durations = self.dispatcher.instance.machine_loads
        for machine_id, machine_load in enumerate(machine_durations):
            self.features[FeatureType.MACHINES][machine_id, 0] = machine_load

    def _initialize_job_durations(self):
        """Sets the cumulative duration of upcoming operations for each job
        node."""
        job_durations = self.dispatcher.instance.job_durations
        for job_id, job_duration in enumerate(job_durations):
            self.features[FeatureType.JOBS][job_id, 0] = job_duration

    def _update_operation_durations(
        self, scheduled_operation: ScheduledOperation
    ):
        """Updates the duration of the scheduled operation."""
        adjusted_start_time = max(
            scheduled_operation.start_time, self.dispatcher.current_time()
        )
        adjusted_duration = scheduled_operation.end_time - adjusted_start_time
        operation_id = scheduled_operation.operation.operation_id
        self.features[FeatureType.OPERATIONS][
            operation_id, 0
        ] = adjusted_duration

    def _update_machine_durations(
        self, scheduled_operation: ScheduledOperation
    ):
        """Updates the cumulative duration of upcoming operations for the
        machine of the scheduled operation."""
        operation_id = scheduled_operation.operation.operation_id
        operation_duration = self.features[FeatureType.OPERATIONS][
            operation_id, 0
        ]
        self.features[FeatureType.MACHINES][
            scheduled_operation.machine_id, 0
        ] -= operation_duration

    def _update_job_durations(self, scheduled_operation: ScheduledOperation):
        """Updates the cumulative duration of upcoming operations for the job
        of the scheduled operation."""
        operation_id = scheduled_operation.operation.operation_id
        operation_duration = self.features[FeatureType.OPERATIONS][
            operation_id, 0
        ]
        job_id = scheduled_operation.job_id
        self.features[FeatureType.JOBS][job_id, 0] -= operation_duration

    def __str__(self) -> str:
        out = ""
        for feature_type, feature_matrix in self.features.items():
            out += f"{feature_type}:\n{feature_matrix}"
        return out
