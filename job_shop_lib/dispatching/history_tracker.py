"""Home of the `HistoryTracker` class."""

from job_shop_lib.dispatching import DispatcherObserver, Dispatcher
from job_shop_lib import ScheduledOperation


class HistoryTracker(DispatcherObserver):
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
