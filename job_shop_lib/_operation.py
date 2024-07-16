"""Home of the `Operation` class."""

from __future__ import annotations

from job_shop_lib.exceptions import UninitializedAttributeError


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

    Attributes:
        machines: A list of machine ids that can perform the operation.
        duration: The time it takes to perform the operation.
    """

    __slots__ = (
        "machines",
        "duration",
        "job_id",
        "position_in_job",
        "operation_id",
    )

    def __init__(self, machines: int | list[int], duration: int):
        """Initializes the object with the given machines and duration.

        Args:
            machines:
                A list of machine ids that can perform the operation. If
                only one machine can perform the operation, it can be passed as
                an integer.
            duration:
                The time it takes to perform the operation.
        """
        self.machines = [machines] if isinstance(machines, int) else machines
        self.duration = duration

        # Defined outside the class by the JobShopInstance class:
        self.job_id: int = -1
        self.position_in_job: int = -1
        self.operation_id: int = -1

    @property
    def machine_id(self) -> int:
        """Returns the id of the machine associated with the operation.

        Raises:
            UninitializedAttributeError: If the operation has multiple machines
            in its list.
        """
        if len(self.machines) > 1:
            raise UninitializedAttributeError(
                "Operation has multiple machines."
            )
        return self.machines[0]

    def is_initialized(self) -> bool:
        """Returns whether the operation has been initialized."""
        return (
            self.job_id == -1
            or self.position_in_job == -1
            or self.operation_id == -1
        )

    def __hash__(self) -> int:
        return hash(self.operation_id)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Operation):
            return False
        return self.__slots__ == value.__slots__

    def __repr__(self) -> str:
        machines = (
            self.machines[0] if len(self.machines) == 1 else self.machines
        )
        return (
            f"O(m={machines}, d={self.duration}, "
            f"j={self.job_id}, p={self.position_in_job})"
        )
