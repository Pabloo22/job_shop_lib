"""Tests for dispatching rules."""

import random
from collections.abc import Sequence

from job_shop_lib import JobShopInstance
from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_observers import (
    DurationObserver,
    FeatureType,
    IsReadyObserver,
)
from job_shop_lib.dispatching.rules import (
    first_come_first_served_rule,
    most_operations_remaining_rule,
    most_work_remaining_rule,
    random_operation_rule,
    score_based_rule,
    score_based_rule_with_tie_breaker,
    shortest_processing_time_rule,
    shortest_processing_time_score,
    first_come_first_served_score,
    MostWorkRemainingScorer,
    most_operations_remaining_score,
    random_score,
    largest_processing_time_rule,
    largest_processing_time_score,
    dispatching_rule_factory,
)


def test_shortest_processing_time_rule(dispatcher: Dispatcher):
    """Tests that the shortest_processing_time_rule selects the operation
    with the shortest duration."""
    selected_operation = shortest_processing_time_rule(dispatcher)
    assert selected_operation.duration == 1
    # Two operations have duration 1, the one from job 0 and job 2.
    # min will return the first one it finds.
    assert selected_operation.job_id in [0, 2]


def test_first_come_first_served_rule(dispatcher: Dispatcher):
    """Tests that the first_come_first_served_rule selects the operation
    with the lowest position in the job."""
    selected_operation = first_come_first_served_rule(dispatcher)
    assert selected_operation.job_id == 0
    assert selected_operation.position_in_job == 0


def test_most_work_remaining_rule(dispatcher: Dispatcher):
    """Tests that the most_work_remaining_rule selects the operation from the
    job with the most remaining work."""
    selected_operation = most_work_remaining_rule(dispatcher)
    assert selected_operation.job_id == 0


def test_most_operations_remaining_rule(dispatcher: Dispatcher):
    """Tests that the most_operations_remaining_rule selects the operation
    from the job with the most remaining operations."""
    selected_operation = most_operations_remaining_rule(dispatcher)
    # All jobs have 3 operations, so it should select the first one.
    assert selected_operation.job_id == 0


def test_random_operation_rule(dispatcher: Dispatcher):
    """Tests that the random_operation_rule selects a random operation from
    the available ones."""
    random.seed(42)
    selected_operation = random_operation_rule(dispatcher)
    available_operations = dispatcher.available_operations()
    assert selected_operation in available_operations


def test_score_based_rule(dispatcher: Dispatcher):
    """Tests the score_based_rule with a simple scoring function."""

    def scoring_function(disp: Dispatcher) -> Sequence[float]:
        scores = [0.0] * disp.instance.num_jobs
        scores[1] = 1.0  # Job 1 has the highest score
        return scores

    rule = score_based_rule(scoring_function)
    selected_operation = rule(dispatcher)
    assert selected_operation.job_id == 1


def test_score_based_rule_with_tie_breaker(dispatcher: Dispatcher):
    """Tests the score_based_rule_with_tie_breaker."""

    def score_function_1(unused_disp: Dispatcher) -> Sequence[int]:
        # All jobs have the same score
        return [1, 1, 1]

    def score_function_2(unused_disp: Dispatcher) -> Sequence[int]:
        # Job 2 has the highest score
        return [0, 0, 1]

    rule = score_based_rule_with_tie_breaker(
        [score_function_1, score_function_2]
    )
    selected_operation = rule(dispatcher)
    assert selected_operation.job_id == 2


def test_score_based_rule_with_tie_breaker_2(dispatcher: Dispatcher):
    """Tests the score_based_rule_with_tie_breaker."""

    def score_function_1(unused_disp: Dispatcher) -> Sequence[int]:
        # All jobs have the same score
        return [1, 1, 1]

    def score_function_2(unused_disp: Dispatcher) -> Sequence[int]:
        return [0, 0, 0]

    rule = score_based_rule_with_tie_breaker(
        [score_function_1, score_function_2]
    )
    selected_operation = rule(dispatcher)
    assert selected_operation.job_id == 0


def test_shortest_processing_time_score(dispatcher: Dispatcher):
    """Tests the shortest_processing_time_score function."""
    scores = shortest_processing_time_score(dispatcher)
    assert scores == [-1, -5, -1]


def test_first_come_first_served_score(dispatcher: Dispatcher):
    """Tests the first_come_first_served_score function."""
    scores = first_come_first_served_score(dispatcher)
    assert scores == [-0, -3, -6]


def test_most_work_remaining_scorer(dispatcher: Dispatcher):
    """Tests the MostWorkRemainingScorer class."""
    scorer = MostWorkRemainingScorer()
    scores = scorer(dispatcher)
    # The returned value might be a numpy array, so we compare element-wise.
    expected_scores = [9, 7, 6]
    assert all(a == b for a, b in zip(scores, expected_scores))


def test_most_operations_remaining_score(dispatcher: Dispatcher):
    """Tests the most_operations_remaining_score function."""
    scores = most_operations_remaining_score(dispatcher)
    assert scores == [3, 3, 3]


def test_random_score(dispatcher: Dispatcher):
    """Tests the random_score function."""
    random.seed(42)
    scores = random_score(dispatcher)
    assert len(scores) == dispatcher.instance.num_jobs
    assert all(isinstance(score, int) for score in scores)


def test_most_work_remaining_scorer_with_observer(
    example_job_shop_instance: JobShopInstance,
):
    """Tests that the MostWorkRemainingScorer gives the same results as the
    most_work_remaining_rule when a DurationObserver is present."""
    dispatcher = Dispatcher(example_job_shop_instance)
    DurationObserver(
        dispatcher, feature_types=[FeatureType.JOBS, FeatureType.OPERATIONS]
    )
    IsReadyObserver(
        dispatcher, feature_types=[FeatureType.JOBS, FeatureType.OPERATIONS]
    )

    # Get scores from the scorer
    scorer = MostWorkRemainingScorer()
    scores = scorer(dispatcher)

    # Get the operation selected by the rule
    rule_selected_op = most_work_remaining_rule(dispatcher)

    # Find the best operation according to the scorer
    available_ops = dispatcher.available_operations()
    scorer_selected_op = max(available_ops, key=lambda op: scores[op.job_id])

    assert rule_selected_op == scorer_selected_op


def test_largest_processing_time_rule(dispatcher: Dispatcher):
    """Tests that the largest_processing_time_rule selects the operation
    with the longest duration."""
    selected_operation = largest_processing_time_rule(dispatcher)
    durations = [op.duration for op in dispatcher.available_operations()]
    assert selected_operation.duration == max(durations)


def test_largest_processing_time_score(dispatcher: Dispatcher):
    """Tests the largest_processing_time_score function."""
    scores = largest_processing_time_score(dispatcher)
    expected_scores = [0] * dispatcher.instance.num_jobs
    for operation in dispatcher.available_operations():
        expected_scores[operation.job_id] = operation.duration
    assert scores == expected_scores


def test_largest_processing_time_rule_factory():
    """Tests that the factory resolves the rule correctly."""
    rule = dispatching_rule_factory("largest_processing_time")
    assert rule.__name__ == "largest_processing_time_rule"
