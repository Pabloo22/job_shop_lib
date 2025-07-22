import pytest

from job_shop_lib import JobShopInstance
from job_shop_lib.dispatching import (
    Dispatcher,
    HistoryObserver,
)
from job_shop_lib.dispatching.rules import DispatchingRuleSolver
from job_shop_lib.exceptions import ValidationError


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
    # try to dispatch an operation that is not ready
    with pytest.raises(ValidationError):
        dispatcher.dispatch(job_3[2])
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

    assert (
        dispatcher.available_operations() == dispatcher.available_operations()
    )
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
    assert (
        dispatcher.available_operations() == dispatcher.available_operations()
    )
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


def test_is_ongoing(example_job_shop_instance: JobShopInstance):
    dispatcher = Dispatcher(example_job_shop_instance)

    job_0 = example_job_shop_instance.jobs[0]
    job_1 = example_job_shop_instance.jobs[1]
    job_2 = example_job_shop_instance.jobs[2]

    m0 = 0
    m1 = 1
    m2 = 2

    # Schedule some operations sequentially
    # job_1[0]: duration=1, starts at 0, ends at 1 on machine_1
    dispatcher.dispatch(job_0[0], m0)
    scheduled_op_1 = dispatcher.schedule.schedule[m0][-1]
    assert dispatcher.is_ongoing(scheduled_op_1)

    # dispatch job_0[0] and job_2[0] on machines 1 and 3 respectively
    dispatcher.dispatch(job_1[0], m1)
    scheduled_op_2 = dispatcher.schedule.schedule[m1][-1]
    assert dispatcher.is_ongoing(scheduled_op_2)

    dispatcher.dispatch(job_2[0], m2)
    scheduled_op_3 = dispatcher.schedule.schedule[m2][-1]
    assert dispatcher.is_ongoing(scheduled_op_2)
    assert not dispatcher.is_ongoing(scheduled_op_1)
    assert not dispatcher.is_ongoing(scheduled_op_3)


def test_next_operation(example_job_shop_instance: JobShopInstance):
    """Tests the next_operation method of the Dispatcher."""
    dispatcher = Dispatcher(example_job_shop_instance)

    # Initially, next_operation should return the first operation of each job
    assert dispatcher.next_operation(0) == example_job_shop_instance.jobs[0][0]
    assert dispatcher.next_operation(1) == example_job_shop_instance.jobs[1][0]
    assert dispatcher.next_operation(2) == example_job_shop_instance.jobs[2][0]

    # Dispatch the first operation of job 0
    dispatcher.dispatch(example_job_shop_instance.jobs[0][0], 0)

    # Now, next_operation for job 0 should return the second operation
    assert dispatcher.next_operation(0) == example_job_shop_instance.jobs[0][1]

    # Dispatch all operations of job 1
    dispatcher.dispatch(example_job_shop_instance.jobs[1][0], 1)
    dispatcher.dispatch(example_job_shop_instance.jobs[1][1], 2)
    dispatcher.dispatch(example_job_shop_instance.jobs[1][2], 0)

    # All operations for job 1 are scheduled, so it should raise an error.
    with pytest.raises(
        ValidationError,
        match="No more operations left for job 1 to schedule.",
    ):
        dispatcher.next_operation(1)


def test_subscribe_and_unsubscribe(example_job_shop_instance: JobShopInstance):
    """Tests the subscribe and unsubscribe methods of the Dispatcher."""
    dispatcher = Dispatcher(example_job_shop_instance)

    history_observer = HistoryObserver(dispatcher)
    assert len(dispatcher.subscribers) == 1
    dispatcher.unsubscribe(history_observer)
    assert len(dispatcher.subscribers) == 0


if __name__ == "__main__":
    pytest.main(["-vv", "tests/dispatching/test_dispatcher.py"])
