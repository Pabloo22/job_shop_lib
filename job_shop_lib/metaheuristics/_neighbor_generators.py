from collections.abc import Callable
import random

from job_shop_lib import Schedule, ScheduledOperation
from job_shop_lib.exceptions import ValidationError


NeighborGenerator = Callable[[Schedule, random.Random], Schedule]

_MAX_ATTEMPTS = 1000


def _swap_with_index_picker(
    schedule: Schedule,
    random_generator: random.Random | None,
    index_picker: Callable[[list, random.Random], tuple[int, int]],
) -> Schedule:
    """Generates a neighbor schedule by swapping two positions chosen by a
    strategy.

    This private helper applies a swap on a randomly selected machine whose
    sequence has at least two operations. The actual indices to swap are
    chosen by the provided picker function. It attempts up to a fixed number
    of times to produce a valid neighbor. If all attempts fail, it returns
    the original schedule unchanged.

    Args:
        schedule:
            Current schedule to perturb.

        random_generator:
            Source of randomness. If ``None``, a new generator is created.

        index_picker:
            Function that receives a machine sequence and a random generator
            and returns two indices to swap.

    Returns:
        A valid neighbor schedule if a feasible swap is found, otherwise the
        original schedule.
    """
    if random_generator is None:
        random_generator = random.Random()
    job_sequences = schedule.job_sequences()
    valid_machines = [i for i, seq in enumerate(job_sequences) if len(seq) > 1]
    if not valid_machines:
        return schedule

    for _ in range(_MAX_ATTEMPTS):
        machine_id = random_generator.choice(valid_machines)
        sequence = job_sequences[machine_id]
        idx1, idx2 = index_picker(sequence, random_generator)
        sequence[idx1], sequence[idx2] = sequence[idx2], sequence[idx1]
        try:
            return Schedule.from_job_sequences(
                schedule.instance, job_sequences
            )
        except ValidationError:
            pass
    return schedule


def swap_adjacent_operations(
    schedule: Schedule, random_generator: random.Random | None = None
) -> Schedule:
    """Generates a neighbor schedule by swapping two adjacent operations.

    Selects a machine at random with at least two operations and swaps a pair
    of adjacent operations in its sequence. Internally tries several times to
    produce a valid neighbor; if none is found, the original schedule is
    returned.

    Args:
        schedule:
            Current schedule to perturb.

        random_generator:
            Source of randomness. If ``None``, a new generator is created.

    Returns:
        A valid neighbor schedule with one adjacent swap applied, or the
        original schedule if no valid swap is found.
    """

    def adjacent_picker(seq: list, rng: random.Random) -> tuple[int, int]:
        idx = rng.randint(0, len(seq) - 2)
        return idx, idx + 1

    return _swap_with_index_picker(schedule, random_generator, adjacent_picker)


def swap_random_operations(
    schedule: Schedule, random_generator: random.Random | None = None
) -> Schedule:
    """Generates a neighbor schedule by swapping two random operations.

    Selects a machine at random with at least two operations and swaps two
    randomly chosen positions in its sequence. Internally tries several times
    to produce a valid neighbor; if none is found, the original schedule is
    returned.

    Args:
        schedule:
            Current schedule to perturb.

        random_generator:
            Source of randomness. If ``None``, a new generator is created.

    Returns:
        A valid neighbor schedule with one random swap applied, or the
        original schedule if no valid swap is found.
    """

    def random_picker(seq: list, rng: random.Random) -> tuple[int, int]:
        idx1, idx2 = rng.sample(range(len(seq)), 2)
        return idx1, idx2

    return _swap_with_index_picker(schedule, random_generator, random_picker)


def swap_in_critical_path(
    schedule: Schedule, random_generator: random.Random | None = None
) -> Schedule:
    """Generates a neighbor by targeting swaps on the critical path.

    This operator focuses on pairs of consecutive scheduled operations along
    the current critical path that share the same machine. Swapping such
    operations directly perturbs the longest-duration chain of precedence
    and resource constraints that determines the makespan.

    Why target the critical path:

    - The makespan is the length of the critical path; operations not on it
      typically have slack, so reordering them often does not improve the
      objective. By contrast, modifying machine order on the critical path
      can shorten the longest path or unlock constraints that reduce
      blocking and idle times.
    - Swapping consecutive critical operations on the same machine always
      results in a feasible schedule.

    Behavior:

    - Identifies all consecutive pairs on the critical path that run on the
      same machine and swaps one of them at random.
    - If no such pairs exist, it falls back to a standard adjacent swap.

    Args:
        schedule:
            Current schedule to perturb.

        random_generator:
            Source of randomness. If ``None``, a new generator is created.

    Returns:
        A valid neighbor schedule that prioritizes swaps on the critical
        path, or a neighbor produced by an adjacent swap fallback when none
        applies.
    """
    if random_generator is None:
        random_generator = random.Random()

    critical_path = schedule.critical_path()
    possible_swaps: list[tuple[ScheduledOperation, ScheduledOperation]] = []
    for i, current_scheduled_op in enumerate(critical_path[:-1]):
        next_scheduled_op = critical_path[i + 1]
        if current_scheduled_op.machine_id == next_scheduled_op.machine_id:
            possible_swaps.append((current_scheduled_op, next_scheduled_op))

    if not possible_swaps:
        return swap_adjacent_operations(schedule, random_generator)

    op1, op2 = random_generator.choice(possible_swaps)
    job_sequences = schedule.job_sequences()
    machine_id = op1.machine_id
    idx1 = job_sequences[machine_id].index(op1.operation.job_id)
    idx2 = job_sequences[machine_id].index(op2.operation.job_id)

    job_sequences[machine_id][idx1], job_sequences[machine_id][idx2] = (
        job_sequences[machine_id][idx2],
        job_sequences[machine_id][idx1],
    )
    return Schedule.from_job_sequences(schedule.instance, job_sequences)
