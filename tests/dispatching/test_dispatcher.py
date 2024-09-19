import pytest

from job_shop_lib import JobShopInstance
from job_shop_lib.dispatching import (
    Dispatcher,
)
from job_shop_lib.dispatching.rules import DispatchingRuleSolver


def test_dispatch(example_job_shop_instance: JobShopInstance):
    dispatcher = Dispatcher(example_job_shop_instance)

    job_1 = example_job_shop_instance.jobs[0]
    job_2 = example_job_shop_instance.jobs[1]
    job_3 = example_job_shop_instance.jobs[2]

    machine_1 = 0
    machine_2 = 1
    machine_3 = 2

    dispatcher.dispatch(job_1[0], machine_1)
    dispatcher.dispatch(job_1[1], machine_2)
    dispatcher.dispatch(job_3[0], machine_3)
    dispatcher.dispatch(job_3[1], machine_1)
    dispatcher.dispatch(job_2[0], machine_2)
    dispatcher.dispatch(job_1[2], machine_3)
    dispatcher.dispatch(job_3[2], machine_2)
    dispatcher.dispatch(job_2[1], machine_3)
    dispatcher.dispatch(job_2[2], machine_1)

    assert dispatcher.schedule.makespan() == 11
    assert dispatcher.job_next_available_time == [9, 11, 9]
    assert dispatcher.machine_next_available_time == [11, 9, 10]
    assert dispatcher.job_next_operation_index == [3, 3, 3]


def test_reset(example_job_shop_instance: JobShopInstance):
    dispatcher = Dispatcher(example_job_shop_instance)

    job_1 = example_job_shop_instance.jobs[0]
    job_2 = example_job_shop_instance.jobs[1]
    job_3 = example_job_shop_instance.jobs[2]

    machine_1 = 0
    machine_2 = 1
    machine_3 = 2

    dispatcher.dispatch(job_1[0], machine_1)
    dispatcher.dispatch(job_1[1], machine_2)
    dispatcher.dispatch(job_3[0], machine_3)
    dispatcher.dispatch(job_3[1], machine_1)
    dispatcher.dispatch(job_2[0], machine_2)
    dispatcher.dispatch(job_1[2], machine_3)

    dispatcher.reset()

    assert dispatcher.schedule.makespan() == 0
    assert dispatcher.job_next_available_time == [0, 0, 0]
    assert dispatcher.machine_next_available_time == [0, 0, 0]
    assert dispatcher.job_next_operation_index == [0, 0, 0]


def test_is_operation_ready(example_job_shop_instance: JobShopInstance):
    dispatcher = Dispatcher(example_job_shop_instance)

    job_1 = example_job_shop_instance.jobs[0]
    job_2 = example_job_shop_instance.jobs[1]
    job_3 = example_job_shop_instance.jobs[2]

    machine_1 = 0
    machine_2 = 1
    machine_3 = 2

    dispatcher.dispatch(job_1[0], machine_1)
    dispatcher.dispatch(job_1[1], machine_2)
    dispatcher.dispatch(job_3[0], machine_3)
    dispatcher.dispatch(job_3[1], machine_1)
    dispatcher.dispatch(job_2[0], machine_2)

    assert not dispatcher.is_operation_ready(job_1[0])
    assert not dispatcher.is_operation_ready(job_1[1])
    assert dispatcher.is_operation_ready(job_1[2])

    assert not dispatcher.is_operation_ready(job_2[0])
    assert dispatcher.is_operation_ready(job_2[1])
    assert not dispatcher.is_operation_ready(job_2[2])

    assert not dispatcher.is_operation_ready(job_3[0])
    assert not dispatcher.is_operation_ready(job_3[1])
    assert dispatcher.is_operation_ready(job_3[2])


def test_cache(example_job_shop_instance: JobShopInstance):
    # pylint: disable=protected-access
    dispatcher = Dispatcher(example_job_shop_instance)

    assert dispatcher.current_time() == dispatcher.current_time()

    assert dispatcher.ready_operations() == dispatcher.ready_operations()
    assert (
        dispatcher.uncompleted_operations()
        == dispatcher.uncompleted_operations()
    )
    job_1 = example_job_shop_instance.jobs[0]
    job_3 = example_job_shop_instance.jobs[2]

    machine_1 = 0
    machine_2 = 1
    machine_3 = 2

    dispatcher.dispatch(job_1[0], machine_1)
    assert dispatcher.ready_operations() == dispatcher.ready_operations()
    dispatcher.dispatch(job_1[1], machine_2)
    dispatcher.dispatch(job_3[0], machine_3)
    assert (
        dispatcher.uncompleted_operations()
        == dispatcher.uncompleted_operations()
    )


def test_current_time(example_job_shop_instance: JobShopInstance):
    dispatcher = Dispatcher(example_job_shop_instance)
    assignments = [
        (0, 0, 0),
        (0, 1, 1),
        (1, 0, 1),
        (2, 0, 2),
        (0, 2, 2),
        (1, 1, 2),
        (2, 1, 0),
        (1, 2, 0),
        (2, 2, 1),
    ]
    current_times = [0, 0, 0, 1, 1, 1, 7, 7, 11]
    for i, current_time in enumerate(current_times):
        job_id, position_in_job, machine_id = assignments[i]
        operation = example_job_shop_instance.jobs[job_id][position_in_job]
        dispatcher.dispatch(operation, machine_id)
        assert dispatcher.current_time() == current_time


def test_unscheduled_operations(example_job_shop_instance: JobShopInstance):
    dispatcher = Dispatcher(example_job_shop_instance)
    solver = DispatchingRuleSolver(dispatching_rule="most_work_remaining")
    expected_uncompleted_operations = set()
    for job in example_job_shop_instance.jobs:
        for operation in job:
            expected_uncompleted_operations.add(operation)

    while not dispatcher.schedule.is_complete():
        assert (
            set(dispatcher.unscheduled_operations())
            == expected_uncompleted_operations
        )
        operation = solver.dispatching_rule(dispatcher)
        solver.step(dispatcher)
        expected_uncompleted_operations.remove(operation)

    assert (
        set(dispatcher.uncompleted_operations())
        == expected_uncompleted_operations
    )


if __name__ == "__main__":
    # Run current file with the following command:
    # python -m pytest tests/test_dispatcher.py
    pytest.main(["-vv", "tests/dispatching/test_dispatcher.py"])
