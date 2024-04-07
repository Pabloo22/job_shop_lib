import pytest

from job_shop_lib import Dispatcher, JobShopInstance
from job_shop_lib.solvers import DispatchingRuleSolver, DispatchingRule
from job_shop_lib.benchmarks import load_all_benchmark_instances


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
    solver = DispatchingRuleSolver(dispatching_rule="most_work_remaining")
    dispatcher = Dispatcher(example_job_shop_instance)
    current_times = [0, 0, 0, 1, 1, 7, 7, 10, 11]
    for i, current_time in enumerate(current_times):
        solver.step(dispatcher)
        assert (
            dispatcher.current_time() == current_time
        ), f"Failed at iteration {i}."


def test_uncompleted_operations(example_job_shop_instance: JobShopInstance):
    dispatcher = Dispatcher(example_job_shop_instance)
    solver = DispatchingRuleSolver(dispatching_rule="most_work_remaining")
    expected_uncompleted_operations = set()
    for job in example_job_shop_instance.jobs:
        for operation in job:
            expected_uncompleted_operations.add(operation)

    while not dispatcher.schedule.is_complete():
        assert (
            set(dispatcher.uncompleted_operations())
            == expected_uncompleted_operations
        )
        operation = solver.dispatching_rule(dispatcher)
        solver.step(dispatcher)
        expected_uncompleted_operations.remove(operation)

    assert (
        set(dispatcher.uncompleted_operations())
        == expected_uncompleted_operations
    )


# RULES_TO_TEST = [
#     DispatchingRule.MOST_WORK_REMAINING,
#     DispatchingRule.FIRST_COME_FIRST_SERVED,
#     DispatchingRule.MOST_OPERATIONS_REMAINING,
# ]

# @pytest.mark.parametrize(
#     "dispatching_rule",
#     [rule for rule in DispatchingRule if rule in RULES_TO_TEST],
# )
# @pytest.mark.parametrize("instance", load_all_benchmark_instances().values())
# def test_filter_bad_choices(
#     dispatching_rule: DispatchingRule, instance: JobShopInstance
# ):
#     optimized_solver = DispatchingRuleSolver(
#         dispatching_rule=dispatching_rule, filter_bad_choices=True
#     )
#     non_optimized_solver = DispatchingRuleSolver(
#         dispatching_rule=dispatching_rule, filter_bad_choices=False
#     )

#     optimized_schedule = optimized_solver.solve(instance)
#     non_optimized_schedule = non_optimized_solver.solve(instance)
#     optimized_makespan = optimized_schedule.makespan()
#     non_optimized_makespan = non_optimized_schedule.makespan()
#     assert optimized_makespan <= non_optimized_makespan, (
#         f"Optimized makespan: {optimized_makespan}, "
#         f"Non-optimized makespan: {non_optimized_makespan} "
#         f"Instance: {instance.name}, "
#         f"Dispatching rule: {dispatching_rule}"
#     )


if __name__ == "__main__":
    pytest.main(["-v", "test_dispatcher.py"])
