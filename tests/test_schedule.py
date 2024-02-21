import pytest
from job_shop_lib import Schedule, ScheduledOperation, JobShopInstance


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
            job_shop_instance.jobs[1][1], start_time=100, machine_id=0
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
        job_shop_instance.jobs[0][0], start_time=0, machine_id=0
    )
    schedule.add(valid_op)
    overlapping_op = ScheduledOperation(
        job_shop_instance.jobs[1][1], start_time=5, machine_id=0
    )
    with pytest.raises(ValueError):
        schedule.add(overlapping_op)
