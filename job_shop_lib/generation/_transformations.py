"""Classes for generating transformed JobShopInstance objects."""

import abc
import copy
import random
from typing import Optional

from job_shop_lib import JobShopInstance, Operation


class Transformation(abc.ABC):
    """Base class for transformations applied to JobShopInstance objects."""

    def __init__(self, suffix: str = ""):
        self.suffix = suffix
        self.counter = 0

    @abc.abstractmethod
    def apply(self, instance: JobShopInstance) -> JobShopInstance:
        """Applies the transformation to a given JobShopInstance.

        Args:
            instance: The JobShopInstance to transform.

        Returns:
            A new JobShopInstance with the transformation applied.
        """

    def __call__(self, instance: JobShopInstance) -> JobShopInstance:
        instance = self.apply(instance)
        suffix = f"{self.suffix}_id={self.counter}"
        instance.name += suffix
        self.counter += 1
        return instance


# pylint: disable=too-few-public-methods
class RemoveMachines(Transformation):
    """Removes operations associated with randomly selected machines until
    there are exactly num_machines machines left."""

    def __init__(self, num_machines: int, suffix: Optional[str] = None):
        if suffix is None:
            suffix = f"_machines={num_machines}"
        super().__init__(suffix=suffix)
        self.num_machines = num_machines

    def apply(self, instance: JobShopInstance) -> JobShopInstance:
        if instance.num_machines <= self.num_machines:
            return instance  # No need to remove machines

        # Select machine indices to keep
        machines_to_keep = set(
            random.sample(range(instance.num_machines), self.num_machines)
        )

        # Re-index machines
        machine_reindex_map = {
            old_id: new_id
            for new_id, old_id in enumerate(sorted(machines_to_keep))
        }

        new_jobs = []
        for job in instance.jobs:
            # Keep operations whose machine_id is in machines_to_keep and
            # re-index them
            new_jobs.append(
                [
                    Operation(machine_reindex_map[op.machine_id], op.duration)
                    for op in job
                    if op.machine_id in machines_to_keep
                ]
            )

        return JobShopInstance(new_jobs, instance.name)


# pylint: disable=too-few-public-methods
class AddDurationNoise(Transformation):
    """Adds uniform integer noise to operation durations."""

    def __init__(
        self,
        min_duration: int = 1,
        max_duration: int = 100,
        noise_level: int = 10,
        suffix: Optional[str] = None,
    ):
        if suffix is None:
            suffix = f"_noise={noise_level}"
        super().__init__(suffix=suffix)
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.noise_level = noise_level

    def apply(self, instance: JobShopInstance) -> JobShopInstance:
        new_jobs = []
        for job in instance.jobs:
            new_job = []
            for op in job:
                noise = random.randint(-self.noise_level, self.noise_level)
                new_duration = max(
                    self.min_duration,
                    min(self.max_duration, op.duration + noise),
                )

                new_job.append(Operation(op.machine_id, new_duration))
            new_jobs.append(new_job)

        return JobShopInstance(new_jobs, instance.name)


class RemoveJobs(Transformation):
    """Removes jobs randomly until the number of jobs is within a specified
    range.

    Args:
        min_jobs:
            The minimum number of jobs to remain in the instance.
        max_jobs:
            The maximum number of jobs to remain in the instance.
        target_jobs:
            If specified, the number of jobs to remain in the
            instance. Overrides ``min_jobs`` and ``max_jobs``.
    """

    def __init__(
        self,
        min_jobs: int,
        max_jobs: int,
        target_jobs: Optional[int] = None,
        suffix: Optional[str] = None,
    ):
        if suffix is None:
            suffix = f"_jobs={min_jobs}-{max_jobs}"
        super().__init__(suffix=suffix)
        self.min_jobs = min_jobs
        self.max_jobs = max_jobs
        self.target_jobs = target_jobs

    def apply(self, instance: JobShopInstance) -> JobShopInstance:
        if self.target_jobs is None:
            target_jobs = random.randint(self.min_jobs, self.max_jobs)
        else:
            target_jobs = self.target_jobs
        new_jobs = copy.deepcopy(instance.jobs)

        while len(new_jobs) > target_jobs:
            new_jobs.pop(random.randint(0, len(new_jobs) - 1))

        return JobShopInstance(new_jobs, instance.name)

    @staticmethod
    def remove_job(
        instance: JobShopInstance, job_index: int
    ) -> JobShopInstance:
        """Removes a specific job from the instance.

        Args:
            instance: The JobShopInstance from which to remove the job.
            job_index: The index of the job to remove.

        Returns:
            A new JobShopInstance with the specified job removed.
        """
        new_jobs = copy.deepcopy(instance.jobs)
        new_jobs.pop(job_index)
        return JobShopInstance(new_jobs, instance.name)
