import pytest

from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.dispatching import (
    Dispatcher,
    no_setup_time_calculator,
    get_matrix_setup_time_calculator,
    get_machine_dependent_setup_time_calculator,
    get_breakdown_calculator,
    get_job_dependent_setup_calculator,
    get_arrival_calculator,
)


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


def test_default_in_machine_setup_time_calculator(
    flexible_job_shop_instance2x2: JobShopInstance,
):
    setup_times = {0: 2}
    setup_calculator = get_machine_dependent_setup_time_calculator(
        setup_times, default=3
    )
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
    ) + 3 == dispatcher.start_time(job_1_op_2, 1)
    assert no_setup_time_calculator(
        dispatcher, job_2_op_2, 0
    ) + 2 == dispatcher.start_time(job_2_op_2, 0)


def test_get_setup_time_by_machine_calculator(
    flexible_job_shop_instance2x2: JobShopInstance,
):
    """Test the setup time by machine calculator."""
    setup_times = {0: 2, 1: 3}  # Machine 0 has 2 units setup, machine 1 has 3
    setup_calculator = get_machine_dependent_setup_time_calculator(setup_times)
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


def test_get_job_dependent_setup_calculator(
    flexible_job_shop_instance2x2: JobShopInstance,
):
    """Test the job-dependent setup time calculator."""
    setup_calculator = get_job_dependent_setup_calculator(
        same_job_setup=1, different_job_setup=3, initial_setup=1
    )
    dispatcher = Dispatcher(
        flexible_job_shop_instance2x2, start_time_calculator=setup_calculator
    )

    job_1_op_1 = flexible_job_shop_instance2x2.jobs[0][0]
    job_1_op_2 = flexible_job_shop_instance2x2.jobs[0][1]
    job_2_op_1 = flexible_job_shop_instance2x2.jobs[1][0]

    # Initial setup time should be 1
    assert dispatcher.start_time(job_1_op_1, 0) == 1
    assert dispatcher.start_time(job_1_op_1, 1) == 1
    assert dispatcher.start_time(job_2_op_1, 0) == 1
    assert dispatcher.start_time(job_2_op_1, 1) == 1

    # Same job setup time should be 1
    dispatcher.dispatch(job_1_op_1, 0)

    assert (
        dispatcher.start_time(job_1_op_2, 0)
        == no_setup_time_calculator(dispatcher, job_1_op_2, 0) + 1
    )

    # Different job setup time should be 3
    assert (
        dispatcher.start_time(job_2_op_1, 0)
        == no_setup_time_calculator(dispatcher, job_2_op_1, 0) + 3
    )


def test_get_arrival_calculator(
    flexible_job_shop_instance2x2: JobShopInstance,
):
    """Test the arrival time calculator."""

    # create arrival times matrix
    arrival_times = [
        [0, 5],  # Job0: operation0 arrives at 0, operation1 at 5
        [2, 10],  # Job1: operation0 arrives at 2, operation1 at 10
    ]

    # Test with the available arrival times matrix
    arrival_calculator = get_arrival_calculator(arrival_times)
    dispatcher = Dispatcher(
        flexible_job_shop_instance2x2, start_time_calculator=arrival_calculator
    )

    job0_op0 = flexible_job_shop_instance2x2.jobs[0][0]  # job_id=0, pos=0
    job0_op1 = flexible_job_shop_instance2x2.jobs[0][1]  # job_id=0, pos=1
    job1_op0 = flexible_job_shop_instance2x2.jobs[1][0]  # job_id=1, pos=0
    job1_op1 = flexible_job_shop_instance2x2.jobs[1][1]  # job_id=1, pos=1

    # check arrival times are respected
    assert (
        dispatcher.start_time(job0_op0, 0) == 0
    )  # Default=0, arrival=0 -> max=0
    assert (
        dispatcher.start_time(job1_op0, 1) == 2
    )  # Default=0, arrival=2 -> max=2
    assert (
        dispatcher.start_time(job0_op1, 0) == 5
    )  # Default=0, arrival=5 -> max=5
    assert (
        dispatcher.start_time(job1_op1, 1) == 10
    )  # Default=0, arrival=10->max=10

    # Test metadata fallback
    flexible_job_shop_instance2x2.metadata["arrival_times_matrix"] = (
        arrival_times
    )
    arrival_calculator_meta = get_arrival_calculator(None)

    dispatcher_meta = Dispatcher(
        flexible_job_shop_instance2x2,
        start_time_calculator=arrival_calculator_meta,
    )

    assert dispatcher_meta.start_time(job0_op0, 0) == 0
    assert dispatcher_meta.start_time(job1_op0, 1) == 2

    # Test no setup behavior
    del flexible_job_shop_instance2x2.metadata["arrival_times_matrix"]
    arrival_calculator_none = get_arrival_calculator(None)
    dispatcher_none = Dispatcher(
        flexible_job_shop_instance2x2,
        start_time_calculator=arrival_calculator_none,
    )

    default_start = no_setup_time_calculator(dispatcher_none, job0_op0, 0)
    assert dispatcher_none.start_time(job0_op0, 0) == default_start

    # Test max(default_start, arrival_time) behavior
    dispatcher_none.dispatch(job0_op0, 0)  # Start at 0, duration=3 → ends at 3
    assert dispatcher_none.start_time(job0_op1, 0) == 3


def test_get_arrival_calculator_machine_ready_time_later_than_arrival(
    flexible_job_shop_instance2x2: JobShopInstance,
):
    """Test the arrival time calculator when machine ready time is later than arrival."""
    arrival_times = [
        [0, 0],  # Job0: both operations available at time 0
        [0, 0],  # Job1: both operations available at time 0
    ]
    arrival_calculator = get_arrival_calculator(arrival_times)
    dispatcher = Dispatcher(
        flexible_job_shop_instance2x2, start_time_calculator=arrival_calculator
    )

    # Make machine 0 busy until time 10
    dispatcher.machine_next_available_time[0] = 10
    job0_op0 = flexible_job_shop_instance2x2.jobs[0][0]

    # Operation arrival=0 but machine ready=10 → start time=10
    assert dispatcher.start_time(job0_op0, 0) == 10


def test_get_arrival_calculator_numpy_array(
    flexible_job_shop_instance2x2: JobShopInstance,
):
    """Test that arrival calculator works with NumPy arrays."""
    import numpy as np

    arrival_times = np.array(
        [
            [0, 5],  # Job0: operation0 arrives at 0, operation1 at 5
            [2, 10],  # Job1: operation0 arrives at 2, operation1 at 10
        ]
    )

    arrival_calculator = get_arrival_calculator(arrival_times)
    dispatcher = Dispatcher(
        flexible_job_shop_instance2x2, start_time_calculator=arrival_calculator
    )

    job0_op0 = flexible_job_shop_instance2x2.jobs[0][0]
    job1_op0 = flexible_job_shop_instance2x2.jobs[1][0]

    # Check arrival times are respected
    assert dispatcher.start_time(job0_op0, 0) == 0
    assert dispatcher.start_time(job1_op0, 1) == 2


if __name__ == "__main__":
    pytest.main(["-vv", __file__])
