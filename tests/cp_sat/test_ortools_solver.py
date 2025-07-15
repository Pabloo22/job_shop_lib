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

    # Verify each operation starts after its arrival time
    for job_index, job in enumerate(example_job_shop_instance.jobs):
        for op_index, operation in enumerate(job):
            scheduled_op = schedule.find_operation(operation)
            assert (
                scheduled_op.start_time >= arrival_times[job_index][op_index]
            )
