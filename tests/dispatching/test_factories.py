import pytest

from job_shop_lib import JobShopInstance
from job_shop_lib.exceptions import ValidationError
from job_shop_lib.dispatching import (
    dispatching_rule_factory,
    shortest_processing_time_rule,
    first_come_first_served_rule,
    most_work_remaining_rule,
    random_operation_rule,
    DispatchingRule,
    create_or_get_observer,
    HistoryObserver,
    Dispatcher,
    DispatcherObserver,
)
from job_shop_lib.dispatching.feature_observers import (
    IsCompletedObserver,
    FeatureType,
    FeatureObserver,
)


def has_machine_feature(observer: DispatcherObserver) -> bool:
    if not isinstance(observer, FeatureObserver):
        return False
    return FeatureType.MACHINES in observer.features


def test_create_or_get_observer(example_job_shop_instance: JobShopInstance):
    dispatcher = Dispatcher(example_job_shop_instance)
    observer = create_or_get_observer(dispatcher, HistoryObserver)
    assert isinstance(observer, HistoryObserver)
    assert observer.dispatcher is dispatcher

    # Test getting the same observer
    assert create_or_get_observer(dispatcher, HistoryObserver) is observer


def test_create_or_get_observer_with_condition(
    example_job_shop_instance: JobShopInstance,
):
    dispatcher = Dispatcher(example_job_shop_instance)
    create_or_get_observer(dispatcher, HistoryObserver)
    is_completed_observer = create_or_get_observer(
        dispatcher,
        IsCompletedObserver,
        feature_types=[FeatureType.OPERATIONS],
    )
    assert isinstance(is_completed_observer, IsCompletedObserver)
    is_completed_observer_2 = create_or_get_observer(
        dispatcher,
        IsCompletedObserver,
        condition=has_machine_feature,
        feature_types=[FeatureType.MACHINES],
        is_singleton=False,
    )
    assert isinstance(is_completed_observer_2, IsCompletedObserver)
    assert is_completed_observer_2 is not is_completed_observer


def test_dispatching_rule_factory():
    # pylint: disable=comparison-with-callable
    # type: ignore[arg-type]
    assert dispatching_rule_factory("random") == random_operation_rule
    assert (
        dispatching_rule_factory("shortest_processing_time")
        == shortest_processing_time_rule
    )
    assert (
        dispatching_rule_factory("first_come_first_served")
        == first_come_first_served_rule
    )
    assert (
        dispatching_rule_factory("most_work_remaining")
        == most_work_remaining_rule
    )

    assert (
        dispatching_rule_factory(DispatchingRule.RANDOM)
        == random_operation_rule
    )
    assert (
        dispatching_rule_factory(DispatchingRule.SHORTEST_PROCESSING_TIME)
        == shortest_processing_time_rule
    )

    assert (
        dispatching_rule_factory(DispatchingRule.FIRST_COME_FIRST_SERVED)
        == first_come_first_served_rule
    )
    assert (
        dispatching_rule_factory(DispatchingRule.MOST_WORK_REMAINING)
        == most_work_remaining_rule
    )

    with pytest.raises(ValidationError):
        dispatching_rule_factory("unknown_rule")


if __name__ == "__main__":
    pytest.main(["-vv", "tests/dispatching/test_factories.py"])
