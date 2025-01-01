"""Home of the `IsCompletedObserver` class."""

from typing import Optional, Union, List
import numpy as np

from job_shop_lib import ScheduledOperation
from job_shop_lib.dispatching import (
    Dispatcher,
    DispatcherObserver,
)
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
    RemainingOperationsObserver,
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

    __slots__ = {
        "remaining_ops_per_machine": (
            "The number of unscheduled operations per machine."
        ),
        "remaining_ops_per_job": (
            "The number of unscheduled operations per job."
        ),
    }

    def __init__(
        self,
        dispatcher: Dispatcher,
        *,
        feature_types: Optional[Union[List[FeatureType], FeatureType]] = None,
        subscribe: bool = True,
    ):
        feature_types = self._get_feature_types_list(feature_types)
        self.remaining_ops_per_machine = np.zeros(
            (dispatcher.instance.num_machines, 1), dtype=int
        )
        self.remaining_ops_per_job = np.zeros(
            (dispatcher.instance.num_jobs, 1), dtype=int
        )
        super().__init__(
            dispatcher,
            feature_types=feature_types,
            subscribe=subscribe,
        )

    def initialize_features(self):
        def _has_same_features(observer: DispatcherObserver) -> bool:
            if not isinstance(observer, RemainingOperationsObserver):
                return False
            return all(
                feature_type in observer.features
                for feature_type in remaining_ops_feature_types
            )

        self.set_features_to_zero()

        remaining_ops_feature_types = [
            feature_type
            for feature_type in self.features.keys()
            if feature_type != FeatureType.OPERATIONS
        ]
        remaining_ops_observer = self.dispatcher.create_or_get_observer(
            RemainingOperationsObserver,
            condition=_has_same_features,
            feature_types=remaining_ops_feature_types,
        )
        if FeatureType.JOBS in self.features:
            self.remaining_ops_per_job = remaining_ops_observer.features[
                FeatureType.JOBS
            ].copy()
        if FeatureType.MACHINES in self.features:
            self.remaining_ops_per_machine = remaining_ops_observer.features[
                FeatureType.MACHINES
            ].copy()

    def reset(self):
        self.initialize_features()

    def update(self, scheduled_operation: ScheduledOperation):
        if FeatureType.OPERATIONS in self.features:
            completed_operations = [
                op.operation_id
                for op in self.dispatcher.completed_operations()
            ]
            self.features[FeatureType.OPERATIONS][completed_operations, 0] = 1
        if FeatureType.MACHINES in self.features:
            self.remaining_ops_per_machine[
                scheduled_operation.operation.machines, 0
            ] -= 1
            is_completed = (
                self.remaining_ops_per_machine[
                    scheduled_operation.operation.machines, 0
                ]
                == 0
            )
            self.features[FeatureType.MACHINES][
                scheduled_operation.operation.machines, 0
            ] = is_completed
        if FeatureType.JOBS in self.features:
            job_id = scheduled_operation.job_id
            self.remaining_ops_per_job[job_id, 0] -= 1
            is_completed = self.remaining_ops_per_job[job_id, 0] == 0
            self.features[FeatureType.JOBS][job_id, 0] = is_completed
