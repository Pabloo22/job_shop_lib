import random

import pytest

from job_shop_lib.generation import range_size_selector, choice_size_selector


def test_range_size_selector_defaults():
    rng = random.Random(123)
    jobs, machines = range_size_selector(rng)
    assert 10 <= jobs <= 20
    assert 5 <= machines <= 10


def test_range_size_selector_enforce_jobs_ge_machines_basic():
    rng = random.Random(0)
    jobs, machines = range_size_selector(
        rng,
        num_jobs_range=(5, 5),
        num_machines_range=(1, 10),
        allow_less_jobs_than_machines=False,
    )
    assert jobs == 5
    assert machines <= jobs


def test_range_size_selector_min_greater_than_jobs_range_collapses():
    # num_machines_range minimum > possible jobs; should collapse to jobs.
    rng = random.Random(1)
    jobs, machines = range_size_selector(
        rng,
        num_jobs_range=(3, 3),
        num_machines_range=(5, 10),
        allow_less_jobs_than_machines=False,
    )
    assert jobs == 3
    # With the fix machines should now be capped at 3 instead of > jobs.
    assert machines == 3


def test_range_size_selector_determinism():
    seed = 42
    rng1 = random.Random(seed)
    rng2 = random.Random(seed)
    assert range_size_selector(
        rng1, (8, 12), (3, 6), True
    ) == range_size_selector(rng2, (8, 12), (3, 6), True)


def test_choice_size_selector_returns_option():
    rng = random.Random(99)
    options = [(1, 2), (3, 4), (5, 6)]
    assert choice_size_selector(rng, options) in options


def test_choice_size_selector_deterministic_seed():
    seed = 77
    options = [(1, 2), (3, 4), (5, 6)]
    rng1 = random.Random(seed)
    rng2 = random.Random(seed)
    assert choice_size_selector(rng1, options) == choice_size_selector(
        rng2, options
    )


def test_choice_size_selector_single_option():
    rng = random.Random(5)
    assert choice_size_selector(rng, [(7, 8)]) == (7, 8)


@pytest.mark.parametrize(
    "options",
    [
        [(1, 1)],
        [(2, 3), (4, 5), (6, 7)],
        [(10, 20), (30, 40)],
    ],
)
def test_choice_size_selector_valid_outputs(options):
    rng = random.Random(1234)
    for _ in range(20):
        assert choice_size_selector(rng, options) in options
