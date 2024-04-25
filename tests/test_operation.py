import pytest
from job_shop_lib import Operation, JobShopLibError


def test_init_single_machine():
    op = Operation(1, 5)
    assert op.machines == [1]
    assert op.duration == 5


def test_init_multiple_machines():
    op = Operation([1, 2, 3], 10)
    assert op.machines == [1, 2, 3]
    assert op.duration == 10


def test_machine_id_single():
    op = Operation(1, 5)
    assert op.machine_id == 1


def test_machine_id_multiple():
    op = Operation([1, 2], 10)
    with pytest.raises(JobShopLibError):
        _ = op.machine_id
