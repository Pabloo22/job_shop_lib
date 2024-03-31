"""Home of the Solver base class."""

import abc

from job_shop_lib import JobShopInstance, Schedule


class Solver(abc.ABC):
    """Base class for all solvers."""

    @abc.abstractmethod
    def solve(self, instance: JobShopInstance) -> Schedule:
        """Solves the job shop scheduling problem for the given instance.

        Args:
            instance: The job shop instance to be
                solved.

        Returns:
            The schedule of operations for the given instance.
        """

    def __call__(self, instance: JobShopInstance) -> Schedule:
        return self.solve(instance)
