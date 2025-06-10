"""Tests for the start time calculator functionality in the Dispatcher class."""

import pytest

from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.dispatching import (
    Dispatcher,
    no_setup_time_calculator,
    get_matrix_setup_time_calculator,
    get_setup_time_by_machine_calculator,
    get_breakdown_calculator,
    get_job_dependent_setup_calculator,
)


def test_default_start_time_calculator(
    flexible_job_shop_instance2x2: JobShopInstance,
):
    """Test that the default start time calculation works when no calculator
    is provided."""
    dispatcher = Dispatcher(flexible_job_shop_instance2x2)

    # Schedule first operation
    job_1_op_1 = flexible_job_shop_instance2x2.jobs[0][0]
    dispatcher.dispatch(job_1_op_1, machine_id=0)

    # Check that the start time for the next operation is calculated correctly
    job_1_op_2 = flexible_job_shop_instance2x2.jobs[0][1]
    expected_start_time = max(
        dispatcher.machine_next_available_time[1],  # machine 1 availability
        dispatcher.job_next_available_time[0],  # job 0 availability
    )
    assert dispatcher.start_time(job_1_op_2, 1) == expected_start_time


def test_custom_start_time_calculator_basic(
    flexible_job_shop_instance2x2: JobShopInstance,
):
    """Test a basic custom start time calculator."""

    def custom_calculator(
        dispatcher: Dispatcher, operation: Operation, machine_id: int
    ) -> int:
        # Add a fixed setup time of 2 units to the default calculation
        default_start = max(
            dispatcher.machine_next_available_time[machine_id],
            dispatcher.job_next_available_time[operation.job_id],
        )
        return default_start + 2

    dispatcher = Dispatcher(
        flexible_job_shop_instance2x2, start_time_calculator=custom_calculator
    )

    # First operation should start at time 2 (0 + 2 setup time)
    job_1_op_1 = flexible_job_shop_instance2x2.jobs[0][0]
    assert dispatcher.start_time(job_1_op_1, 0) == 2

    # Dispatch the operation and check it was scheduled correctly
    dispatcher.dispatch(job_1_op_1, machine_id=0)
    scheduled_ops = dispatcher.scheduled_operations()
    assert len(scheduled_ops) == 1
    assert scheduled_ops[0].start_time == 2
    assert scheduled_ops[0].end_time == 5  # start_time + duration (2 + 3)


def test_machine_dependent_setup_time(
    flexible_job_shop_instance2x2: JobShopInstance,
):
    """Test setup times that depend on the machine."""

    def machine_setup_calculator(
        dispatcher: Dispatcher, operation: Operation, machine_id: int
    ) -> int:
        # Different setup times for different machines
        setup_times = {
            0: 5,
            1: 1,
        }  # Machine 0 has 5 units setup, machine 1 has 1 unit

        default_start = max(
            dispatcher.machine_next_available_time[machine_id],
            dispatcher.job_next_available_time[operation.job_id],
        )
        return default_start + setup_times.get(machine_id, 0)

    dispatcher = Dispatcher(
        flexible_job_shop_instance2x2,
        start_time_calculator=machine_setup_calculator,
    )

    job_1_op_1 = flexible_job_shop_instance2x2.jobs[0][0]  # Goes to machine 0
    job_2_op_1 = flexible_job_shop_instance2x2.jobs[1][0]  # Goes to machine 1

    # Machine 0 should have 5 units setup time
    assert dispatcher.start_time(job_1_op_1, 0) == 5

    # Machine 1 should have 1 unit setup time
    assert dispatcher.start_time(job_2_op_1, 1) == 1


def test_context_dependent_downtime(
    flexible_job_shop_instance2x2: JobShopInstance,
):
    """Test downtime that depends on the current schedule state."""

    def downtime_calculator(
        dispatcher: Dispatcher, operation: Operation, machine_id: int
    ) -> int:
        default_start = max(
            dispatcher.machine_next_available_time[machine_id],
            dispatcher.job_next_available_time[operation.job_id],
        )

        # Add downtime if the machine has been used before
        machine_schedule = dispatcher.schedule.schedule[machine_id]
        if len(machine_schedule) > 0:
            # Add 3 units of downtime between operations
            return default_start + 3

        return default_start

    dispatcher = Dispatcher(
        flexible_job_shop_instance2x2,
        start_time_calculator=downtime_calculator,
    )

    # First operation on machine 0 - no downtime
    job_1_op_1 = flexible_job_shop_instance2x2.jobs[0][0]
    assert dispatcher.start_time(job_1_op_1, 0) == 0
    dispatcher.dispatch(job_1_op_1, machine_id=0)

    # Second operation on machine 0 - should have downtime
    job_2_op_2 = flexible_job_shop_instance2x2.jobs[1][
        1
    ]  # Operation that can go to machine 0
    expected_start = (
        dispatcher.machine_next_available_time[0] + 3
    )  # machine availability + downtime
    assert dispatcher.start_time(job_2_op_2, 0) == expected_start


