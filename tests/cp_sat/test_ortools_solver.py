import pytest

from job_shop_lib.exceptions import NoSolutionFoundError
from job_shop_lib.constraint_programming import ORToolsSolver


def test_solve(example_job_shop_instance):
    solver = ORToolsSolver()
    schedule = solver.solve(example_job_shop_instance)
    assert schedule.makespan() == schedule.metadata["makespan"]
    assert schedule.metadata["makespan"] == 11
    assert schedule.metadata["status"] == "optimal"
    assert schedule.metadata["elapsed_time"] > 0


def test_solve_with_time_limit(example_job_shop_instance):
    solver = ORToolsSolver(max_time_in_seconds=0.000000001)

    with pytest.raises(NoSolutionFoundError):
        solver(example_job_shop_instance)


def test_solver_with_arrival_times(example_job_shop_instance):
    """Tests the CP Solver correctly handles arrival times constraints."""
    arrival_times = [
        [0, 2, 4],  # Job 0 operations
        [1, 3, 5],  # Job 1 operations
        [0, 1, 2],  # Job 2 operations
    ]

    solver = ORToolsSolver()
    schedule = solver.solve(
        example_job_shop_instance, arrival_times=arrival_times
    )

    # Build mapping from operation to start time
    operation_to_start = {}
    for machine_schedule in schedule.schedule:
        for scheduled_op in machine_schedule:
            operation_to_start[scheduled_op.operation] = (
                scheduled_op.start_time
            )

    # Verify each operation starts after its arrival time
    for job_index, job in enumerate(example_job_shop_instance.jobs):
        for op_index, operation in enumerate(job):
            start_time = operation_to_start[operation]
            assert start_time >= arrival_times[job_index][op_index]


def test_solver_with_deadlines(example_job_shop_instance):
    """Tests the CP Solver correctly handles deadlines constraints."""
    deadlines = [
        [10, 15, 20],  # Job 0 operations
        [8, 12, 15],  # Job 1 operations
        [5, 10, 15],  # Job 2 operations
    ]

    solver = ORToolsSolver()
    schedule = solver.solve(example_job_shop_instance, deadlines=deadlines)

    # Build mapping from operation to start time
    operation_to_start = {}
    for machine_schedule in schedule.schedule:
        for scheduled_op in machine_schedule:
            operation_to_start[scheduled_op.operation] = (
                scheduled_op.start_time
            )

    # Verify each operation finishes before its deadline
    for job_index, job in enumerate(example_job_shop_instance.jobs):
        for op_index, operation in enumerate(job):
            start_time = operation_to_start[operation]
            completion_time = start_time + operation.duration
            assert completion_time <= deadlines[job_index][op_index]


def test_solver_with_arrival_times_and_deadlines(example_job_shop_instance):
    """Tests the CP Solver with both arrival times and deadlines together."""
    arrival_times = [[0, 3, 6], [1, 4, 7], [0, 2, 4]]
    deadlines = [[10, 15, 20], [9, 14, 18], [8, 12, 16]]

    solver = ORToolsSolver()
    schedule = solver.solve(
        example_job_shop_instance,
        arrival_times=arrival_times,
        deadlines=deadlines,
    )

    # Build mapping from operation to start time
    operation_to_start = {}
    for machine_schedule in schedule.schedule:
        for scheduled_op in machine_schedule:
            operation_to_start[scheduled_op.operation] = (
                scheduled_op.start_time
            )

    # Verify constraints are satisfied
    for job_index, job in enumerate(example_job_shop_instance.jobs):
        for op_index, operation in enumerate(job):
            start_time = operation_to_start[operation]
            completion_time = start_time + operation.duration
            assert start_time >= arrival_times[job_index][op_index]
            assert completion_time <= deadlines[job_index][op_index]


def test_infeasible_constraints(minimal_infeasible_instance):
    """Tests the CP Solver raises an error for infeasible constraints."""
    arrival_times = [[0], [0]]
    deadlines = [[5], [5]]

    solver = ORToolsSolver()

    with pytest.raises(NoSolutionFoundError):
        solver.solve(
            minimal_infeasible_instance,
            arrival_times=arrival_times,
            deadlines=deadlines,
        )
