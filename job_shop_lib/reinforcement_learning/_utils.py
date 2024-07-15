"""Utility functions for reinforcement learning."""

from typing import TypeVar, Any

import numpy as np
from numpy.typing import NDArray

from job_shop_lib.exceptions import ValidationError

T = TypeVar("T", bound=np.number)


def add_padding(
    array: NDArray[Any],
    output_shape: tuple[int, ...],
    padding_value: float = -1,
    dtype: type[T] | None = None,
) -> NDArray[T]:
    """Adds padding to the array.

    Pads the input array to the specified output shape with a given padding
    value. If the ``dtype`` is not specified, the ``dtype`` of the input array
    is used.

    Args:
        array:
            The input array to be padded.
        output_shape:
            The desired shape of the output array.
        padding_value:
            The value to use for padding. Defaults to -1.
        dtype:
            The data type for the output array. Defaults to ``None``, in which
            case the dtype of the input array is used.

    Returns:
        The padded array with the specified output shape.

    Raises:
        ValidationError:
            If the output shape is smaller than the input shape.

    Examples:

    .. doctest::

        >>> array = np.array([[1, 2], [3, 4]])
        >>> add_padding(array, (3, 3))
        array([[ 1,  2, -1],
               [ 3,  4, -1],
               [-1, -1, -1]])

        >>> add_padding(array, (3, 3), padding_value=0)
        array([[1, 2, 0],
               [3, 4, 0],
               [0, 0, 0]])

        >>> bool_array = np.array([[True, False], [False, True]])
        >>> add_padding(bool_array, (3, 3), padding_value=False, dtype=int)
        array([[1, 0, 0],
               [0, 1, 0],
               [0, 0, 0]])

        >>> add_padding(bool_array, (3, 3), dtype=int)
        array([[ 1,  0, -1],
               [ 0,  1, -1],
               [-1, -1, -1]])
    """

    if np.any(np.less(output_shape, array.shape)):
        raise ValidationError(
            "Output shape must be greater than the input shape. "
            f"Got output shape: {output_shape}, input shape: {array.shape}."
        )

    if dtype is None:
        dtype = array.dtype.type

    padded_array = np.full(
        output_shape,
        fill_value=padding_value,
        dtype=dtype,
    )

    if array.size == 0:
        return padded_array

    slices = tuple(slice(0, dim) for dim in array.shape)
    padded_array[slices] = array
    return padded_array


if __name__ == "__main__":
    import doctest

    doctest.testmod()
