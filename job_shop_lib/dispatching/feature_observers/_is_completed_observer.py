"""Home of the `IsCompletedObserver` class."""

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
    scheduled.

    .. note::

        This observer requires a
        :class:`~job_shop_lib.dispatching.RemainingOperationsObserver` to track
        the remaining operations. For efficiency reasons, it will automatically
        create one if it does not exist.

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
        "remaining_ops_observer": (
            "The :class:`RemainingOperationsObserver` used to track remaining "
            "operations."
        ),
    }

    def __init__(
        self,
        dispatcher: Dispatcher,
        *,
        feature_types: list[FeatureType] | FeatureType | None = None,
        subscribe: bool = True,
    ):
        def _has_same_features(observer: DispatcherObserver) -> bool:
            if not isinstance(observer, RemainingOperationsObserver):
                return False
            return all(
                feature_type in observer.features
                for feature_type in feature_types_list
            )

        feature_types_list = self._get_feature_types_list(feature_types)
        self.remaining_ops_observer = self.dispatcher.create_or_get_observer(
            RemainingOperationsObserver,
            condition=_has_same_features,
            feature_types=feature_types,
        )
        super().__init__(
            dispatcher,
            feature_types=feature_types,
            subscribe=subscribe,
        )

    def initialize_features(self):
        self.set_features_to_zero()
        # Initialize the features based on the remaining operations
        for feature_type in self.features.keys():
            if feature_type != FeatureType.OPERATIONS:
                self.features[feature_type] = (
                    self.remaining_ops_observer.features[feature_type] == 0
                ).astype(int)

    def reset(self):
        self.initialize_features()

    def update(self, scheduled_operation: ScheduledOperation):
        if FeatureType.OPERATIONS in self.features:
            completed_operations = [
                op.operation_id
                for op in self.dispatcher.completed_operations()
            ]
            self.features[FeatureType.OPERATIONS][completed_operations, 0] = 1

        for feature_type in [FeatureType.MACHINES, FeatureType.JOBS]:
            if feature_type in self.features:
                self.features[feature_type] = (
                    self.remaining_ops_observer.features[feature_type] == 0
                ).astype(int)
