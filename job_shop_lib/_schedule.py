"""Home of the `Schedule` class."""

from __future__ import annotations

from typing import Any, List, Union, Dict, Optional
from collections import deque

from job_shop_lib import ScheduledOperation, JobShopInstance
from job_shop_lib.exceptions import ValidationError


class Schedule:
    """Data structure to store a complete or partial solution for a particular
    :class:`JobShopInstance`.

    A schedule is a list of lists of :class:`ScheduledOperation` objects. Each
    list represents the order of operations on a machine.

    The main methods of this class are:

    .. autosummary::
        :nosignatures:

        makespan
        is_complete
        add
        reset

    Args:
        instance:
            The :class:`JobShopInstance` object that the schedule is for.
        schedule:
            A list of lists of :class:`ScheduledOperation` objects. Each
            list represents the order of operations on a machine. If
            not provided, the schedule is initialized as an empty schedule.
        **metadata:
            Additional information about the schedule.
    """

    __slots__ = {
        "instance": (
            "The :class:`JobShopInstance` object that the schedule is for."
        ),
        "_schedule": (
            "A list of lists of :class:`ScheduledOperation` objects. "
            "Each list represents the order of operations on a machine."
        ),
        "metadata": (
            "A dictionary with additional information about the "
            "schedule. It can be used to store information about the "
            "algorithm that generated the schedule, for example."
        ),
    }

    def __init__(
        self,
        instance: JobShopInstance,
        schedule: Optional[List[List[ScheduledOperation]]] = None,
        **metadata: Any,
    ):
        if schedule is None:
            schedule = [[] for _ in range(instance.num_machines)]

        Schedule.check_schedule(schedule)

        self.instance: JobShopInstance = instance
        self._schedule = schedule
        self.metadata: Dict[str, Any] = metadata

    def __repr__(self) -> str:
        return str(self.schedule)

    @property
    def schedule(self) -> List[List[ScheduledOperation]]:
        """A list of lists of :class:`ScheduledOperation` objects. Each list
        represents the order of operations on a machine."""
        return self._schedule

    @schedule.setter
    def schedule(self, new_schedule: List[List[ScheduledOperation]]):
        Schedule.check_schedule(new_schedule)
        self._schedule = new_schedule

    @property
    def num_scheduled_operations(self) -> int:
        """The number of operations that have been scheduled so far."""
        return sum(len(machine_schedule) for machine_schedule in self.schedule)

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the schedule.

        This representation is useful for saving the instance to a JSON file.

        Returns:
            A dictionary representation of the schedule with the following
            keys:

                - **"instance"**: A dictionary representation of the instance.
                - **"job_sequences"**: A list of lists of job ids. Each list
                  of job ids represents the order of operations on the machine.
                  The machine that the list corresponds to is determined by the
                  index of the list.
                - **"metadata"**: A dictionary with additional information
                  about the schedule.
        """
        job_sequences: List[List[int]] = []
        for machine_schedule in self.schedule:
            job_sequences.append(
                [operation.job_id for operation in machine_schedule]
            )

        return {
            "instance": self.instance.to_dict(),
            "job_sequences": job_sequences,
            "metadata": self.metadata,
        }

    @staticmethod
    def from_dict(
        instance: Union[Dict[str, Any], JobShopInstance],
        job_sequences: List[List[int]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Schedule:
        """Creates a schedule from a dictionary representation."""
        if isinstance(instance, dict):
            instance = JobShopInstance.from_matrices(**instance)
        schedule = Schedule.from_job_sequences(instance, job_sequences)
        schedule.metadata = metadata if metadata is not None else {}
        return schedule

    @staticmethod
    def from_job_sequences(
        instance: JobShopInstance,
        job_sequences: List[List[int]],
    ) -> Schedule:
        """Creates an active schedule from a list of job sequences.

        An active schedule is the optimal schedule for the given job sequences.
        In other words, it is not possible to construct another schedule,
        through changes in the order of processing on the machines, with at
        least one operation finishing earlier and no operation finishing later.

        Args:
            instance:
                The :class:`JobShopInstance` object that the schedule is for.
            job_sequences:
                A list of lists of job ids. Each list of job ids represents the
                order of operations on the machine. The machine that the list
                corresponds to is determined by the index of the list.

        Returns:
            A :class:`Schedule` object with the given job sequences.
        """
        from job_shop_lib.dispatching import Dispatcher

        dispatcher = Dispatcher(instance)
        dispatcher.reset()
        raw_solution_deques = [deque(job_ids) for job_ids in job_sequences]

        while not dispatcher.schedule.is_complete():
            at_least_one_operation_scheduled = False
            for machine_id, job_ids in enumerate(raw_solution_deques):
                if not job_ids:
                    continue
                job_id = job_ids[0]
                operation_index = dispatcher.job_next_operation_index[job_id]
                operation = instance.jobs[job_id][operation_index]
                is_ready = dispatcher.is_operation_ready(operation)
                if is_ready and machine_id in operation.machines:
                    dispatcher.dispatch(operation, machine_id)
                    job_ids.popleft()
                    at_least_one_operation_scheduled = True

            if not at_least_one_operation_scheduled:
                raise ValidationError(
                    "Invalid job sequences. No valid operation to schedule."
                )
        return dispatcher.schedule

    def reset(self):
        """Resets the schedule to an empty state."""
        self.schedule = [[] for _ in range(self.instance.num_machines)]

    def makespan(self) -> int:
        """Returns the makespan of the schedule.

        The makespan is the time at which all operations are completed.
        """
        max_end_time = 0
        for machine_schedule in self.schedule:
            if machine_schedule:
                max_end_time = max(max_end_time, machine_schedule[-1].end_time)
        return max_end_time

    def is_complete(self) -> bool:
        """Returns ``True`` if all operations have been scheduled."""
        return self.num_scheduled_operations == self.instance.num_operations

    def add(self, scheduled_operation: ScheduledOperation):
        """Adds a new :class:`ScheduledOperation` to the schedule.

        Args:
            scheduled_operation:
                The :class:`ScheduledOperation` to add to the schedule.

        Raises:
            ValidationError:
                If the start time of the new operation is before the
                end time of the last operation on the same machine. In favor of
                performance, this method does not checks precedence
                constraints.
        """
        self._check_start_time_of_new_operation(scheduled_operation)
        self.schedule[scheduled_operation.machine_id].append(
            scheduled_operation
        )

    def _check_start_time_of_new_operation(
        self,
        new_operation: ScheduledOperation,
    ):
        is_first_operation = not self.schedule[new_operation.machine_id]
        if is_first_operation:
            return

        last_operation = self.schedule[new_operation.machine_id][-1]
        if not self._is_valid_start_time(new_operation, last_operation):
            raise ValidationError(
                "Operation cannot be scheduled before the last operation on "
                "the same machine: end time of last operation "
                f"({last_operation.end_time}) > start time of new operation "
                f"({new_operation.start_time})."
            )

    @staticmethod
    def _is_valid_start_time(
        scheduled_operation: ScheduledOperation,
        previous_operation: ScheduledOperation,
    ):
        return previous_operation.end_time <= scheduled_operation.start_time

    @staticmethod
    def check_schedule(schedule: List[List[ScheduledOperation]]):
        """Checks if a schedule is valid and raises a
        :class:`~exceptions.ValidationError` if it is not.

        A schedule is considered invalid if:
            - A :class:`ScheduledOperation` has a machine id that does not
              match the machine id of the machine schedule (the list of
              :class:`ScheduledOperation` objects) that it belongs to.
            - The start time of a :class:`ScheduledOperation` is before the
              end time of the last operation on the same machine.

        Args:
            schedule:
                The schedule (a list of lists of :class:`ScheduledOperation`
                objects) to check.

        Raises:
            ValidationError: If the schedule is invalid.
        """
        for machine_id, scheduled_operations in enumerate(schedule):
            for i, scheduled_operation in enumerate(scheduled_operations):
                if scheduled_operation.machine_id != machine_id:
                    raise ValidationError(
                        "The machine id of the scheduled operation "
                        f"({ScheduledOperation.machine_id}) does not match "
                        f"the machine id of the machine schedule ({machine_id}"
                        f"). Index of the operation: [{machine_id}][{i}]."
                    )

                if i == 0:
                    continue

                if not Schedule._is_valid_start_time(
                    scheduled_operation, scheduled_operations[i - 1]
                ):
                    raise ValidationError(
                        "Invalid schedule. The start time of the new "
                        "operation is before the end time of the last "
                        "operation on the same machine."
                        "End time of last operation: "
                        f"{scheduled_operations[i - 1].end_time}. "
                        f"Start time of new operation: "
                        f"{scheduled_operation.start_time}. At index "
                        f"[{machine_id}][{i}]."
                    )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Schedule):
            return False

        return self.schedule == value.schedule
