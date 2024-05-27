"""Home of the `EarliestStartTimeObserver` class."""

import numpy as np

from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
)
from job_shop_lib.scheduled_operation import ScheduledOperation


class EarliestStartTimeObserver(FeatureObserver):
    """Observer that adds a feature indicating the earliest start time of
    each operation, machine, and job in the graph."""

    def __init__(
        self,
        dispatcher: Dispatcher,
        feature_types: list[FeatureType] | FeatureType | None = None,
        subscribe: bool = True,
    ):

        # Earliest start times initialization
        # -------------------------------
        squared_duration_matrix = dispatcher.instance.durations_matrix_array
        self.earliest_start_times = np.hstack(
            (
                np.zeros((squared_duration_matrix.shape[0], 1)),
                np.cumsum(squared_duration_matrix[:, :-1], axis=1),
            )
        )
        self.earliest_start_times[np.isnan(squared_duration_matrix)] = np.nan
        # -------------------------------
        super().__init__(
            dispatcher, feature_types, feature_size=1, subscribe=subscribe
        )

    def update(self, scheduled_operation: ScheduledOperation):
        """Recomputes the earliest start times and calls the
        `initialize_features` method.

        The earliest start times is computed as the cumulative sum of the
        previous unscheduled operations in the job plus the maximum of the
        completion time of the last scheduled operation and the next available
        time of the machine(s) the operation is assigned.

        After that, we substract the current time.
        """
        # We compute the gap that the current scheduled operation could be
        # adding to each job.
        job_id = scheduled_operation.job_id
        next_operation_idx = self.dispatcher.job_next_operation_index[job_id]
        if next_operation_idx < len(self.dispatcher.instance.jobs[job_id]):
            old_start_time = self.earliest_start_times[
                job_id, next_operation_idx
            ]
            next_operation = self.dispatcher.instance.jobs[job_id][
                next_operation_idx
            ]
            new_start_time = max(
                scheduled_operation.end_time,
                old_start_time,
                self.dispatcher.earliest_start_time(next_operation),
            )
            gap = new_start_time - old_start_time
            self.earliest_start_times[job_id, next_operation_idx:] += gap

        # Now, we compute the gap that could be introduced by the new
        # next_available_time of the machine.
        operations_by_machine = self.dispatcher.instance.operations_by_machine
        for operation in operations_by_machine[scheduled_operation.machine_id]:
            if self.dispatcher.is_scheduled(operation):
                continue
            old_start_time = self.earliest_start_times[
                operation.job_id, operation.position_in_job
            ]
            new_start_time = max(old_start_time, scheduled_operation.end_time)
            gap = new_start_time - old_start_time
            self.earliest_start_times[
                operation.job_id, operation.position_in_job :
            ] += gap

        self.initialize_features()

    def initialize_features(self):
        """Initializes the features based on the current state of the
        dispatcher."""
        mapping = {
            FeatureType.OPERATIONS: self._update_operation_features,
            FeatureType.MACHINES: self._update_machine_features,
            FeatureType.JOBS: self._update_job_features,
        }
        for feature_type in self.features:
            mapping[feature_type]()

    def _update_operation_features(self):
        """Ravels the 2D array into a 1D array"""
        current_time = self.dispatcher.current_time()
        next_index = 0
        for job_id, operations in enumerate(self.dispatcher.instance.jobs):
            self.features[FeatureType.OPERATIONS][
                next_index : next_index + len(operations), 0
            ] = (
                self.earliest_start_times[job_id, : len(operations)]
                - current_time
            )
            next_index += len(operations)

    def _update_machine_features(self):
        """Picks the minimum start time of all operations that can be scheduled
        on that machine"""
        current_time = self.dispatcher.current_time()
        operations_by_machine = self.dispatcher.instance.operations_by_machine
        for machine_id, operations in enumerate(operations_by_machine):
            min_earliest_start_time = min(
                (
                    self.earliest_start_times[
                        operation.job_id, operation.position_in_job
                    ]
                    for operation in operations
                    if not self.dispatcher.is_scheduled(operation)
                ),
                default=0,
            )
            self.features[FeatureType.MACHINES][machine_id, 0] = (
                min_earliest_start_time - current_time
            )

    def _update_job_features(self):
        """Picks the earliest start time of the next operation in the job"""
        current_time = self.dispatcher.current_time()
        for job_id, next_operation_idx in enumerate(
            self.dispatcher.job_next_operation_index
        ):
            job_length = len(self.dispatcher.instance.jobs[job_id])
            if next_operation_idx == job_length:
                continue
            self.features[FeatureType.JOBS][job_id, 0] = (
                self.earliest_start_times[job_id, next_operation_idx]
                - current_time
            )


if __name__ == "__main__":
    squared_durations_matrix = np.array([[1, 1, 7], [5, 1, 1], [1, 3, 2]])
    # Add a zeros column to the left of the matrix
    cumulative_durations = np.hstack(
        (
            np.zeros((squared_durations_matrix.shape[0], 1)),
            squared_durations_matrix[:, :-1],
        )
    )
    # Set to nan the values that are not available
    cumulative_durations[np.isnan(squared_durations_matrix)] = np.nan
    print(cumulative_durations)
