import pytest
from job_shop_lib import Schedule, ScheduledOperation, JobShopInstance
from job_shop_lib.exceptions import ValidationError
from job_shop_lib.dispatching import Dispatcher
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
    dispatching_rule: DispatchingRuleType,
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

    schedule = Schedule.from_job_sequences(
        instance, job_sequences, dispatcher=Dispatcher(instance=instance)
    )
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


def test_from_job_sequences_invalid(
    example_job_shop_instance: JobShopInstance,
):
    job_sequences = [
        [0, 1, 2],
        [2, 0, 1],
        [1, 0, 2],
    ]
    with pytest.raises(ValidationError):
        Schedule.from_job_sequences(example_job_shop_instance, job_sequences)


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


def test_from_partial_job_sequences(
    example_job_shop_instance: JobShopInstance,
):
    job_sequences = [
        [0],
        [0],
        [0],
    ]
    schedule = Schedule.from_job_sequences(
        example_job_shop_instance, job_sequences
    )
    assert not schedule.is_complete()


def test_from_partial_job_sequences_invalid(
    example_job_shop_instance: JobShopInstance,
):
    job_sequences = [
        [0],
        [0],
        [1],
    ]
    with pytest.raises(ValidationError):
        Schedule.from_job_sequences(example_job_shop_instance, job_sequences)


def test_from_dict_partial(
    example_job_shop_instance: JobShopInstance,
):
    job_sequences = [
        [0],
        [0],
        [0],
    ]
    schedule = Schedule.from_job_sequences(
        example_job_shop_instance, job_sequences
    )
    schedule_dict = schedule.to_dict()
    new_schedule = Schedule.from_dict(**schedule_dict)
    assert not new_schedule.is_complete()


def test_copy(example_job_shop_instance: JobShopInstance):
    job_sequences = [
        [0],
        [0],
        [0],
    ]
    schedule = Schedule.from_job_sequences(
        example_job_shop_instance, job_sequences
    )
    schedule_copy = schedule.copy()
    assert schedule == schedule_copy
    assert schedule is not schedule_copy

    # Add an operation to the original schedule
    new_op = ScheduledOperation(
        example_job_shop_instance.jobs[0][0],
        start_time=20,
        machine_id=example_job_shop_instance.jobs[0][0].machine_id,
    )
    schedule.add(new_op)
    assert schedule != schedule_copy


def test_check_schedule(
    complete_schedule: Schedule, job_shop_instance: JobShopInstance
):
    # This should not raise an error
    Schedule.check_schedule(complete_schedule.schedule)

    # Create a schedule with an invalid operation
    invalid_schedule: list[list[ScheduledOperation]] = [
        [] for _ in range(job_shop_instance.num_machines)
    ]
    op1 = ScheduledOperation(
        job_shop_instance.jobs[0][0], start_time=0, machine_id=0
    )
    op2 = ScheduledOperation(
        job_shop_instance.jobs[1][0], start_time=0, machine_id=1
    )
    invalid_operation = ScheduledOperation(
        job_shop_instance.jobs[0][1], start_time=0, machine_id=1
    )
    invalid_schedule[0].append(op1)
    invalid_schedule[1].append(op2)
    invalid_schedule[1].append(invalid_operation)

    with pytest.raises(ValidationError):
        Schedule.check_schedule(invalid_schedule)

    # remove the invalid operation
    invalid_schedule[1].remove(invalid_operation)
    # This should not raise an error now
    Schedule.check_schedule(invalid_schedule)

    # Move the operation in machine 1 to machine 0
    invalid_schedule[0].append(invalid_operation)
    with pytest.raises(
        ValidationError, match="The machine id of the scheduled operation"
    ):
        Schedule.check_schedule(invalid_schedule)


def test_repr(complete_schedule: Schedule):
    repr_str = repr(complete_schedule)
    assert isinstance(repr_str, str)
    assert repr_str == str(complete_schedule.schedule)


def test_eq(complete_schedule: Schedule):
    assert complete_schedule != []


if __name__ == "__main__":
    pytest.main(["-vv", "tests/test_schedule.py"])
