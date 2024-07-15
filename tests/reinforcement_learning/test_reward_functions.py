from job_shop_lib import JobShopInstance
from job_shop_lib.reinforcement_learning import MakespanReward, IdleTimeReward
from job_shop_lib.dispatching import (
    Dispatcher,
    prune_dominated_operations,
)
from job_shop_lib.dispatching.rules import DispatchingRuleSolver


def test_makespan_reward(example_job_shop_instance: JobShopInstance):
    dispatcher = Dispatcher(example_job_shop_instance)
    reward_function = MakespanReward(dispatcher)
    assert not reward_function.rewards
    solver = DispatchingRuleSolver("most_work_remaining")
    while not dispatcher.schedule.is_complete():
        solver.step(dispatcher)
        assert sum(reward_function.rewards) == -dispatcher.schedule.makespan()


def test_idle_time_reward(example_job_shop_instance: JobShopInstance):
    dispatcher = Dispatcher(
        example_job_shop_instance, pruning_function=prune_dominated_operations
    )
    reward_function = IdleTimeReward(dispatcher)
    assert not reward_function.rewards
    solver = DispatchingRuleSolver("most_work_remaining")
    solver.solve(example_job_shop_instance, dispatcher)

    assert sum(reward_function.rewards) == -(1 + 1 + 6)


if __name__ == "__main__":
    import pytest

    pytest.main(["-vv", __file__])
