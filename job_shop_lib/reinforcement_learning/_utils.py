"""Utility functions for reinforcement learning."""

from typing import TypeVar, Any

import numpy as np
from numpy.typing import NDArray

from job_shop_lib import ScheduledOperation
from job_shop_lib.exceptions import ValidationError
from job_shop_lib.dispatching import OptimalOperationsObserver, Dispatcher

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


def create_edge_type_dict(
    edge_index: NDArray[T],
    type_ranges: dict[str, tuple[int, int]],
    relationship: str = "to",
) -> dict[tuple[str, str, str], NDArray[T]]:
    """Organizes edges based on node types.

    Args:
        edge_index:
            numpy array of shape (2, E) where E is number of edges
        type_ranges: dict[str, tuple[int, int]]
            Dictionary mapping type names to their corresponding index ranges
            [start, end) in the ``edge_index`` array.
        relationship:
            A string representing the relationship type between nodes.

    Returns:
        A dictionary with keys (type_i, relationship, type_j) and values as
        edge indices
    """
    edge_index_dict: dict[tuple[str, str, str], NDArray] = {}
    for type_name_i, (start_i, end_i) in type_ranges.items():
        for type_name_j, (start_j, end_j) in type_ranges.items():
            key: tuple[str, str, str] = (
                type_name_i,
                relationship,
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


def map_values(array: NDArray[T], mapping: dict[int, int]) -> NDArray[T]:
    """Maps values in an array using a mapping.

    Args:
        array:
            An NumPy array.

    Returns:
        A NumPy array where each element has been replaced by its
        corresponding value from the mapping.

    Raises:
        ValidationError:
            If the array contains values that are not in the mapping.

    Examples:
        >>> map_values(np.array([1, 2, 3]), {1: 10, 2: 20, 3: 30})
        array([10, 20, 30])

        >>> map_values(np.array([1, 2]), {1: 10, 2: 10, 3: 30})
        array([10, 10])

    """
    if array.size == 0:
        return array
    try:
        vectorized_mapping = np.vectorize(mapping.get)
        return vectorized_mapping(array)
    except TypeError as e:
        raise ValidationError(
            "The array contains values that are not in the mapping."
        ) from e


def get_optimal_actions(
    optimal_ops_observer: OptimalOperationsObserver,
    available_operations_with_ids: list[tuple[int, int, int]],
) -> dict[tuple[int, int, int], int]:
    """Indicates if each action is optimal according to a
    :class:`~job_shop_lib.dispatching.OptimalOperationsObserver` instance.

    Args:
        optimal_ops_observer: The observer that provides optimal operations.
        available_operations_with_ids: List of available operations with their
        IDs (operation_id, machine_id, job_id).

    Returns:
        A dictionary mapping each tuple
        (operation_id, machine_id, job_id) in the available actions to a binary
        indicator (1 if optimal, 0 otherwise).
    """
    optimal_actions = {}
    optimal_ops = optimal_ops_observer.optimal_available
    optimal_ops_ids = [
        (op.operation_id, op.machine_id, op.job_id) for op in optimal_ops
    ]
    for operation_id, machine_id, job_id in available_operations_with_ids:
        is_optimal = (operation_id, machine_id, job_id) in optimal_ops_ids
        optimal_actions[(operation_id, machine_id, job_id)] = int(is_optimal)
    return optimal_actions


def get_deadline_violation_penalty(
    scheduled_operation: ScheduledOperation,
    unused_dispatcher: Dispatcher,
    deadline_penalty_factor: float = 10_000,
) -> float:
    """Compute the penalty for a scheduled operation that violates its
    deadline.

    Args:
        scheduled_operation:
            The scheduled operation to evaluate.
        unused_dispatcher:
            This argument is unused but included for compatibility with the
            penalty function signature.
        deadline_penalty_factor:
            Cost added for each operation that
            finishes after its deadline. Defaults to 10_000.
    Returns:
        The penalty for the scheduled operation if it violates its deadline,
        otherwise 0.

    .. versionadded:: 1.7.0
    """
    if (
        scheduled_operation.operation.deadline is not None
        and scheduled_operation.end_time
        > scheduled_operation.operation.deadline
    ):
        return deadline_penalty_factor
    return 0.0


def get_due_date_violation_penalty(
    scheduled_operation: ScheduledOperation,
    unused_dispatcher: Dispatcher,
    due_date_penalty_factor: float = 100,
) -> float:
    """Compute the penalty for a scheduled operation that violates its
    due date.

    Args:
        scheduled_operation:
            The scheduled operation to evaluate.
        unused_dispatcher:
            This argument is unused but included for compatibility with the
            penalty function signature.
        due_date_penalty_factor:
            Cost added for each operation that
            finishes after its due date. Defaults to 100.
    Returns:
        The penalty for the scheduled operation if it violates its due date,
        otherwise 0.

    .. versionadded:: 1.7.0
    """
    if (
        scheduled_operation.operation.due_date is not None
        and scheduled_operation.end_time
        > scheduled_operation.operation.due_date
    ):
        return due_date_penalty_factor
    return 0.0
