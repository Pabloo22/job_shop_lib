"""Home of the `UnscheduledOperationsObserver` class."""

import collections
from collections.abc import Iterable
import itertools
from typing import Deque, List

from job_shop_lib import Operation, ScheduledOperation
from job_shop_lib.dispatching import DispatcherObserver, Dispatcher


class UnscheduledOperationsObserver(DispatcherObserver):
    """Stores the operations that have not been dispatched yet.

    This observer maintains a list of deques, each containing unscheduled
    operations for a specific job. It provides methods to access and
    manipulate unscheduled operations efficiently.
    """

    def __init__(self, dispatcher: Dispatcher, *, subscribe: bool = True):
        super().__init__(dispatcher, subscribe=subscribe)
        self.unscheduled_operations_per_job: List[Deque[Operation]] = []
        self.reset()
        # In case the dispatcher has already scheduled some operations,
        # we need to remove them.
        # Note that we don't need to remove the operations in order.
        for scheduled_operation in itertools.chain(
            *self.dispatcher.schedule.schedule
        ):
            self.update(scheduled_operation)

    @property
    def unscheduled_operations(self) -> Iterable[Operation]:
        """An iterable of all unscheduled operations across all jobs."""
        return itertools.chain(*self.unscheduled_operations_per_job)

    @property
    def num_unscheduled_operations(self) -> int:
        """The total number of unscheduled operations."""
        total_operations = self.dispatcher.instance.num_operations
        num_scheduled_operations = (
            self.dispatcher.schedule.num_scheduled_operations
        )
        return total_operations - num_scheduled_operations

    def update(self, scheduled_operation: ScheduledOperation) -> None:
        """Removes a scheduled operation from the unscheduled operations.

        This method is called by the dispatcher when an operation is
        scheduled. It removes the operation from its job's deque of
        unscheduled operations.

        Args:
            scheduled_operation:
                The operation that has been scheduled.
        """
        job_id = scheduled_operation.operation.job_id
        job_deque = self.unscheduled_operations_per_job[job_id]
        if job_deque:
            job_deque.popleft()

    def reset(self) -> None:
        """Resets unscheduled operations to include all operations.

        This method reinitializes the list of deques with all operations
        from all jobs in the instance.
        """
        self.unscheduled_operations_per_job = [
            collections.deque(job) for job in self.dispatcher.instance.jobs
        ]
