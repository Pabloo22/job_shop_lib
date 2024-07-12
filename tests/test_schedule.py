import pytest
from job_shop_lib import Schedule, ScheduledOperation, JobShopInstance
from job_shop_lib.exceptions import ValidationError
from job_shop_lib.dispatching import (
    DispatchingRuleSolver,
    DispatchingRule,
)
from job_shop_lib.benchmarking import load_benchmark_instance


RULES_TO_TEST = [
    DispatchingRule.MOST_WORK_REMAINING,
    DispatchingRule.FIRST_COME_FIRST_SERVED,
    DispatchingRule.MOST_OPERATIONS_REMAINING,
]
INSTANCES_TO_TEST = [
    load_benchmark_instance(f"la{i:02d}") for i in range(1, 11)
]


@pytest.fixture(name="complete_schedule")
def fixture_complete_schedule(job_shop_instance):
    schedule = Schedule(instance=job_shop_instance, check=True)
    operations = [
        ScheduledOperation(
            job_shop_instance.jobs[0][0], start_time=0, machine_id=0
        ),
        ScheduledOperation(
            job_shop_instance.jobs[0][1], start_time=0, machine_id=1
        ),
        ScheduledOperation(
            job_shop_instance.jobs[1][0], start_time=100, machine_id=1
        ),
        ScheduledOperation(
            job_shop_instance.jobs[1][1], start_time=100, machine_id=2
        ),
    ]
    for op in operations:
        schedule.add(op)
    return schedule


def test_schedule_is_complete_true(complete_schedule: Schedule):
    assert complete_schedule.is_complete()


def test_schedule_is_complete_false(job_shop_instance: JobShopInstance):
    schedule = Schedule(instance=job_shop_instance)
    # Schedule only a subset of operations
    partial_operations = [
        ScheduledOperation(
            job_shop_instance.jobs[0][0], start_time=0, machine_id=0
        ),
        ScheduledOperation(
            job_shop_instance.jobs[1][0], start_time=0, machine_id=1
        ),
    ]
    for op in partial_operations:
        schedule.add(op)
    assert not schedule.is_complete()


def test_check_start_time_raises_error(job_shop_instance: JobShopInstance):
    schedule = Schedule(instance=job_shop_instance)
    valid_op = ScheduledOperation(
        job_shop_instance.jobs[0][1], start_time=0, machine_id=1
    )
    schedule.add(valid_op)
    overlapping_op = ScheduledOperation(
        job_shop_instance.jobs[1][0], start_time=0, machine_id=1
    )
    with pytest.raises(ValidationError):
        schedule.add(overlapping_op)


@pytest.mark.parametrize("dispatching_rule", RULES_TO_TEST)
@pytest.mark.parametrize("instance", INSTANCES_TO_TEST)
def test_from_job_sequences_2(
    dispatching_rule: DispatchingRule,
    instance: JobShopInstance,
):
    solver = DispatchingRuleSolver(dispatching_rule=dispatching_rule)
    expected_schedule = solver(instance)

    job_sequences: list[list[int]] = [[] for _ in range(instance.num_machines)]
    for machine_schedule in expected_schedule.schedule:
        for scheduled_operation in machine_schedule:
            job_sequences[scheduled_operation.machine_id].append(
                scheduled_operation.operation.job_id
            )

    schedule = Schedule.from_job_sequences(instance, job_sequences)
    assert schedule == expected_schedule


def test_from_job_sequences(example_job_shop_instance: JobShopInstance):
    job_sequences = [
        [0, 2, 1],
        [0, 1, 2],
        [2, 0, 1],
    ]
    schedule = Schedule.from_job_sequences(
        example_job_shop_instance, job_sequences
    )
    assert schedule.is_complete()
    assert schedule.makespan() == 11


def test_to_dict(example_job_shop_instance: JobShopInstance):
    job_sequences = [
        [0, 2, 1],
        [0, 1, 2],
        [2, 0, 1],
    ]
    schedule = Schedule.from_job_sequences(
        example_job_shop_instance, job_sequences
    )
    schedule_dict = schedule.to_dict()
    new_schedule = Schedule.from_dict(**schedule_dict)
    assert schedule == new_schedule


if __name__ == "__main__":
    pytest.main(["-vv", "tests/test_schedule.py"])
