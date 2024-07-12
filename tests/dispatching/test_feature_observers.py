from job_shop_lib import JobShopInstance
from job_shop_lib.generation import GeneralInstanceGenerator
from job_shop_lib.dispatching.feature_observers import (
    feature_observer_factory,
    FeatureObserverType,
    FeatureType,
    CompositeFeatureObserver,
    DurationObserver,
    EarliestStartTimeObserver,
    FeatureObserver,
    IsCompletedObserver,
)

from job_shop_lib.dispatching import (
    Dispatcher,
    DispatchingRuleSolver,
    PruningFunction,
    pruning_function_factory,
)

# Disable flake8 line-too-long check
# flake8: noqa
STEP_0 = """CompositeFeatureObserver:
------------------------
operations:
   IsReady  EarliestStartTime  Duration  IsScheduled  PositionInJob  IsCompleted
0      1.0                0.0       1.0          0.0            0.0          0.0
1      0.0                1.0       1.0          0.0            1.0          0.0
2      0.0                2.0       7.0          0.0            2.0          0.0
3      0.0                9.0       2.0          0.0            3.0          0.0
4      1.0                0.0       5.0          0.0            0.0          0.0
5      0.0                5.0       1.0          0.0            1.0          0.0
6      0.0                6.0       1.0          0.0            2.0          0.0
7      1.0                0.0       1.0          0.0            0.0          0.0
8      0.0                1.0       3.0          0.0            1.0          0.0
9      0.0                4.0       2.0          0.0            2.0          0.0
machines:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      1.0                0.0       7.0          0.0                  4.0          0.0
1      1.0                0.0       8.0          0.0                  3.0          0.0
2      1.0                0.0       9.0          0.0                  3.0          0.0
jobs:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      1.0                0.0      11.0          0.0                  4.0          0.0
1      1.0                0.0       7.0          0.0                  3.0          0.0
2      1.0                0.0       6.0          0.0                  3.0          0.0"""

STEP_1 = """CompositeFeatureObserver:
------------------------
operations:
   IsReady  EarliestStartTime  Duration  IsScheduled  PositionInJob  IsCompleted
0      0.0                0.0       1.0          1.0            0.0          0.0
1      1.0                1.0       1.0          0.0            0.0          0.0
2      0.0                2.0       7.0          0.0            1.0          0.0
3      0.0                9.0       2.0          0.0            2.0          0.0
4      1.0                0.0       5.0          0.0            0.0          0.0
5      0.0                5.0       1.0          0.0            1.0          0.0
6      0.0                6.0       1.0          0.0            2.0          0.0
7      1.0                0.0       1.0          0.0            0.0          0.0
8      0.0                1.0       3.0          0.0            1.0          0.0
9      0.0                4.0       2.0          0.0            2.0          0.0
machines:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0                1.0       6.0          1.0                  3.0          0.0
1      1.0                0.0       8.0          0.0                  3.0          0.0
2      1.0                0.0       9.0          0.0                  3.0          0.0
jobs:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      1.0                1.0      10.0          1.0                  3.0          0.0
1      1.0                0.0       7.0          0.0                  3.0          0.0
2      1.0                0.0       6.0          0.0                  3.0          0.0"""


STEP_2 = """CompositeFeatureObserver:
------------------------
operations:
   IsReady  EarliestStartTime  Duration  IsScheduled  PositionInJob  IsCompleted
0      0.0                0.0       1.0          1.0            0.0          0.0
1      0.0                1.0       1.0          1.0            0.0          0.0
2      0.0                2.0       7.0          0.0            0.0          0.0
3      0.0                9.0       2.0          0.0            1.0          0.0
4      1.0                2.0       5.0          0.0            0.0          0.0
5      0.0                7.0       1.0          0.0            1.0          0.0
6      0.0                8.0       1.0          0.0            2.0          0.0
7      1.0                0.0       1.0          0.0            0.0          0.0
8      0.0                1.0       3.0          0.0            1.0          0.0
9      0.0                4.0       2.0          0.0            2.0          0.0
machines:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0                1.0       6.0          1.0                  3.0          0.0
1      1.0                2.0       7.0          1.0                  2.0          0.0
2      1.0                0.0       9.0          0.0                  3.0          0.0
jobs:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0                2.0       9.0          2.0                  2.0          0.0
1      1.0                2.0       7.0          0.0                  3.0          0.0
2      1.0                0.0       6.0          0.0                  3.0          0.0"""

