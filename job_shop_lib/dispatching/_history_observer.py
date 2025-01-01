"""Home of the `HistoryObserver` class."""

from typing import List
from job_shop_lib.dispatching import DispatcherObserver, Dispatcher
from job_shop_lib import ScheduledOperation


class HistoryObserver(DispatcherObserver):
    """Observer that stores the history of the dispatcher."""

    def __init__(self, dispatcher: Dispatcher, *, subscribe: bool = True):
        super().__init__(dispatcher, subscribe=subscribe)
        self.history: List[ScheduledOperation] = []

    def update(self, scheduled_operation: ScheduledOperation):
        self.history.append(scheduled_operation)

    def reset(self):
        self.history = []
