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
    cpu = 0
    gpu = 1
    data_center = 2

    job_1 = [Operation(cpu, 1), Operation(gpu, 1), Operation(data_center, 7)]
    job_2 = [Operation(gpu, 5), Operation(data_center, 1), Operation(cpu, 1)]
    job_3 = [Operation(data_center, 1), Operation(cpu, 3), Operation(gpu, 2)]

    jobs = [job_1, job_2, job_3]

    instance = JobShopInstance(
        jobs,
        name="Example",
        lower_bound=7,
    )
    return instance
