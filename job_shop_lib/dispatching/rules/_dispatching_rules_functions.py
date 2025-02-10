"""Dispatching rules for the job shop scheduling problem.

This module contains functions that implement different dispatching rules for
the job shop scheduling problem. A dispatching rule determines the order in
which operations are selected for execution based on certain criteria such as
shortest processing time, first come first served, etc.
"""

from typing import List, Optional
from collections.abc import Callable, Sequence
import random

from job_shop_lib import Operation
from job_shop_lib.dispatching import Dispatcher, DispatcherObserver
from job_shop_lib.dispatching.feature_observers import (
    DurationObserver,
    FeatureType,
    IsReadyObserver,
)


def shortest_processing_time_rule(dispatcher: Dispatcher) -> Operation:
    """Dispatches the operation with the shortest duration."""
    return min(
        dispatcher.available_operations(),
        key=lambda operation: operation.duration,
    )


def first_come_first_served_rule(dispatcher: Dispatcher) -> Operation:
    """Dispatches the operation with the lowest position in job."""
    return min(
        dispatcher.available_operations(),
        key=lambda operation: operation.position_in_job,
    )


def most_work_remaining_rule(dispatcher: Dispatcher) -> Operation:
    """Dispatches the operation which job has the most remaining work."""
    job_remaining_work = [0] * dispatcher.instance.num_jobs
    for operation in dispatcher.unscheduled_operations():
        job_remaining_work[operation.job_id] += operation.duration

    return max(
        dispatcher.available_operations(),
        key=lambda operation: job_remaining_work[operation.job_id],
    )


def most_operations_remaining_rule(dispatcher: Dispatcher) -> Operation:
    """Dispatches the operation which job has the most remaining operations."""
    job_remaining_operations = [0] * dispatcher.instance.num_jobs
    for operation in dispatcher.uncompleted_operations():
        job_remaining_operations[operation.job_id] += 1

    return max(
        dispatcher.available_operations(),
        key=lambda operation: job_remaining_operations[operation.job_id],
    )


def random_operation_rule(dispatcher: Dispatcher) -> Operation:
    """Dispatches a random operation."""
    return random.choice(dispatcher.available_operations())


def score_based_rule(
    score_function: Callable[[Dispatcher], Sequence[float]]
) -> Callable[[Dispatcher], Operation]:
    """Creates a dispatching rule based on a scoring function.

    Args:
        score_function: A function that takes a Dispatcher instance as input
            and returns a list of scores for each job.

    Returns:
        A dispatching rule function that selects the operation with the highest
        score based on the specified scoring function.
    """

    def rule(dispatcher: Dispatcher) -> Operation:
        scores = score_function(dispatcher)
        return max(
            dispatcher.available_operations(),
            key=lambda operation: scores[operation.job_id],
        )

    return rule


def score_based_rule_with_tie_breaker(
    score_functions: List[Callable[[Dispatcher], Sequence[int]]],
) -> Callable[[Dispatcher], Operation]:
    """Creates a dispatching rule based on multiple scoring functions.

    If there is a tie between two operations based on the first scoring
    function, the second scoring function is used as a tie breaker. If there is
    still a tie, the third scoring function is used, and so on.

    Args:
        score_functions: A list of scoring functions that take a Dispatcher
            instance as input and return a list of scores for each job.
    """

    def rule(dispatcher: Dispatcher) -> Operation:
        candidates = dispatcher.available_operations()
        for scoring_function in score_functions:
            scores = scoring_function(dispatcher)
            best_score = max(scores)
            candidates = [
                operation
                for operation in candidates
                if scores[operation.job_id] == best_score
            ]
            if len(candidates) == 1:
                return candidates[0]
        return candidates[0]

    return rule


# SCORING FUNCTIONS
# -----------------


def shortest_processing_time_score(dispatcher: Dispatcher) -> List[int]:
    """Scores each job based on the duration of the next operation."""
    num_jobs = dispatcher.instance.num_jobs
    scores = [0] * num_jobs
    for operation in dispatcher.available_operations():
        scores[operation.job_id] = -operation.duration
    return scores


def first_come_first_served_score(dispatcher: Dispatcher) -> List[int]:
    """Scores each job based on the position of the next operation."""
    num_jobs = dispatcher.instance.num_jobs
    scores = [0] * num_jobs
    for operation in dispatcher.available_operations():
        scores[operation.job_id] = operation.operation_id
    return scores


class MostWorkRemainingScorer:  # pylint: disable=too-few-public-methods
    """Scores each job based on the remaining work in the job.

    This class is conceptually a function: it can be called with a
    :class:`~job_shop_lib.dispatching.Dispatcher` instance as input, and it
    returns a list of scores for each job. The reason for using a class instead
    of a function is to cache the observers that are created for each
    dispatcher instance. This way, the observers do not have to be retrieved
    every time the function is called.

    """

    def __init__(self) -> None:
        self._duration_observer: Optional[DurationObserver] = None
        self._is_ready_observer: Optional[IsReadyObserver] = None
        self._current_dispatcher: Optional[Dispatcher] = None

    def __call__(self, dispatcher: Dispatcher) -> Sequence[int]:
        """Scores each job based on the remaining work in the job."""

        if self._current_dispatcher is not dispatcher:
            self._duration_observer = None
            self._is_ready_observer = None
            self._current_dispatcher = dispatcher

        def has_job_feature(observer: DispatcherObserver) -> bool:
            if not isinstance(observer, DurationObserver):
                return False
            return FeatureType.JOBS in observer.features

        if self._duration_observer is None:
            self._duration_observer = dispatcher.create_or_get_observer(
                DurationObserver,
                condition=has_job_feature,
                feature_types=FeatureType.JOBS,
            )
        if self._is_ready_observer is None:
            self._is_ready_observer = dispatcher.create_or_get_observer(
                IsReadyObserver,
                condition=has_job_feature,
                feature_types=FeatureType.JOBS,
            )

        work_remaining = self._duration_observer.features[
            FeatureType.JOBS
        ].copy()
        is_ready = self._is_ready_observer.features[FeatureType.JOBS]
        work_remaining[~is_ready.astype(bool)] = 0

        return work_remaining.ravel()  # type: ignore[return-value]


observer_based_most_work_remaining_rule = score_based_rule(
    MostWorkRemainingScorer()
)


def most_operations_remaining_score(dispatcher: Dispatcher) -> List[int]:
    """Scores each job based on the remaining operations in the job."""
    num_jobs = dispatcher.instance.num_jobs
    scores = [0] * num_jobs
    for operation in dispatcher.uncompleted_operations():
        scores[operation.job_id] += 1
    return scores


def random_score(dispatcher: Dispatcher) -> List[int]:
    """Scores each job randomly."""
    return [
        random.randint(0, 100) for _ in range(dispatcher.instance.num_jobs)
    ]
