from collections.abc import Callable
import random

import numpy as np
from numpy.typing import NDArray

from job_shop_lib.exceptions import ValidationError


def get_default_duration_matrix_creator(
    duration_range: tuple[int, int] = (1, 99),
) -> Callable[
    [list[list[list[int]]] | list[list[int]], random.Random],
    list[list[int]],
]:
    """Creates a duration matrix generator function.

    Internally, it wraps :func:`generate_duration_matrix`.

    .. note::

       This function assumes that the machine matrix has the shape (num_jobs,
       num_machines).

    Args:
        duration_range:
            A tuple specifying the inclusive range for operation durations.

    Returns:
        A callable that generates a duration matrix of shape (num_jobs,
        num_machines) when called with a machine matrix and a
        `random.Random` instance.
    """

    def duration_matrix_creator(
        machine_matrix: list[list[list[int]]] | list[list[int]],
        rng: random.Random,
    ) -> list[list[int]]:
        seed_for_np = rng.randint(0, 2**16 - 1)
        numpy_rng = np.random.default_rng(seed_for_np)
        num_jobs = len(machine_matrix)
        num_machines = len(machine_matrix[0])
        return generate_duration_matrix(
            num_jobs, num_machines, duration_range, numpy_rng
        ).tolist()

    return duration_matrix_creator


def generate_duration_matrix(
    num_jobs: int,
    num_machines: int,
    duration_range: tuple[int, int],
    rng: np.random.Generator | None = None,
) -> NDArray[np.int32]:
    """Generates a duration matrix.

    Args:
        num_jobs: The number of jobs.
        num_machines: The number of machines.
        duration_range: The range of the duration values.
        rng: A numpy random number generator.

    Returns:
        A duration matrix with shape (num_jobs, num_machines).
    """
    rng = rng or np.random.default_rng()
    if duration_range[0] > duration_range[1]:
        raise ValidationError(
            "The lower bound of the duration range must be less than or equal "
            "to the upper bound."
        )
    if num_jobs <= 0:
        raise ValidationError("The number of jobs must be greater than 0.")
    if num_machines <= 0:
        raise ValidationError("The number of machines must be greater than 0.")

    return rng.integers(
        duration_range[0],
        duration_range[1] + 1,
        size=(num_jobs, num_machines),
        dtype=np.int32,
    )
