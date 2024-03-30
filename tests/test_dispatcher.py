from job_shop_lib import Dispatcher, JobShopInstance
from job_shop_lib.solvers import DispatchingRuleSolver


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


def test_current_time(example_job_shop_instance: JobShopInstance):
    solver = DispatchingRuleSolver(dispatching_rule="mwkr")
    dispatcher = Dispatcher(example_job_shop_instance)
    current_times = [0, 0, 2, 9, 10, 10, 13, 13, 15]
    for i, current_time in enumerate(current_times):
        solver.step(dispatcher)
        assert (
            dispatcher.current_time() == current_time
        ), f"Failed at iteration {i}."
