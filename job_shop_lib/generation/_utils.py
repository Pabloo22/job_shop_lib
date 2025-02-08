from typing import Tuple
import numpy as np
from numpy.typing import NDArray

from job_shop_lib.exceptions import ValidationError


def generate_duration_matrix(
    num_jobs: int, num_machines: int, duration_range: Tuple[int, int]
) -> NDArray[np.int32]:
    """Generates a duration matrix.

    Args:
        num_jobs: The number of jobs.
        num_machines: The number of machines.
        duration_range: The range of the duration values.

    Returns:
        A duration matrix with shape (num_jobs, num_machines).
    """
    if duration_range[0] > duration_range[1]:
        raise ValidationError(
            "The lower bound of the duration range must be less than or equal "
            "to the upper bound."
        )
    if num_jobs <= 0:
        raise ValidationError("The number of jobs must be greater than 0.")
    if num_machines <= 0:
        raise ValidationError("The number of machines must be greater than 0.")

    return np.random.randint(
        duration_range[0],
        duration_range[1] + 1,
        size=(num_jobs, num_machines),
        dtype=np.int32,
    )


def generate_machine_matrix_with_recirculation(
    num_jobs: int, num_machines: int
) -> NDArray[np.int32]:
    """Generate a machine matrix with recirculation.

    Args:
        num_jobs: The number of jobs.
        num_machines: The number of machines.

    Returns:
        A machine matrix with recirculation with shape (num_machines,
        num_jobs).
    """
    if num_jobs <= 0:
        raise ValidationError("The number of jobs must be greater than 0.")
    if num_machines <= 0:
        raise ValidationError("The number of machines must be greater than 0.")
    num_machines_is_correct = False
    while not num_machines_is_correct:
        machine_matrix: np.ndarray = np.random.randint(
            0, num_machines, size=(num_machines, num_jobs)
        )
        num_machines_is_correct = (
            len(np.unique(machine_matrix)) == num_machines
        )

    return machine_matrix


def generate_machine_matrix_without_recirculation(
    num_jobs: int, num_machines: int
) -> NDArray[np.int32]:
    """Generate a machine matrix without recirculation.

    Args:
        num_jobs: The number of jobs.
        num_machines: The number of machines.

    Returns:
        A machine matrix without recirculation.
    """
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
    machine_matrix = np.apply_along_axis(
        np.random.permutation, 1, machine_matrix
    )
    return machine_matrix


if __name__ == "__main__":

    NUM_JOBS = 3
    NUM_MACHINES = 3
    DURATION_RANGE = (1, 10)

    duration_matrix = generate_duration_matrix(
        num_jobs=NUM_JOBS,
        num_machines=NUM_MACHINES,
        duration_range=DURATION_RANGE,
    )
    print(duration_matrix)

    machine_matrix_with_recirculation = (
        generate_machine_matrix_with_recirculation(
            num_jobs=NUM_JOBS, num_machines=NUM_MACHINES
        )
    )
    print(machine_matrix_with_recirculation)

    machine_matrix_without_recirculation = (
        generate_machine_matrix_without_recirculation(
            num_jobs=NUM_JOBS, num_machines=NUM_MACHINES
        )
    )
    print(machine_matrix_without_recirculation)
