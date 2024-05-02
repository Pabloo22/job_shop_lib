import pytest
from job_shop_lib import ScheduledOperation, Operation, JobShopLibError


def test_scheduled_operation_initialization():
    operation = Operation(machines=[1, 2], duration=5)
    scheduled_operation = ScheduledOperation(
        operation, start_time=10, machine_id=1
    )
    assert scheduled_operation.operation is operation
    assert scheduled_operation.start_time == 10
    assert scheduled_operation.machine_id == 1


def test_machine_id_setter_success():
    operation = Operation(machines=[1, 2], duration=5)
    scheduled_operation = ScheduledOperation(
        operation, start_time=10, machine_id=1
    )
    scheduled_operation.machine_id = 2  # Changing to another valid machine
    assert scheduled_operation.machine_id == 2


def test_machine_id_setter_failure():
    operation = Operation(machines=[1, 2], duration=5)
    scheduled_operation = ScheduledOperation(
        operation, start_time=10, machine_id=1
    )
    with pytest.raises(JobShopLibError):
        scheduled_operation.machine_id = 3  # Invalid machine


def test_end_time_calculation():
    operation = Operation(machines=[1], duration=5)
    scheduled_operation = ScheduledOperation(
        operation, start_time=10, machine_id=1
    )
    assert scheduled_operation.end_time == 15
