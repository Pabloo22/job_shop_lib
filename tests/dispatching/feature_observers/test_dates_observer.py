import numpy as np

from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_observers import (
    DatesObserver,
    FeatureType,
)


def test_initialization_with_all_attributes(
    dispatcher_with_extras: Dispatcher,
):
    observer = DatesObserver(dispatcher_with_extras)
    assert observer.attributes_to_observe == [
        "release_date",
        "deadline",
        "due_date",
    ]
    assert observer.feature_sizes[FeatureType.OPERATIONS] == 3
    assert observer.features[FeatureType.OPERATIONS].shape == (4, 3)


def test_initialization_with_specific_attributes(
    dispatcher_with_extras: Dispatcher,
):
    observer = DatesObserver(
        dispatcher_with_extras,
        attributes_to_observe=["release_date", "deadline"],
    )
    assert observer.attributes_to_observe == ["release_date", "deadline"]
    assert observer.feature_sizes[FeatureType.OPERATIONS] == 2
    assert observer.features[FeatureType.OPERATIONS].shape == (4, 2)


def test_initialization_with_no_date_attributes(dispatcher: Dispatcher):
    observer = DatesObserver(dispatcher)
    assert observer.attributes_to_observe == []
    assert observer.feature_sizes[FeatureType.OPERATIONS] == 0
    assert observer.features[FeatureType.OPERATIONS].shape == (9, 0)


def test_initialize_features(dispatcher_with_extras: Dispatcher):
    observer = DatesObserver(dispatcher_with_extras)
    expected_features = np.array(
        [
            [0.0, 100.0, 80.0],
            [10.0, 110.0, 90.0],
            [5.0, 105.0, 85.0],
            [15.0, 115.0, 95.0],
        ]
    )
    np.testing.assert_array_equal(
        observer.features[FeatureType.OPERATIONS], expected_features
    )


def test_update_features(dispatcher_with_extras: Dispatcher):
    observer = DatesObserver(dispatcher_with_extras)
    initial_features = observer.features[FeatureType.OPERATIONS].copy()

    # Dispatch an operation
    operation_to_schedule = dispatcher_with_extras.available_operations()[0]
    dispatcher_with_extras.dispatch(operation_to_schedule, machine_id=0)

    current_time = dispatcher_with_extras.current_time()
    expected_features = initial_features - current_time

    np.testing.assert_array_equal(
        observer.features[FeatureType.OPERATIONS], expected_features
    )

    while not dispatcher_with_extras.schedule.is_complete():
        op = (
            dispatcher_with_extras.available_operations()[0]
        )
        dispatcher_with_extras.dispatch(op)
        current_time = dispatcher_with_extras.current_time()
        expected_features = initial_features - current_time
        np.testing.assert_array_equal(
            observer.features[FeatureType.OPERATIONS], expected_features
        )


def test_reset_features(dispatcher_with_extras: Dispatcher):
    observer = DatesObserver(dispatcher_with_extras)
    initial_features = observer.features[FeatureType.OPERATIONS].copy()

    # Dispatch an operation to change the state
    operation_to_schedule = dispatcher_with_extras.available_operations()[0]
    dispatcher_with_extras.dispatch(operation_to_schedule, machine_id=0)

    # Reset the dispatcher and observer
    dispatcher_with_extras.reset()
    observer.reset()

    np.testing.assert_array_equal(
        observer.features[FeatureType.OPERATIONS], initial_features
    )


def test_attribute_map(dispatcher_with_extras: Dispatcher):
    observer = DatesObserver(dispatcher_with_extras)
    expected_map = {
        "release_date": 0,
        "deadline": 1,
        "due_date": 2,
    }
    assert observer.attribute_map == expected_map
