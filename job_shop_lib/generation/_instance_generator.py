"""Home of the `InstanceGenerator` class."""

import abc

import random
from typing import Iterator, Optional, Tuple, Union

from job_shop_lib import JobShopInstance
from job_shop_lib.exceptions import UninitializedAttributeError


class InstanceGenerator(abc.ABC):
    """Common interface for all generators.

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
        name_suffix:
            A suffix to append to each instance's name for identification.
        seed:
            Seed for the random number generator to ensure reproducibility.

    Args:
        num_jobs:
            The range of the number of jobs to generate.
        num_machines:
            The range of the number of machines available.
        duration_range:
            The range of durations for each operation.
        name_suffix:
            Suffix for instance names.
        seed:
            Seed for the random number generator.
        iteration_limit:
            Maximum number of instances to generate in iteration mode.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        num_jobs: Union[int, Tuple[int, int]] = (10, 20),
        num_machines: Union[int, Tuple[int, int]] = (5, 10),
        duration_range: Tuple[int, int] = (1, 99),
        name_suffix: str = "generated_instance",
        seed: Optional[int] = None,
        iteration_limit: Optional[int] = None,
    ):
        if isinstance(num_jobs, int):
            num_jobs = (num_jobs, num_jobs)
        if isinstance(num_machines, int):
            num_machines = (num_machines, num_machines)
        if seed is not None:
            random.seed(seed)

        self.num_jobs_range = num_jobs
        self.num_machines_range = num_machines
        self.duration_range = duration_range
        self.name_suffix = name_suffix

        self._counter = 0
        self._current_iteration = 0
        self._iteration_limit = iteration_limit

    @abc.abstractmethod
    def generate(
        self,
        num_jobs: Optional[int] = None,
        num_machines: Optional[int] = None,
    ) -> JobShopInstance:
        """Generates a single job shop instance

        Args:
            num_jobs: The number of jobs to generate. If None, a random value
                within the specified range will be used.
            num_machines: The number of machines to generate. If None, a random
                value within the specified range will be used.
        """

    def _next_name(self) -> str:
        self._counter += 1
        return f"{self.name_suffix}_{self._counter}"

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

    def __len__(self) -> int:
        if self._iteration_limit is None:
            raise UninitializedAttributeError("Iteration limit is not set.")
        return self._iteration_limit

    @property
    def max_num_jobs(self) -> int:
        """Returns the maximum number of jobs that can be generated."""
        return self.num_jobs_range[1]

    @property
    def min_num_jobs(self) -> int:
        """Returns the minimum number of jobs that can be generated."""
        return self.num_jobs_range[0]

    @property
    def max_num_machines(self) -> int:
        """Returns the maximum number of machines that can be generated."""
        return self.num_machines_range[1]

    @property
    def min_num_machines(self) -> int:
        """Returns the minimum number of machines that can be generated."""
        return self.num_machines_range[0]
