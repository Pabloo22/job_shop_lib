"""Home of the `Dispatcher` class."""

from __future__ import annotations

import abc
from typing import Any, TypeVar, List, Optional, Type, Set
from collections.abc import Callable
from functools import wraps

from job_shop_lib import (
    JobShopInstance,
    Schedule,
    ScheduledOperation,
    Operation,
)
from job_shop_lib.exceptions import ValidationError


# Added here to avoid circular imports
class DispatcherObserver(abc.ABC):
    """Abstract class that allows objects to observe and respond to changes
    within the :class:`Dispatcher`.

    It follows the Observer design pattern, where observers subscribe to the
    dispatcher and receive updates when certain events occur, such as when
    an operation is scheduled or when the dispatcher is reset.

    Attributes:
        dispatcher:
            The :class:`Dispatcher` instance to observe.

    Args:
        dispatcher:
            The :class:`Dispatcher` instance to observe.
        subscribe:
            If ``True``, automatically subscribes the observer to the
            dispatcher when it is initialized. Defaults to ``True``.

    Raises:
        ValidationError: If ``is_singleton`` is ``True`` and an observer of the
            same type already exists in the dispatcher's list of
            subscribers.

    Example:

    .. code-block:: python

        from job_shop_lib.dispatching import DispatcherObserver, Dispatcher
        from job_shop_lib import ScheduledOperation


        class HistoryObserver(DispatcherObserver):
            def __init__(self, dispatcher: Dispatcher):
                super().__init__(dispatcher)
                self.history: List[ScheduledOperation] = []

            def update(self, scheduled_operation: ScheduledOperation):
                self.history.append(scheduled_operation)

            def reset(self):
                self.history = []

    """

    # Made read-only following Google Style Guide recommendation
    _is_singleton = True
    """If True, ensures only one instance of this observer type is subscribed
    to the dispatcher."""

    def __init__(
        self,
        dispatcher: Dispatcher,
        *,
        subscribe: bool = True,
    ):
        if self._is_singleton and any(
            isinstance(observer, self.__class__)
            for observer in dispatcher.subscribers
        ):
            raise ValidationError(
                f"An observer of type {self.__class__.__name__} already "
                "exists in the dispatcher's list of subscribers. If you want "
                "to create multiple instances of this observer, set "
                "`is_singleton` to False."
            )

        self.dispatcher = dispatcher
        if subscribe:
            self.dispatcher.subscribe(self)

    @property
    def is_singleton(self) -> bool:
        """Returns whether this observer is a singleton.

        This is a class attribute that determines whether only one
        instance of this observer type can be subscribed to the dispatcher.
        """
        return self._is_singleton

    @abc.abstractmethod
    def update(self, scheduled_operation: ScheduledOperation):
        """Called when an operation is scheduled on a machine."""

    @abc.abstractmethod
    def reset(self):
        """Called when the dispatcher is reset."""

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return self.__class__.__name__


