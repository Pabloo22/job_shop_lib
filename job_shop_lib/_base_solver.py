"""Type hint and base class for all solvers."""

import abc
from typing import Callable
import time

from job_shop_lib import JobShopInstance, Schedule


# Every solver should be a callable that takes a JobShopInstance and returns a
# Schedule.
Solver = Callable[[JobShopInstance], Schedule]


class BaseSolver(abc.ABC):
    """Base class for all solvers implemented as classes.

    A `Solver` is any `Callable` that takes a `JobShopInstance` and returns a
    `Schedule`. Therefore, solvers can be implemented as functions or as
    classes. This class is provided as a base class for solvers implemented as
    classes. It provides a default implementation of the `__call__` method that
    measures the time taken to solve the instance and stores it in the
    schedule's metadata under the key "elapsed_time" if it is not already
    present.
    """

    @abc.abstractmethod
    def solve(self, instance: JobShopInstance) -> Schedule:
        """Solves the given job shop instance and returns the schedule."""

    def __call__(self, instance: JobShopInstance) -> Schedule:
        time_start = time.perf_counter()
        schedule = self.solve(instance)
        elapsed_time = time_start - time.perf_counter()
        schedule.metadata["elapsed_time"] = elapsed_time
        schedule.metadata["solved_by"] = self.__class__.__name__
        return schedule
