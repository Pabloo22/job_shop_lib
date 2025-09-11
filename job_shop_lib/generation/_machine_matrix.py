from collections.abc import Callable
import random

import numpy as np
from numpy.typing import NDArray

from job_shop_lib.exceptions import ValidationError


def get_default_machine_matrix_creator(
    size_selector: Callable[[random.Random], tuple[int, int]] = (
        lambda _: (10, 10)
    ),
    with_recirculation: bool = True,
) -> Callable[[random.Random], list[list[list[int]]] | list[list[int]]]:
    """Creates a machine matrix generator function.

    Internally, it wraps either
    :func:`generate_machine_matrix_with_recirculation`
    or :func:`generate_machine_matrix_without_recirculation`
    based on the `with_recirculation` parameter.

    .. note::

       The generated machine matrix will have the shape (num_jobs,
       num_machines).

    Args:
        rng:
            A random.Random instance.
        size_selector:
            A callable that takes a random.Random instance and returns a
            tuple (num_jobs, num_machines).
        with_recirculation:
            If ``True``, generates a machine matrix with recirculation;
            otherwise, without recirculation. Recirculation means that a job
            can visit the same machine more than once.

    Returns:
        A callable that generates a machine matrix when called with a
        random.Random instance.
    """

    def generator(
        rng: random.Random,
    ) -> list[list[list[int]]]:
        num_jobs, num_machines = size_selector(rng)
        seed_for_np = rng.randint(0, 2**16 - 1)
        numpy_rng = np.random.default_rng(seed_for_np)
        if with_recirculation:
            return generate_machine_matrix_with_recirculation(
                num_jobs, num_machines, numpy_rng
            ).tolist()

        return generate_machine_matrix_without_recirculation(
            num_jobs, num_machines, numpy_rng
        ).tolist()

    return generator


def generate_machine_matrix_with_recirculation(
    num_jobs: int, num_machines: int, rng: np.random.Generator | None = None
) -> NDArray[np.int32]:
    """Generate a machine matrix with recirculation.

    Args:
        num_jobs: The number of jobs.
        num_machines: The number of machines.
        rng: A numpy random number generator.

    Returns:
        A machine matrix with recirculation with shape (num_jobs,
        num_machines).
    """
    rng = rng or np.random.default_rng()
    if num_jobs <= 0:
        raise ValidationError("The number of jobs must be greater than 0.")
    if num_machines <= 0:
        raise ValidationError("The number of machines must be greater than 0.")
    num_machines_is_correct = False
    while not num_machines_is_correct:
        machine_matrix: np.ndarray = rng.integers(
            0, num_machines, size=(num_jobs, num_machines), dtype=np.int32
        )
        num_machines_is_correct = (
            len(np.unique(machine_matrix)) == num_machines
        )

    return machine_matrix


def generate_machine_matrix_without_recirculation(
    num_jobs: int, num_machines: int, rng: np.random.Generator | None = None
) -> NDArray[np.int32]:
    """Generate a machine matrix without recirculation.

    Args:
        num_jobs: The number of jobs.
        num_machines: The number of machines.
        rng: A numpy random number generator.

    Returns:
        A machine matrix without recirculation.
    """
    rng = rng or np.random.default_rng()
    if num_jobs <= 0:
        raise ValidationError("The number of jobs must be greater than 0.")
    if num_machines <= 0:
        raise ValidationError("The number of machines must be greater than 0.")
    # Start with an arange repeated:
    # m1: [0, 1, 2]
    # m2: [0, 1, 2]
    # m3: [0, 1, 2]
    machine_matrix = np.tile(
        np.arange(num_machines).reshape(1, num_machines),
        (num_jobs, 1),
    )
    # Shuffle the columns:
    machine_matrix = np.apply_along_axis(rng.permutation, 1, machine_matrix)
    return machine_matrix
