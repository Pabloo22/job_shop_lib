import random


def range_size_selector(
    rng: random.Random,
    num_jobs_range: tuple[int, int] = (10, 20),
    num_machines_range: tuple[int, int] = (5, 10),
    allow_less_jobs_than_machines: bool = True,
) -> tuple[int, int]:
    """Selects the number of jobs and machines based on the provided ranges
    and constraints.

    Args:
        rng:
            A ``random.Random`` instance.
        num_jobs_range:
            A tuple specifying the inclusive range for the number of jobs.
        num_machines_range:
            A tuple specifying the inclusive range for the number of machines.
        allow_less_jobs_than_machines:
            If ``False``, ensures that the number of jobs is not less than the
            number of machines.

    Returns:
        A tuple containing the selected number of jobs and machines.
    """
    num_jobs = rng.randint(num_jobs_range[0], num_jobs_range[1])

    min_num_machines, max_num_machines = num_machines_range
    if not allow_less_jobs_than_machines:
        # Cap the maximum machines to the sampled number of jobs.
        max_num_machines = min(max_num_machines, num_jobs)
        # If min > capped max, collapse interval so we return a valid value
        # (e.g. jobs=3, range=(5,10)).
        if min_num_machines > max_num_machines:
            min_num_machines = max_num_machines
    num_machines = rng.randint(min_num_machines, max_num_machines)

    return num_jobs, num_machines


def choice_size_selector(
    rng: random.Random,
    options: list[tuple[int, int]],
) -> tuple[int, int]:
    """Selects the number of jobs and machines from a list of options.

    Args:
        rng:
            A ``random.Random`` instance.
        options:
            A list of tuples, where each tuple contains a pair of integers
            representing the number of jobs and machines.

    Returns:
        A tuple containing the selected number of jobs and machines.
    """
    return rng.choice(options)