STEP_3 = """CompositeFeatureObserver:
------------------------
operations:
   IsReady  EarliestStartTime  Duration  IsScheduled  PositionInJob  IsCompleted
0      0.0                0.0       1.0          1.0            0.0          0.0
1      0.0                1.0       1.0          1.0            0.0          0.0
2      0.0                2.0       7.0          0.0            0.0          0.0
3      0.0                9.0       2.0          0.0            1.0          0.0
4      0.0                2.0       5.0          1.0            0.0          0.0
5      0.0                7.0       1.0          0.0            0.0          0.0
6      0.0                8.0       1.0          0.0            1.0          0.0
7      1.0                0.0       1.0          0.0            0.0          0.0
8      0.0                1.0       3.0          0.0            1.0          0.0
9      0.0                7.0       2.0          0.0            2.0          0.0
machines:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0                1.0       6.0          1.0                  3.0          0.0
1      0.0                7.0       2.0          2.0                  1.0          0.0
2      1.0                0.0       9.0          0.0                  3.0          0.0
jobs:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0                2.0       9.0          2.0                  2.0          0.0
1      0.0                7.0       2.0          1.0                  2.0          0.0
2      1.0                0.0       6.0          0.0                  3.0          0.0"""

STEP_4 = """CompositeFeatureObserver:
------------------------
operations:
   IsReady  EarliestStartTime  Duration  IsScheduled  PositionInJob  IsCompleted
0      0.0               -1.0       1.0          1.0            0.0          1.0
1      0.0                0.0       1.0          1.0            0.0          0.0
2      1.0                1.0       7.0          0.0            0.0          0.0
3      0.0                8.0       2.0          0.0            1.0          0.0
4      0.0                1.0       5.0          1.0            0.0          0.0
5      1.0                6.0       1.0          0.0            0.0          0.0
6      0.0                7.0       1.0          0.0            1.0          0.0
7      0.0               -1.0       0.0          1.0            0.0          1.0
8      1.0                0.0       3.0          0.0            0.0          0.0
9      0.0                6.0       2.0          0.0            1.0          0.0
machines:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      1.0                0.0       6.0          0.0                  3.0          0.0
1      0.0                6.0       2.0          2.0                  1.0          0.0
2      1.0                1.0       8.0          0.0                  2.0          0.0
jobs:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      1.0                1.0       9.0          1.0                  2.0          0.0
1      1.0                6.0       2.0          1.0                  2.0          0.0
2      1.0                0.0       5.0          0.0                  2.0          0.0"""

STEP_5 = """CompositeFeatureObserver:
------------------------
operations:
   IsReady  EarliestStartTime  Duration  IsScheduled  PositionInJob  IsCompleted
0      0.0               -1.0       1.0          1.0            0.0          1.0
1      0.0                0.0       1.0          1.0            0.0          0.0
2      0.0                1.0       7.0          1.0            0.0          0.0
3      0.0                8.0       2.0          0.0            0.0          0.0
4      0.0                1.0       5.0          1.0            0.0          0.0
5      1.0                8.0       1.0          0.0            0.0          0.0
6      0.0                9.0       1.0          0.0            1.0          0.0
7      0.0               -1.0       0.0          1.0            0.0          1.0
8      1.0                0.0       3.0          0.0            0.0          0.0
9      0.0                6.0       2.0          0.0            1.0          0.0
machines:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      1.0                0.0       6.0          0.0                  3.0          0.0
1      0.0                6.0       2.0          2.0                  1.0          0.0
2      1.0                8.0       1.0          1.0                  1.0          0.0
jobs:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0                8.0       2.0          2.0                  1.0          0.0
1      1.0                8.0       2.0          1.0                  2.0          0.0
2      1.0                0.0       5.0          0.0                  2.0          0.0"""

STEP_6 = """CompositeFeatureObserver:
------------------------
operations:
   IsReady  EarliestStartTime  Duration  IsScheduled  PositionInJob  IsCompleted
0      0.0               -1.0       1.0          1.0            0.0          1.0
1      0.0                0.0       1.0          1.0            0.0          0.0
2      0.0                1.0       7.0          1.0            0.0          0.0
3      0.0                8.0       2.0          0.0            0.0          0.0
4      0.0                1.0       5.0          1.0            0.0          0.0
5      0.0                8.0       1.0          1.0            0.0          0.0
6      0.0                9.0       1.0          0.0            0.0          0.0
7      0.0               -1.0       0.0          1.0            0.0          1.0
8      1.0                0.0       3.0          0.0            0.0          0.0
9      0.0                6.0       2.0          0.0            1.0          0.0
machines:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      1.0                0.0       6.0          0.0                  3.0          0.0
1      0.0                6.0       2.0          2.0                  1.0          0.0
2      0.0               -1.0       0.0          2.0                  0.0          1.0
jobs:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0                8.0       2.0          2.0                  1.0          0.0
1      0.0                9.0       1.0          2.0                  1.0          0.0
2      1.0                0.0       5.0          0.0                  2.0          0.0"""

