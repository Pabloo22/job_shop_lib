"""Home of the `MostWorkRemainingRule` class."""

import numpy as np

from job_shop_lib import Operation
from job_shop_lib._scheduled_operation import ScheduledOperation
from job_shop_lib.exceptions import ValidationError
from job_shop_lib.dispatching import (
    Dispatcher,
    DispatcherObserver,
)
from job_shop_lib.dispatching.feature_observers import (
    DurationObserver,
    FeatureType,
    IsReadyObserver,
)
from job_shop_lib.dispatching.rules import DispatchingRuleObserver


class MostWorkRemainingRuleObserver(DispatchingRuleObserver):
    """Dispatching rule that selects the operation with the most work
    remaining."""

    def __init__(
        self,
        dispatcher: Dispatcher,
        *,
        subscribe: bool = True,
    ):

        def has_job_feature(observer: DispatcherObserver) -> bool:
            if not isinstance(observer, DurationObserver):
                return False
            return FeatureType.JOBS in observer.features

        self._duration_observer = dispatcher.create_or_get_observer(
            DurationObserver,
            condition=has_job_feature,
        )
        self._is_ready_observer = dispatcher.create_or_get_observer(
            IsReadyObserver,
            condition=has_job_feature,
        )
        super().__init__(dispatcher, subscribe=subscribe)

    def scores(self) -> np.ndarray:
        """Returns the scores for each job based on the remaining work."""
        work_remaining = self._duration_observer.features[FeatureType.JOBS]
        # Set to +inf if job is not ready
        work_remaining[~self._is_ready_observer.features[FeatureType.JOBS]] = (
            float("inf")
        )
        return work_remaining.flatten()

    def select_operation(self) -> Operation:
        # Choose job with the most work remaining
        work_remaining = self.scores()
        job_ids = work_remaining.argsort()
        for job_id in job_ids:
            operation = self.dispatcher.next_operation(job_id)
            return operation

        raise ValidationError("No operation available found to dispatch.")

    def reset(self):
        pass

    def update(self, scheduled_operation: ScheduledOperation):
        pass
