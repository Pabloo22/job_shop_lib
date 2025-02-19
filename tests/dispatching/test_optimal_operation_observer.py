# pylint: disable=missing-function-docstring, redefined-outer-name,
# pylint: disable=protected-access
import pytest

import random

from job_shop_lib import JobShopInstance, Operation, Schedule
from job_shop_lib.constraint_programming._ortools_solver import ORToolsSolver
from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching import OptimalOperationsObserver
from job_shop_lib.generation import GeneralInstanceGenerator


@pytest.fixture
def small_instance() -> JobShopInstance:
    # Create a small instance with 2 jobs and 2 operations each.
    jobs = [
        [Operation(0, 10), Operation(1, 20)],
        [Operation(1, 15), Operation(2, 10)],
    ]
    return JobShopInstance(jobs, "SmallInstance")


@pytest.fixture
def solved_schedule(small_instance: JobShopInstance):
    solver = ORToolsSolver(max_time_in_seconds=10, log_search_progress=False)
    return solver.solve(small_instance)


@pytest.fixture
def dispatcher(small_instance: JobShopInstance):
    return Dispatcher(small_instance)


@pytest.fixture
def optimal_observer(dispatcher: Dispatcher, solved_schedule):
    return OptimalOperationsObserver(dispatcher, solved_schedule)


def test_optimal_observer_small_instance(
    solved_schedule: Schedule,
    dispatcher: Dispatcher,
    optimal_observer: OptimalOperationsObserver,
):
    while not dispatcher.schedule.is_complete():
        optimal_ops = list(optimal_observer.optimal_available)
        optimal_op = random.choice(optimal_ops)
        dispatcher.dispatch(optimal_op)
    assert dispatcher.schedule.makespan() == solved_schedule.makespan()


def test_optimal_observer_with_random_instances():
    generator = GeneralInstanceGenerator(
        num_jobs=(3, 6),
        num_machines=(3, 6),
        iteration_limit=10,
    )
    for instance in generator:
        solver = ORToolsSolver(
            max_time_in_seconds=10, log_search_progress=False
        )
        solved_schedule = solver.solve(instance)
        dispatcher = Dispatcher(instance)
        optimal_observer = OptimalOperationsObserver(
            dispatcher, solved_schedule
        )
        while not dispatcher.schedule.is_complete():
            optimal_ops = list(optimal_observer.optimal_available)
            optimal_op = random.choice(optimal_ops)
            dispatcher.dispatch(optimal_op)
        assert dispatcher.schedule.makespan() == solved_schedule.makespan()


if __name__ == "__main__":
    pytest.main(["-vv", __file__])