def test_machine_breakdown_simulation(
    flexible_job_shop_instance2x2: JobShopInstance,
):
    """Test simulating machine breakdowns that affect start times."""
    # Simulate machine 0 breaking down at time 2 for 4 time units
    breakdown_start = 2
    breakdown_duration = 4
    breakdown_end = breakdown_start + breakdown_duration

    def breakdown_calculator(
        dispatcher: Dispatcher, operation: Operation, machine_id: int
    ) -> int:
        default_start = max(
            dispatcher.machine_next_available_time[machine_id],
            dispatcher.job_next_available_time[operation.job_id],
        )

        # If this is machine 0 and the default start time overlaps with
        # breakdown
        if machine_id == 0 and default_start < breakdown_end:
            # Operation must start after breakdown ends
            return max(default_start, breakdown_end)

        return default_start

    dispatcher = Dispatcher(
        flexible_job_shop_instance2x2,
        start_time_calculator=breakdown_calculator,
    )

    # Schedule an operation that would normally start at time 0 but machine
    # breaks down
    job_1_op_1 = flexible_job_shop_instance2x2.jobs[0][0]
    dispatcher.dispatch(job_1_op_1, machine_id=0)

    # The operation should start after the breakdown ends
    scheduled_ops = dispatcher.scheduled_operations()
    assert scheduled_ops[0].start_time == breakdown_end


def test_start_time_calculator_with_ready_operations_filter(
    flexible_job_shop_instance2x2: JobShopInstance,
):
    """Test that start time calculator works together with ready operations
    filter."""

    def simple_setup_calculator(
        dispatcher: Dispatcher, operation: Operation, machine_id: int
    ) -> int:
        default_start = max(
            dispatcher.machine_next_available_time[machine_id],
            dispatcher.job_next_available_time[operation.job_id],
        )
        return default_start + 1  # Add 1 unit setup time

    dispatcher = Dispatcher(
        flexible_job_shop_instance2x2,
        start_time_calculator=simple_setup_calculator,
    )

    available_ops = dispatcher.available_operations()
    assert len(available_ops) > 0

    first_op = available_ops[0]
    if first_op.machines[0] == 0:
        machine_id = 0
    else:
        machine_id = first_op.machines[0]

    start_time = dispatcher.start_time(first_op, machine_id)
    assert start_time == 1  # 0 (default) + 1 (setup)


def test_none_start_time_calculator(
    flexible_job_shop_instance2x2: JobShopInstance,
):
    """Test that None start_time_calculator works (uses default behavior)."""
    dispatcher = Dispatcher(flexible_job_shop_instance2x2)

    job_1_op_1 = flexible_job_shop_instance2x2.jobs[0][0]

    # Should use default calculation
    expected_start_time = max(
        dispatcher.machine_next_available_time[0],
        dispatcher.job_next_available_time[0],
    )
    assert dispatcher.start_time(job_1_op_1, 0) == expected_start_time


