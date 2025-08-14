import random

import pytest

from job_shop_lib import Schedule
from job_shop_lib.dispatching.rules import DispatchingRuleSolver
from job_shop_lib.metaheuristics import (
    swap_adjacent_operations,
    swap_random_operations,
    swap_in_critical_path,
)
from job_shop_lib.benchmarking import load_benchmark_instance


def _diff_positions(a: list[int], b: list[int]) -> list[int]:
    return [i for i, (x, y) in enumerate(zip(a, b)) if x != y]


def _is_adjacent_swap(before: list[int], after: list[int]) -> bool:
    if len(before) != len(after):
        return False
    diffs = _diff_positions(before, after)
    if len(diffs) != 2:
        return False
    i, j = diffs
    if j != i + 1:
        return False
    # elements must be swapped
    return (
        before[i] == after[j]
        and before[j] == after[i]
        and before[:i] == after[:i]
        and before[j + 1 :] == after[j + 1 :]
    )


def _is_two_position_swap(before: list[int], after: list[int]) -> bool:
    if len(before) != len(after):
        return False
    diffs = _diff_positions(before, after)
    if len(diffs) != 2:
        return False
    i, j = diffs
    return (
        before[i] == after[j]
        and before[j] == after[i]
        and before[: min(i, j)] == after[: min(i, j)]
        and before[max(i, j) + 1 :] == after[max(i, j) + 1 :]
    )


def _assert_valid_schedule(schedule: Schedule) -> None:
    # Should not raise
    Schedule.check_schedule(schedule.schedule)


def test_swap_adjacent_operations_valid_and_local_change(
    example_schedule: Schedule, seeded_rng: random.Random
):
    before = example_schedule.job_sequences()
    neighbor = swap_adjacent_operations(example_schedule, seeded_rng)
    _assert_valid_schedule(neighbor)

    after = neighbor.job_sequences()
    # Either unchanged (no feasible swap found) or exactly one machine
    # changed via adjacent swap
    diff_machines = [
        m for m, (b, a) in enumerate(zip(before, after)) if b != a
    ]
    assert len(diff_machines) in (0, 1)
    if diff_machines:
        m = diff_machines[0]
        assert _is_adjacent_swap(before[m], after[m])


def test_swap_random_operations_valid_and_two_position_change(
    example_schedule: Schedule, seeded_rng: random.Random
):
    before = example_schedule.job_sequences()
    neighbor = swap_random_operations(example_schedule, seeded_rng)
    _assert_valid_schedule(neighbor)

    after = neighbor.job_sequences()
    diff_machines = [
        m for m, (b, a) in enumerate(zip(before, after)) if b != a
    ]
    assert len(diff_machines) in (0, 1)
    if diff_machines:
        m = diff_machines[0]
        assert _is_two_position_swap(before[m], after[m])


@pytest.mark.parametrize("instance_name", [f"la{i:02d}" for i in range(1, 6)])
def test_swap_in_critical_path_returns_valid_neighbor(
    instance_name: str, seeded_rng: random.Random
):
    instance = load_benchmark_instance(instance_name)
    schedule = DispatchingRuleSolver().solve(instance)

    neighbor = swap_in_critical_path(schedule, seeded_rng)
    _assert_valid_schedule(neighbor)

    # Preferably the neighbor changes something; if no suitable CP pair
    # exists, a fallback may keep it same
    if neighbor != schedule:
        before = schedule.job_sequences()
        after = neighbor.job_sequences()
        # exactly one machine should have changed order
        diff_machines = [
            m for m, (b, a) in enumerate(zip(before, after)) if b != a
        ]
        assert len(diff_machines) == 1


def test_generators_return_same_instance_object(
    example_schedule: Schedule
):
    for gen in (
        swap_adjacent_operations,
        swap_random_operations,
        swap_in_critical_path,
    ):
        neighbor = gen(example_schedule, None)
        assert neighbor.instance is example_schedule.instance
        _assert_valid_schedule(neighbor)
