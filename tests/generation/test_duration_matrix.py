import random

import numpy as np
import pytest

from job_shop_lib.generation import (
    generate_duration_matrix,
    get_default_duration_matrix_creator,
)
from job_shop_lib.exceptions import ValidationError


def test_generate_duration_matrix_shape_and_range():
    rng = np.random.default_rng(123)
    mat = generate_duration_matrix(4, 5, (2, 7), rng)
    assert mat.shape == (4, 5)
    assert mat.min() >= 2 and mat.max() <= 7


def test_generate_duration_matrix_invalid_range():
    with pytest.raises(ValidationError):
        generate_duration_matrix(2, 2, (5, 4))  # invalid range


def test_generate_duration_matrix_invalid_jobs():
    with pytest.raises(ValidationError):
        generate_duration_matrix(0, 2, (1, 5))


def test_generate_duration_matrix_invalid_machines():
    with pytest.raises(ValidationError):
        generate_duration_matrix(2, 0, (1, 5))


def test_generate_duration_matrix_rng_determinism():
    seed = 999
    rng1 = np.random.default_rng(seed)
    rng2 = np.random.default_rng(seed)
    mat1 = generate_duration_matrix(3, 3, (1, 9), rng1)
    mat2 = generate_duration_matrix(3, 3, (1, 9), rng2)
    assert np.array_equal(mat1, mat2)


def test_get_default_duration_matrix_creator_basic():
    seed = 42
    python_rng = random.Random(seed)
    creator = get_default_duration_matrix_creator((3, 5))
    machine_matrix = [[0, 1, 2], [2, 1, 0]]  # shape (jobs=2, machines=3)
    durations = creator(machine_matrix, python_rng)
    assert len(durations) == 2
    assert all(len(row) == 3 for row in durations)
    flat = [d for row in durations for d in row]
    assert all(3 <= v <= 5 for v in flat)


def test_get_default_duration_matrix_creator_different_rngs_differ():
    seed1 = 7
    seed2 = 8
    creator = get_default_duration_matrix_creator((1, 10))
    mm = [[0, 1], [1, 0], [0, 1]]  # (3,2)
    out1 = creator(mm, random.Random(seed1))
    out2 = creator(mm, random.Random(seed2))
    # Extremely small chance they are equal; treated as different expectation
    assert out1 != out2


def test_get_default_duration_matrix_creator_deterministic_with_same_seed():
    seed = 101
    creator = get_default_duration_matrix_creator((4, 9))
    mm = [[0, 1], [1, 0]]
    rng1 = random.Random(seed)
    rng2 = random.Random(seed)
    out1 = creator(mm, rng1)
    out2 = creator(mm, rng2)
    assert out1 == out2
