# pylint: disable=missing-function-docstring, redefined-outer-name
import pytest

from job_shop_lib import (
    JobShopInstance,
    Operation,
    Schedule,
    ScheduledOperation,
)
from job_shop_lib.metaheuristics import (
    get_makespan_with_penalties_objective,
    compute_penalty_for_deadlines,
    compute_penalty_for_due_dates,
)


@pytest.fixture
def schedule_no_penalties() -> Schedule:
    # Two machines; set due_date/deadline None
    jobs = [[Operation(0, 2)], [Operation(1, 3)]]
    instance = JobShopInstance(jobs, name="NoPenalties")
    # Build schedule manually: M0: job0@t0..2; M1: job1@t0..3
    s0 = ScheduledOperation(instance.jobs[0][0], start_time=0, machine_id=0)
    s1 = ScheduledOperation(instance.jobs[1][0], start_time=0, machine_id=1)
    schedule = Schedule(instance, [[s0], [s1]])
    return schedule


@pytest.fixture
def schedule_with_deadlines() -> Schedule:
    # Single machine sequence; second op violates deadline
    jobs = [
        [Operation(0, 2, deadline=1)],  # ends at 2 -> violation
        [Operation(0, 3, deadline=5)],  # ends at 5 -> boundary, no violation
    ]
    instance = JobShopInstance(jobs, name="Deadlines")
    s0 = ScheduledOperation(instance.jobs[0][0], start_time=0, machine_id=0)
    s1 = ScheduledOperation(instance.jobs[1][0], start_time=2, machine_id=0)
    schedule = Schedule(instance, [[s0, s1]])
    return schedule


@pytest.fixture
def schedule_with_due_dates() -> Schedule:
    # Single machine sequence; first op OK, second violates due date
    jobs = [
        [Operation(0, 1, due_date=1)],  # ends at 1 -> equal, OK
        [Operation(0, 4, due_date=3)],  # ends at 5 -> violation
    ]
    instance = JobShopInstance(jobs, name="DueDates")
    s0 = ScheduledOperation(instance.jobs[0][0], start_time=0, machine_id=0)
    s1 = ScheduledOperation(instance.jobs[1][0], start_time=1, machine_id=0)
    schedule = Schedule(instance, [[s0, s1]])
    return schedule


@pytest.fixture
def schedule_with_both() -> Schedule:
    # Mixed: first violates deadline, second violates due date
    jobs = [
        [Operation(0, 3, deadline=2, due_date=10)],  # deadline violation
        [Operation(0, 4, deadline=10, due_date=6)],  # due date violation
    ]
    instance = JobShopInstance(jobs, name="Both")
    s0 = ScheduledOperation(instance.jobs[0][0], start_time=0, machine_id=0)
    s1 = ScheduledOperation(instance.jobs[1][0], start_time=3, machine_id=0)
    schedule = Schedule(instance, [[s0, s1]])
    return schedule


def test_compute_penalty_for_deadlines_none(schedule_no_penalties: Schedule):
    assert compute_penalty_for_deadlines(schedule_no_penalties, 1000) == 0.0


def test_compute_penalty_for_due_dates_none(schedule_no_penalties: Schedule):
    assert compute_penalty_for_due_dates(schedule_no_penalties, 100) == 0.0


def test_compute_penalty_for_deadlines(schedule_with_deadlines: Schedule):
    # Only first op violates -> 1 penalty
    assert compute_penalty_for_deadlines(schedule_with_deadlines, 7.5) == 7.5


def test_compute_penalty_for_due_dates(schedule_with_due_dates: Schedule):
    # Only second op violates -> 1 penalty
    assert compute_penalty_for_due_dates(schedule_with_due_dates, 3.0) == 3.0


def test_objective_makespan_only_when_zero_factors(
    schedule_with_both: Schedule,
):
    objective = get_makespan_with_penalties_objective(
        deadline_penalty_factor=0, due_date_penalty_factor=0
    )
    assert objective(schedule_with_both) == schedule_with_both.makespan()


def test_objective_with_penalties(schedule_with_both: Schedule):
    # s0: 0..3 (violates deadline=2) -> +d_factor
    # s1: 3..7 (violates due_date=6) -> +dd_factor
    d_factor = 123.0
    dd_factor = 4.0
    objective = get_makespan_with_penalties_objective(
        deadline_penalty_factor=d_factor,
        due_date_penalty_factor=dd_factor,
    )
    expected = schedule_with_both.makespan() + d_factor + dd_factor
    assert objective(schedule_with_both) == expected