STEP_7 = """CompositeFeatureObserver:
------------------------
operations:
   IsReady  EarliestStartTime  Duration  IsScheduled  PositionInJob  IsCompleted
0      0.0               -7.0       1.0          1.0            0.0          1.0
1      0.0               -6.0       1.0          1.0            0.0          1.0
2      0.0               -5.0       7.0          1.0            0.0          0.0
3      1.0                2.0       2.0          0.0            0.0          0.0
4      0.0               -5.0       5.0          1.0            0.0          1.0
5      0.0                2.0       1.0          1.0            0.0          0.0
6      1.0                3.0       1.0          0.0            0.0          0.0
7      0.0               -7.0       0.0          1.0            0.0          1.0
8      0.0               -6.0      -3.0          1.0            0.0          1.0
9      1.0                0.0       2.0          0.0            0.0          0.0
machines:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      1.0                2.0       3.0          0.0                  2.0          0.0
1      1.0                0.0       2.0          0.0                  1.0          0.0
2      0.0               -7.0       0.0          2.0                  0.0          1.0
jobs:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      1.0                2.0       2.0          1.0                  1.0          0.0
1      1.0                3.0       1.0          1.0                  1.0          0.0
2      1.0                0.0       2.0          0.0                  1.0          0.0"""

STEP_8 = """CompositeFeatureObserver:
------------------------
operations:
   IsReady  EarliestStartTime  Duration  IsScheduled  PositionInJob  IsCompleted
0      0.0               -7.0       1.0          1.0            0.0          1.0
1      0.0               -6.0       1.0          1.0            0.0          1.0
2      0.0               -5.0       7.0          1.0            0.0          0.0
3      0.0                2.0       2.0          1.0            0.0          0.0
4      0.0               -5.0       5.0          1.0            0.0          1.0
5      0.0                2.0       1.0          1.0            0.0          0.0
6      1.0                4.0       1.0          0.0            0.0          0.0
7      0.0               -7.0       0.0          1.0            0.0          1.0
8      0.0               -6.0      -3.0          1.0            0.0          1.0
9      1.0                0.0       2.0          0.0            0.0          0.0
machines:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      1.0                4.0       1.0          1.0                  1.0          0.0
1      1.0                0.0       2.0          0.0                  1.0          0.0
2      0.0               -7.0       0.0          2.0                  0.0          1.0
jobs:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0                2.0       0.0          2.0                  0.0          1.0
1      1.0                4.0       1.0          1.0                  1.0          0.0
2      1.0                0.0       2.0          0.0                  1.0          0.0"""

STEP_9 = """CompositeFeatureObserver:
------------------------
operations:
   IsReady  EarliestStartTime  Duration  IsScheduled  PositionInJob  IsCompleted
0      0.0               -7.0       1.0          1.0            0.0          1.0
1      0.0               -6.0       1.0          1.0            0.0          1.0
2      0.0               -5.0       7.0          1.0            0.0          0.0
3      0.0                2.0       2.0          1.0            0.0          0.0
4      0.0               -5.0       5.0          1.0            0.0          1.0
5      0.0                2.0       1.0          1.0            0.0          0.0
6      0.0                4.0       1.0          1.0            0.0          0.0
7      0.0               -7.0       0.0          1.0            0.0          1.0
8      0.0               -6.0      -3.0          1.0            0.0          1.0
9      1.0                0.0       2.0          0.0            0.0          0.0
machines:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0               -7.0       0.0          2.0                  0.0          1.0
1      1.0                0.0       2.0          0.0                  1.0          0.0
2      0.0               -7.0       0.0          2.0                  0.0          1.0
jobs:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0                2.0       0.0          2.0                  0.0          1.0
1      0.0                4.0       0.0          2.0                  0.0          1.0
2      1.0                0.0       2.0          0.0                  1.0          0.0"""

