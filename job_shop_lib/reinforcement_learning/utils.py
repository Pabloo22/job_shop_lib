"""Utility functions for reinforcement learning."""

import numpy as np

from job_shop_lib import ValidationError


def add_padding(
    array: np.ndarray,
    output_shape: tuple[int, ...],
    padding_value: float = -1,
    dtype: type[np.number] | None = None,
) -> np.ndarray:
    """Adds padding to the array."""

    if np.any(np.less(output_shape, array.shape)):
        raise ValidationError(
            "Output shape must be greater than the input shape. "
            f"Got output shape: {output_shape}, input shape: {array.shape}."
        )

    if dtype is None:
        dtype = array.dtype

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
