import pytest
from job_shop_lib.generators import SimpleGenerator


def test_simple_generator_initialization_defaults():
    """Test initialization with default parameters"""
    generator = SimpleGenerator(max_duration=10)
    assert generator.max_duration == 10
    assert generator.min_duration == 1


def test_simple_generator_initialization_custom():
    """Test initialization with custom parameters"""
    generator = SimpleGenerator(
        max_duration=15, min_duration=5, max_num_jobs=30
    )
    assert generator.max_duration == 15
    assert generator.min_duration == 5
    assert generator.max_num_jobs == 30


def test_generate():
    """Test generation of job shop instances"""
    generator = SimpleGenerator(max_duration=10, min_duration=5, seed=42)
    instance = generator.generate(num_jobs=5, num_machines=5)
    assert len(instance.jobs) == 5
    for job in instance.jobs:
        assert len(job) == 5  # Ensure each job has 5 operations
        machine_ids = [op.machine_id for op in job]
        machines_are_unique = len(set(machine_ids)) == 5
        assert machines_are_unique
        for op in job:
            assert (
                5 <= op.duration <= 10
            )  # Ensure operation duration is within bounds


@pytest.mark.parametrize("limit", [1, 5, 10])
def test_iteration_limit(limit):
    generator = SimpleGenerator(
        max_duration=10, iteration_limit=limit, seed=42
    )
    instances = list(generator)  # Utilize the generator's iterable nature
    assert (
        len(instances) == limit
    )  # Ensure the number of instances matches the iteration limit
