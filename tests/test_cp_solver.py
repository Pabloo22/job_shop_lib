import pytest

from job_shop_lib.solvers import CPSolver, NoSolutionFound


def test_solve(example_job_shop_instance):
    solver = CPSolver()
    schedule = solver.solve(example_job_shop_instance)
    assert schedule.makespan() == schedule.metadata["makespan"]
    assert schedule.metadata["status"] == "optimal"
    assert schedule.metadata["elapsed_time"] > 0


def test_solve_with_time_limit(example_job_shop_instance):
    solver = CPSolver(time_limit=0.000000001)

    with pytest.raises(NoSolutionFound):
        solver(example_job_shop_instance)
