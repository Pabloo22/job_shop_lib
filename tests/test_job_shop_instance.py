import pytest
import numpy as np
from job_shop_lib import (
    JobShopInstance,
    Operation,
)


@pytest.fixture
def job_shop_instance():
    jobs = [
        [Operation(0, 10), Operation(1, 20)],
        [Operation(1, 15), Operation(2, 10)],
    ]
    instance = JobShopInstance(jobs, "TestInstance")
    return instance


def test_num_jobs(job_shop_instance):
    assert job_shop_instance.num_jobs == 2


def test_bounds(job_shop_instance):
    # Assuming you set these metadata values somewhere or pass
    # them during instantiation
    job_shop_instance.metadata["lower_bound"] = 10.0
    job_shop_instance.metadata["upper_bound"] = 100.0
    assert job_shop_instance.bounds == (10.0, 100.0)


def test_durations_matrix(job_shop_instance):
    expected_matrix = np.array([[10, 20], [15, 10]])
    np.testing.assert_array_equal(
        job_shop_instance.durations_matrix, expected_matrix
    )


def test_machines_matrix(job_shop_instance):
    expected_matrix = [[[0], [1]], [[1], [2]]]
    assert job_shop_instance.machines_matrix == expected_matrix


def test_job_durations(job_shop_instance):
    assert job_shop_instance.job_durations == [30, 25]


def test_total_duration(job_shop_instance):
    assert job_shop_instance.total_duration == 55


def test_num_machines(job_shop_instance):
    assert job_shop_instance.num_machines == 3


def test_max_duration(job_shop_instance):
    assert job_shop_instance.max_duration == 20


def test_max_job_duration(job_shop_instance):
    assert job_shop_instance.max_job_duration == 30


def test_machine_loads(job_shop_instance):
    expected_loads = [
        10,
        35,
        10,
    ]  # Machine 0 has 10, Machine 1 has 35 (20 from Job 1 and 15 from Job 2),
    # Machine 2 has 10
    assert job_shop_instance.machine_loads == expected_loads


def test_num_operations(job_shop_instance):
    assert job_shop_instance.num_operations == 4


def test_max_machine_load(job_shop_instance):
    assert job_shop_instance.max_machine_load == 35


def test_mean_machine_load(job_shop_instance):
    # Total duration is 55, and there are 3 machines
    expected_mean_load = 55 / 3
    assert job_shop_instance.mean_machine_load == expected_mean_load
