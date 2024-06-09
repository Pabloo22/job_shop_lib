import pytest

from job_shop_lib import ValidationError
from job_shop_lib.dispatching import (
    dispatching_rule_factory,
    shortest_processing_time_rule,
    first_come_first_served_rule,
    most_work_remaining_rule,
    random_operation_rule,
    DispatchingRule,
)


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
    test_dispatching_rule_factory()
