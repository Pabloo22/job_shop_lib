import numpy as np
import pytest

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


def test_from_matrices(job_shop_instance_with_extras: JobShopInstance):
    duration_matrix = job_shop_instance_with_extras.duration_matrix
    machines_matrix = job_shop_instance_with_extras.machines_matrix
    release_dates_matrix = job_shop_instance_with_extras.release_dates_matrix
    deadlines_matrix = job_shop_instance_with_extras.deadlines_matrix
    due_dates_matrix = job_shop_instance_with_extras.due_dates_matrix
    name = job_shop_instance_with_extras.name
    metadata = job_shop_instance_with_extras.metadata

    new_instance = JobShopInstance.from_matrices(
        duration_matrix=duration_matrix,
        machines_matrix=machines_matrix,
        release_dates_matrix=release_dates_matrix,
        deadlines_matrix=deadlines_matrix,
        due_dates_matrix=due_dates_matrix,
        name=name,
        metadata=metadata,
    )

    assert new_instance.duration_matrix == duration_matrix
    assert new_instance.machines_matrix == machines_matrix
    assert new_instance.release_dates_matrix == release_dates_matrix
    assert new_instance.deadlines_matrix == deadlines_matrix
    assert new_instance.due_dates_matrix == due_dates_matrix
    assert new_instance.name == name
    assert new_instance.metadata == metadata


def test_to_dict(job_shop_instance_with_extras: JobShopInstance):
    instance_dict = job_shop_instance_with_extras.to_dict()
    assert "release_dates_matrix" in instance_dict
    assert "deadlines_matrix" in instance_dict
    assert "due_dates_matrix" in instance_dict

    instance = JobShopInstance(
        jobs=[[Operation(0, 1)]], name="test"
    )  # No extras
    instance_dict = instance.to_dict()
    assert "release_dates_matrix" not in instance_dict
    assert "deadlines_matrix" not in instance_dict
    assert "due_dates_matrix" not in instance_dict


def test_num_jobs(job_shop_instance: JobShopInstance):
    assert job_shop_instance.num_jobs == 2


def test_durations_matrix(job_shop_instance: JobShopInstance):
    expected_matrix = [
        [10, 20],
        [15, 10],
    ]
    assert job_shop_instance.duration_matrix == expected_matrix

    # check that "durations_matrix" is deprecated
    with pytest.warns(DeprecationWarning):
        assert job_shop_instance.durations_matrix == expected_matrix


def test_machines_matrix(job_shop_instance: JobShopInstance):
    expected_matrix = [
        [0, 1],
        [1, 2],
    ]
    assert job_shop_instance.machines_matrix == expected_matrix


def test_has_release_dates(
    job_shop_instance: JobShopInstance,
    job_shop_instance_with_extras: JobShopInstance,
):
    assert not job_shop_instance.has_release_dates
    assert job_shop_instance_with_extras.has_release_dates


def test_has_deadlines(
    job_shop_instance: JobShopInstance,
    job_shop_instance_with_extras: JobShopInstance,
):
    assert not job_shop_instance.has_deadlines
    assert job_shop_instance_with_extras.has_deadlines


def test_has_due_dates(
    job_shop_instance: JobShopInstance,
    job_shop_instance_with_extras: JobShopInstance,
):
    assert not job_shop_instance.has_due_dates
    assert job_shop_instance_with_extras.has_due_dates


def test_release_dates_matrix(job_shop_instance_with_extras: JobShopInstance):
    expected_matrix = [
        [0, 10],
        [5, 15],
    ]
    assert (
        job_shop_instance_with_extras.release_dates_matrix == expected_matrix
    )


def test_deadlines_matrix(job_shop_instance_with_extras: JobShopInstance):
    expected_matrix = [
        [100, 110],
        [105, 115],
    ]
    assert job_shop_instance_with_extras.deadlines_matrix == expected_matrix


def test_due_dates_matrix(job_shop_instance_with_extras: JobShopInstance):
    expected_matrix = [
        [80, 90],
        [85, 95],
    ]
    assert job_shop_instance_with_extras.due_dates_matrix == expected_matrix


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


