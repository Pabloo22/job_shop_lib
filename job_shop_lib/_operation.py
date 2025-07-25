"""Home of the `Operation` class."""

from __future__ import annotations

from job_shop_lib.exceptions import ValidationError


class Operation:
    """Stores machine and duration information for a job operation.

    An operation is a task that must be performed on a machine. It is part of a
    job and has a duration that represents the time it takes to complete the
    task.

    Tip:
        To use custom attributes, such as due dates or priorities, subclass
        this class and add the desired attributes.

    Note:
        To increase performance, some solvers such as the CP-SAT solver use
        only integers to represent the operation's attributes. Should a
        problem involve operations with non-integer durations, it would be
        necessary to multiply all durations by a sufficiently large integer so
        that every duration is an integer.

    Args:
        machines:
            A list of machine ids that can perform the operation. If
            only one machine can perform the operation, it can be passed as
            an integer.
        duration:
            The time it takes to perform the operation.
        release_date:
            The earliest moment this operation can be scheduled to start.
            Defaults to ``0``.
        deadline:
            A hard cutoff time by which the job must be finished. A schedule
            is invalid if the job completes after this time. Defaults to
            ``None``.
        due_date:
            The target completion time for the job. Finishing late is allowed
            but incurs a penalty (e.g., tardiness). Defaults to ``None``.
    """

    __slots__ = {
        "machines": (
            "A list of machine ids that can perform the operation. If "
            "only one machine can perform the operation, it can be passed as "
            "an integer."
        ),
        "duration": (
            "The time it takes to perform the operation. Often referred"
            " to as the processing time."
        ),
        "release_date": (
            "The earliest moment this operation can be scheduled to start. "
            "Defaults to ``0``."
        ),
        "deadline": (
            "A hard cutoff time by which the job must be finished. A schedule "
            "is invalid if the job completes after this time. Defaults to "
            "``None``."
        ),
        "due_date": (
            "The target completion time for the job. Finishing late is "
            "allowed but incurs a penalty (e.g., tardiness). Defaults to "
            "``None``."
        ),
        "job_id": (
            "The id of the job the operation belongs to. Defaults to -1. "
            "It is usually set by the :class:`JobShopInstance` class after "
            "initialization."
        ),
        "position_in_job": (
            "The index of the operation in the job. Defaults to -1. "
            "It is usually set by the :class:`JobShopInstance` class after "
            "initialization."
        ),
        "operation_id": (
            "The id of the operation. This is unique within a "
            ":class:`JobShopInstance`. Defaults to -1. It is usually set by "
            "the :class:`JobShopInstance` class after initialization."
        ),
    }

    def __init__(
        self,
        machines: int | list[int],
        duration: int,
        release_date: int = 0,
        deadline: int | None = None,
        due_date: int | None = None,
    ):
        self.machines: list[int] = (
            [machines] if isinstance(machines, int) else machines
        )
        self.duration: int = duration
        self.release_date: int = release_date
        self.deadline: int | None = deadline
        self.due_date: int | None = due_date

        # Defined outside the class by the JobShopInstance class:
        self.job_id: int = -1
        self.position_in_job: int = -1
        self.operation_id: int = -1

    @property
    def machine_id(self) -> int:
        """Returns the id of the machine associated with the operation.

        Raises:
            UninitializedAttributeError:
                If the operation has multiple machines in its list.
        """
        if len(self.machines) > 1:
            raise ValidationError(
                "Operation has multiple machines. The `machine_id` property "
                "should only be used when working with a classic JSSP "
                "instance. This error prevents silent bugs. To handle "
                "operations with more machines you have to use the machines "
                "attribute. If you get this error using `job_shop_lib` "
                "objects, it means that that object does not support "
                "operations with multiple machines yet."
            )
        return self.machines[0]

    def is_initialized(self) -> bool:
        """Returns whether the operation has been initialized."""
        return (
            self.job_id != -1
            and self.position_in_job != -1
            and self.operation_id != -1
        )

    def __hash__(self) -> int:
        return hash(self.operation_id)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Operation):
            return False
        return (
            self.machines == value.machines
            and self.duration == value.duration
            and self.release_date == value.release_date
            and self.deadline == value.deadline
            and self.due_date == value.due_date
            and self.job_id == value.job_id
            and self.position_in_job == value.position_in_job
            and self.operation_id == value.operation_id
        )

    def __repr__(self) -> str:
        machines = (
            self.machines[0] if len(self.machines) == 1 else self.machines
        )
        return (
            f"O(m={machines}, d={self.duration}, "
            f"j={self.job_id}, p={self.position_in_job})"
        )
