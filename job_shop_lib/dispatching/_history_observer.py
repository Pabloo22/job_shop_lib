"""Home of the `HistoryObserver` class."""

from warnings import warn

from job_shop_lib.dispatching import DispatcherObserver, Dispatcher
from job_shop_lib import ScheduledOperation


class HistoryObserver(DispatcherObserver):
    """Observer that stores the history of the dispatcher."""

    def __init__(self, dispatcher: Dispatcher):
        """Initializes the observer with the current state of the
        dispatcher."""
        super().__init__(dispatcher)
        self.history: list[ScheduledOperation] = []

    def update(self, scheduled_operation: ScheduledOperation):
        self.history.append(scheduled_operation)

    def reset(self):
        self.history = []


class HistoryTracker(HistoryObserver):
    """Deprecated class. Use `HistoryObserver` instead."""

    def __init__(self, dispatcher: Dispatcher):
        warn(
            "`HistoryTracker` is deprecated and will be removed in verion "
            "1.0.0. Use `HistoryObserver` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(dispatcher)
