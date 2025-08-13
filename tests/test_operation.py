import pytest

from job_shop_lib import Operation
from job_shop_lib.exceptions import ValidationError


def test_init_single_machine():
    op = Operation(1, 5)
    assert op.machines == [1]
    assert op.duration == 5


def test_init_multiple_machines():
    op = Operation([1, 2, 3], 10)
    assert op.machines == [1, 2, 3]
    assert op.duration == 10
    assert op.release_date == 0
    assert op.deadline is None
    assert op.due_date is None


def test_init_with_extra_attributes():
    op = Operation(1, 5, release_date=10, deadline=20, due_date=15)
    assert op.release_date == 10
    assert op.deadline == 20
    assert op.due_date == 15


def test_machine_id_single():
    op = Operation(1, 5)
    assert op.machine_id == 1


def test_machine_id_multiple():
    op = Operation([1, 2], 10)
    with pytest.raises(ValidationError):
        _ = op.machine_id


def test_eq():
    op1 = Operation(1, 5, release_date=10, deadline=20, due_date=15)
    op2 = Operation(1, 5, release_date=10, deadline=20, due_date=15)
    assert op1 == op2

    op3 = Operation(1, 5, release_date=11, deadline=20, due_date=15)
    assert op1 != op3
    assert op1 != "not an operation"


def test_is_initialized():
    op = Operation(1, 5)
    assert not op.is_initialized()

    op.job_id = 0
    op.position_in_job = 0
    op.operation_id = 0
    assert op.is_initialized()


def test_repr():
    op = Operation(1, 5)
    op.job_id = 0
    op.position_in_job = 0
    assert repr(op) == "O(m=1, d=5, j=0, p=0)"

    op_flex = Operation([1, 2], 5)
    op_flex.job_id = 0
    op_flex.position_in_job = 0
    assert repr(op_flex) == "O(m=[1, 2], d=5, j=0, p=0)"
