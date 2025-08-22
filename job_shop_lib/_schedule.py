"""Home of the `Schedule` class."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from collections import deque

from job_shop_lib import ScheduledOperation, JobShopInstance, Operation
from job_shop_lib.exceptions import ValidationError

if TYPE_CHECKING:
    from job_shop_lib.dispatching import Dispatcher


class Schedule:
    r"""Data structure to store a complete or partial solution for a particular
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
        \**metadata:
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
        "operation_to_scheduled_operation": (
            "A dictionary that maps an :class:`Operation` to its "
            ":class:`ScheduledOperation` in the schedule. This is used to "
            "quickly find the scheduled operation associated with a given "
            "operation."
        ),
        "num_scheduled_operations": (
            "The number of operations that have been scheduled so far."
        ),
        "operation_with_latest_end_time": (
            "The :class:`ScheduledOperation` with the latest end time. "
            "This is used to quickly find the last operation in the schedule."
        ),
    }

    def __init__(
        self,
        instance: JobShopInstance,
        schedule: list[list[ScheduledOperation]] | None = None,
        **metadata: Any,
    ):
        if schedule is None:
            schedule = [[] for _ in range(instance.num_machines)]

        Schedule.check_schedule(schedule)

        self.instance: JobShopInstance = instance
        self._schedule = schedule
        self.metadata: dict[str, Any] = metadata
        self.operation_to_scheduled_operation: dict[
            Operation, ScheduledOperation
        ] = {
            scheduled_op.operation: scheduled_op
            for machine_schedule in schedule
            for scheduled_op in machine_schedule
        }
        self.num_scheduled_operations = sum(
            len(machine_schedule) for machine_schedule in schedule
        )
        self.operation_with_latest_end_time: ScheduledOperation | None = max(
            (
                scheduled_op
                for machine_schedule in schedule
                for scheduled_op in machine_schedule
            ),
            key=lambda op: op.end_time,  # type: ignore[union-attr]
            default=None,
        )

    def __repr__(self) -> str:
        return str(self.schedule)

    @property
    def schedule(self) -> list[list[ScheduledOperation]]:
        """A list of lists of :class:`ScheduledOperation` objects. Each list
        represents the order of operations on a machine."""
        return self._schedule

    @schedule.setter
    def schedule(self, new_schedule: list[list[ScheduledOperation]]):
        Schedule.check_schedule(new_schedule)
        self._schedule = new_schedule

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
        return {
            "instance": self.instance.to_dict(),
            "job_sequences": self.job_sequences(),
            "metadata": self.metadata,
        }

    @staticmethod
    def from_dict(
        instance: dict[str, Any] | JobShopInstance,
        job_sequences: list[list[int]],
        metadata: dict[str, Any] | None = None,
    ) -> Schedule:
        """Creates a schedule from a dictionary representation.

        Args:
            instance:
                The instance to create the schedule for. Can be a dictionary
                representation of a :class:`JobShopInstance` or a
                :class:`JobShopInstance` object.
            job_sequences:
                A list of lists of job ids. Each list of job ids represents the
                order of operations on the machine. The machine that the list
                corresponds to is determined by the index of the list.
            metadata:
                A dictionary with additional information about the schedule.

        Returns:
            A :class:`Schedule` object with the given job sequences.
        """
        if isinstance(instance, dict):
            instance = JobShopInstance.from_matrices(**instance)
        schedule = Schedule.from_job_sequences(instance, job_sequences)
        schedule.metadata = metadata if metadata is not None else {}
        return schedule

    @staticmethod
    def from_job_sequences(
        instance: JobShopInstance,
        job_sequences: list[list[int]],
        dispatcher: Dispatcher | None = None,
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
            dispatcher:
                A :class:`~job_shop_lib.dispatching.Dispatcher` to use for
                scheduling. If not provided, a new dispatcher will be
                created.

                .. note::
                    You will need to provide a dispatcher if you want to
                    take into account start time calculators different from
                    the default one.

        Returns:
            A :class:`Schedule` object with the given job sequences.

        .. seealso::
            See :mod:`job_shop_lib.dispatching` for more information
            about dispatchers and the start time calculators available.
        """
        from job_shop_lib.dispatching import Dispatcher

        if dispatcher is None:
            dispatcher = Dispatcher(instance)
        dispatcher.reset()
        raw_solution_deques = [deque(job_ids) for job_ids in job_sequences]

        while any(job_seq for job_seq in raw_solution_deques):
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

    def job_sequences(self) -> list[list[int]]:
        """Returns the sequence of jobs for each machine in the schedule.

        This method returns a list of lists, where each sublist contains the
        job ids of the operations scheduled on that machine.
        """
        job_sequences: list[list[int]] = []
        for machine_schedule in self.schedule:
            job_sequences.append(
                [operation.job_id for operation in machine_schedule]
            )
        return job_sequences

    def reset(self):
        """Resets the schedule to an empty state."""
        self.schedule = [[] for _ in range(self.instance.num_machines)]
        self.operation_to_scheduled_operation = {}
        self.num_scheduled_operations = 0
        self.operation_with_latest_end_time = None

    def makespan(self) -> int:
        """Returns the makespan of the schedule.

        The makespan is the time at which all operations are completed.
        """
        last_operation = self.operation_with_latest_end_time
        if last_operation is None:
            return 0
        return last_operation.end_time

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

        # Update attributes:
        self.schedule[scheduled_operation.machine_id].append(
            scheduled_operation
        )

        self.operation_to_scheduled_operation[
            scheduled_operation.operation
        ] = scheduled_operation

        self.num_scheduled_operations += 1

        if (
            self.operation_with_latest_end_time is None
            or scheduled_operation.end_time
            > self.operation_with_latest_end_time.end_time
        ):
            self.operation_with_latest_end_time = scheduled_operation

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
    def check_schedule(schedule: list[list[ScheduledOperation]]):
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

    def copy(self) -> Schedule:
        """Returns a copy of the schedule."""
        return Schedule(
            self.instance,
            [machine_schedule.copy() for machine_schedule in self.schedule],
            **self.metadata,
        )

    def critical_path(self) -> list[ScheduledOperation]:
        """Returns the critical path of the schedule.

        The critical path is the longest path of dependent operations through
        the schedule, which determines the makespan. This implementation
        correctly identifies the path even in non-compact schedules where
        idle time may exist.

        It works by starting from an operation that determines the makespan
        and tracing backwards, at each step choosing the predecessor (either
        from the same job or the same machine) that finished latest.
        """
        # 1. Start from the operation that determines the makespan
        last_scheduled_op = self.operation_with_latest_end_time
        if last_scheduled_op is None:
            return []

        critical_path = deque([last_scheduled_op])
        current_scheduled_op = last_scheduled_op

        machine_op_index = {}
        for machine_id, schedule_list in enumerate(self.schedule):
            machine_op_index[machine_id] = {op: idx for idx, op in
                                            enumerate(schedule_list)}

        # 2. Trace backwards from the last operation
        while True:
            job_pred: ScheduledOperation | None = None
            machine_pred: ScheduledOperation | None = None

            # Find job predecessor (the previous operation in the same job)
            op_idx_in_job = current_scheduled_op.operation.position_in_job
            if op_idx_in_job > 0:
                prev_op_in_job = self.instance.jobs[
                    current_scheduled_op.job_id
                ][op_idx_in_job - 1]
                job_pred = self.operation_to_scheduled_operation[
                    prev_op_in_job
                ]

            # Find machine predecessor (the previous operation on the same
            # machine)
            machine_schedule = self.schedule[current_scheduled_op.machine_id]
            op_idx_on_machine = (
                machine_op_index
                [current_scheduled_op.machine_id][current_scheduled_op])
            if op_idx_on_machine > 0:
                machine_pred = machine_schedule[
                    op_idx_on_machine - 1
                ]

            # 3. Determine the critical predecessor
            # The critical predecessor is the one that finished latest, as it
            # determined the start time of the current operation.

            if job_pred is None and machine_pred is None:
                # Reached the beginning of the schedule, no more predecessors
                break

            job_pred_end_time = (
                job_pred.end_time if job_pred is not None else -1
            )
            machine_pred_end_time = (
                machine_pred.end_time if machine_pred is not None else -1
            )
            critical_pred = (
                job_pred
                if job_pred_end_time >= machine_pred_end_time
                else machine_pred
            )
            assert critical_pred is not None
            # Prepend the critical predecessor to the path and continue tracing
            critical_path.appendleft(critical_pred)
            current_scheduled_op = critical_pred

        return list(critical_path)