STEP_10 = """CompositeFeatureObserver:
------------------------
operations:
   IsReady  EarliestStartTime  Duration  IsScheduled  PositionInJob  IsCompleted
0      0.0              -12.0       1.0          1.0            0.0          1.0
1      0.0              -11.0       1.0          1.0            0.0          1.0
2      0.0              -10.0       7.0          1.0            0.0          1.0
3      0.0               -3.0       2.0          1.0            0.0          1.0
4      0.0              -10.0       5.0          1.0            0.0          1.0
5      0.0               -3.0       1.0          1.0            0.0          1.0
6      0.0               -1.0       1.0          1.0            0.0          1.0
7      0.0              -12.0       0.0          1.0            0.0          1.0
8      0.0              -11.0      -3.0          1.0            0.0          1.0
9      0.0               -5.0      -3.0          1.0            0.0          1.0
machines:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0              -12.0       0.0          0.0                  0.0          1.0
1      0.0              -12.0       0.0          0.0                  0.0          1.0
2      0.0              -12.0       0.0          0.0                  0.0          1.0
jobs:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0                2.0       0.0          0.0                  0.0          1.0
1      0.0                4.0       0.0          0.0                  0.0          1.0
2      0.0                0.0       0.0          0.0                  0.0          1.0"""


def test_every_feature_observer(irregular_job_shop_instance: JobShopInstance):
    pruning_function = pruning_function_factory(
        PruningFunction.DOMINATED_OPERATIONS
    )
    dispatcher = Dispatcher(
        irregular_job_shop_instance, pruning_function=pruning_function
    )
    feature_observers_types: list[
        FeatureObserverType | type[FeatureObserver]
    ] = [
        FeatureObserverType.IS_READY,
        EarliestStartTimeObserver,  # For checking the factory
        DurationObserver,
        FeatureObserverType.IS_SCHEDULED,
        FeatureObserverType.POSITION_IN_JOB,
        FeatureObserverType.REMAINING_OPERATIONS,
        FeatureObserverType.IS_COMPLETED,
    ]
    feature_observers = [
        feature_observer_factory(
            feature_observer_type,
            dispatcher=dispatcher,
        )
        for feature_observer_type in feature_observers_types
    ]
    composite = CompositeFeatureObserver(
        dispatcher, feature_observers=feature_observers
    )
    assert str(composite) == STEP_0
    solver = DispatchingRuleSolver("most_work_remaining")

    steps = [
        STEP_1,
        STEP_2,
        STEP_3,
        STEP_4,
        STEP_5,
        STEP_6,
        STEP_7,
        STEP_8,
        STEP_9,
        STEP_10,
    ]
    for step in steps:
        solver.step(dispatcher)
        assert str(composite) == step


def test_duration_observer_init(irregular_job_shop_instance: JobShopInstance):
    dispatcher = Dispatcher(irregular_job_shop_instance)
    feature_observer = feature_observer_factory(
        FeatureObserverType.DURATION, dispatcher=dispatcher
    )
    expected_shape = (10, 1)
    assert (
        feature_observer.features["operations"].shape  # type: ignore[index]
        == expected_shape
    )


def test_is_completed_observer(example_job_shop_instance: JobShopInstance):
    dispatcher = Dispatcher(example_job_shop_instance)
    feature_types = [
        FeatureType.MACHINES,
        FeatureType.JOBS,
    ]
    is_completed_observer = feature_observer_factory(
        FeatureObserverType.IS_COMPLETED,
        dispatcher=dispatcher,
        feature_types=feature_types,
    )

    assert isinstance(is_completed_observer, IsCompletedObserver)
    if not example_job_shop_instance.is_flexible:
        assert (
            is_completed_observer.remaining_ops_per_machine.sum()
            == example_job_shop_instance.num_operations
        )
        assert (
            is_completed_observer.remaining_ops_per_job.sum()
            == example_job_shop_instance.num_operations
        )
    # Solve the job shop instance to simulate completing all operations
    solver = DispatchingRuleSolver(dispatching_rule="most_work_remaining")
    for _ in range(dispatcher.instance.num_operations):
        solver.step(dispatcher)
        assert all(is_completed_observer.remaining_ops_per_machine >= 0)
        assert all(is_completed_observer.remaining_ops_per_job >= 0)

    assert dispatcher.schedule.is_complete()

    assert set(is_completed_observer.features) == set(feature_types)
    for feature_type in feature_types:
        try:
            assert all(is_completed_observer.features[feature_type] == 1)
        except AssertionError:
            print(is_completed_observer.features[feature_type])
            print(feature_type)
            print(is_completed_observer.remaining_ops_per_machine)
            print(dispatcher.instance.to_dict())
            raise


def test_is_completed_observer_with_random_instances():
    generator = GeneralInstanceGenerator(
        num_jobs=(2, 10),
        num_machines=(2, 10),
        iteration_limit=100,
        allow_less_jobs_than_machines=False,
        seed=42,
        machines_per_operation=(1, 2),
    )
    for instance in generator:
        test_is_completed_observer(instance)


if __name__ == "__main__":
    import pytest

    pytest.main(["-vv", __file__])
