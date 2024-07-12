"""Home of the `MostWorkRemainingRule` class."""

from job_shop_lib import Operation
from job_shop_lib.exceptions import ValidationError
from job_shop_lib.dispatching import (
    Dispatcher,
    DispatcherObserver,
    MachineChooser,
    MachineChooserType,
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
        machine_chooser: (
            str | MachineChooser | MachineChooserType
        ) = MachineChooserType.FIRST,
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
        super().__init__(
            dispatcher, subscribe=subscribe, machine_chooser=machine_chooser
        )

    def select_action(self) -> tuple[Operation, int]:
        # Choose job with the most work remaining
        work_remaining = self._duration_observer.features[
            FeatureType.JOBS
        ].flatten()
        job_ids = work_remaining.argsort()
        for job_id in job_ids:
            if not self._is_ready_observer.features[FeatureType.JOBS][
                job_id, 0
            ]:
                continue
            operation = self.dispatcher.next_operation(job_id)
            return operation, self.machine_chooser(self.dispatcher, operation)

        raise ValidationError("No operation available found to dispatch.")
