"""Home of the `Dispatcher` class."""

from __future__ import annotations

import abc
from typing import Any
from collections.abc import Callable
from collections import deque
from functools import wraps
from warnings import warn

from job_shop_lib import (
    JobShopInstance,
    Schedule,
    ScheduledOperation,
    Operation,
)


# Added here to avoid circular imports
class DispatcherObserver(abc.ABC):
    """Interface for classes that observe the dispatcher."""

    def __init__(self, dispatcher: Dispatcher):
        """Initializes the observer with the dispatcher and subscribes to
        it."""
        self.dispatcher = dispatcher
        self.dispatcher.subscribe(self)

    @abc.abstractmethod
    def update(self, scheduled_operation: ScheduledOperation):
        """Called when an operation is scheduled on a machine."""

    @abc.abstractmethod
    def reset(self):
        """Called when the dispatcher is reset."""

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return str(self)


def _dispatcher_cache(method):
    """Decorator to cache results of a method based on its name.

    This decorator assumes that the class has an attribute called `_cache`
    that is a dictionary. It caches the result of the method based on its
    name. If the result is already cached, it returns the cached result
    instead of recomputing it.

    The decorator is useful since the dispatcher class can clear the cache
    when the state of the dispatcher changes.
    """

    @wraps(method)
    def wrapper(self: Dispatcher, *args, **kwargs):
        # pylint: disable=protected-access
        cache_key = method.__name__
        cached_result = self._cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        result = method(self, *args, **kwargs)
        self._cache[cache_key] = result
        return result

    return wrapper