def test_get_matrix_setup_time_calculator(
    flexible_job_shop_instance2x2: JobShopInstance,
):
    """Test the matrix setup time calculator."""

    setup_times = [
        [0, 0, 1, 2],  # O_11 = O_0 -> O_ij
        [0, 0, 3, 4],  # O_12 = O_1 -> O_ij
        [0, 0, 0, 0],  # O_21 = O_2 -> O_ij
        [0, 0, 0, 0],  # O_22 = O_3 -> O_ij
    ]
    setup_calculator = get_matrix_setup_time_calculator(setup_times)
    dispatcher = Dispatcher(
        flexible_job_shop_instance2x2, start_time_calculator=setup_calculator
    )
    job_1_op_1 = flexible_job_shop_instance2x2.jobs[0][0]
    job_2_op_1 = flexible_job_shop_instance2x2.jobs[1][0]
    job_2_op_2 = flexible_job_shop_instance2x2.jobs[1][1]
    job_1_op_2 = flexible_job_shop_instance2x2.jobs[0][1]

    # First operation should have no setup time
    assert dispatcher.start_time(job_1_op_1, 0) == 0
    assert dispatcher.start_time(job_1_op_2, 1) == 0
    dispatcher.dispatch(job_1_op_1, 0)
    dispatcher.dispatch(job_1_op_2, 1)
    # Second operation on different machine should have setup time

    # Machine 0: O_11 -> O_21 / O_11 -> O_21
    assert no_setup_time_calculator(  # O_12 -> O_21
        dispatcher, job_2_op_1, 0
    ) + 1 == dispatcher.start_time(job_2_op_1, 0)
    assert no_setup_time_calculator(  # O_12 -> O_22
        dispatcher, job_2_op_2, 0
    ) + 2 == dispatcher.start_time(job_2_op_2, 0)

    # Machine 1: O_12 -> O_21 / O_12 -> O_22
    assert no_setup_time_calculator(  # O_11 -> O_21
        dispatcher, job_2_op_1, 1
    ) + 3 == dispatcher.start_time(job_2_op_1, 1)
    assert no_setup_time_calculator(  # O_11 -> O_22
        dispatcher, job_2_op_2, 1
    ) + 4 == dispatcher.start_time(job_2_op_2, 1)


def test_get_setup_time_by_machine_calculator(
    flexible_job_shop_instance2x2: JobShopInstance,
):
    """Test the setup time by machine calculator."""
    setup_times = {0: 2, 1: 3}  # Machine 0 has 2 units setup, machine 1 has 3
    setup_calculator = get_setup_time_by_machine_calculator(setup_times)
    dispatcher = Dispatcher(
        flexible_job_shop_instance2x2, start_time_calculator=setup_calculator
    )

    job_1_op_1 = flexible_job_shop_instance2x2.jobs[0][0]
    job_2_op_1 = flexible_job_shop_instance2x2.jobs[1][0]
    job_1_op_2 = flexible_job_shop_instance2x2.jobs[0][1]
    job_2_op_2 = flexible_job_shop_instance2x2.jobs[1][1]

    # First operation should have setup time of 2 on machine 0
    assert dispatcher.start_time(job_1_op_1, 0) == 2

    # Second operation should have setup time of 3 on machine 1
    assert dispatcher.start_time(job_2_op_1, 1) == 3

    dispatcher.dispatch(job_1_op_1, 0)
    dispatcher.dispatch(job_2_op_1, 1)

    assert no_setup_time_calculator(
        dispatcher, job_1_op_2, 1
    ) + 3 == dispatcher.start_time(job_1_op_1, 1)
    assert no_setup_time_calculator(
        dispatcher, job_2_op_2, 0
    ) + 2 == dispatcher.start_time(job_2_op_2, 0)


def test_get_breakdown_calculator(
    flexible_job_shop_instance2x2: JobShopInstance,
):
    """Test the breakdown calculator."""
    breakdowns = {
        0: [(2, 3)],  # Machine 0 breaks down at time 2 for 3 time units
        1: [(5, 2)],  # Machine 1 breaks down at time 5 for 2 time units
    }
    breakdown_calculator = get_breakdown_calculator(breakdowns)
    dispatcher = Dispatcher(
        flexible_job_shop_instance2x2,
        start_time_calculator=breakdown_calculator,
    )

    job_1_op_1 = flexible_job_shop_instance2x2.jobs[0][0]  # d=3
    job_2_op_1 = flexible_job_shop_instance2x2.jobs[1][0]  # d=4

    # No breakdown:
    assert dispatcher.start_time(job_1_op_1, 1) == 0
    assert dispatcher.start_time(job_2_op_1, 1) == 0

    # With breakdown:
    assert dispatcher.start_time(job_1_op_1, 0) == 5
    dispatcher.dispatch(job_1_op_1, 1)
    assert dispatcher.start_time(job_2_op_1, 1) == 7  # after breakdown


if __name__ == "__main__":
    pytest.main(["-vv", __file__])
