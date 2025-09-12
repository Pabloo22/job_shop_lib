# pylint: disable=missing-function-docstring, redefined-outer-name
import functools
import pytest

from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.exceptions import ValidationError
from job_shop_lib.reinforcement_learning import (
    MakespanReward,
    IdleTimeReward,
    RewardWithPenalties,
    get_due_date_violation_penalty,
    get_deadline_violation_penalty,
)


def test_makespan_reward_basic(single_machine_instance: JobShopInstance):
    dispatcher = Dispatcher(single_machine_instance)
    reward_obs = MakespanReward(dispatcher)

    # Schedule first job on machine 0
    op0 = single_machine_instance.jobs[0][0]
    dispatcher.dispatch(op0, 0)
    assert reward_obs.rewards[-1] == -2

    # Schedule second job on same machine
    op1 = single_machine_instance.jobs[1][0]
    dispatcher.dispatch(op1, 0)
    # makespan increases from 2 to 5
    assert reward_obs.rewards[-1] == -3

    # Sum of rewards equals -final_makespan
    assert sum(reward_obs.rewards) == -dispatcher.schedule.makespan() == -5


def test_makespan_reward_zero_when_no_increase(
    two_machines_instance: JobShopInstance,
):
    dispatcher = Dispatcher(two_machines_instance)
    reward_obs = MakespanReward(dispatcher)

    # Schedule the longer op first -> makespan = 5
    op_long = two_machines_instance.jobs[0][0]
    dispatcher.dispatch(op_long, 0)
    assert reward_obs.rewards[-1] == -5

    # Now schedule the shorter op on another machine -> ends 
    # at 3 < current makespan
    op_short = two_machines_instance.jobs[1][0]
    dispatcher.dispatch(op_short, 1)
    # No makespan increase -> zero reward
    assert reward_obs.rewards[-1] == 0


def test_idle_time_reward_computation():
    # Construct instance that creates idle time on machine 0
    # Job1: M0(1) then M1(1)
    # Job0: M1(5) then M0(1) -> causes M0 idle from t=1 to t=5
    jobs = [
        [Operation(1, 5), Operation(0, 1)],  # job 0
        [Operation(0, 1), Operation(1, 1)],  # job 1
    ]
    instance = JobShopInstance(jobs, name="IdleTimeExample")
    dispatcher = Dispatcher(instance)
    idle_obs = IdleTimeReward(dispatcher)

    # 1) j1[0] on M0 at t=0..1
    dispatcher.dispatch(instance.jobs[1][0], 0)
    assert idle_obs.rewards[-1] == 0  # first op on machine -> start_time 0

    # 2) j0[0] on M1 at t=0..5
    dispatcher.dispatch(instance.jobs[0][0], 1)
    assert idle_obs.rewards[-1] == 0  # first op on machine -> start_time 0

    # 3) j1[1] on M1 at t=5..6 (no idle on M1)
    dispatcher.dispatch(instance.jobs[1][1], 1)
    assert idle_obs.rewards[-1] == 0

    # 4) j0[1] on M0 at t=5..6 (idle on M0 from 1 to 5 -> reward = -4)
    dispatcher.dispatch(instance.jobs[0][1], 0)
    assert idle_obs.rewards[-1] == -4


def test_reward_with_penalties_due_date():
    # Build small instance where second op violates due date
    jobs = [
        [Operation(0, 1)],
        [
            Operation(0, 10, due_date=5)
        ],  # will start at 1 and end at 11 -> late
    ]
    instance = JobShopInstance(jobs, name="DueDatePenalty")
    dispatcher = Dispatcher(instance)

    base = MakespanReward(dispatcher)
    penalty_fn = functools.partial(
        get_due_date_violation_penalty, due_date_penalty_factor=7
    )
    reward = RewardWithPenalties(
        dispatcher,
        base_reward_observer=base,
        penalty_function=penalty_fn,
    )

    # First op (no penalty)
    dispatcher.dispatch(instance.jobs[0][0], 0)
    assert base.rewards[-1] == -1
    assert reward.rewards[-1] == -1

    # Second op violates due date -> penalty 7
    dispatcher.dispatch(instance.jobs[1][0], 0)
    assert base.rewards[-1] == -10
    assert reward.rewards[-1] == -10 - 7


def test_reward_with_penalties_deadline():
    jobs = [
        [Operation(0, 1)],
        [Operation(0, 10, deadline=5)],  # ends at 11 -> deadline violation
    ]
    instance = JobShopInstance(jobs, name="DeadlinePenalty")
    dispatcher = Dispatcher(instance)

    base = MakespanReward(dispatcher)
    penalty_fn = functools.partial(
        get_deadline_violation_penalty, deadline_penalty_factor=13
    )
    reward = RewardWithPenalties(
        dispatcher,
        base_reward_observer=base,
        penalty_function=penalty_fn,
    )

    dispatcher.dispatch(instance.jobs[0][0], 0)
    dispatcher.dispatch(instance.jobs[1][0], 0)
    assert reward.rewards[-1] == -10 - 13


def test_reward_with_penalties_requires_same_dispatcher():
    instance = JobShopInstance([[Operation(0, 1)]])
    d1 = Dispatcher(instance)
    d2 = Dispatcher(instance)
    base = MakespanReward(d1)

    with pytest.raises(ValidationError):
        RewardWithPenalties(
            d2, base_reward_observer=base, penalty_function=lambda op, d: 0.0
        )


def test_reward_with_penalties_unsubscribes_base():
    instance = JobShopInstance([[Operation(0, 1)], [Operation(0, 1)]])
    dispatcher = Dispatcher(instance)

    base = MakespanReward(dispatcher)
    assert base in dispatcher.subscribers

    reward = RewardWithPenalties(
        dispatcher,
        base_reward_observer=base,
        penalty_function=lambda op, d: 0.0,
    )
    # Base should be unsubscribed; wrapper is subscribed
    assert base not in dispatcher.subscribers
    assert reward in dispatcher.subscribers

    # test reset
    reward.reset()
    assert not reward.rewards
    assert not base.rewards


def test_reward_observers_reset():
    instance = JobShopInstance([[Operation(0, 1)], [Operation(0, 1)]])
    dispatcher = Dispatcher(instance)

    m_reward = MakespanReward(dispatcher)
    i_reward = IdleTimeReward(dispatcher)

    dispatcher.dispatch(instance.jobs[0][0], 0)
    dispatcher.dispatch(instance.jobs[1][0], 0)

    # Ensure rewards collected
    assert m_reward.rewards
    assert i_reward.rewards

    # Reset and ensure cleared and internal state matches
    m_reward.reset()
    i_reward.reset()
    assert not m_reward.rewards
    assert not i_reward.rewards
