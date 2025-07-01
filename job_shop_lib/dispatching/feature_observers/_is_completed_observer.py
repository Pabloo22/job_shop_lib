"""Home of the `IsCompletedObserver` class."""

import numpy as np

from job_shop_lib import ScheduledOperation
from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
)


class IsCompletedObserver(FeatureObserver):
    """Adds a binary feature indicating whether each operation,
    machine, or job has been completed.

    An operation is considered completed if it has been scheduled and the
    current time is greater than or equal to the sum of the operation's start
    time and duration.

    A machine or job is considered completed if all of its operations have been
    completed.

    Args:
        dispatcher:
            The :class:`~job_shop_lib.dispatching.Dispatcher` to observe.
        feature_types:
            A list of :class:`FeatureType` or a single :class:`FeatureType`
            that specifies the types of features to observe. They must be a
            subset of the class attribute :attr:`supported_feature_types`.
            If ``None``, all supported feature types are tracked.
        subscribe:
            If ``True``, the observer is subscribed to the dispatcher upon
            initialization. Otherwise, the observer must be subscribed later
            or manually updated.
    """

    def __init__(
        self,
        dispatcher: Dispatcher,
        *,
        feature_types: list[FeatureType] | FeatureType | None = None,
        subscribe: bool = True,
    ):
        feature_types = self._get_feature_types_list(feature_types)
        self._num_of_operations_per_machine = np.array(
            [
                len(operations_by_machine)
                for operations_by_machine in (
                    dispatcher.instance.operations_by_machine
                )
            ]
        )
        self._num_of_operations_per_job = np.array(
            [len(job) for job in dispatcher.instance.jobs]
        )
        super().__init__(
            dispatcher,
            feature_types=feature_types,
            subscribe=subscribe,
        )

    def initialize_features(self):
        if FeatureType.OPERATIONS in self.features:
            completed_operations = [
                op.operation.operation_id
                for op in self.dispatcher.completed_operations()
            ]
            self.features[FeatureType.OPERATIONS][completed_operations, 0] = 1
        if FeatureType.MACHINES in self.features:
            num_completed_ops_per_machine = np.zeros(
                len(self._num_of_operations_per_machine)
            )
            for op in self.dispatcher.completed_operations():
                for machine_id in op.operation.machines:
                    num_completed_ops_per_machine[machine_id] += 1
            self.features[FeatureType.MACHINES][:, 0] = (
                num_completed_ops_per_machine
                == self._num_of_operations_per_machine
            ).astype(np.float32)
        if FeatureType.JOBS in self.features:
            num_completed_ops_per_job = np.zeros(
                len(self._num_of_operations_per_job)
            )
            for op in self.dispatcher.completed_operations():
                num_completed_ops_per_job[op.operation.job_id] += 1
            self.features[FeatureType.JOBS][:, 0] = (
                num_completed_ops_per_job == self._num_of_operations_per_job
            ).astype(np.float32)

    def reset(self):
        self.set_features_to_zero()

    def update(self, scheduled_operation: ScheduledOperation):
        self.initialize_features()
