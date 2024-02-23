import pytest

from job_shop_lib.solvers import (
    dispatching_rule_factory,
    shortest_processing_time_rule,
    first_come_first_served_rule,
    most_work_remaining_rule,
    random_operation_rule,
)


def test_dispatching_rule_factory():
    # pylint: disable=comparison-with-callable
    assert dispatching_rule_factory("spt") == shortest_processing_time_rule
    assert dispatching_rule_factory("fcfs") == first_come_first_served_rule
    assert dispatching_rule_factory("mwkr") == most_work_remaining_rule
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

    with pytest.raises(ValueError):
        dispatching_rule_factory("unknown_rule")
