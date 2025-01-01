"""Contains the `JobShopInstance` class."""

from __future__ import annotations

import os
import functools
from typing import Any, List, Union, Dict

import numpy as np
from numpy.typing import NDArray

from job_shop_lib import Operation


class JobShopInstance:
    """Data structure to store a Job Shop Scheduling Problem instance.

    Additional attributes such as ``num_machines`` or ``durations_matrix`` can
    be computed from the instance and are cached for performance if they
    require expensive computations.

    Methods:

    .. autosummary::
        :nosignatures:

        from_taillard_file
        to_dict
        from_matrices
        set_operation_attributes

    Properties:

    .. autosummary::
        :nosignatures:

        num_jobs
        num_machines
        num_operations
        is_flexible
        durations_matrix
        machines_matrix
        durations_matrix_array
        machines_matrix_array
        operations_by_machine
        max_duration
        max_duration_per_job
        max_duration_per_machine
        job_durations
        machine_loads
        total_duration

    Attributes:
        jobs (List[List[Operation]]):
            A list of lists of operations. Each list of operations represents
            a job, and the operations are ordered by their position in the job.
            The ``job_id``, ``position_in_job``, and ``operation_id``
            attributes of the operations are set when the instance is created.
        name (str):
            A string with the name of the instance.
        metadata (Dict[str, Any]):
            A dictionary with additional information about the instance.

    Args:
        jobs:
            A list of lists of operations. Each list of operations
            represents a job, and the operations are ordered by their
            position in the job. The ``job_id``, ``position_in_job``, and
            ``operation_id`` attributes of the operations are set when the
            instance is created.
        name:
            A string with the name of the instance.
        set_operation_attributes:
            If True, the ``job_id``, ``position_in_job``, and ``operation_id``
            attributes of the operations are set when the instance is created.
            See :meth:`set_operation_attributes` for more information. Defaults
            to True.
        **metadata:
            Additional information about the instance.
    """

    def __init__(
        self,
        jobs: List[List[Operation]],
        name: str = "JobShopInstance",
        set_operation_attributes: bool = True,
        **metadata: Any,
    ):
        self.jobs: List[List[Operation]] = jobs
        if set_operation_attributes:
            self.set_operation_attributes()
        self.name: str = name
        self.metadata: Dict[str, Any] = metadata

    def set_operation_attributes(self):
        """Sets the ``job_id``, ``position_in_job``, and ``operation_id``
        attributes for each operation in the instance.

        The ``job_id`` attribute is set to the id of the job to which the
        operation belongs.

        The ``position_in_job`` attribute is set to the
        position of the operation in the job (starts from 0).

        The ``operation_id`` attribute is set to a unique identifier for the
        operation (starting from 0).

        The formula to compute the ``operation_id`` in a job shop instance with
        a fixed number of operations per job is:

        .. code-block:: python

            operation_id = job_id * num_operations_per_job + position_in_job

        """

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
        file_path: Union[os.PathLike, str, bytes],
        encoding: str = "utf-8",
        comment_symbol: str = "#",
        name: Union[str, None] = None,
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
            A :class:`JobShopInstance` object with the operations read from the
            file, and the name and metadata provided.
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

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dictionary representation of the instance.

        This representation is useful for saving the instance to a JSON file,
        which is a more computer-friendly format than more traditional ones
        like Taillard's.

        Returns:
            Dict[str, Any]: The returned dictionary has the following
            structure:

            .. code-block:: python

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
        duration_matrix: List[List[int]],
        machines_matrix: List[List[List[int]]] | List[List[int]],
        name: str = "JobShopInstance",
        metadata: Dict[str, Any] | None = None,
    ) -> JobShopInstance:
        """Creates a :class:`JobShopInstance` from duration and machines
        matrices.

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
            A :class:`JobShopInstance` object.
        """
        jobs: List[List[Operation]] = [[] for _ in range(len(duration_matrix))]

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
        """Returns ``True`` if any operation has more than one machine."""
        return any(
            any(len(operation.machines) > 1 for operation in job)
            for job in self.jobs
        )

    @functools.cached_property
    def durations_matrix(self) -> List[List[int]]:
        """Returns the duration matrix of the instance.

        The duration of the operation with ``job_id`` i and ``position_in_job``
        j is stored in the i-th position of the j-th list of the returned
        matrix:

        .. code-block:: python

            duration = instance.durations_matrix[i][j]

        """
        return [[operation.duration for operation in job] for job in self.jobs]

    @functools.cached_property
    def machines_matrix(self) -> Union[List[List[List[int]]], List[List[int]]]:
        """Returns the machines matrix of the instance.

        If the instance is flexible (i.e., if any operation has more than one
        machine in which it can be processed), the returned matrix is a list of
        lists of lists of integers.

        Otherwise, the returned matrix is a list of lists of integers.

        To access the machines of the operation with position i in the job
        with id j, the following code must be used:

        .. code-block:: python

            machines = instance.machines_matrix[j][i]

        """
        if self.is_flexible:
            return [
                [operation.machines for operation in job] for job in self.jobs
            ]
        return [
            [operation.machine_id for operation in job] for job in self.jobs
        ]

    @functools.cached_property
    def durations_matrix_array(self) -> NDArray[np.float32]:
        """Returns the duration matrix of the instance as a numpy array.

        The returned array has shape (``num_jobs``,
        ``max_num_operations_per_job``).
        Non-existing operations are filled with ``np.nan``.

        Example:
            >>> jobs = [[Operation(0, 2), Operation(1, 3)], [Operation(0, 4)]]
            >>> instance = JobShopInstance(jobs)
            >>> instance.durations_matrix_array
            array([[ 2.,  3.],
                   [ 4., nan]], dtype=float32)
        """
        duration_matrix = self.durations_matrix
        return self._fill_matrix_with_nans_2d(duration_matrix)

    @functools.cached_property
    def machines_matrix_array(self) -> NDArray[np.float32]:
        """Returns the machines matrix of the instance as a numpy array.

        The returned array has shape (``num_jobs``,
        ``max_num_operations_per_job``, ``max_num_machines_per_operation``).
        Non-existing machines are filled with ``np.nan``.

        Example:
            >>> jobs = [
            ...     [Operation([0, 1], 2), Operation(1, 3)], [Operation(0, 6)]
            ... ]
            >>> instance = JobShopInstance(jobs)
            >>> instance.machines_matrix_array
            array([[[ 0.,  1.],
                    [ 1., nan]],
                   [[ 0., nan],
                    [nan, nan]]], dtype=float32)
        """

        machines_matrix = self.machines_matrix
        if self.is_flexible:
            # False positive from mypy, the type of machines_matrix is
            # List[List[List[int]]] here
            return self._fill_matrix_with_nans_3d(
                machines_matrix  # type: ignore[arg-type]
            )

        # False positive from mypy, the type of machines_matrix is
        # List[List[int]] here
        return self._fill_matrix_with_nans_2d(
            machines_matrix  # type: ignore[arg-type]
        )

    @functools.cached_property
    def operations_by_machine(self) -> List[List[Operation]]:
        """Returns a list of lists of operations.

        The i-th list contains the operations that can be processed in the
        machine with id i.
        """
        operations_by_machine: List[List[Operation]] = [
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
    def max_duration_per_job(self) -> List[float]:
        """Returns the maximum duration of each job in the instance.

        The maximum duration of the job with id i is stored in the i-th
        position of the returned list.

        Useful for normalizing the durations of the operations.
        """
        return [max(op.duration for op in job) for job in self.jobs]

    @functools.cached_property
    def max_duration_per_machine(self) -> List[int]:
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
    def job_durations(self) -> List[int]:
        """Returns a list with the duration of each job in the instance.

        The duration of a job is the sum of the durations of its operations.

        The duration of the job with id i is stored in the i-th position of the
        returned list.
        """
        return [sum(op.duration for op in job) for job in self.jobs]

    @functools.cached_property
    def machine_loads(self) -> List[int]:
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

    @staticmethod
    def _fill_matrix_with_nans_2d(
        matrix: List[List[int]],
    ) -> NDArray[np.float32]:
        """Fills a matrix with ``np.nan`` values.

        Args:
            matrix:
                A list of lists of integers.

        Returns:
            A numpy array with the same shape as the input matrix, filled with
            ``np.nan`` values.
        """
        max_length = max(len(row) for row in matrix)
        squared_matrix = np.full(
            (len(matrix), max_length), np.nan, dtype=np.float32
        )
        for i, row in enumerate(matrix):
            squared_matrix[i, : len(row)] = row
        return squared_matrix

    @staticmethod
    def _fill_matrix_with_nans_3d(
        matrix: List[List[List[int]]],
    ) -> NDArray[np.float32]:
        """Fills a 3D matrix with ``np.nan`` values.

        Args:
            matrix:
                A list of lists of lists of integers.

        Returns:
            A numpy array with the same shape as the input matrix, filled with
            ``np.nan`` values.
        """
        max_length = max(len(row) for row in matrix)
        max_inner_length = len(matrix[0][0])
        for row in matrix:
            for inner_row in row:
                max_inner_length = max(max_inner_length, len(inner_row))
        squared_matrix = np.full(
            (len(matrix), max_length, max_inner_length),
            np.nan,
            dtype=np.float32,
        )
        for i, row in enumerate(matrix):
            for j, inner_row in enumerate(row):
                squared_matrix[i, j, : len(inner_row)] = inner_row
        return squared_matrix


if __name__ == "__main__":
    import doctest

    doctest.testmod()
