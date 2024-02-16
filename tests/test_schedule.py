import pytest
from job_shop_lib import (
    Schedule,
    Operation,
    ScheduledOperation,
    JobShopInstance,
)


@pytest.fixture
def job_shop_instance():
    jobs = [
        [Operation([0], 10), Operation([1], 20)],
        [Operation([1], 15), Operation([0], 10)],
    ]
    return JobShopInstance(jobs=jobs)


@pytest.fixture
def complete_schedule(job_shop_instance):
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
            job_shop_instance.jobs[1][1], start_time=100, machine_id=0
        ),
    ]
    for op in operations:
        schedule.dispatch(op)
    return schedule


def test_empty_schedule_initialization(job_shop_instance):
    schedule = Schedule(instance=job_shop_instance)
    assert schedule.is_empty()


def test_schedule_is_complete_true(complete_schedule):
    assert complete_schedule.is_complete()


def test_schedule_is_complete_false(job_shop_instance):
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
        schedule.dispatch(op)
    assert not schedule.is_complete()


def test_check_start_time_raises_error(job_shop_instance):
    schedule = Schedule(instance=job_shop_instance)
    valid_op = ScheduledOperation(
        job_shop_instance.jobs[0][0], start_time=0, machine_id=0
    )
    schedule.dispatch(valid_op)
    overlapping_op = ScheduledOperation(
        job_shop_instance.jobs[1][1], start_time=5, machine_id=0
    )
    with pytest.raises(ValueError):
        schedule.dispatch(overlapping_op)
