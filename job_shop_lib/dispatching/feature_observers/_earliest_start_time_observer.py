"""Home of the `EarliestStartTimeObserver` class."""

from typing import List, Optional, Union

import numpy as np
from numpy.typing import NDArray

from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
)
from job_shop_lib import ScheduledOperation


class EarliestStartTimeObserver(FeatureObserver):
    """Observer that adds a feature indicating the earliest start time of
    each operation, machine, and job in the graph.

    The earliest start time of an operation refers to the earliest time at
    which the operation could potentially start without violating any
    constraints. This time is normalized by the current time (i.e., the
    difference between the earliest start time and the current time).

    The earliest start time of a machine is the earliest start time of the
    next operation that can be scheduled on that machine.

    Finally, the earliest start time of a job is the earliest start time of the
    next operation in the job.

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

    __slots__ = {
        "earliest_start_times": (
            "A 2D numpy array with the earliest start "
            "times of each operation. The array has "
            "shape (``num_jobs``, ``max_operations_per_job``). "
            "The value at index (i, j) is the earliest start "
            "time of the j-th operation in the i-th job. "
            "If a job has fewer than the maximum number of "
            "operations in a job, the remaining values are "
            "set to ``np.nan``. Similarly to "
            ":class:`~job_shop_lib.JobShopInstance`'s "
            ":meth:`~job_shop_lib.JobShopInstance.durations_matrix_array` "
            "method."
        ),
        "_job_ids": (
            "An array that stores the job IDs for each operation in the "
            "dispatcher's instance. The array has shape "
            "(``num_machines``, ``max_operations_per_machine``)."
        ),
        "_positions": (
            "An array that stores the positions of each operation in their "
            "respective jobs. The array has shape "
            "(``num_machines``, ``max_operations_per_machine``)."
        ),
        "_is_regular_instance": (
            "Whether the dispatcher's instance is a regular "
            "instance, where each job has the same number of operations."
        ),
    }

    def __init__(
        self,
        dispatcher: Dispatcher,
        *,
        subscribe: bool = True,
        feature_types: Optional[Union[List[FeatureType], FeatureType]] = None,
    ):

        # Earliest start times initialization
        # -------------------------------
        squared_duration_matrix = dispatcher.instance.durations_matrix_array
        self.earliest_start_times: NDArray[np.float32] = np.hstack(
            (
                np.zeros((squared_duration_matrix.shape[0], 1), dtype=float),
                np.cumsum(squared_duration_matrix[:, :-1], axis=1),
            )
        )
        self.earliest_start_times[np.isnan(squared_duration_matrix)] = np.nan
        # -------------------------------

        # Cache:
        operations_by_machine = dispatcher.instance.operations_by_machine
        self._is_regular_instance = all(
            len(job) == len(dispatcher.instance.jobs[0])
            for job in dispatcher.instance.jobs
        )
        if self._is_regular_instance:
            self._job_ids = np.array(
                [
                    [op.job_id for op in machine_ops]
                    for machine_ops in operations_by_machine
                ]
            )
            self._positions = np.array(
                [
                    [op.position_in_job for op in machine_ops]
                    for machine_ops in operations_by_machine
                ]
            )
        else:
            self._job_ids = np.array([])
            self._positions = np.array([])

        super().__init__(
            dispatcher, feature_types=feature_types, subscribe=subscribe
        )

    def update(self, scheduled_operation: ScheduledOperation):
        """Recomputes the earliest start times and calls the
        ``initialize_features`` method.

        The earliest start times is computed as the cumulative sum of the
        previous unscheduled operations in the job plus the maximum of the
        completion time of the last scheduled operation and the next available
        time of the machine(s) the operation is assigned.

        After that, we substract the current time.

        Args:
            scheduled_operation: The operation that has been scheduled.
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
        machine_ops = self.dispatcher.instance.operations_by_machine[
            scheduled_operation.machine_id
        ]
        unscheduled_mask = np.array(
            [not self.dispatcher.is_scheduled(op) for op in machine_ops]
        )
        if np.any(unscheduled_mask):
            if self._job_ids.size == 0:
                job_ids = np.array([op.job_id for op in machine_ops])[
                    unscheduled_mask
                ]
            else:
                job_ids = self._job_ids[scheduled_operation.machine_id][
                    unscheduled_mask
                ]

            if self._positions.size == 0:
                positions = np.array(
                    [op.position_in_job for op in machine_ops]
                )[unscheduled_mask]
            else:
                positions = self._positions[scheduled_operation.machine_id][
                    unscheduled_mask
                ]
            old_start_times = self.earliest_start_times[job_ids, positions]
            new_start_times = np.maximum(
                scheduled_operation.end_time, old_start_times
            )
            gaps = new_start_times - old_start_times

            for job_id, position, gap in zip(job_ids, positions, gaps):
                self.earliest_start_times[job_id, position:] += gap

        self.initialize_features()

    def initialize_features(self):
        """Initializes the features based on the current state of the
        dispatcher."""
        for feature_type in self.features:
            if feature_type == FeatureType.OPERATIONS:
                self._update_operation_features()
            elif (
                feature_type == FeatureType.MACHINES
                and self._is_regular_instance
            ):
                self._update_machine_features_vectorized()
            elif feature_type == FeatureType.MACHINES:
                self._update_machine_features()
            elif feature_type == FeatureType.JOBS:
                self._update_job_features()

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

    def _update_machine_features_vectorized(self):
        """Picks the minimum start time of all operations that can be scheduled
        on that machine"""
        current_time = self.dispatcher.current_time()
        operations_by_machine = self.dispatcher.instance.operations_by_machine

        # Create a mask for unscheduled operations
        is_unscheduled = np.array(
            [
                [not self.dispatcher.is_scheduled(op) for op in machine_ops]
                for machine_ops in operations_by_machine
            ]
        )

        # Get earliest start times for all operations
        earliest_start_times = self.earliest_start_times[
            self._job_ids, self._positions
        ]

        # Apply mask for unscheduled operations
        masked_start_times = np.where(
            is_unscheduled, earliest_start_times, np.inf
        )

        # Find minimum start time for each machine
        min_start_times = np.min(masked_start_times, axis=1)

        # Handle cases where all operations are scheduled
        min_start_times = np.where(
            np.isinf(min_start_times), 0, min_start_times
        )

        self.features[FeatureType.MACHINES][:, 0] = (
            min_start_times - current_time
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
