import pytest

from job_shop_lib.benchmarking import load_benchmark_instance
from job_shop_lib.metaheuristics import (
    JobShopAnnealer,
    SimulatedAnnealingSolver,
    swap_adjacent_operations,
    swap_random_operations,
)
from job_shop_lib import Schedule
from job_shop_lib.exceptions import ValidationError


# Basic Functionality Test
def test_basic_functionality(instance_with_release_dates_and_deadlines):
    solver = SimulatedAnnealingSolver(initial_temperature=100, steps=100)
    schedule = solver.solve(instance_with_release_dates_and_deadlines)

    assert isinstance(schedule, Schedule)
    assert schedule.instance == instance_with_release_dates_and_deadlines
    assert (
        len(schedule.schedule)
        == instance_with_release_dates_and_deadlines.num_machines
    )

    # Check that all operations are scheduled
    scheduled_ops = sum(len(m) for m in schedule.schedule)
    total_ops = sum(
        len(job) for job in instance_with_release_dates_and_deadlines.jobs
    )
    assert scheduled_ops == total_ops


# Initialization Test
def test_initialization(instance_with_release_dates_and_deadlines):
    # Create a custom initial state
    initial_state_seq = [
        [0, 1],  # Machine 0: Job0 then Job1
        [0, 1],  # Machine 1: Job0 then Job1
    ]
    initial_state = Schedule.from_job_sequences(
        instance_with_release_dates_and_deadlines, initial_state_seq
    )
    annealer = JobShopAnnealer(
        instance_with_release_dates_and_deadlines,
        initial_state,
    )

    assert annealer.state == initial_state


# Deadlines constraint test
def test_deadlines_constraint(instance_with_release_dates_and_deadlines):

    solver = SimulatedAnnealingSolver(
        initial_temperature=1000,
        steps=5000,
        updates=0,
        seed=42,
    )
    schedule = solver.solve(instance_with_release_dates_and_deadlines)

    # Check last operation of each job completes before deadline
    for job_id, job in enumerate(
        instance_with_release_dates_and_deadlines.jobs
    ):
        last_op = job[-1]
        scheduled_op = next(
            op
            for machine_schedule in schedule.schedule
            for op in machine_schedule
            if op.operation == last_op
        )
        completion_time = scheduled_op.start_time + last_op.duration
        assert (
            completion_time <= last_op.deadline
        ), f"Job {job_id} last operation completes after deadline"


def test_solution_quality_and_seed():
    for i in range(10):
        ft06_instance = load_benchmark_instance("ft06")
        solver = SimulatedAnnealingSolver(
            seed=42,
            initial_temperature=10,
            steps=1000,
            updates=0,
        )

        schedule = solver.solve(ft06_instance)
        makespan = schedule.makespan()

        # For this seed and settings, we expect a makespan of 55
        assert (
            makespan == 55
        ), f"Failed at iteration {i}: Expected 55, got {makespan}"


def test_min_temperature_is_not_zero():
    """Ensure that the minimum temperature is not set to zero."""
    solver = SimulatedAnnealingSolver(
        initial_temperature=1000,
        ending_temperature=0,  # This should raise an error
        steps=1000,
    )
    with pytest.raises(
        ValidationError,
        match="Exponential cooling requires a minimum temperature greater "
        "than zero.",
    ):
        solver.solve(load_benchmark_instance("ft06"))


def test_with_adjacent_swap(ft06_instance):
    """Test the simulated annealing solver with adjacent job swaps."""
    for i in range(10):
        solver = SimulatedAnnealingSolver(
            seed=42,
            initial_temperature=10,
            steps=100,
            updates=0,
            neighbor_generator=swap_adjacent_operations,
        )
        schedule = solver.solve(ft06_instance)
        makespan = schedule.makespan()

        # For this seed and settings, we expect a makespan of 61
        assert (
            makespan == 61
        ), f"Failed at iteration {i}: Expected 61, got {makespan}"


def test_with_random_swap(ft06_instance):
    """Test the simulated annealing solver with random job swaps."""
    for i in range(10):
        solver = SimulatedAnnealingSolver(
            seed=42,
            initial_temperature=10,
            steps=10,
            updates=0,
            neighbor_generator=swap_random_operations,
        )
        schedule = solver.solve(ft06_instance)
        makespan = schedule.makespan()

        # For this seed and settings, we expect a makespan of 61
        assert (
            makespan == 61
        ), f"Failed at iteration {i}: Expected 61, got {makespan}"
