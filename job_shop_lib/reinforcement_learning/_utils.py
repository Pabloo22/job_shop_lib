"""Utility functions for reinforcement learning."""

from typing import TypeVar, Any, Type, Literal

import numpy as np
from numpy.typing import NDArray

from job_shop_lib.exceptions import ValidationError

T = TypeVar("T", bound=np.number)


def add_padding(
    array: NDArray[Any],
    output_shape: tuple[int, ...],
    padding_value: float = -1,
    dtype: Type[T] | None = None,
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


def create_edge_type_dict(
    edge_index: NDArray[T], type_ranges: dict[str, tuple[int, int]]
) -> dict[tuple[str, Literal["to"], str], NDArray[T]]:
    """Organizes edges based on node types.

    Args:
        edge_index:
            numpy array of shape (2, E) where E is number of edges
        type_ranges: dict[str, tuple[int, int]]
            Dictionary mapping type names to their corresponding index ranges
            [start, end) in the ``edge_index`` array.

    Returns:
        A dictionary with keys (type_i, "to", type_j) and values as edge
        indices
    """
    edge_index_dict: dict[tuple[str, Literal["to"], str], NDArray] = {}
    for type_name_i, (start_i, end_i) in type_ranges.items():
        for type_name_j, (start_j, end_j) in type_ranges.items():
            key: tuple[str, Literal["to"], str] = (
                type_name_i,
                "to",
                type_name_j,
            )
            # Find edges where source is in type_i and target is in type_j
            mask = (
                (edge_index[0] >= start_i)
                & (edge_index[0] < end_i)
                & (edge_index[1] >= start_j)
                & (edge_index[1] < end_j)
            )
            edge_index_dict[key] = edge_index[:, mask]

    return edge_index_dict


if __name__ == "__main__":
    import doctest

    doctest.testmod()
