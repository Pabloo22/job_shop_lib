"""Home of the `DispatchingRule` class."""

from abc import abstractmethod
from job_shop_lib import Operation
from job_shop_lib.dispatching import DispatcherObserver


class DispatchingRuleObserver(DispatcherObserver):
    """Base class for dispatching rules.

    Dispatching rules are used to determine the order in which operations
    should be processed next on a particular machine when that machine becomes
    available.
    """

    @abstractmethod
    def select_operation(self) -> Operation:
        """Returns the selected operation."""

    def __call__(self) -> tuple[Operation, int]:
        return self.select_operation()
