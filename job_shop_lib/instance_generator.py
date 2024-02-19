import random
from typing import Optional, Iterator

from job_shop_lib import JobShopInstance, Operation


class InstanceGenerator:  # pylint: disable=too-many-instance-attributes
    """Generates classic job shop instances with random operations.

    The number of operations per job is the same as the number of machines,
    and there is no recirculation of machines. The duration of each operation
    is a random integer between `min_duration` and `max_duration`.
    The minimum number of machines is the same as the number of jobs.

    Useful for generating instances with similar characteristics to most
    benchmark ones.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        num_jobs: int | tuple[int, int] = (10, 20),
        num_machines: int | tuple[int, int] = (5, 10),
        duration_range: tuple[int, int] = (1, 99),
        allow_less_jobs_than_machines: bool = True,
        allow_recirculation: bool = False,
        name_suffix: str = "classic_generated_instance",
        seed: Optional[int] = None,
        iteration_limit: Optional[int] = None,
    ):
        if isinstance(num_jobs, int):
            num_jobs = (num_jobs, num_jobs)
        self.num_jobs_range = num_jobs

        if isinstance(num_machines, int):
            num_machines = (num_machines, num_machines)
        self.num_machines_range = num_machines
        self.duration_range = duration_range

        self.allow_less_jobs_than_machines = allow_less_jobs_than_machines
        self.allow_recirculation = allow_recirculation

        self.name_suffix = name_suffix

        self._counter = 0
        self._current_iteration = 0
        self._iteration_limit = iteration_limit

        if seed is not None:
            random.seed(seed)

    def generate(self) -> JobShopInstance:
        num_jobs = random.randint(*self.num_jobs_range)

        min_num_machines, max_num_machines = self.num_machines_range
        if not self.allow_less_jobs_than_machines:
            min_num_machines = min(num_jobs, max_num_machines)

        num_machines = random.randint(min_num_machines, max_num_machines)

        jobs = []
        available_machines = list(range(num_machines))
        for _ in range(num_jobs):
            job = []
            for _ in range(num_machines):
                operation = self._create_random_operation(available_machines)
                job.append(operation)
            jobs.append(job)
            available_machines = list(range(num_machines))

        return JobShopInstance(jobs=jobs, name=self._get_name())

    def __iter__(self) -> Iterator[JobShopInstance]:
        self._current_iteration = 0
        return self

    def __next__(self) -> JobShopInstance:
        if (
            self._iteration_limit is not None
            and self._current_iteration >= self._iteration_limit
        ):
            raise StopIteration
        self._current_iteration += 1
        return self.generate()

    def _create_random_operation(
        self, available_machines: list[int]
    ) -> Operation:
        machine_id = random.choice(available_machines)
        if not self.allow_recirculation:
            available_machines.remove(machine_id)
        duration = random.randint(*self.duration_range)
        return Operation(machines=machine_id, duration=duration)

    def _get_name(self) -> str:
        self._counter += 1
        return f"{self.name_suffix}_{self._counter}"