# pylint: disable=too-many-instance-attributes
class Dispatcher:
    """Handles the logic of scheduling operations on machines.

    This class allow us to just define the order in which operations are
    sequenced and the machines in which they are processed. It is then
    responsible for scheduling the operations on the machines and keeping
    track of the next available time for each machine and job.

    Attributes:
        instance:
            The instance of the job shop problem to be scheduled.
        schedule:
            The schedule of operations on machines.
        pruning_function:
            A function that filters out operations that are not ready to be
            scheduled.
        subscribers:
            A list of observers that are subscribed to the dispatcher.
    """

    __slots__ = (
        "instance",
        "schedule",
        "_machine_next_available_time",
        "_job_next_operation_index",
        "_job_next_available_time",
        "pruning_function",
        "subscribers",
        "_cache",
    )

    def __init__(
        self,
        instance: JobShopInstance,
        pruning_function: (
            Callable[[Dispatcher, list[Operation]], list[Operation]] | None
        ) = None,
    ) -> None:
        """Initializes the object with the given instance.

        Args:
            instance:
                The instance of the job shop problem to be solved.
            pruning_function:
                A function that filters out operations that are not ready to
                be scheduled. The function should take the dispatcher and a
                list of operations as input and return a list of operations
                that are ready to be scheduled. If `None`, no pruning is done.
        """

        self.instance = instance
        self.schedule = Schedule(self.instance)
        self.pruning_function = pruning_function

        self._machine_next_available_time = [0] * self.instance.num_machines
        self._job_next_operation_index = [0] * self.instance.num_jobs
        self._job_next_available_time = [0] * self.instance.num_jobs
        self.subscribers: list[DispatcherObserver] = []
        self._cache: dict[str, Any] = {}

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.instance})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def machine_next_available_time(self) -> list[int]:
        """Returns the next available time for each machine."""
        return self._machine_next_available_time

    @property
    def job_next_operation_index(self) -> list[int]:
        """Returns the index of the next operation to be scheduled for each
        job."""
        return self._job_next_operation_index

    @property
    def job_next_available_time(self) -> list[int]:
        """Returns the next available time for each job."""
        return self._job_next_available_time

    @classmethod
    def create_schedule_from_raw_solution(
        cls, instance: JobShopInstance, raw_solution: list[list[Operation]]
    ) -> Schedule:
        """Deprecated method, use `Schedule.from_job_sequences` instead."""
        warn(
            "Dispatcher.create_schedule_from_raw_solution is deprecated. "
            "Use Schedule.from_job_sequences instead. It will be removed in "
            "version 1.0.0.",
            DeprecationWarning,
        )
        dispatcher = cls(instance)
        dispatcher.reset()
        raw_solution_deques = [
            deque(operations) for operations in raw_solution
        ]
        while not dispatcher.schedule.is_complete():
            for machine_id, operations in enumerate(raw_solution_deques):
                if not operations:
                    continue
                operation = operations[0]
                if dispatcher.is_operation_ready(operation):
                    dispatcher.dispatch(operation, machine_id)
                    operations.popleft()
        return dispatcher.schedule

    def subscribe(self, observer: DispatcherObserver):
        """Subscribes an observer to the dispatcher."""
        self.subscribers.append(observer)

    def unsubscribe(self, observer: DispatcherObserver):
        """Unsubscribes an observer from the dispatcher."""
        self.subscribers.remove(observer)

    def reset(self) -> None:
        """Resets the dispatcher to its initial state."""
        self.schedule.reset()
        self._machine_next_available_time = [0] * self.instance.num_machines
        self._job_next_operation_index = [0] * self.instance.num_jobs
        self._job_next_available_time = [0] * self.instance.num_jobs
        self._cache = {}
        for subscriber in self.subscribers:
            subscriber.reset()

    def dispatch(self, operation: Operation, machine_id: int) -> None:
        """Schedules the given operation on the given machine.

        The start time of the operation is computed based on the next
        available time for the machine and the next available time for the
        job to which the operation belongs. The operation is then scheduled
        on the machine and the tracking attributes are updated.
        Args:
            operation:
                The operation to be scheduled.
            machine_id:
                The id of the machine on which the operation is to be
                scheduled.

        Raises:
            ValueError: If the operation is not ready to be scheduled.
        """

        if not self.is_operation_ready(operation):
            raise ValueError("Operation is not ready to be scheduled.")

        start_time = self.start_time(operation, machine_id)

        scheduled_operation = ScheduledOperation(
            operation, start_time, machine_id
        )
        self.schedule.add(scheduled_operation)
        self._update_tracking_attributes(scheduled_operation)

        # Notify subscribers
        for subscriber in self.subscribers:
            subscriber.update(scheduled_operation)

    def is_operation_ready(self, operation: Operation) -> bool:
        """Returns True if the given operation is ready to be scheduled.

        An operation is ready to be scheduled if it is the next operation
        to be scheduled for its job.

        Args:
            operation:
                The operation to be checked.
        """
        return (
            self._job_next_operation_index[operation.job_id]
            == operation.position_in_job
        )

    def start_time(
        self,
        operation: Operation,
        machine_id: int,
    ) -> int:
        """Computes the start time for the given operation on the given
        machine.

        The start time is the maximum of the next available time for the
        machine and the next available time for the job to which the
        operation belongs.

        Args:
            operation:
                The operation to be scheduled.
            machine_id:
                The id of the machine on which the operation is to be
                scheduled. If None, the start time is computed based on the
                next available time for the operation on any machine.
        """
        return max(
            self._machine_next_available_time[machine_id],
            self._job_next_available_time[operation.job_id],
        )

    def _update_tracking_attributes(
        self, scheduled_operation: ScheduledOperation
    ) -> None:
        # Variables defined here to make the lines shorter
        job_id = scheduled_operation.job_id
        machine_id = scheduled_operation.machine_id
        end_time = scheduled_operation.end_time

        self._machine_next_available_time[machine_id] = end_time
        self._job_next_operation_index[job_id] += 1
        self._job_next_available_time[job_id] = end_time
        self._cache = {}

    @_dispatcher_cache
    def current_time(self) -> int:
        """Returns the current time of the schedule.

        The current time is the minimum start time of the available
        operations.
        """
        available_operations = self.available_operations()
        current_time = self.min_start_time(available_operations)
        return current_time

    def min_start_time(self, operations: list[Operation]) -> int:
        """Returns the minimum start time of the available operations."""
        if not operations:
            return self.schedule.makespan()
        min_start_time = float("inf")
        for op in operations:
            for machine_id in op.machines:
                start_time = self.start_time(op, machine_id)
                min_start_time = min(min_start_time, start_time)
        return int(min_start_time)

    @_dispatcher_cache
    def uncompleted_operations(self) -> list[Operation]:
        """Returns the list of operations that have not been scheduled.

        An operation is uncompleted if it has not been scheduled yet.

        It is more efficient than checking all operations in the instance.
        """
        uncompleted_operations = []
        for job_id, next_position in enumerate(self._job_next_operation_index):
            operations = self.instance.jobs[job_id][next_position:]
            uncompleted_operations.extend(operations)
        return uncompleted_operations

    @_dispatcher_cache
    def available_operations(self) -> list[Operation]:
        """Returns a list of available operations for processing, optionally
        filtering out operations using the pruning function.

        This method first gathers all possible next operations from the jobs
        being processed. It then optionally filters these operations using the
        pruning function.

        Returns:
            A list of Operation objects that are available for scheduling.
        """

        available_operations = self._available_operations()
        if self.pruning_function is not None:
            available_operations = self.pruning_function(
                self, available_operations
            )
        return available_operations

    def _available_operations(self) -> list[Operation]:
        available_operations = []
        for job_id, next_position in enumerate(self._job_next_operation_index):
            if next_position == len(self.instance.jobs[job_id]):
                continue
            operation = self.instance.jobs[job_id][next_position]
            available_operations.append(operation)
        return available_operations
