"""Contains the JobShopInstance and Operation classes."""

import functools
from typing import Any

from job_shop_lib import Operation


class JobShopInstance:
    """Data structure which stores a Job Shop Scheduling Problem instance."""

    def __init__(
        self,
        jobs: list[list[Operation]],
        name: str = "JobShopInstance",
        **metadata: Any,
    ):
        self.jobs = jobs
        self.set_operation_attributes()
        self.name = name
        self.metadata = metadata

    def set_operation_attributes(self):
        """Sets the job_id and position of each operation."""
        operation_id = 0
        for job_id, job in enumerate(self.jobs):
            for position, operation in enumerate(job):
                operation.job_id = job_id
                operation.position_in_job = position
                operation.operation_id = operation_id
                operation_id += 1

    @property
    def num_jobs(self) -> int:
        """Returns the number of jobs in the instance."""
        return len(self.jobs)

    @functools.cached_property
    def num_machines(self) -> int:
        """Returns the number of machines in the instance.

        Computed as the maximum machine id present in the instance plus one.
        """
        max_machine_id = -1
        for job in self.jobs:
            for operation in job:
                max_machine_id = max(max_machine_id, *operation.machines)
        return max_machine_id + 1

    @functools.cached_property
    def num_operations(self) -> int:
        """Returns the number of operations in the instance."""
        return sum(len(job) for job in self.jobs)

    @functools.cached_property
    def is_flexible(self) -> bool:
        """Returns True if any operation has more than one machine."""
        return any(
            any(len(operation.machines) > 1 for operation in job)
            for job in self.jobs
        )

    @functools.cached_property
    def durations_matrix(self) -> list[list[int]]:
        """Returns the duration matrix of the instance.

        The duration of the operation with `job_id` i and `position_in_job` j
        is stored in the i-th position of the j-th list of the returned matrix:

        ```python
        duration = instance.durations_matrix[i][j]
        ```
        """
        return [[operation.duration for operation in job] for job in self.jobs]

    @functools.cached_property
    def machines_matrix(self) -> list[list[list[int]]] | list[list[int]]:
        """Returns the machines matrix of the instance.

        If the instance is flexible (i.e., if any operation has more than one
        machine in which it can be processed), the returned matrix is a list of
        lists of lists of integers.

        Otherwise, the returned matrix is a list of lists of integers.

        To access the machines of the operation with id i in the job with id j,
        the following code must be used:
        ```python
        machines = instance.machines_matrix[j][i]
        ```

        """
        if self.is_flexible:
            return [
                [operation.machines for operation in job] for job in self.jobs
            ]
        return [
            [operation.machine_id for operation in job] for job in self.jobs
        ]

    @functools.cached_property
    def max_duration(self) -> float:
        """Returns the maximum duration of the instance.

        Useful for normalizing the durations of the operations."""
        return max(
            max(operation.duration for operation in job) for job in self.jobs
        )

    @functools.cached_property
    def max_duration_per_job(self) -> list[float]:
        """Returns the maximum duration of each job in the instance.

        The maximum duration of the job with id i is stored in the i-th
        position of the returned list.

        Useful for normalizing the durations of the operations.
        """
        return [max(op.duration for op in job) for job in self.jobs]

    @functools.cached_property
    def max_duration_per_machine(self) -> list[int]:
        """Returns the maximum duration of each machine in the instance.

        The maximum duration of the machine with id i is stored in the i-th
        position of the returned list.

        Useful for normalizing the durations of the operations.
        """
        max_duration_per_machine = [0] * self.num_machines
        for job in self.jobs:
            for operation in job:
                for machine_id in operation.machines:
                    max_duration_per_machine[machine_id] = max(
                        max_duration_per_machine[machine_id],
                        operation.duration,
                    )
        return max_duration_per_machine

    @functools.cached_property
    def job_durations(self) -> list[int]:
        """Returns a list with the duration of each job in the instance.

        The duration of a job is the sum of the durations of its operations.

        The duration of the job with id i is stored in the i-th position of the
        returned list.
        """
        return [sum(op.duration for op in job) for job in self.jobs]

    @functools.cached_property
    def machine_loads(self) -> list[int]:
        """Returns the total machine load of each machine in the instance.

        The total machine load of a machine is the sum of the durations of the
        operations that can be processed in that machine.

        The total machine load of the machine with id i is stored in the i-th
        position of the returned list.
        """
        machine_times = [0] * self.num_machines
        for job in self.jobs:
            for operation in job:
                for machine_id in operation.machines:
                    machine_times[machine_id] += operation.duration

        return machine_times

    @functools.cached_property
    def total_duration(self) -> int:
        """Returns the total duration of the instance."""
        return sum(self.job_durations)
