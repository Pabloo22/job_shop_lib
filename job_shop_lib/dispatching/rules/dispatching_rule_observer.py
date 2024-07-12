"""Home of the `DispatchingRule` class."""

from abc import abstractmethod
from job_shop_lib import Operation
from job_shop_lib.dispatching import (
    DispatcherObserver,
    Dispatcher,
    MachineChooser,
    MachineChooserType,
    machine_chooser_factory,
)


class DispatchingRuleObserver(DispatcherObserver):
    """Base class for dispatching rules.

    Dispatching rules are used to determine the order in which operations
    should be processed next on a particular machine when that machine becomes
    available.
    """

    def __init__(
        self,
        dispatcher: Dispatcher,
        *,
        subscribe: bool = True,
        machine_chooser: (
            str | MachineChooser | MachineChooserType
        ) = MachineChooserType.FIRST,
    ):
        super().__init__(dispatcher, subscribe=subscribe)
        self.machine_chooser = machine_chooser_factory(machine_chooser)

    @abstractmethod
    def select_action(self) -> tuple[Operation, int]:
        """Returns the selected operation and the ID of the machine
        where it should be dispatched."""

    def __call__(self) -> tuple[Operation, int]:
        return self.select_action()