# Disable pylint's false positive
# pylint: disable=invalid-name
ObserverType = TypeVar("ObserverType", bound=DispatcherObserver)


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

    The core method of the class are:

    .. autosummary::

        dispatch
        reset

    It also provides methods to query the state of the schedule and the
    operations:

    .. autosummary::

        current_time
        available_operations
        available_machines
        available_jobs
        unscheduled_operations
        scheduled_operations
        ongoing_operations
        completed_operations
        uncompleted_operations
        is_scheduled
        is_ongoing
        next_operation
        earliest_start_time
        remaining_duration

    The above methods which do not take any arguments are cached to improve
    performance. After each scheduling operation, the cache is cleared.

    Args:
        instance:
            The instance of the job shop problem to be solved.
        ready_operations_filter:
            A function that filters out operations that are not ready to
            be scheduled. The function should take the dispatcher and a
            list of operations as input and return a list of operations
            that are ready to be scheduled. If ``None``, no filtering is
            done.
    """

    __slots__ = {
        "instance": "The instance of the job shop problem to be scheduled.",
        "schedule": "The schedule of operations on machines.",
        "_machine_next_available_time": "",
        "_job_next_operation_index": "",
        "_job_next_available_time": "",
        "ready_operations_filter": (
            "A function that filters out operations that are not ready to be "
            "scheduled."
        ),
        "subscribers": "A list of observers subscribed to the dispatcher.",
        "_cache": "A dictionary to cache the results of the cached methods.",
    }

    def __init__(
        self,
        instance: JobShopInstance,
        ready_operations_filter: (
            Optional[Callable[[Dispatcher, List[Operation]], List[Operation]]]
        ) = None,
    ) -> None:

        self.instance = instance
        self.schedule = Schedule(self.instance)
        self.ready_operations_filter = ready_operations_filter
        self.subscribers: List[DispatcherObserver] = []

        self._machine_next_available_time = [0] * self.instance.num_machines
        self._job_next_operation_index = [0] * self.instance.num_jobs
        self._job_next_available_time = [0] * self.instance.num_jobs
        self._cache: dict[str, Any] = {}

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.instance})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def machine_next_available_time(self) -> List[int]:
        """Returns the next available time for each machine."""
        return self._machine_next_available_time

    @property
    def job_next_operation_index(self) -> List[int]:
        """Returns the index of the next operation to be scheduled for each
        job."""
        return self._job_next_operation_index

    @property
    def job_next_available_time(self) -> List[int]:
        """Returns the next available time for each job."""
        return self._job_next_available_time

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

    def dispatch(
        self, operation: Operation, machine_id: Optional[int] = None
    ) -> None:
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
                scheduled. If ``None``, the :class:`~job_shop_lib.Operation`'s
                :attr:`~job_shop_lib.Operation.machine_id` attribute is used.

        Raises:
            ValidationError: If the operation is not ready to be scheduled.
            UninitializedAttributeError: If the operation has multiple
                machines in its list and no ``machine_id`` is provided.
        """

        if not self.is_operation_ready(operation):
            raise ValidationError("Operation is not ready to be scheduled.")

        if machine_id is None:
            machine_id = operation.machine_id

        start_time = self.start_time(operation, machine_id)

        scheduled_operation = ScheduledOperation(
            operation, start_time, machine_id
        )
        self.schedule.add(scheduled_operation)
        self._update_tracking_attributes(scheduled_operation)

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
                scheduled. If ``None``, the start time is computed based on the
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

        # Notify subscribers
        for subscriber in self.subscribers:
            subscriber.update(scheduled_operation)

    def create_or_get_observer(
        self,
        observer: Type[ObserverType],
        condition: Callable[[DispatcherObserver], bool] = lambda _: True,
        **kwargs,
    ) -> ObserverType:
        """Creates a new observer of the specified type or returns an existing
        observer of the same type if it already exists in the dispatcher's list
        of observers.

        Args:
            observer:
                The type of observer to be created or retrieved.
            condition:
                A function that takes an observer and returns True if it is
                the observer to be retrieved. By default, it returns True for
                all observers.
            **kwargs:
                Additional keyword arguments to be passed to the observer's
                constructor.
        """
        for existing_observer in self.subscribers:
            if isinstance(existing_observer, observer) and condition(
                existing_observer
            ):
                return existing_observer

        new_observer = observer(self, **kwargs)
        return new_observer

    @_dispatcher_cache
    def current_time(self) -> int:
        """Returns the current time of the schedule.

        The current time is the minimum start time of the available
        operations.
        """
        available_operations = self.available_operations()
        current_time = self.min_start_time(available_operations)
        return current_time

    def min_start_time(self, operations: List[Operation]) -> int:
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
    def available_operations(self) -> List[Operation]:
        """Returns a list of available operations for processing, optionally
        filtering out operations using the filter function.

        This method first gathers all possible next operations from the jobs
        being processed. It then optionally filters these operations using the
        filter function.

        Returns:
            A list of :class:`Operation` objects that are available for
            scheduling.
        """
        available_operations = self.raw_ready_operations()
        if self.ready_operations_filter is not None:
            available_operations = self.ready_operations_filter(
                self, available_operations
            )
        return available_operations

    @_dispatcher_cache
    def raw_ready_operations(self) -> List[Operation]:
        """Returns a list of available operations for processing without
        applying the filter function.

        Returns:
            A list of :class:`Operation` objects that are available for
            scheduling based on precedence and machine constraints only.
        """
        available_operations = [
            self.instance.jobs[job_id][position]
            for job_id, position in enumerate(self._job_next_operation_index)
            if position < len(self.instance.jobs[job_id])
        ]
        return available_operations

    @_dispatcher_cache
    def unscheduled_operations(self) -> List[Operation]:
        """Returns the list of operations that have not been scheduled."""
        unscheduled_operations = []
        for job_id, next_position in enumerate(self._job_next_operation_index):
            operations = self.instance.jobs[job_id][next_position:]
            unscheduled_operations.extend(operations)
        return unscheduled_operations

    @_dispatcher_cache
    def scheduled_operations(self) -> List[Operation]:
        """Returns the list of operations that have been scheduled."""
        scheduled_operations = []
        for job_id, next_position in enumerate(self._job_next_operation_index):
            operations = self.instance.jobs[job_id][:next_position]
            scheduled_operations.extend(operations)
        return scheduled_operations

    @_dispatcher_cache
    def available_machines(self) -> List[int]:
        """Returns the list of ready machines."""
        available_operations = self.available_operations()
        available_machines = set()
        for operation in available_operations:
            available_machines.update(operation.machines)
        return list(available_machines)

    @_dispatcher_cache
    def available_jobs(self) -> List[int]:
        """Returns the list of ready jobs."""
        available_operations = self.available_operations()
        available_jobs = set(
            operation.job_id for operation in available_operations
        )
        return list(available_jobs)

    def earliest_start_time(self, operation: Operation) -> int:
        """Calculates the earliest start time for a given operation based on
        machine and job constraints.

        This method is different from the ``start_time`` method in that it
        takes into account every machine that can process the operation, not
        just the one that will process it. However, it also assumes that
        the operation is ready to be scheduled in the job in favor of
        performance.

        Args:
            operation:
                The operation for which to calculate the earliest start time.

        Returns:
            The earliest start time for the operation.
        """
        machine_earliest_start_time = min(
            self._machine_next_available_time[machine_id]
            for machine_id in operation.machines
        )
        job_start_time = self._job_next_available_time[operation.job_id]
        return max(machine_earliest_start_time, job_start_time)

    def remaining_duration(
        self, scheduled_operation: ScheduledOperation
    ) -> int:
        """Calculates the remaining duration of a scheduled operation.

        The method computes the remaining time for an operation to finish,
        based on the maximum of the operation's start time or the current time.
        This helps in determining how much time is left from 'now' until the
        operation is completed.

        Args:
            scheduled_operation:
                The operation for which to calculate the remaining time.

        Returns:
            The remaining duration.
        """
        adjusted_start_time = max(
            scheduled_operation.start_time, self.current_time()
        )
        return scheduled_operation.end_time - adjusted_start_time

    @_dispatcher_cache
    def completed_operations(self) -> Set[Operation]:
        """Returns the set of operations that have been completed.

        This method returns the operations that have been scheduled and the
        current time is greater than or equal to the end time of the operation.
        """
        scheduled_operations = set(self.scheduled_operations())
        ongoing_operations = set(
            map(
                lambda scheduled_op: scheduled_op.operation,
                self.ongoing_operations(),
            )
        )
        completed_operations = scheduled_operations - ongoing_operations
        return completed_operations

    @_dispatcher_cache
    def uncompleted_operations(self) -> List[Operation]:
        """Returns the list of operations that have not been completed yet.

        This method checks for operations that either haven't been scheduled
        or have been scheduled but haven't reached their completion time.

        Note:
        The behavior of this method changed in version 0.5.0. Previously, it
        only returned unscheduled operations. For the old behavior, use the
        `unscheduled_operations` method.
        """
        uncompleted_operations = self.unscheduled_operations()
        uncompleted_operations.extend(
            scheduled_operation.operation
            for scheduled_operation in self.ongoing_operations()
        )
        return uncompleted_operations

    @_dispatcher_cache
    def ongoing_operations(self) -> List[ScheduledOperation]:
        """Returns the list of operations that are currently being processed.

        This method returns the operations that have been scheduled and are
        currently being processed by the machines.
        """
        current_time = self.current_time()
        ongoing_operations = []
        for machine_schedule in self.schedule.schedule:
            for scheduled_operation in reversed(machine_schedule):
                is_completed = scheduled_operation.end_time <= current_time
                if is_completed:
                    break
                ongoing_operations.append(scheduled_operation)
        return ongoing_operations

    def is_scheduled(self, operation: Operation) -> bool:
        """Checks if the given operation has been scheduled."""
        job_next_op_idx = self._job_next_operation_index[operation.job_id]
        return operation.position_in_job < job_next_op_idx

    def is_ongoing(self, scheduled_operation: ScheduledOperation) -> bool:
        """Checks if the given operation is currently being processed."""
        current_time = self.current_time()
        return scheduled_operation.start_time <= current_time

    def next_operation(self, job_id: int) -> Operation:
        """Returns the next operation to be scheduled for the given job.

        Args:
            job_id:
                The id of the job for which to return the next operation.

        Raises:
            ValidationError: If there are no more operations left for the job.
        """
        if (
            len(self.instance.jobs[job_id])
            <= self._job_next_operation_index[job_id]
        ):
            raise ValidationError(
                f"No more operations left for job {job_id} to schedule."
            )
        return self.instance.jobs[job_id][
            self._job_next_operation_index[job_id]
        ]