def test_duration_matrix_array():
    jobs = [
        [Operation(machines=0, duration=1), Operation(machines=1, duration=2)],
        [Operation(machines=1, duration=3)],
    ]
    instance = JobShopInstance(jobs=jobs)
    assert str(instance.duration_matrix_array) == str(
        np.array([[1.0, 2.0], [3.0, np.nan]], dtype=np.float32)
    )

    # check that "durations_matrix_array" is deprecated
    with pytest.warns(DeprecationWarning):
        assert str(instance.durations_matrix_array) == str(
            np.array([[1.0, 2.0], [3.0, np.nan]], dtype=np.float32)
        )

def test_release_dates_matrix_array():
    jobs = [
        [
            Operation(machines=0, duration=1, release_date=5),
            Operation(machines=1, duration=2, release_date=10),
        ],
        [Operation(machines=1, duration=3, release_date=15)],
    ]
    instance = JobShopInstance(jobs=jobs)
    assert str(instance.release_dates_matrix_array) == str(
        np.array([[5.0, 10.0], [15.0, np.nan]], dtype=np.float32)
    )


def test_deadlines_matrix_array():
    jobs = [
        [
            Operation(machines=0, duration=1, deadline=None),
            Operation(machines=1, duration=2, deadline=110),
        ],
        [Operation(machines=1, duration=3, deadline=None)],
    ]
    instance = JobShopInstance(jobs=jobs)
    assert str(instance.deadlines_matrix_array) == str(
        np.array([[np.nan, 110.0], [np.nan, np.nan]], dtype=np.float32)
    )


def test_due_dates_matrix_array():
    jobs = [
        [
            Operation(machines=0, duration=1, due_date=80),
            Operation(machines=1, duration=2, due_date=None),
        ],
        [Operation(machines=1, duration=3, due_date=95)],
    ]
    instance = JobShopInstance(jobs=jobs)
    assert str(instance.due_dates_matrix_array) == str(
        np.array([[80.0, np.nan], [95.0, np.nan]], dtype=np.float32)
    )


def test_machine_matrix_array_3d():
    jobs = [
        [Operation(machines=0, duration=1), Operation(machines=1, duration=2)],
        [Operation(machines=[0, 1], duration=3)],
    ]
    instance = JobShopInstance(jobs=jobs)
    assert str(instance.machines_matrix_array) == str(
        np.array(
            [
                [[0.0, np.nan], [1.0, np.nan]],
                [[0.0, 1.0], [np.nan, np.nan]],
            ],
            dtype=np.float32,
        )
    )


def test_machine_matrix_array_2d():
    jobs = [
        [Operation(machines=0, duration=1), Operation(machines=1, duration=2)],
        [Operation(machines=1, duration=3)],
    ]
    instance = JobShopInstance(jobs=jobs)
    assert str(instance.machines_matrix_array) == str(
        np.array([[0.0, 1.0], [1.0, np.nan]], dtype=np.float32)
    )


def test_deprecation_warning_for_metadata():
    """Tests that a deprecation warning is raised for deprecated keys."""
    with pytest.warns(DeprecationWarning):
        JobShopInstance(
            jobs=[[Operation(0, 1)]],
            name="test",
            release_dates_matrix=[[0]],
        )
    with pytest.warns(DeprecationWarning):
        JobShopInstance(
            jobs=[[Operation(0, 1)]],
            name="test",
            deadlines_matrix=[[100]],
        )
    with pytest.warns(DeprecationWarning):
        JobShopInstance(
            jobs=[[Operation(0, 1)]],
            name="test",
            due_dates_matrix=[[80]],
        )


def test_eq():
    """Test equality of JobShopInstance objects."""
    instance1 = JobShopInstance(
        jobs=[[Operation(0, 1)], [Operation(1, 2)]], name="test1"
    )
    instance2 = JobShopInstance(
        jobs=[[Operation(0, 1)], [Operation(1, 2)]], name="test2"
    )
    instance3 = JobShopInstance(
        jobs=[[Operation(0, 2)], [Operation(1, 3)]], name="test3"
    )

    assert instance1 == instance2
    assert instance1 != instance3
    assert instance1 != "not a JobShopInstance"


def test_repr(job_shop_instance: JobShopInstance):
    """Test the string representation of JobShopInstance."""
    expected_repr = (
        "JobShopInstance(name=TestInstance, num_jobs=2, "
        "num_machines=3)"
    )
    assert repr(job_shop_instance) == expected_repr

if __name__ == "__main__":
    pytest.main(["-vv", __file__])
