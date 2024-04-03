"""Contains the `JobShopInstance` class."""

from __future__ import annotations

import os
import functools
from typing import Any

from job_shop_lib import Operation


class JobShopInstance:
    """Data structure to store a Job Shop Scheduling Problem instance.

    Additional attributes such as `num_jobs` or `num_machines` can be computed
    from the instance and are cached for performance if they require expensive
    computations.

    Attributes:
        jobs:
            A list of lists of operations. Each list of operations represents
            a job, and the operations are ordered by their position in the job.
            The `job_id`, `position_in_job`, and `operation_id` attributes of
            the operations are set when the instance is created.
        name:
            A string with the name of the instance.
        metadata:
            A dictionary with additional information about the instance.
    """

    def __init__(
        self,
        jobs: list[list[Operation]],
        name: str = "JobShopInstance",
        **metadata: Any,
    ):
        """Initializes the instance based on a list of lists of operations.

        Args:
            jobs:
                A list of lists of operations. Each list of operations
                represents a job, and the operations are ordered by their
                position in the job. The `job_id`, `position_in_job`, and
                `operation_id` attributes of the operations are set when the
                instance is created.
            name:
                A string with the name of the instance.
            **metadata:
                Additional information about the instance.
        """
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

    @classmethod
    def from_taillard_file(
        cls,
        file_path: os.PathLike | str | bytes,
        encoding: str = "utf-8",
        comment_symbol: str = "#",
        name: str | None = None,
        **metadata: Any,
    ) -> JobShopInstance:
        """Creates a JobShopInstance from a file following Taillard's format.

        Args:
            file_path:
                A path-like object or string representing the path to the file.
            encoding:
                The encoding of the file.
            comment_symbol:
                A string representing the comment symbol used in the file.
                Lines starting with this symbol are ignored.
            name:
                A string with the name of the instance. If not provided, the
                name of the instance is set to the name of the file.
            **metadata:
                Additional information about the instance.

        Returns:
            A JobShopInstance object with the operations read from the file,
            and the name and metadata provided.
        """
        with open(file_path, "r", encoding=encoding) as file:
            lines = file.readlines()

        first_non_comment_line_reached = False
        jobs = []
        for line in lines:
            line = line.strip()
            if line.startswith(comment_symbol):
                continue
            if not first_non_comment_line_reached:
                first_non_comment_line_reached = True
                continue

            row = list(map(int, line.split()))
            pairs = zip(row[::2], row[1::2])
            operations = [
                Operation(machines=machine_id, duration=duration)
                for machine_id, duration in pairs
            ]
            jobs.append(operations)

        if name is None:
            name = os.path.basename(str(file_path))
            if "." in name:
                name = name.split(".")[0]
        return cls(jobs=jobs, name=name, **metadata)

    def to_dict(self) -> dict[str, Any]:
        """Returns a dictionary representation of the instance.

        This representation is useful for saving the instance to a JSON file,
        which is a more computer-friendly format than more traditional ones
        like Taillard's.

        Returns:
        The returned dictionary has the following structure:
        {
            "name": self.name,
            "duration_matrix": self.durations_matrix,
            "machines_matrix": self.machines_matrix,
            "metadata": self.metadata,
        }
        """
        return {
            "name": self.name,
            "duration_matrix": self.durations_matrix,
            "machines_matrix": self.machines_matrix,
            "metadata": self.metadata,
        }

    @classmethod
    def from_matrices(
        cls,
        duration_matrix: list[list[int]],
        machines_matrix: list[list[list[int]]] | list[list[int]],
        name: str = "JobShopInstance",
        metadata: dict[str, Any] | None = None,
    ) -> JobShopInstance:
        """Creates a JobShopInstance from duration and machines matrices.

        Args:
            duration_matrix:
                A list of lists of integers. The i-th list contains the
                durations of the operations of the job with id i.
            machines_matrix:
            A list of lists of lists of integers if the
                instance is flexible, or a list of lists of integers if the
                instance is not flexible. The i-th list contains the machines
                in which the operations of the job with id i can be processed.
            name:
                A string with the name of the instance.
            metadata:
                A dictionary with additional information about the instance.

        Returns:
            A JobShopInstance object.
        """
        jobs: list[list[Operation]] = [[] for _ in range(len(duration_matrix))]

        num_jobs = len(duration_matrix)
        for job_id in range(num_jobs):
            num_operations = len(duration_matrix[job_id])
            for position_in_job in range(num_operations):
                duration = duration_matrix[job_id][position_in_job]
                machines = machines_matrix[job_id][position_in_job]
                jobs[job_id].append(
                    Operation(duration=duration, machines=machines)
                )

        metadata = {} if metadata is None else metadata
        return cls(jobs=jobs, name=name, **metadata)

    def __repr__(self) -> str:
        return (
            f"JobShopInstance(name={self.name}, "
            f"num_jobs={self.num_jobs}, num_machines={self.num_machines})"
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, JobShopInstance):
            return False
        return self.jobs == other.jobs

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

        To access the machines of the operation with position i in the job
        with id j, the following code must be used:

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
    def operations_by_machine(self) -> list[list[Operation]]:
        """Returns a list of lists of operations.

        The i-th list contains the operations that can be processed in the
        machine with id i.
        """
        operations_by_machine: list[list[Operation]] = [
            [] for _ in range(self.num_machines)
        ]
        for job in self.jobs:
            for operation in job:
                for machine_id in operation.machines:
                    operations_by_machine[machine_id].append(operation)

        return operations_by_machine

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
        """Returns the sum of the durations of all operations in all jobs."""
        return sum(self.job_durations)
