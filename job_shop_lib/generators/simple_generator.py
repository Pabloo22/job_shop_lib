import random
from typing import Optional

from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.generators import BaseGenerator


class ClassicGenerator(BaseGenerator):
    """Generates classic job shop instances with random operations.

    The number of operations per job is the same as the number of machines,
    and there is no recirculation of machines. The duration of each operation
    is a random integer between `min_duration` and `max_duration`.
    The minimum number of machines is the same as the number of jobs.

    Useful for generating instances with similar characteristics to most
    benchmark ones.
    """

    def __init__(
        self,
        max_duration: int,
        min_duration: int = 1,
        max_num_jobs: int = 20,
        min_num_jobs: int = 2,
        max_num_machines: int = 10,
        name_suffix: str = "classic_generated_instance",
        seed: Optional[int] = None,
        iteration_limit: Optional[int] = None,
    ):
        super().__init__(iteration_limit)

        self.max_num_jobs = max_num_jobs
        self.max_num_machines = max_num_machines
        self.max_duration = max_duration
        self.min_duration = min_duration
        self.min_num_jobs = min_num_jobs
        self.name_suffix = name_suffix
        self.counter = 0
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    def generate(
        self,
        num_jobs: Optional[int] = None,
        num_machines: Optional[int] = None,
    ) -> JobShopInstance:
        if num_jobs is None:
            num_jobs = random.randint(self.min_num_jobs, self.max_num_jobs)
        if num_machines is None:
            min_num_machines = min(num_jobs, self.max_num_machines)
            num_machines = random.randint(
                min_num_machines, self.max_num_machines
            )

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

    def _create_random_operation(
        self, available_machines: list[int]
    ) -> Operation:
        machine_id = random.choice(available_machines)
        available_machines.remove(machine_id)
        duration = random.randint(self.min_duration, self.max_duration)
        return Operation(machines=machine_id, duration=duration)

    def _get_name(self) -> str:
        self.counter += 1
        return f"{self.name_suffix}_{self.counter}"
