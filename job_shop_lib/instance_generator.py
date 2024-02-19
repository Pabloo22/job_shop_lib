import random
from typing import Optional, Iterator

from job_shop_lib import JobShopInstance, Operation


class InstanceGenerator:  # pylint: disable=too-many-instance-attributes
    """Generates job shop instances with random operations.

    The number of operations per job is the same as the number of machines,
    and there is no recirculation of machines. The duration of each operation
    is a random integer between `min_duration` and `max_duration`.
    The minimum number of machines is the same as the number of jobs.

    Useful for generating instances with similar characteristics to most
    benchmark ones.

    This class has many attributes and arguments to avoid having
    to create many different classes for different types of instances.
    This class should be general enough to cover most use cases.

    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        num_jobs: int | tuple[int, int] = (10, 20),
        num_machines: int | tuple[int, int] = (5, 10),
        duration_range: tuple[int, int] = (1, 99),
        allow_less_jobs_than_machines: bool = True,
        allow_recirculation: bool = False,
        machines_per_operation: int | tuple[int, int] = 1,
        name_suffix: str = "classic_generated_instance",
        seed: Optional[int] = None,
        iteration_limit: Optional[int] = None,
    ):
        if isinstance(num_jobs, int):
            num_jobs = (num_jobs, num_jobs)

        if isinstance(num_machines, int):
            num_machines = (num_machines, num_machines)

        if isinstance(machines_per_operation, int):
            machines_per_operation = (
                machines_per_operation,
                machines_per_operation,
            )

        self.num_jobs_range = num_jobs
        self.duration_range = duration_range
        self.num_machines_range = num_machines
        self.machines_per_operation = machines_per_operation

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
                operation = self.create_random_operation(available_machines)
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

    def create_random_operation(
        self, available_machines: Optional[list[int]] = None
    ) -> Operation:
        duration = random.randint(*self.duration_range)

        if self.machines_per_operation[1] > 1:
            machines = self._choose_multiple_machines()
            return Operation(machines=machines, duration=duration)

        machine_id = self._choose_one_machine(available_machines)
        return Operation(machines=machine_id, duration=duration)

    def _choose_multiple_machines(self) -> list[int]:
        num_machines = random.randint(*self.machines_per_operation)
        available_machines = list(range(num_machines))
        machines = []
        for _ in range(num_machines):
            machine = random.choice(available_machines)
            machines.append(machine)
            available_machines.remove(machine)
        return machines

    def _choose_one_machine(
        self, available_machines: Optional[list[int]] = None
    ) -> int:
        if available_machines is None:
            _, max_num_machines = self.num_machines_range
            available_machines = list(range(max_num_machines))

        machine_id = random.choice(available_machines)
        if not self.allow_recirculation:
            available_machines.remove(machine_id)

        return machine_id

    def _get_name(self) -> str:
        self._counter += 1
        return f"{self.name_suffix}_{self._counter}"
