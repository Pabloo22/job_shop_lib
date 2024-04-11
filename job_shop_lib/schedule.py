"""Home of the `Schedule` class."""

from job_shop_lib import ScheduledOperation, JobShopInstance


class Schedule:
    """Data structure to store a schedule for a `JobShopInstance` object.

    Attributes:
        instance:
            The `JobShopInstance` object that the schedule is for.
        schedule:
            A list of lists of `ScheduledOperation` objects. Each list of
            `ScheduledOperation` objects represents the order of operations
            on a machine.
        metadata:
            A dictionary with additional information about the schedule. It
            can be used to store information about the algorithm that generated
            the schedule, for example.
    """

    __slots__ = (
        "instance",
        "_schedule",
        "metadata",
    )

    def __init__(
        self,
        instance: JobShopInstance,
        schedule: list[list[ScheduledOperation]] | None = None,
        **metadata,
    ):
        """Initializes the object with the given instance and schedule.

        Args:
            instance:
                The `JobShopInstance` object that the schedule is for.
            schedule:
                A list of lists of `ScheduledOperation` objects. Each list of
                `ScheduledOperation` objects represents the order of operations
                on a machine. If not provided, the schedule is initialized as
                an empty schedule.
            **metadata:
                Additional information about the schedule.
        """
        if schedule is None:
            schedule = [[] for _ in range(instance.num_machines)]

        Schedule.check_schedule(schedule)

        self.instance = instance
        self._schedule = schedule
        self.metadata = metadata

    def __repr__(self) -> str:
        return str(self.schedule)

    @property
    def schedule(self) -> list[list[ScheduledOperation]]:
        """Returns the schedule attribute."""
        return self._schedule

    @schedule.setter
    def schedule(self, new_schedule: list[list[ScheduledOperation]]):
        Schedule.check_schedule(new_schedule)
        self._schedule = new_schedule

    @property
    def num_scheduled_operations(self) -> int:
        """Returns the number of operations that have been scheduled."""
        return sum(len(machine_schedule) for machine_schedule in self.schedule)

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
        """Returns True if all operations have been scheduled."""
        return self.num_scheduled_operations == self.instance.num_operations

    def add(self, scheduled_operation: ScheduledOperation):
        """Adds a new `ScheduledOperation` to the schedule.

        Args:
            scheduled_operation:
                The `ScheduledOperation` to add to the schedule.

        Raises:
            ValueError: If the start time of the new operation is before the
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
        self._check_start_time(new_operation, last_operation)

    @staticmethod
    def _check_start_time(
        scheduled_operation: ScheduledOperation,
        previous_operation: ScheduledOperation,
    ):
        """Raises a ValueError if the start time of the new operation is before
        the end time of the last operation on the same machine."""

        if previous_operation.end_time <= scheduled_operation.start_time:
            return

        raise ValueError(
            "Operation cannot be scheduled before the last operation on "
            "the same machine: end time of last operation "
            f"({previous_operation.end_time}) > start time of new operation "
            f"({scheduled_operation.start_time})."
        )

    @staticmethod
    def check_schedule(schedule: list[list[ScheduledOperation]]):
        """Checks if a schedule is valid and raises a ValueError if it is not.

        A schedule is considered invalid if:
            - A `ScheduledOperation` has a machine id that does not match the
              machine id of the machine schedule (the list of
              `ScheduledOperation` objects) that it belongs to.
            - The start time of a `ScheduledOperation` is before the end time
              of the last operation on the same machine.

        Args:
            schedule:
                The schedule (a list of lists of `ScheduledOperation` objects)
                to check.

        Raises:
            ValueError: If the schedule is invalid.
        """
        for machine_id, scheduled_operations in enumerate(schedule):
            for i, scheduled_operation in enumerate(scheduled_operations):
                if scheduled_operation.machine_id != machine_id:
                    raise ValueError(
                        "The machine id of the scheduled operation "
                        f"({ScheduledOperation.machine_id}) does not match "
                        f"the machine id of the machine schedule ({machine_id}"
                        f"). Index of the operation: [{machine_id}][{i}]."
                    )

                if i == 0:
                    continue

                Schedule._check_start_time(
                    scheduled_operation, scheduled_operations[i - 1]
                )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Schedule):
            return False

        return self.schedule == value.schedule
