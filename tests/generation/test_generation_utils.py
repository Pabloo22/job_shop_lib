import pytest
import numpy as np

from job_shop_lib.exceptions import ValidationError
from job_shop_lib.generation import (
    generate_duration_matrix,
    generate_machine_matrix_with_recirculation,
    generate_machine_matrix_without_recirculation,
)


@pytest.fixture
def basic_params():
    return {"num_jobs": 3, "num_machines": 3, "duration_range": (1, 10)}


def test_generate_duration_matrix_shape(basic_params):
    """Test if the generated duration matrix has the correct shape."""
    duration_matrix = generate_duration_matrix(**basic_params)
    assert len(duration_matrix) == basic_params["num_jobs"]
    assert all(
        len(row) == basic_params["num_machines"] for row in duration_matrix
    )


def test_generate_duration_matrix_range(basic_params):
    """Test if all values in duration matrix are within the specified range."""
    duration_matrix = generate_duration_matrix(**basic_params)
    min_val, max_val = basic_params["duration_range"]

    for row in duration_matrix:
        assert all(min_val <= val <= max_val for val in row)


def test_generate_duration_matrix_different_seeds():
    """Test if different seeds generate different matrices."""
    params = {"num_jobs": 3, "num_machines": 3, "duration_range": (1, 10)}

    np.random.seed(42)
    matrix1 = generate_duration_matrix(**params)
    np.random.seed(43)
    matrix2 = generate_duration_matrix(**params)

    assert not np.array_equal(matrix1, matrix2)


def test_generate_machine_matrix_with_recirculation_shape(basic_params):
    """Test if the generated machine matrix with recirculation has correct
    shape."""
    matrix = generate_machine_matrix_with_recirculation(
        basic_params["num_jobs"], basic_params["num_machines"]
    )
    assert len(matrix) == basic_params["num_machines"]
    assert all(len(row) == basic_params["num_jobs"] for row in matrix)


def test_generate_machine_matrix_with_recirculation_values(basic_params):
    """Test if all machines are used in the matrix with recirculation."""
    matrix = generate_machine_matrix_with_recirculation(
        basic_params["num_jobs"], basic_params["num_machines"]
    )
    unique_machines = set(val for row in matrix for val in row)
    assert len(unique_machines) == basic_params["num_machines"]
    assert all(
        0 <= val < basic_params["num_machines"]
        for row in matrix
        for val in row
    )


def test_generate_machine_matrix_without_recirculation_shape(basic_params):
    """Test if the generated machine matrix without recirculation has correct
    shape."""
    matrix = generate_machine_matrix_without_recirculation(
        basic_params["num_jobs"], basic_params["num_machines"]
    )
    assert len(matrix) == basic_params["num_jobs"]
    assert all(len(row) == basic_params["num_machines"] for row in matrix)


def test_generate_machine_matrix_without_recirculation_values(basic_params):
    """Test if each job uses each machine exactly once without
    recirculation."""
    matrix = generate_machine_matrix_without_recirculation(
        basic_params["num_jobs"], basic_params["num_machines"]
    )

    for row in matrix:
        # Check if each machine appears exactly once in each job
        unique_machines = set(row)
        assert len(unique_machines) == basic_params["num_machines"]
        assert all(0 <= val < basic_params["num_machines"] for val in row)


def test_edge_cases():
    """Test edge cases with minimum values."""
    min_params = {"num_jobs": 1, "num_machines": 1, "duration_range": (1, 1)}

    # Test duration matrix
    duration_matrix = generate_duration_matrix(**min_params)  # type: ignore
    assert len(duration_matrix) == 1
    assert len(duration_matrix[0]) == 1
    assert duration_matrix[0][0] == 1

    # Test machine matrix with recirculation
    matrix_with_recirc = generate_machine_matrix_with_recirculation(1, 1)
    assert len(matrix_with_recirc) == 1
    assert len(matrix_with_recirc[0]) == 1
    assert matrix_with_recirc[0][0] == 0

    # Test machine matrix without recirculation
    matrix_without_recirc = generate_machine_matrix_without_recirculation(1, 1)
    assert len(matrix_without_recirc) == 1
    assert len(matrix_without_recirc[0]) == 1
    assert matrix_without_recirc[0][0] == 0


def test_invalid_inputs():
    """Test if functions handle invalid inputs appropriately."""

    with pytest.raises(ValidationError):
        generate_duration_matrix(0, 3, (1, 10))

    with pytest.raises(ValidationError):
        generate_duration_matrix(3, 0, (10, 1))

    with pytest.raises(ValidationError):
        generate_duration_matrix(3, 0, (1, 10))

    with pytest.raises(ValidationError):
        generate_duration_matrix(3, 3, (10, 1))

    with pytest.raises(ValidationError):
        generate_machine_matrix_with_recirculation(0, 3)

    with pytest.raises(ValidationError):
        generate_machine_matrix_with_recirculation(3, 0)


def test_rng_determinism():
    """Tests that passing a custom RNG with a fixed seed produces deterministic
    results."""
    import numpy as np
    from job_shop_lib.generation import (
        generate_duration_matrix,
        generate_machine_matrix_with_recirculation,
        generate_machine_matrix_without_recirculation,
    )

    params = {"num_jobs": 3, "num_machines": 3, "duration_range": (1, 10)}
    seed = 12345
    rng1 = np.random.default_rng(seed)
    rng2 = np.random.default_rng(seed)
    # Duration matrix
    mat1 = generate_duration_matrix(**params, rng=rng1)
    mat2 = generate_duration_matrix(**params, rng=rng2)
    assert np.array_equal(mat1, mat2)
    # Machine matrix with recirculation
    rng1 = np.random.default_rng(seed)
    rng2 = np.random.default_rng(seed)
    mat1 = generate_machine_matrix_with_recirculation(
        params["num_jobs"], params["num_machines"], rng=rng1
    )
    mat2 = generate_machine_matrix_with_recirculation(
        params["num_jobs"], params["num_machines"], rng=rng2
    )
    assert np.array_equal(mat1, mat2)
    # Machine matrix without recirculation
    rng1 = np.random.default_rng(seed)
    rng2 = np.random.default_rng(seed)
    mat1 = generate_machine_matrix_without_recirculation(
        params["num_jobs"], params["num_machines"], rng=rng1
    )
    mat2 = generate_machine_matrix_without_recirculation(
        params["num_jobs"], params["num_machines"], rng=rng2
    )
    assert np.array_equal(mat1, mat2)
