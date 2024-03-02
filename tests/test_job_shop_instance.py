from job_shop_lib import JobShopInstance, Operation


def test_set_operation_attributes():
    op1 = Operation(machines=0, duration=1)
    op2 = Operation(machines=1, duration=2)
    op3 = Operation(machines=2, duration=3)

    job1 = [op1, op2]
    job2 = [op3]

    JobShopInstance(jobs=[job1, job2])

    assert (
        job1[0].job_id == 0
        and job1[0].position_in_job == 0
        and job1[0].operation_id == 0
    ), "Job 1 Operation 1 attributes not set correctly"
    assert (
        job1[1].job_id == 0
        and job1[1].position_in_job == 1
        and job1[1].operation_id == 1
    ), "Job 1 Operation 2 attributes not set correctly"
    assert (
        job2[0].job_id == 1
        and job2[0].position_in_job == 0
        and job2[0].operation_id == 2
    ), "Job 2 Operation 1 attributes not set correctly"


def test_from_matrices(job_shop_instance: JobShopInstance):
    duration_matrix = job_shop_instance.durations_matrix
    machines_matrix = job_shop_instance.machines_matrix
    name = job_shop_instance.name
    metadata = job_shop_instance.metadata

    new_instance = JobShopInstance.from_matrices(
        duration_matrix=duration_matrix,
        machines_matrix=machines_matrix,
        name=name,
        metadata=metadata,
    )

    assert new_instance.durations_matrix == duration_matrix
    assert new_instance.machines_matrix == machines_matrix
    assert new_instance.name == name
    assert new_instance.metadata == metadata


def test_num_jobs(job_shop_instance: JobShopInstance):
    assert job_shop_instance.num_jobs == 2


def test_durations_matrix(job_shop_instance: JobShopInstance):
    expected_matrix = [
        [10, 20],
        [15, 10],
    ]
    assert job_shop_instance.durations_matrix == expected_matrix


def test_machines_matrix(job_shop_instance: JobShopInstance):
    expected_matrix = [
        [0, 1],
        [1, 2],
    ]
    assert job_shop_instance.machines_matrix == expected_matrix


def test_operations_by_machine(job_shop_instance: JobShopInstance):
    expected_operations = [
        [job_shop_instance.jobs[0][0]],
        [job_shop_instance.jobs[0][1], job_shop_instance.jobs[1][0]],
        [job_shop_instance.jobs[1][1]],
    ]
    assert job_shop_instance.operations_by_machine == expected_operations


def test_job_durations(job_shop_instance: JobShopInstance):
    assert job_shop_instance.job_durations == [30, 25]


def test_total_duration(job_shop_instance: JobShopInstance):
    assert job_shop_instance.total_duration == 55


def test_num_machines(job_shop_instance: JobShopInstance):
    assert job_shop_instance.num_machines == 3


def test_max_duration(job_shop_instance: JobShopInstance):
    assert job_shop_instance.max_duration == 20


def test_machine_loads(job_shop_instance: JobShopInstance):
    expected_loads = [
        10,
        35,
        10,
    ]  # Machine 0 has 10, Machine 1 has 35 (20 from Job 1 and 15 from Job 2),
    # Machine 2 has 10
    assert job_shop_instance.machine_loads == expected_loads


def test_num_operations(job_shop_instance: JobShopInstance):
    assert job_shop_instance.num_operations == 4


def test_max_duration_per_job(job_shop_instance):
    assert job_shop_instance.max_duration_per_job == [20, 15]


def test_max_duration_per_machine(job_shop_instance):
    assert job_shop_instance.max_duration_per_machine == [10, 20, 10]
