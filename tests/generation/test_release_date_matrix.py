import random

import pytest

from job_shop_lib.exceptions import ValidationError
from job_shop_lib.generation import (
    create_release_dates_matrix,
    compute_horizon_proxy,
    get_independent_release_date_strategy,
    get_cumulative_release_date_strategy,
    get_mixed_release_date_strategy,
)


def test_independent_strategy_basic():
    strategy = get_independent_release_date_strategy(5)
    rng = random.Random(123)
    values = [strategy(rng, 0) for _ in range(10)]
    assert all(0 <= v <= 5 for v in values)
    # Determinism
    rng2 = random.Random(123)
    values2 = [strategy(rng2, 0) for _ in range(10)]
    assert values == values2


def test_independent_strategy_invalid():
    with pytest.raises(ValidationError):
        get_independent_release_date_strategy(-1)


def test_cumulative_strategy_no_slack():
    strat = get_cumulative_release_date_strategy(0)
    rng = random.Random(0)
    # Should return cumulative prev unchanged (non-negative) when slack=0
    assert strat(rng, 10) == 10


def test_cumulative_strategy_with_slack():
    strat = get_cumulative_release_date_strategy(5)
    rng = random.Random(1)
    # Generate multiple to sample slack branch
    results = {strat(rng, 20) for _ in range(20)}
    # All results >= 20 and <= 25 (20 + max slack)
    assert all(20 <= r <= 25 for r in results)
    # At least one value different from 20 to ensure slack applied
    assert any(r != 20 for r in results)


def test_cumulative_strategy_invalid():
    with pytest.raises(ValidationError):
        get_cumulative_release_date_strategy(-2)


def test_mixed_strategy_basic():
    horizon = 50
    strat = get_mixed_release_date_strategy(
        alpha=0.5, beta=0.4, horizon_proxy=horizon
    )
    rng = random.Random(2)
    v = strat(rng, 40)  # = 0.5*40 + random in [0, 0.4*50]
    assert 20 <= v <= 20 + int(0.4 * horizon)


def test_mixed_strategy_zero_random_component():
    # horizon_proxy=0 => random_component_upper=0 => no random addition
    strat = get_mixed_release_date_strategy(
        alpha=0.3, beta=0.9, horizon_proxy=0
    )
    rng = random.Random(0)
    assert strat(rng, 100) == int(0.3 * 100)


def test_mixed_strategy_invalid_params():
    with pytest.raises(ValidationError):
        get_mixed_release_date_strategy(alpha=0.5, beta=0.5, horizon_proxy=-1)


def test_compute_horizon_proxy_empty():
    assert compute_horizon_proxy([]) == 0


def test_compute_horizon_proxy_non_empty():
    # total_duration =3+2+4 =9; ops=3; jobs=2; avg_ops_per_job=3/2=1.5; 9/1.5=6
    dm = [[3, 2], [4]]
    assert compute_horizon_proxy(dm) == 6


def test_create_release_dates_matrix_with_strategy():
    dm = [[3, 2], [4, 1]]
    strat = get_cumulative_release_date_strategy(maximum_slack=0)
    rng = random.Random(0)
    rd = create_release_dates_matrix(dm, strategy=strat, rng=rng)
    # Cumulative release dates should equal cumulative previous durations
    assert rd[0][0] == 0  # first op
    assert rd[0][1] == 3  # previous duration
    assert rd[1][0] == 0
    assert rd[1][1] == 4


def test_create_release_dates_matrix_default_strategy():
    dm = [[5, 1, 2], [4]]
    rng = random.Random(42)
    rd = create_release_dates_matrix(dm, rng=rng)
    # Structure preserved
    assert len(rd) == len(dm)
    assert all(len(r1) == len(r2) for r1, r2 in zip(rd, dm))
    # All non-negative
    assert all(all(v >= 0 for v in row) for row in rd)


def test_create_release_dates_matrix_empty():
    assert not create_release_dates_matrix([], rng=random.Random(0))


def test_compute_horizon_proxy_all_empty_jobs():
    # num_jobs > 0 but zero operations overall -> denominator protection path
    dm: list[list[int]] = [[], [], []]
    assert compute_horizon_proxy(dm) == 0


def test_compute_horizon_proxy_some_empty_jobs():
    # total_duration = 5+1 =6; total_ops=3; jobs=3; avg_ops_per_job=3/3=1; 6/1=6
    dm = [[2, 3], [], [1]]
    assert compute_horizon_proxy(dm) == 6


def test_create_release_dates_matrix_with_empty_job_and_custom_strategy():
    dm = [[4, 2], [], [3]]
    # Use cumulative strategy with slack to exercise slack branch too
    strat = get_cumulative_release_date_strategy(maximum_slack=2)
    rng = random.Random(10)
    rdm = create_release_dates_matrix(dm, strategy=strat, rng=rng)
    assert len(rdm) == 3
    assert rdm[1] == []  # empty job preserved
    # Durations accumulate + forward slack (release date >= cumulative prev)
    cum_prev = 0
    for dur, rel in zip(dm[0], rdm[0]):
        assert rel >= cum_prev
        # slack bounded by 2
        assert rel <= cum_prev + 2
        cum_prev += dur


def test_mixed_release_date_strategy_determinism_and_bounds():
    horizon = 120
    alpha = 0.6
    beta = 0.25
    strat = get_mixed_release_date_strategy(alpha, beta, horizon)
    rng1 = random.Random(123)
    rng2 = random.Random(123)
    vals1 = [strat(rng1, c) for c in range(0, 200, 25)]
    vals2 = [strat(rng2, c) for c in range(0, 200, 25)]
    assert vals1 == vals2  # deterministic
    # Bounds check
    upper_rand = int(beta * horizon)
    for c, v in zip(range(0, 200, 25), vals1):
        assert int(alpha * c) <= v <= int(alpha * c) + upper_rand


def test_independent_release_date_strategy_variability():
    strat = get_independent_release_date_strategy(3)
    rng = random.Random(7)
    values = {strat(rng, 0) for _ in range(30)}
    # Expect to have seen all numbers 0..3 in 30 draws with high probability
    assert values == {0, 1, 2, 3}


def test_create_release_dates_matrix_default_strategy_coverage_zero_horizon_case():
    # Provide durations such that horizon_proxy becomes 0 when averaged
    # Use empty jobs only -> already covered; we now mix empty and zero durations
    dm = [[], [0, 0], []]
    rng = random.Random(5)
    rd = create_release_dates_matrix(dm, rng=rng)
    assert rd[0] == [] and rd[2] == []
    assert rd[1][0] == 0 and rd[1][1] >= 0  # second op non-negative
