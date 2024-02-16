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
