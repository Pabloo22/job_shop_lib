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
    m1 = 0
    m2 = 1
    m3 = 2

    job_1 = [Operation(m1, 1), Operation(m2, 1), Operation(m3, 7)]
    job_2 = [Operation(m2, 5), Operation(m3, 1), Operation(m1, 1)]
    job_3 = [Operation(m3, 1), Operation(m1, 3), Operation(m2, 2)]

    jobs = [job_1, job_2, job_3]

    instance = JobShopInstance(
        jobs,
        name="Example",
        lower_bound=7,
    )
    return instance


@pytest.fixture
def irregular_job_shop_instance():
    m1 = 0
    m2 = 1
    m3 = 2

    job_1 = [
        Operation(m1, 1),
        Operation(m2, 1),
        Operation(m3, 7),
        Operation(m1, 2),
    ]
    job_2 = [Operation(m2, 5), Operation(m3, 1), Operation(m1, 1)]
    job_3 = [Operation(m3, 1), Operation(m1, 3), Operation(m2, 2)]

    jobs = [job_1, job_2, job_3]

    instance = JobShopInstance(
        jobs,
        name="Irregular",
    )
    return instance
