import pytest
from job_shop_lib import InstanceGenerator


def test_generate():
    """Test generation of job shop instances"""
    generator = InstanceGenerator(
        duration_range=(5, 10), seed=42, num_jobs=5, num_machines=5
    )
    instance = generator.generate()
    assert len(instance.jobs) == 5
    for job in instance.jobs:
        assert len(job) == 5
        machine_ids = [op.machine_id for op in job]
        machines_are_unique = len(set(machine_ids)) == 5
        assert machines_are_unique
        for op in job:
            assert 5 <= op.duration <= 10


@pytest.mark.parametrize("limit", [1, 5, 10, 20])
def test_iteration_limit(limit):
    generator = InstanceGenerator(iteration_limit=limit, seed=42)
    instances = list(generator)
    assert len(instances) == limit


def test_different_names():
    generator = InstanceGenerator()
    instance1 = generator.generate()
    instance2 = generator.generate()
    assert instance1.name != instance2.name
    assert instance1.name.startswith("classic_generated_instance")
    assert instance2.name.startswith("classic_generated_instance")
