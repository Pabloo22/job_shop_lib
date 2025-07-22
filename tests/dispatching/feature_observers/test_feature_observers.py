import numpy as np

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
    IsReadyObserver,
)

from job_shop_lib.dispatching import (
    Dispatcher,
    ReadyOperationsFilterType,
    ready_operations_filter_factory,
)
from job_shop_lib.dispatching.rules import (
    DispatchingRuleSolver,
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
7      0.0               -1.0       1.0          1.0            0.0          1.0
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
7      0.0               -1.0       1.0          1.0            0.0          1.0
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
0      0.0               -7.0       1.0          1.0            0.0          1.0
1      0.0               -6.0       1.0          1.0            0.0          1.0
2      0.0               -5.0       2.0          1.0            0.0          0.0
3      1.0                2.0       2.0          0.0            0.0          0.0
4      0.0               -5.0       5.0          1.0            0.0          1.0
5      1.0                2.0       1.0          0.0            0.0          0.0
6      0.0                3.0       1.0          0.0            1.0          0.0
7      0.0               -7.0       1.0          1.0            0.0          1.0
8      0.0               -6.0       3.0          1.0            0.0          1.0
9      1.0                0.0       2.0          0.0            0.0          0.0
machines:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      1.0                2.0       3.0          0.0                  2.0          0.0
1      1.0                0.0       2.0          0.0                  1.0          0.0
2      1.0                2.0       1.0          1.0                  1.0          0.0
jobs:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      1.0                2.0       2.0          1.0                  1.0          0.0
1      1.0                2.0       2.0          0.0                  2.0          0.0
2      1.0                0.0       2.0          0.0                  1.0          0.0"""

STEP_7 = """CompositeFeatureObserver:
------------------------
operations:
   IsReady  EarliestStartTime  Duration  IsScheduled  PositionInJob  IsCompleted
0      0.0               -7.0       1.0          1.0            0.0          1.0
1      0.0               -6.0       1.0          1.0            0.0          1.0
2      0.0               -5.0       2.0          1.0            0.0          0.0
3      0.0                2.0       2.0          1.0            0.0          0.0
4      0.0               -5.0       5.0          1.0            0.0          1.0
5      1.0                2.0       1.0          0.0            0.0          0.0
6      0.0                4.0       1.0          0.0            1.0          0.0
7      0.0               -7.0       1.0          1.0            0.0          1.0
8      0.0               -6.0       3.0          1.0            0.0          1.0
9      1.0                0.0       2.0          0.0            0.0          0.0
machines:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0                4.0       1.0          1.0                  1.0          0.0
1      1.0                0.0       2.0          0.0                  1.0          0.0
2      1.0                2.0       1.0          1.0                  1.0          0.0
jobs:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0                2.0       0.0          2.0                  0.0          0.0
1      1.0                2.0       2.0          0.0                  2.0          0.0
2      1.0                0.0       2.0          0.0                  1.0          0.0"""

STEP_8 = """CompositeFeatureObserver:
------------------------
operations:
   IsReady  EarliestStartTime  Duration  IsScheduled  PositionInJob  IsCompleted
0      0.0               -7.0       1.0          1.0            0.0          1.0
1      0.0               -6.0       1.0          1.0            0.0          1.0
2      0.0               -5.0       2.0          1.0            0.0          0.0
3      0.0                2.0       2.0          1.0            0.0          0.0
4      0.0               -5.0       5.0          1.0            0.0          1.0
5      0.0                2.0       1.0          1.0            0.0          0.0
6      1.0                4.0       1.0          0.0            0.0          0.0
7      0.0               -7.0       1.0          1.0            0.0          1.0
8      0.0               -6.0       3.0          1.0            0.0          1.0
9      1.0                0.0       2.0          0.0            0.0          0.0
machines:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      1.0                4.0       1.0          1.0                  1.0          0.0
1      1.0                0.0       2.0          0.0                  1.0          0.0
2      0.0               -7.0       0.0          2.0                  0.0          0.0
jobs:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0                2.0       0.0          2.0                  0.0          0.0
1      1.0                4.0       1.0          1.0                  1.0          0.0
2      1.0                0.0       2.0          0.0                  1.0          0.0"""

STEP_9 = """CompositeFeatureObserver:
------------------------
operations:
   IsReady  EarliestStartTime  Duration  IsScheduled  PositionInJob  IsCompleted
0      0.0              -11.0       1.0          1.0            0.0          1.0
1      0.0              -10.0       1.0          1.0            0.0          1.0
2      0.0               -9.0       2.0          1.0            0.0          1.0
3      0.0               -2.0       2.0          1.0            0.0          1.0
4      0.0               -9.0       5.0          1.0            0.0          1.0
5      0.0               -2.0       1.0          1.0            0.0          1.0
6      1.0                0.0       1.0          0.0            0.0          0.0
7      0.0              -11.0       1.0          1.0            0.0          1.0
8      0.0              -10.0       3.0          1.0            0.0          1.0
9      0.0               -4.0       2.0          1.0            0.0          1.0
machines:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      1.0                0.0       1.0          0.0                  1.0          0.0
1      0.0              -11.0       0.0          0.0                  0.0          1.0
2      0.0              -11.0       0.0          0.0                  0.0          1.0
jobs:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0                2.0       0.0          0.0                  0.0          1.0
1      1.0                0.0       1.0          0.0                  1.0          0.0
2      0.0                0.0       0.0          0.0                  0.0          1.0"""

STEP_10 = """CompositeFeatureObserver:
------------------------
operations:
   IsReady  EarliestStartTime  Duration  IsScheduled  PositionInJob  IsCompleted
0      0.0              -12.0       1.0          1.0            0.0          1.0
1      0.0              -11.0       1.0          1.0            0.0          1.0
2      0.0              -10.0       2.0          1.0            0.0          1.0
3      0.0               -3.0       2.0          1.0            0.0          1.0
4      0.0              -10.0       5.0          1.0            0.0          1.0
5      0.0               -3.0       1.0          1.0            0.0          1.0
6      0.0               -1.0       1.0          1.0            0.0          1.0
7      0.0              -12.0       1.0          1.0            0.0          1.0
8      0.0              -11.0       3.0          1.0            0.0          1.0
9      0.0               -5.0       2.0          1.0            0.0          1.0
machines:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0              -12.0       0.0          0.0                  0.0          1.0
1      0.0              -12.0       0.0          0.0                  0.0          1.0
2      0.0              -12.0       0.0          0.0                  0.0          1.0
jobs:
   IsReady  EarliestStartTime  Duration  IsScheduled  RemainingOperations  IsCompleted
0      0.0                2.0       0.0          0.0                  0.0          1.0
1      0.0                0.0       0.0          0.0                  0.0          1.0
2      0.0                0.0       0.0          0.0                  0.0          1.0"""


def test_every_feature_observer(irregular_job_shop_instance: JobShopInstance):
    pruning_function = ready_operations_filter_factory(
        ReadyOperationsFilterType.DOMINATED_OPERATIONS
    )
    dispatcher = Dispatcher(
        irregular_job_shop_instance,
        ready_operations_filter=pruning_function,
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
        assert str(composite) == step, f"index: {steps.index(step)}"


def test_composite_feature_observer_none_observers(
    irregular_job_shop_instance: JobShopInstance,
):
    dispatcher = Dispatcher(irregular_job_shop_instance)
    # Add some observers to the dispatcher
    feature_observer_factory(
        FeatureObserverType.DURATION, dispatcher=dispatcher
    )
    feature_observer_factory(
        FeatureObserverType.IS_READY, dispatcher=dispatcher
    )

    composite = CompositeFeatureObserver(dispatcher, feature_observers=None)
    # Check that the composite observer picked up the observers from the
    # dispatcher
    assert len(composite.feature_observers) == 2
    assert isinstance(composite.feature_observers[0], DurationObserver)
    assert isinstance(composite.feature_observers[1], IsReadyObserver)


def test_composite_observer_of_composites_column_names(
    irregular_job_shop_instance: JobShopInstance,
):
    """
    Tests that CompositeFeatureObserver correctly generates column names
    when aggregating features from other CompositeFeatureObserver instances,
    specifically testing the case where the inner composite's feature matrix
    has more than one column.
    """
    dispatcher = Dispatcher(irregular_job_shop_instance)

    # Create inner observers for the first composite observer (composite1)
    obs1_comp1 = feature_observer_factory(
        FeatureObserverType.DURATION, dispatcher=dispatcher
    )
    obs2_comp1 = feature_observer_factory(
        FeatureObserverType.IS_READY, dispatcher=dispatcher
    )
    composite1 = CompositeFeatureObserver(
        dispatcher, feature_observers=[obs1_comp1, obs2_comp1]
    )

    # Create inner observers for the second composite observer (composite2)
    obs1_comp2 = feature_observer_factory(
        FeatureObserverType.EARLIEST_START_TIME, dispatcher=dispatcher
    )
    obs2_comp2 = feature_observer_factory(
        FeatureObserverType.IS_SCHEDULED, dispatcher=dispatcher
    )
    composite2 = CompositeFeatureObserver(
        dispatcher, feature_observers=[obs1_comp2, obs2_comp2]
    )

    # Create the top-level composite observer (top_composite)
    # This top_composite will observe composite1 and composite2.
    top_composite = CompositeFeatureObserver(
        dispatcher, feature_observers=[composite1, composite2]
    )

    # Expected column names:
    # Each inner composite (composite1, composite2) provides a 2-column matrix
    # to the top_composite. The feature_name for these is "CompositeFeature".
    # So, top_composite should generate
    # ["CompositeFeature_0", "CompositeFeature_1"]
    # for each of them.
    expected_column_names = [
        "CompositeFeature_0",
        "CompositeFeature_1",
        "CompositeFeature_0",
        "CompositeFeature_1",
    ]

    # All chosen base observers support OPERATIONS, MACHINES, and JOBS feature
    # types.
    # Thus, composite1 and composite2 will have features for these types,
    # and their feature matrices for these types will have 2 columns.

    assert (
        top_composite.column_names[FeatureType.OPERATIONS]
        == expected_column_names
    ), (
        f"Incorrect column names for OPERATIONS. "
        f"Expected: {expected_column_names}, "
        f"Got: {top_composite.column_names[FeatureType.OPERATIONS]}"
    )

    assert (
        top_composite.column_names[FeatureType.MACHINES]
        == expected_column_names
    ), (
        f"Incorrect column names for MACHINES. "
        f"Expected: {expected_column_names}, "
        f"Got: {top_composite.column_names[FeatureType.MACHINES]}"
    )

    assert (
        top_composite.column_names[FeatureType.JOBS] == expected_column_names
    ), (
        f"Incorrect column names for JOBS. "
        f"Expected: {expected_column_names}, "
        f"Got: {top_composite.column_names[FeatureType.JOBS]}"
    )

    # Verify the shape of the concatenated features in top_composite
    num_ops = irregular_job_shop_instance.num_operations
    num_machines = irregular_job_shop_instance.num_machines
    num_jobs = irregular_job_shop_instance.num_jobs

    # Each base observer -> 1 column.
    # composite1 (2 base observers) -> 2 columns.
    # composite2 (2 base observers) -> 2 columns.
    # top_composite (aggregating composite1 and composite2) -> 2+2 = 4 columns.
    assert top_composite.features[FeatureType.OPERATIONS].shape == (num_ops, 4)
    assert top_composite.features[FeatureType.MACHINES].shape == (
        num_machines,
        4,
    )
    assert top_composite.features[FeatureType.JOBS].shape == (num_jobs, 4)


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
    # Solve the job shop instance to simulate completing all operations
    solver = DispatchingRuleSolver(dispatching_rule="most_work_remaining")
    for _ in range(dispatcher.instance.num_operations):
        solver.step(dispatcher)

    assert dispatcher.schedule.is_complete()

    assert set(is_completed_observer.features) == set(feature_types)
    for feature_type in feature_types:
        try:
            assert all(is_completed_observer.features[feature_type] == 1)
        except AssertionError:
            print(is_completed_observer.features[feature_type])
            print(feature_type)
            print(dispatcher.instance.to_dict())
            raise


def test_is_completed_observer_with_random_instances():
    generator = GeneralInstanceGenerator(
        num_jobs=(2, 10),
        num_machines=(2, 10),
        iteration_limit=100,
        allow_less_jobs_than_machines=False,
        seed=42,
    )
    for instance in generator:
        test_is_completed_observer(instance)


def test_earliest_start_time_observer_with_recirculation(
    instance_with_recirculation: JobShopInstance,
):
    dispatcher = Dispatcher(instance_with_recirculation)
    feature_observer_factory(
        FeatureObserverType.EARLIEST_START_TIME, dispatcher=dispatcher
    )


def test_earliest_start_time_observer_without_cache(
    irregular_job_shop_instance: JobShopInstance,
):
    pruning_function = ready_operations_filter_factory(
        ReadyOperationsFilterType.DOMINATED_OPERATIONS
    )
    dispatcher = Dispatcher(
        irregular_job_shop_instance,
        ready_operations_filter=pruning_function,
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
    # REMOVE CACHE
    earliest_start_time_observer = dispatcher.create_or_get_observer(
        EarliestStartTimeObserver
    )
    # pylint: disable=protected-access
    earliest_start_time_observer._is_regular_instance = False
    earliest_start_time_observer._job_ids = np.array([])
    earliest_start_time_observer._positions = np.array([])

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
        assert str(composite) == step, f"index: {steps.index(step)}"


if __name__ == "__main__":
    import pytest

    pytest.main(["-vv", __file__])
