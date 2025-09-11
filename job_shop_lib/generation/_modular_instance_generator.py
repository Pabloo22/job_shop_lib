from collections.abc import Callable
from typing import Generator
import random

from job_shop_lib import JobShopInstance


def modular_instance_generator(
    machine_matrix_creator: Callable[
        [random.Random], list[list[list[int]]] | list[list[int]]
    ],
    duration_matrix_creator: Callable[
        [list[list[list[int]]] | list[list[int]], random.Random],
        list[list[int]],
    ],
    *,
    name_creator: Callable[[int], str] = lambda x: f"generated_instance_{x}",
    release_dates_matrix_creator: (
        Callable[
            [list[list[int]], random.Random],
            list[list[int]],
        ]
        | None
    ) = None,
    deadlines_matrix_creator: (
        Callable[[list[list[int]], random.Random], list[list[int | None]]]
        | None
    ) = None,
    due_dates_matrix_creator: (
        Callable[[list[list[int]], random.Random], list[list[int | None]]]
        | None
    ) = None,
    seed: int | None = None,
) -> Generator[JobShopInstance, None, None]:
    """Creates a generator function that produces job shop instances using
    the provided components.

    Args:
        machine_matrix_creator:
            A callable that creates a machine matrix.
        duration_matrix_creator:
            A callable that creates a duration matrix.
        name_creator:
            A callable that generates unique names for instances.
        release_dates_matrix_creator:
            An optional callable that generates release dates for jobs.
        deadlines_matrix_creator:
            An optional callable that generates deadlines for jobs.
        due_dates_matrix_creator:
            An optional callable that generates due dates for jobs.
        seed:
            An optional seed for random number generation.

    Yields:
        JobShopInstance:
            A generated job shop instance created using the generated matrices.

    Example:

        >>> from job_shop_lib.generation import (
        ...     get_default_machine_matrix_creator,
        ...     get_default_duration_matrix_creator,
        ...     modular_instance_generator,
        ... )
        >>> machine_matrix_gen = get_default_machine_matrix_creator(
        ...     size_selector=lambda rng: (3, 3),
        ...     with_recirculation=False,
        ... )
        >>> duration_matrix_gen = get_default_duration_matrix_creator(
        ...     duration_range=(1, 10),
        ... )
        >>> instance_gen = modular_instance_generator(
        ...     machine_matrix_creator=machine_matrix_gen,
        ...     duration_matrix_creator=duration_matrix_gen,
        ...     seed=42,
        ... )
        >>> instance = next(instance_gen)
        >>> print(instance)
        JobShopInstance(name=generated_instance_0, num_jobs=3, num_machines=3)
        >>> print(instance.duration_matrix_array)
        [[ 5.  6.  4.]
         [ 5.  7. 10.]
         [ 9.  9.  5.]]

    .. versionadded:: 1.7.0
    """
    rng = random.Random(seed)
    i = 0
    while True:
        machine_matrix = machine_matrix_creator(rng)
        duration_matrix = duration_matrix_creator(machine_matrix, rng)
        release_dates = (
            release_dates_matrix_creator(duration_matrix, rng)
            if release_dates_matrix_creator
            else None
        )
        deadlines = (
            deadlines_matrix_creator(duration_matrix, rng)
            if deadlines_matrix_creator
            else None
        )
        due_dates = (
            due_dates_matrix_creator(duration_matrix, rng)
            if due_dates_matrix_creator
            else None
        )
        instance = JobShopInstance.from_matrices(
            duration_matrix,
            machine_matrix,
            name=name_creator(i),
            release_dates_matrix=release_dates,
            deadlines_matrix=deadlines,
            due_dates_matrix=due_dates,
        )
        i += 1
        yield instance
