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
    return JobShopInstance(jobs=jobs)


# Fixture for ft06 instance
@pytest.fixture
def ft06_instance():
    jobs = []
    with open("ft06.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()[4:]  # Skip header
        num_jobs, num_machines = map(int, lines[0].split())
        for job_id in range(num_jobs):
            operations = []
            data = lines[job_id + 1].split()
            for op_idx in range(num_machines):
                machine_id = int(data[2 * op_idx])
                duration = int(data[2 * op_idx + 1])
                operations.append(
                    Operation(
                        machine_id=machine_id,
                        duration=duration,
                        job_id=job_id,
                        position_in_job=op_idx,
                    )
                )
            jobs.append(operations)
    return JobShopInstance(jobs=jobs)
