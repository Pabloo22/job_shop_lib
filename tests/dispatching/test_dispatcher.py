import pytest

from job_shop_lib import JobShopInstance
from job_shop_lib.dispatching import (
    Dispatcher,
)
from job_shop_lib.dispatching.rules import (
    DispatchingRuleSolver,
    DispatchingRuleType,
)
from job_shop_lib.benchmarking import load_benchmark_instance


RULES_TO_TEST = [
    DispatchingRuleType.MOST_WORK_REMAINING,
    DispatchingRuleType.FIRST_COME_FIRST_SERVED,
    DispatchingRuleType.MOST_OPERATIONS_REMAINING,
]
INSTANCES_TO_TEST = [
    load_benchmark_instance(f"la{i:02d}") for i in range(1, 11)
]


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


@pytest.mark.parametrize(
    "dispatching_rule",
    [rule for rule in DispatchingRuleType if rule in RULES_TO_TEST],
)
@pytest.mark.parametrize("instance", INSTANCES_TO_TEST)
def test_filter_bad_choices(
    dispatching_rule: DispatchingRuleType, instance: JobShopInstance
):
    """Test that the optimized solver produces a schedule with a makespan
    less than or equal to the non-optimized solver.

    It is important to note, though, that there is no theoretical guarantee
    that the optimized solver will always produce a better schedule. Although
    the optimized solver always filter out non-optimal choices, removing that
    option may lead to the solver to choose an even worse option. For example,
    consider we have three operations A, B, and C, and operation A is the best
    choice according to the dispatching rule, then B, and finally C. Our
    opimized scheduler will remove B from the list of choices, however, the
    solver may choose C instead of A, which would lead to a worse schedule
    than if it had chosen B. This may result in the optimized solver producing
    a worse schedule than the non-optimized solver. However, in practice, the
    optimized solver will usually produce better schedules than the
    non-optimized solver. From all the benchmarks we have tested, the optimized
    solver only produced worse schedules in "ta51" and "orb09" instances.

    A smaller example to illustrate the point:

    ```python
    instance_dict = {
        "name": "classic_generated_instance_375",
        "duration_matrix": [[3, 5, 9],
                            [6, 1, 6],
                            [2, 4, 4]],
        "machines_matrix": [[0, 2, 1],
                            [2, 0, 1],
                            [2, 1, 0]],
        "metadata": {
            "optimized_makespan": 30,
            "non_optimized_makespan": 27,
            "dispatching_rule": "most_work_remaining",
        },
    }
    ```

    You can see the plots of the schedules in the `examples` folder.
    """
    optimized_solver = DispatchingRuleSolver(dispatching_rule=dispatching_rule)
    non_optimized_solver = DispatchingRuleSolver(
        dispatching_rule=dispatching_rule, ready_operations_filter=None
    )

    optimized_schedule = optimized_solver.solve(instance)
    non_optimized_schedule = non_optimized_solver.solve(instance)
    optimized_makespan = optimized_schedule.makespan()
    non_optimized_makespan = non_optimized_schedule.makespan()
    assert optimized_makespan <= non_optimized_makespan, (
        f"Optimized makespan: {optimized_makespan}, "
        f"Non-optimized makespan: {non_optimized_makespan} "
        f"Instance: {instance.name}, "
        f"Dispatching rule: {dispatching_rule}"
    )


if __name__ == "__main__":
    # Run current file with the following command:
    # python -m pytest tests/test_dispatcher.py
    pytest.main(["-vv", "tests/dispatching/test_dispatcher.py"])
