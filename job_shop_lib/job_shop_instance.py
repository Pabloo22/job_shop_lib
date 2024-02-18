"""Contains the JobShopInstance and Operation classes."""

from __future__ import annotations

import functools
from typing import Optional, Any

from job_shop_lib import Operation


class JobShopInstance:
    """Stores a classic job-shop scheduling problem instance."""

    def __init__(
        self,
        jobs: list[list[Operation]],
        name: str = "JobShopInstance",
        **metadata: Any,
    ):
        self.jobs = jobs
        self.set_operation_ids()
        self.name = name
        self.metadata = metadata

    def set_operation_ids(self):
        """Sets the job_id and position of each operation."""
        for job_id, job in enumerate(self.jobs):
            for position, operation in enumerate(job):
                operation.job_id = job_id
                operation.position = position

    # --- PROPERTIES ---
    @property
    def num_jobs(self) -> int:
        """Returns the number of jobs in the instance."""
        return len(self.jobs)

    @property
    def bounds(self) -> tuple[float | None, float | None]:
        """Returns the lower and upper bounds of the instance."""
        return self.lower_bound, self.upper_bound

    @property
    def upper_bound(self) -> Optional[float]:
        """Returns the upper bound of the instance."""
        return self.metadata.get("upper_bound")

    @property
    def lower_bound(self) -> Optional[float]:
        """Returns the lower bound of the instance."""
        return self.metadata.get("lower_bound")

    @property
    def optimum(self) -> Optional[float]:
        """Returns the optimum of the instance."""
        return self.metadata.get("optimum")

    @functools.cached_property
    def is_flexible(self) -> bool:
        """Returns True is any operation has more than one machine."""
        return any(
            len(operation.machines) > 1
            for job in self.jobs
            for operation in job
        )

    @functools.cached_property
    def durations_matrix(self) -> list[list[int]]:
        """Returns the duration matrix of the instance."""
        return [[operation.duration for operation in job] for job in self.jobs]

    @functools.cached_property
    def machines_matrix(self) -> list[list[list[int]]] | list[list[int]]:
        """Returns the machines matrix of the instance."""
        if self.is_flexible:
            return [
                [operation.machines for operation in job] for job in self.jobs
            ]
        return [
            [operation.machine_id for operation in job] for job in self.jobs
        ]

    @functools.cached_property
    def job_durations(self) -> list[float]:
        """Returns the duration of each job in the instance."""
        return [
            sum(operation.duration for operation in job) for job in self.jobs
        ]

    @functools.cached_property
    def total_duration(self) -> float:
        """Returns the total duration of the instance."""
        return sum(self.job_durations)

    @functools.cached_property
    def num_machines(self) -> int:
        """Returns the number of machines in the instance."""
        mx = 0
        for job in self.jobs:
            mx_machine = max(max(operation.machines) for operation in job)
            mx = max(mx, mx_machine)
        return mx + 1

    @functools.cached_property
    def num_operations(self) -> int:
        """Returns the number of operations in the instance."""
        return sum(len(job) for job in self.jobs)

    @functools.cached_property
    def max_duration(self) -> float:
        """Returns the maximum duration of the instance."""
        mx = 0
        for job in self.jobs:
            mx_duration = max(operation.duration for operation in job)
            mx = max(mx, mx_duration)
        return mx

    @functools.cached_property
    def max_job_duration(self) -> float:
        """Returns the maximum duration of a job in the instance."""
        return max(
            sum(operation.duration for operation in job) for job in self.jobs
        )

    @functools.cached_property
    def machine_loads(self) -> list[int]:
        """Returns the total duration of each machine in the instance."""
        machine_times = [0 for _ in range(self.num_machines)]
        for job in self.jobs:
            for operation in job:
                for machine_id in operation.machines:
                    machine_times[machine_id] += operation.duration
        return machine_times

    @functools.cached_property
    def max_machine_load(self) -> float:
        """Returns the maximum duration of a machine in the instance."""
        return max(self.machine_loads)

    @functools.cached_property
    def mean_machine_load(self) -> float:
        """Returns the mean duration of a machine in the instance."""
        return self.total_duration / self.num_machines

    # -------------------
