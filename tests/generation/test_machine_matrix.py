import random

import numpy as np
import pytest

from job_shop_lib.generation import (
    generate_machine_matrix_with_recirculation,
    generate_machine_matrix_without_recirculation,
    get_default_machine_matrix_creator,
)
from job_shop_lib.exceptions import ValidationError


def test_machine_matrix_with_recirculation_shape_and_coverage():
    num_jobs = 6
    num_machines = 4
    rng = np.random.default_rng(123)
    mat = generate_machine_matrix_with_recirculation(
        num_jobs, num_machines, rng
    )
    # Shape (num_jobs, num_machines)
    assert mat.shape == (num_jobs, num_machines)
    # All machines used at least once
    assert set(mat.flatten()) == set(range(num_machines))


def test_machine_matrix_with_recirculation_validation_errors():
    with pytest.raises(ValidationError):
        generate_machine_matrix_with_recirculation(0, 3)
    with pytest.raises(ValidationError):
        generate_machine_matrix_with_recirculation(3, 0)


def test_machine_matrix_without_recirculation_validation_errors():
    with pytest.raises(ValidationError):
        generate_machine_matrix_without_recirculation(0, 3)
    with pytest.raises(ValidationError):
        generate_machine_matrix_without_recirculation(3, 0)


def test_machine_matrix_with_recirculation_determinism():
    seed = 9876
    rng1 = np.random.default_rng(seed)
    rng2 = np.random.default_rng(seed)
    m1 = generate_machine_matrix_with_recirculation(5, 3, rng1)
    m2 = generate_machine_matrix_with_recirculation(5, 3, rng2)
    assert np.array_equal(m1, m2)


def test_machine_matrix_without_recirculation_shape_and_permutation():
    num_jobs = 5
    num_machines = 3
    rng = np.random.default_rng(321)
    mat = generate_machine_matrix_without_recirculation(
        num_jobs, num_machines, rng
    )
    # Shape (num_jobs, num_machines)
    assert mat.shape == (num_jobs, num_machines)
    # Each row is a permutation of all machines
    expected = set(range(num_machines))
    for row in mat:
        assert set(row) == expected
        # no duplicates inside a row
        assert len(set(row)) == num_machines


def test_machine_matrix_without_recirculation_determinism():
    seed = 444
    rng1 = np.random.default_rng(seed)
    rng2 = np.random.default_rng(seed)
    m1 = generate_machine_matrix_without_recirculation(4, 4, rng1)
    m2 = generate_machine_matrix_without_recirculation(4, 4, rng2)
    assert np.array_equal(m1, m2)


def test_get_default_machine_matrix_creator_with_recirculation():
    creator = get_default_machine_matrix_creator(
        size_selector=lambda _: (5, 3)
    )
    seed = 2024
    out1 = creator(random.Random(seed))
    out2 = creator(random.Random(seed))
    # With recirculation underlying shape is (num_jobs, num_machines) => (5,3)
    assert len(out1) == 5
    assert all(len(row) == 3 for row in out1)
    assert out1 == out2  # deterministic with same seed
    # Coverage check
    assert {m for row in out1 for m in row} == {0, 1, 2}


def test_get_default_machine_matrix_creator_without_recirculation():
    creator = get_default_machine_matrix_creator(
        size_selector=lambda rng: (4, 2), with_recirculation=False
    )
    seed = 55
    out1 = creator(random.Random(seed))
    out2 = creator(random.Random(seed))
    # Without recirculation shape is (num_jobs, num_machines) => (4,2)
    assert len(out1) == 4
    assert all(len(row) == 2 for row in out1)
    assert out1 == out2
    # Each row should contain both machines 0 and 1 exactly once
    for row in out1:
        assert set(row) == {0, 1}
        assert len(row) == 2


if __name__ == "__main__":
    pytest.main()
