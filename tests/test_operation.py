import pytest
from job_shop_lib import Operation


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
    with pytest.raises(ValueError):
        _ = op.machine_id


def test_get_id():
    op = Operation(1, 5, 1, 2)
    assert op.operation_id == "J1M1P2"


def test_get_job_id_from_id():
    assert Operation.get_job_id_from_id("J1M2P3") == 1


def test_get_machine_id_from_id():
    assert Operation.get_machine_id_from_id("J1M2P3") == 2


def test_get_position_from_id():
    assert Operation.get_position_from_id("J1M2P3") == 3
