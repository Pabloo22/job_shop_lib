import pytest
import numpy as np
from numpy.typing import NDArray

from job_shop_lib import ValidationError
from job_shop_lib.reinforcement_learning import add_padding


def test_add_padding_int_array():
    array = np.array(
        [
            [1, 2],
            [3, 4],
        ],
        dtype=np.int32,
    )
    output_shape = (3, 3)
    result: NDArray[np.int32] = add_padding(array, output_shape)
    expected = np.array(
        [
            [1, 2, -1],
            [3, 4, -1],
            [-1, -1, -1],
        ],
    )
    assert np.array_equal(result, expected)


def test_add_padding_float_array():
    array = np.array(
        [
            [1.0, 2.0],
            [3.0, 4.0],
        ],
        dtype=np.float32,
    )
    output_shape = (3, 3)
    result: NDArray[np.float32] = add_padding(array, output_shape)
    expected = np.array(
        [
            [1.0, 2.0, -1.0],
            [3.0, 4.0, -1.0],
            [-1.0, -1.0, -1.0],
        ],
    )
    assert np.array_equal(result, expected)


def test_add_padding_bool_array():
    array = np.array(
        [
            [True, False],
            [False, True],
        ],
        dtype=bool,
    )
    output_shape = (3, 3)
    result: NDArray[np.bool_] = add_padding(
        array, output_shape, padding_value=False
    )
    expected = np.array(
        [
            [True, False, False],
            [False, True, False],
            [False, False, False],
        ],
    )
    assert np.array_equal(result, expected)


def test_add_padding_int_array_with_padding_value():
    array = np.array(
        [
            [1, 2],
            [3, 4],
        ],
        dtype=np.int32,
    )
    output_shape = (3, 3)
    padding_value = 0
    result: NDArray[np.int32] = add_padding(array, output_shape, padding_value)
    expected = np.array(
        [
            [1, 2, 0],
            [3, 4, 0],
            [0, 0, 0],
        ],
    )
    assert np.array_equal(result, expected)


def test_add_padding_bool_array_with_dtype():
    array = np.array(
        [
            [True, False],
            [False, True],
        ],
        dtype=bool,
    )
    output_shape = (3, 3)
    result = add_padding(
        array, output_shape, dtype=np.int32
    )
    expected = np.array(
        [
            [1, 0, -1],
            [0, 1, -1],
            [-1, -1, -1],
        ],
    )
    assert np.array_equal(result, expected)


def test_add_padding_raises_error():
    array = np.array(
        [
            [1, 2],
            [3, 4],
        ],
        dtype=np.int32,
    )
    output_shape = (1, 3)
    with pytest.raises(ValidationError):
        add_padding(array, output_shape)


if __name__ == "__main__":
    pytest.main(["-vv", __file__])
