import pytest
from job_shop_lib.generation import GeneralInstanceGenerator


def test_generate():
    """Test generation of job shop instances"""
    generator = GeneralInstanceGenerator(
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
    generator = GeneralInstanceGenerator(iteration_limit=limit, seed=42)
    instances = list(generator)
    assert len(instances) == limit


def test_different_names():
    generator = GeneralInstanceGenerator()
    instance1 = generator.generate()
    instance2 = generator.generate()
    assert instance1.name != instance2.name
    assert instance1.name.startswith("classic_generated_instance")
    assert instance2.name.startswith("classic_generated_instance")


@pytest.mark.skip
def test_machines_per_operation():
    generator = GeneralInstanceGenerator(
        machines_per_operation=(2, 3), seed=42
    )

    instance = generator.generate()
    for job in instance.jobs:
        for operation in job:
            assert 2 <= len(operation.machines) <= 3
            for machine_id in operation.machines:
                assert 0 <= machine_id < instance.num_machines


def test_rng_determinism_class():
    """Tests that GeneralInstanceGenerator produces deterministic results with
    the same seed."""
    params = {
        "duration_range": (1, 10),
        "seed": 12345,
        "num_jobs": 4,
        "num_machines": 4,
    }
    gen1 = GeneralInstanceGenerator(**params)  # type: ignore[arg-type]
    gen2 = GeneralInstanceGenerator(**params)  # type: ignore[arg-type]
    inst1 = gen1.generate()
    inst2 = gen2.generate()
    # Compare job durations and machine assignments
    for job1, job2 in zip(inst1.jobs, inst2.jobs):
        for op1, op2 in zip(job1, job2):
            assert op1.duration == op2.duration
            assert op1.machine_id == op2.machine_id
