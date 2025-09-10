from typing import Sequence, Callable
import random

from job_shop_lib.exceptions import ValidationError


ReleaseDateStrategy = Callable[[random.Random, int], int]


def create_release_dates_matrix(
    duration_matrix: list[list[int]],
    strategy: ReleaseDateStrategy | None = None,
    rng: random.Random | None = None,
) -> list[list[int]]:
    """Generate per-operation release dates for ragged job durations.

    Args:
        duration_matrix:
            Ragged list of per-job operation durations.
        strategy:
            Callable implementing the release date policy. If ``None``
            a default mixed strategy (alpha=0.7, beta=0.3) is built using the
            computed horizon proxy.
        rng:
            Optional numpy random generator (one will be created if omitted).

    Returns:
        A ragged list mirroring ``duration_matrix`` structure with per-
        operation release dates.
    """
    rng = rng or random.Random()

    num_jobs = len(duration_matrix)
    if num_jobs == 0:
        return []

    if strategy is None:
        horizon_proxy = compute_horizon_proxy(duration_matrix)
        strategy = mixed_release_date_strategy(0.7, 0.3, horizon_proxy)

    release_dates_matrix: list[list[int]] = []
    for job_durations in duration_matrix:
        job_release_dates: list[int] = []
        cumulative_previous_duration = 0
        for duration_value in job_durations:
            release_date_value = strategy(rng, cumulative_previous_duration)
            job_release_dates.append(release_date_value)
            cumulative_previous_duration += int(duration_value)
        release_dates_matrix.append(job_release_dates)

    return release_dates_matrix


def compute_horizon_proxy(duration_matrix: Sequence[Sequence[int]]) -> int:
    """Compute the horizon proxy used previously for the mixed strategy.

    It is defined as: int(total_duration / avg_operations_per_job)
    with protections against division by zero.

    Args:
        duration_matrix:
            Ragged list of per-job operation durations.

    .. seealso::
        :meth:`job_shop_lib.JobShopInstance.duration_matrix`
    """
    num_jobs = len(duration_matrix)
    if num_jobs == 0:
        return 0
    total_duration = sum(sum(job) for job in duration_matrix)
    total_operations = sum(len(job) for job in duration_matrix)
    avg_ops_per_job = total_operations / max(1, num_jobs)
    return int(total_duration / max(1, avg_ops_per_job))


def independent_release_date_strategy(
    max_release_time: int,
) -> ReleaseDateStrategy:
    """Factory for an independent (pure random) release date strategy.

    Args:
        max_release_time:
            Inclusive upper bound for the random value.
    """
    if max_release_time < 0:
        raise ValidationError("'max_release_time' must be >= 0.")

    def _strategy(rng: random.Random, unused_cumulative_prev: int) -> int:
        return int(rng.randint(0, max_release_time))

    return _strategy


def cumulative_release_date_strategy(
    backward_slack: int = 0,
) -> ReleaseDateStrategy:
    """Factory for a cumulative strategy allowing backward slack.

    The release date is the cumulative previous processing time potentially
    reduced by a random slack in ``[0, backward_slack]`` (never below zero).
    """
    if backward_slack < 0:
        raise ValidationError("'backward_slack' must be >= 0.")

    def _strategy(rng: random.Random, cumulative_prev: int) -> int:
        if backward_slack > 0:
            slack_value = int(rng.randint(0, backward_slack))
        else:
            slack_value = 0
        return max(0, cumulative_prev - slack_value)

    return _strategy


def mixed_release_date_strategy(
    alpha: float,
    beta: float,
    horizon_proxy: int,
) -> ReleaseDateStrategy:
    """Factory for the mixed heuristic strategy.

    release_date = alpha * cumulative_previous + U(0, beta * horizon_proxy)

    Args:
        alpha:
            Weight in [0,1] for the proportional cumulative component.
        beta:
            Weight in [0,1] scaling the random component upper bound.
        horizon_proxy:
            Non-negative proxy for the time horizon (e.g. derived
            from durations to scale the random component consistently).
    """
    if not 0.0 <= alpha <= 1.0:
        raise ValidationError("'alpha' must be in [0, 1].")
    if not 0.0 <= beta <= 1.0:
        raise ValidationError("'beta' must be in [0, 1].")
    if horizon_proxy < 0:
        raise ValidationError("'horizon_proxy' must be >= 0.")

    random_component_upper = int(beta * horizon_proxy)

    def _strategy(rng: random.Random, cumulative_prev: int) -> int:
        if random_component_upper > 0:
            random_component = int(rng.randint(0, random_component_upper))
        else:
            random_component = 0
        return int(alpha * cumulative_prev) + random_component

    return _strategy
