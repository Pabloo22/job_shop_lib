"""Contains factory functions for creating dispatching rules, machine choosers,
and pruning functions for the job shop scheduling problem.

The factory functions create and return the appropriate functions based on the
specified names or enums.
"""

from typing import Union, Dict
from enum import Enum
from collections.abc import Callable
import random

from job_shop_lib import Operation
from job_shop_lib.exceptions import ValidationError
from job_shop_lib.dispatching import Dispatcher


class MachineChooserType(str, Enum):
    """Enumeration of machine chooser strategies for the job shop scheduling"""

    FIRST = "first"
    RANDOM = "random"


MachineChooser = Callable[[Dispatcher, Operation], int]


def machine_chooser_factory(
    machine_chooser: Union[str, MachineChooser],
) -> MachineChooser:
    """Creates and returns a machine chooser function based on the specified
    machine chooser strategy name.

    The machine chooser function determines which machine an operation should
    be assigned to for execution. The selection can be based on different
    strategies such as choosing the first available machine or selecting a
    machine randomly.

    Args:
        machine_chooser: The name of the machine chooser strategy to be
            used. Supported values are 'first' and 'random'.

    Returns:
        A function that takes a :class:`~job_shop_lib.dispatching.Dispatcher`
        and an :class:`~job_shop_lib.Operation` as input
        and returns the index of the selected machine based on the specified
        machine chooser strategy.

    Raises:
        ValueError: If the machine_chooser argument is not recognized or is
            not supported.
    """
    machine_choosers: Dict[str, Callable[[Dispatcher, Operation], int]] = {
        MachineChooserType.FIRST: lambda _, operation: operation.machines[0],
        MachineChooserType.RANDOM: lambda _, operation: random.choice(
            operation.machines
        ),
    }

    if callable(machine_chooser):
        return machine_chooser

    machine_chooser = machine_chooser.lower()
    if machine_chooser not in machine_choosers:
        raise ValidationError(
            f"Machine chooser {machine_chooser} not recognized. Available "
            f"machine choosers: {', '.join(machine_choosers)}."
        )

    return machine_choosers[machine_chooser]
