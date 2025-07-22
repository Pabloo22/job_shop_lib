import pytest

from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.benchmarking import load_benchmark_instance
from job_shop_lib.dispatching import (
    Dispatcher,
    filter_non_idle_machines,
    filter_non_immediate_machines,
    filter_non_immediate_operations,
)
from job_shop_lib.dispatching.rules import (
    DispatchingRuleType,
    DispatchingRuleSolver,
)

INSTANCES_TO_TEST = [
    load_benchmark_instance(f"la{i:02d}") for i in range(1, 11)
]
RULES_TO_TEST = [
    DispatchingRuleType.MOST_WORK_REMAINING,
    DispatchingRuleType.FIRST_COME_FIRST_SERVED,
    DispatchingRuleType.MOST_OPERATIONS_REMAINING,
]


@pytest.mark.parametrize("instance", INSTANCES_TO_TEST)
def test_filter_remove_non_idle_machines(instance: JobShopInstance):
    dispatcher = Dispatcher(
        instance,
        ready_operations_filter=filter_non_idle_machines,
    )

    while not dispatcher.schedule.is_complete():
        available_operations = dispatcher.available_operations()
        ongoing_operations = dispatcher.ongoing_operations()

        non_idle_machines = set()
        for scheduled_op in ongoing_operations:
            non_idle_machines.add(scheduled_op.machine_id)

        idle_machines = set(range(instance.num_machines)) - non_idle_machines
        for op in available_operations:
            assert any(m in idle_machines for m in op.machines)

        next_operation = available_operations[0]
        dispatcher.dispatch(next_operation, next_operation.machines[0])


@pytest.mark.parametrize("instance", INSTANCES_TO_TEST)
def test_filter_remove_non_immediate_operations(instance: JobShopInstance):
    dispatcher = Dispatcher(
        instance,
        ready_operations_filter=filter_non_immediate_operations,
    )

    while not dispatcher.schedule.is_complete():
        available_operations = dispatcher.available_operations()
        current_time = dispatcher.current_time()

        for op in available_operations:
            assert dispatcher.earliest_start_time(op) == current_time

        next_operation = available_operations[0]
        dispatcher.dispatch(next_operation, next_operation.machines[0])


@pytest.mark.parametrize("instance", INSTANCES_TO_TEST)
def test_filter_non_immediate_machines(instance: JobShopInstance):
    dispatcher = Dispatcher(
        instance,
        ready_operations_filter=filter_non_immediate_machines,
    )

    while not dispatcher.schedule.is_complete():
        current_time = dispatcher.current_time()
        available_operations = dispatcher.available_operations()
        operations_per_machine: list[list[Operation]] = [
            [] for _ in range(instance.num_machines)
        ]
        for op in available_operations:
            for m in op.machines:
                operations_per_machine[m].append(op)

        for m, ops in enumerate(operations_per_machine):
            if ops:
                assert any(
                    dispatcher.start_time(op, m) == current_time for op in ops
                )

        next_operation = available_operations[0]
        dispatcher.dispatch(next_operation, next_operation.machines[0])


@pytest.mark.parametrize(
    "dispatching_rule",
    [rule for rule in DispatchingRuleType if rule in RULES_TO_TEST],
)
@pytest.mark.parametrize("instance", INSTANCES_TO_TEST)
def test_dominated_operation_filter(
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

    .. code-block:: python

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

    You can see the plots of the schedules in the `examples` folder.
    """
    optimized_solver = DispatchingRuleSolver(
        dispatching_rule=dispatching_rule,
        ready_operations_filter="dominated_operations",
    )
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


def test_filter_non_immediate_operations_with_release_date():
    """
    Tests that `filter_non_immediate_operations` correctly filters out
    operations that are not yet released.
    """
    # Operation 0_0 has no release date.
    # Operation 1_0 has a release date of 10.
    jobs = [
        [Operation(machines=0, duration=5)],
        [Operation(machines=0, duration=5, release_date=10)],
    ]
    instance = JobShopInstance(jobs, "test_instance")

    dispatcher = Dispatcher(
        instance, ready_operations_filter=filter_non_immediate_operations
    )

    # At time 0, only operation 0_0 is available and immediate.
    # Operation 1_0 is available but not immediate due to its release date.
    available_ops = dispatcher.available_operations()
    assert len(available_ops) == 1
    assert available_ops[0].operation_id == 0

    # Schedule operation 0_0. It runs from t=0 to t=5.
    dispatcher.dispatch(available_ops[0], machine_id=0)

    # At time 5, machine 0 is free. Operation 1_0 is still not released.
    # The dispatcher's current_time should advance to the release date of
    # the next operation.
    # The only available operation is 1_0, which can start at t=10.
    # So, available_operations will return operation 1_0.
    available_ops = dispatcher.available_operations()
    assert len(available_ops) == 1
    assert available_ops[0].operation_id == 1

    # The filter should identify that it can start at t=10, which is the
    # min_start_time, so it is considered immediate.
    assert dispatcher.current_time() == 10

    # Dispatch operation 1_0
    dispatcher.dispatch(available_ops[0], machine_id=0)

    # Schedule should be complete
    assert dispatcher.schedule.is_complete()

    # Verify schedule
    scheduled_op_0_0 = dispatcher.schedule.schedule[0][0]
    assert scheduled_op_0_0.start_time == 0
    assert scheduled_op_0_0.end_time == 5

    scheduled_op_1_0 = dispatcher.schedule.schedule[0][1]
    assert scheduled_op_1_0.start_time == 10
    assert scheduled_op_1_0.end_time == 15


if __name__ == "__main__":
    pytest.main(["-vv", __file__])
