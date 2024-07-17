"""Home of the `BasicGenerator` class."""

import random

from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.exceptions import ValidationError
from job_shop_lib.generation import InstanceGenerator


class GeneralInstanceGenerator(InstanceGenerator):
    """Generates instances for job shop problems.

    This class is designed to be versatile, enabling the creation of various
    job shop instances without the need for multiple dedicated classes.

    It supports customization of the number of jobs, machines, operation
    durations, and more.

    The class supports both single instance generation and iteration over
    multiple instances, controlled by the `iteration_limit` parameter. It
    implements the iterator protocol, allowing it to be used in a `for` loop.

    Note:
        When used as an iterator, the generator will produce instances until it
        reaches the specified `iteration_limit`. If `iteration_limit` is None,
        it will continue indefinitely.

    Attributes:
        num_jobs_range:
            The range of the number of jobs to generate. If a single
            int is provided, it is used as both the minimum and maximum.
        duration_range:
            The range of durations for each operation.
        num_machines_range:
            The range of the number of machines available. If a
            single int is provided, it is used as both the minimum and maximum.
        machines_per_operation:
            Specifies how many machines each operation
            can be assigned to. If a single int is provided, it is used for
            all operations.
        allow_less_jobs_than_machines:
            If True, allows generating instances where the number of jobs is
            less than the number of machines.
        allow_recirculation:
            If True, a job can visit the same machine more than once.
        name_suffix:
            A suffix to append to each instance's name for identification.
        seed:
            Seed for the random number generator to ensure reproducibility.
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
        seed: int | None = None,
        iteration_limit: int | None = None,
    ):
        """Initializes the instance generator with the given parameters.

        Args:
            num_jobs:
                The range of the number of jobs to generate.
            num_machines:
                The range of the number of machines available.
            duration_range:
                The range of durations for each operation.
            allow_less_jobs_than_machines:
                Allows instances with fewer jobs than machines.
            allow_recirculation:
                Allows jobs to visit the same machine multiple times.
            machines_per_operation:
                Specifies how many machines each operation can be assigned to.
                If a single int is provided, it is used for all operations.
            name_suffix:
                Suffix for instance names.
            seed:
                Seed for the random number generator.
            iteration_limit:
                Maximum number of instances to generate in iteration mode.
        """
        super().__init__(
            num_jobs=num_jobs,
            num_machines=num_machines,
            duration_range=duration_range,
            name_suffix=name_suffix,
            seed=seed,
            iteration_limit=iteration_limit,
        )
        if isinstance(machines_per_operation, int):
            machines_per_operation = (
                machines_per_operation,
                machines_per_operation,
            )
        self.machines_per_operation = machines_per_operation

        self.allow_less_jobs_than_machines = allow_less_jobs_than_machines
        self.allow_recirculation = allow_recirculation
        self.name_suffix = name_suffix

        if seed is not None:
            random.seed(seed)

    def __repr__(self) -> str:
        return (
            f"GeneralInstanceGenerator("
            f"num_jobs_range={self.num_jobs_range}, "
            f"num_machines_range={self.num_machines_range}, "
            f"duration_range={self.duration_range})"
        )

    def generate(
        self, num_jobs: int | None = None, num_machines: int | None = None
    ) -> JobShopInstance:
        if num_jobs is None:
            num_jobs = random.randint(*self.num_jobs_range)

        if num_machines is None:
            min_num_machines, max_num_machines = self.num_machines_range
            if not self.allow_less_jobs_than_machines:
                min_num_machines = min(num_jobs, max_num_machines)
            num_machines = random.randint(min_num_machines, max_num_machines)
        elif (
            not self.allow_less_jobs_than_machines and num_jobs < num_machines
        ):
            raise ValidationError(
                "Theere are fewer jobs than machines, which is not allowed"
                "when `allow_less_jobs_than_machines` attribute is False."
            )

        jobs = []
        available_machines = list(range(num_machines))
        for _ in range(num_jobs):
            job = []
            for _ in range(num_machines):
                operation = self.create_random_operation(available_machines)
                job.append(operation)
            jobs.append(job)
            available_machines = list(range(num_machines))

        return JobShopInstance(jobs=jobs, name=self._next_name())

    def create_random_operation(
        self, available_machines: list[int] | None = None
    ) -> Operation:
        """Creates a random operation with the given available machines.

        Args:
            available_machines:
                A list of available machine_ids to choose from.
                If None, all machines are available.
        """
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
        self, available_machines: list[int] | None = None
    ) -> int:
        if available_machines is None:
            _, max_num_machines = self.num_machines_range
            available_machines = list(range(max_num_machines))

        machine_id = random.choice(available_machines)
        if not self.allow_recirculation:
            available_machines.remove(machine_id)

        return machine_id
