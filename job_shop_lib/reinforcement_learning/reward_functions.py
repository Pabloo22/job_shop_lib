"""Rewards functions are defined as `DispatcherObervers` and are used to
calculate the reward for a given state."""

from job_shop_lib.dispatching import DispatcherObserver, Dispatcher
from job_shop_lib import ScheduledOperation


class RewardFunction(DispatcherObserver):
    """Base class for all reward functions.

    Attributes:
        rewards:
            List of rewards calculated for each operation scheduled by the
            dispatcher.
    """

    def __init__(self, dispatcher: Dispatcher, subscribe: bool = True) -> None:
        super().__init__(dispatcher, subscribe=subscribe)
        self.rewards: list[float] = []

    def reset(self) -> None:
        self.rewards = []


class MakespanReward(RewardFunction):
    """Dense reward function based on the negative makespan of the schedule.

    The reward is calculated as the difference between the makespan of the
    schedule before and after the last operation was scheduled. The makespan
    is the time at which the last operation is completed.

    Attributes:
        current_makespan:
            Makespan of the schedule after the last operation was scheduled.
    """

    def __init__(self, dispatcher: Dispatcher) -> None:
        super().__init__(dispatcher)
        self.current_makespan = dispatcher.schedule.makespan()

    def reset(self) -> None:
        super().reset()
        self.current_makespan = self.dispatcher.schedule.makespan()

    def update(self, scheduled_operation: ScheduledOperation):
        last_makespan = self.current_makespan
        self.current_makespan = max(
            last_makespan, scheduled_operation.end_time
        )
        reward = last_makespan - self.current_makespan
        self.rewards.append(reward)


class IdleTimeReward(RewardFunction):
    """Dense reward function based on the negative idle time of the schedule.

    The reward is calculated as the difference between the idle time of the
    schedule before and after the last operation was scheduled. The idle time
    is the sum of the time between the end of the last operation and the start
    of the next operation.
    """

    def update(self, scheduled_operation: ScheduledOperation):
        machine_id = scheduled_operation.machine_id
        machine_schedule = self.dispatcher.schedule.schedule[machine_id][:-1]

        if machine_schedule:
            last_operation = machine_schedule[-1]
            idle_time = (
                scheduled_operation.start_time - last_operation.end_time
            )
        else:
            idle_time = scheduled_operation.start_time

        reward = -idle_time
        self.rewards.append(reward)


if __name__ == "__main__":
    a = [1, 2]
    print(a[:-1])
