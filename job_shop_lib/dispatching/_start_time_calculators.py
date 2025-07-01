"""Predefined start time calculator functions for the Dispatcher class.

This module contains commonly used start time calculators that can be used
with the Dispatcher class to implement different scheduling behaviors.
"""

from collections.abc import Sequence
import numpy as np
from numpy.typing import NDArray

from job_shop_lib import Operation
from job_shop_lib.dispatching import (
    Dispatcher,
    no_setup_time_calculator,
    StartTimeCalculator,
)


def get_matrix_setup_time_calculator(
    setup_times: Sequence[Sequence[int]] | NDArray[np.integer],
) -> StartTimeCalculator:
    """Returns a start time calculator that adds setup times based on a
    matrix of setup times.

    Args:
        setup_times:
            A 2D matrix where setup_times[i][j] is the setuptime
            for switching from operation ``i`` to operation ``j``. Here,
            ``i`` and ``j`` are operation's IDs.
    Returns:
        A start time calculator function that adds setup times based on the
        matrix.

    Example:
        >>> setup_calc = get_matrix_setup_time_calculator([[0, 2], [1, 0]])
        >>> dispatcher = Dispatcher(instance, start_time_calculator=setup_calc)
    """

    def calculator(
        dispatcher: Dispatcher, operation: Operation, machine_id: int
    ) -> int:
        default_start = no_setup_time_calculator(
            dispatcher, operation, machine_id
        )
        machine_schedule = dispatcher.schedule.schedule[machine_id]
        if not machine_schedule:
            return default_start

        last_operation = machine_schedule[-1].operation
        setup_time = setup_times[last_operation.operation_id][
            operation.operation_id
        ]

        return default_start + setup_time

    return calculator


def get_machine_dependent_setup_time_calculator(
    setup_times: dict[int, int], default: int = 0
):
    """Returns a start time calculator that adds setup times based on
    machine IDs.

    Args:
        setup_times:
            Dictionary mapping machine_id to setup time in time units.
        default:
            Default setup time to use if a machine_id is not found
            in the setup_times dictionary.

    Returns:
        A start time calculator function that adds setup times.

    Example:
        >>> setup_calc = get_machine_dependent_setup_time_calculator(
        ...     {0: 2, 1: 1, 2: 3}
        ... )
        >>> dispatcher = Dispatcher(instance, start_time_calculator=setup_calc)
    """

    def calculator(
        dispatcher: Dispatcher, operation: Operation, machine_id: int
    ) -> int:
        default_start = no_setup_time_calculator(
            dispatcher, operation, machine_id
        )
        setup_time = setup_times.get(machine_id, default)
        return default_start + setup_time

    return calculator


def get_breakdown_calculator(breakdowns: dict[int, list[tuple[int, int]]]):
    """Returns a start time calculator that accounts for machine breakdowns.

    This calculator adjusts the start time of an operation based on
    when the machine is expected to be down due to breakdowns, maintenance,
    holidays, etc.

    Args:
        breakdowns: Dictionary mapping machine_id to list of
                   (start_time, duration) tuples representing when
                   the machine breaks down.

    Returns:
        A start time calculator function that accounts for breakdowns.

    Example:
        >>> breakdown_calc = breakdown_calculator({0: [(5, 3)], 1: [(8, 2)]})
        >>> dispatcher = Dispatcher(instance,
        ...                        start_time_calculator=breakdown_calc)
    """

    def calculator(
        dispatcher: Dispatcher, operation: Operation, machine_id: int
    ) -> int:
        default_start = no_setup_time_calculator(
            dispatcher, operation, machine_id
        )
        if machine_id not in breakdowns:
            return default_start

        start_time = default_start
        for breakdown_start, breakdown_duration in breakdowns[machine_id]:
            breakdown_end = breakdown_start + breakdown_duration

            start_during_breakdown = (
                breakdown_start <= start_time < breakdown_end
            )
            completion_time = start_time + operation.duration
            run_into_breakdown = start_time < breakdown_start < completion_time
            if start_during_breakdown or run_into_breakdown:
                start_time = breakdown_end

        return start_time

    return calculator


def get_job_dependent_setup_calculator(
    same_job_setup: int = 0,
    different_job_setup: int = 4,
    initial_setup: int = 0,
):
    """Factory for a calculator with sequence-dependent setup times.

    This calculator determines setup time based on whether the current
    operation's job matches the job of the previously processed operation
    on the same machine.

    Args:
        same_job_setup:
            Setup time when the previous operation on the
            machine was from the same job.
        different_job_setup:
            Setup time when the previous operation
            on the machine was from a different job.
        initial_setup:
            Setup time for the first operation on a machine
            or if the machine is currently idle.

    Returns:
        A start time calculator function that applies
        sequence-dependent setup times.

    Example:
        >>> seq_dep_calc = sequence_dependent_setup_calculator(
        ...     same_job_setup=1, different_job_setup=4, initial_setup=1
        ... )
        >>> # Assuming 'instance' is a JobShopInstance
        >>> dispatcher = Dispatcher(
        ...     instance, start_time_calculator=seq_dep_calc
        ... )
    """

    def calculator(
        dispatcher: Dispatcher, operation: Operation, machine_id: int
    ) -> int:
        default_start = no_setup_time_calculator(
            dispatcher, operation, machine_id
        )
        machine_schedule = dispatcher.schedule.schedule[machine_id]
        if not machine_schedule:
            setup_time = initial_setup
        else:
            last_operation_on_machine = machine_schedule[-1].operation
            if last_operation_on_machine.job_id == operation.job_id:
                setup_time = same_job_setup
            else:
                setup_time = different_job_setup

        return default_start + setup_time

    return calculator
