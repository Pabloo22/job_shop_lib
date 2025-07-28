import pytest
from job_shop_lib import JobShopInstance, Operation


# Fixture for a simple job shop instance
@pytest.fixture
def simple_instance():
    jobs = [
        [
            Operation(machine_id=0, duration=3, job_id=0, position_in_job=0),
            Operation(machine_id=1, duration=2, job_id=0, position_in_job=1),
        ],
        [
            Operation(machine_id=0, duration=2, job_id=1, position_in_job=0),
            Operation(machine_id=1, duration=1, job_id=1, position_in_job=1),
        ],
    ]
    return JobShopInstance(jobs=jobs, num_machines=2)
