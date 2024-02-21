import pytest
from job_shop_lib import JobShopInstance, Operation


@pytest.fixture
def job_shop_instance():
    jobs = [
        [Operation(0, 10), Operation(1, 20)],
        [Operation(1, 15), Operation(2, 10)],
    ]
    instance = JobShopInstance(jobs, "TestInstance")
    return instance


@pytest.fixture
def example_job_shop_instance():
    machine_1 = 0
    machine_2 = 1
    machine_3 = 2

    job_1 = [
        Operation(machine_1, 1),
        Operation(machine_2, 1),
        Operation(machine_3, 7),
    ]
    job_2 = [
        Operation(machine_2, 5),
        Operation(machine_3, 1),
        Operation(machine_1, 1),
    ]
    job_3 = [
        Operation(machine_3, 1),
        Operation(machine_1, 3),
        Operation(machine_2, 2),
    ]

    jobs = [job_1, job_2, job_3]

    instance = JobShopInstance(
        jobs,
        name="Example",
        lower_bound=7,
    )
    return instance
