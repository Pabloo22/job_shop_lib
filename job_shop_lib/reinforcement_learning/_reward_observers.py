"""Rewards functions are defined as `DispatcherObervers` and are used to
calculate the reward for a given state."""

from collections.abc import Callable

from job_shop_lib.exceptions import ValidationError
from job_shop_lib.dispatching import DispatcherObserver, Dispatcher
from job_shop_lib import ScheduledOperation


class RewardObserver(DispatcherObserver):
    """Base class for all reward functions.

    Attributes:
        rewards:
            List of rewards calculated for each operation scheduled by the
            dispatcher.
    """

    def __init__(
        self, dispatcher: Dispatcher, *, subscribe: bool = True
    ) -> None:
        super().__init__(dispatcher, subscribe=subscribe)
        self.rewards: list[float] = []

    @property
    def last_reward(self) -> float:
        """Returns the reward of the last step or 0 if no rewards have been
        calculated."""
        return self.rewards[-1] if self.rewards else 0

    def reset(self) -> None:
        """Sets rewards attribute to a new empty list."""
        self.rewards = []


class MakespanReward(RewardObserver):
    """Dense reward function based on the negative makespan of the schedule.

    The reward is calculated as the difference between the makespan of the
    schedule before and after the last operation was scheduled. The makespan
    is the time at which the last operation is completed.

    Attributes:
        current_makespan:
            Makespan of the schedule after the last operation was scheduled.
    """

    def __init__(self, dispatcher: Dispatcher, *, subscribe=True) -> None:
        super().__init__(dispatcher, subscribe=subscribe)
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


class IdleTimeReward(RewardObserver):
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


class RewardWithPenalties(RewardObserver):
    """Reward function that adds penalties to another reward function.

    The reward is calculated as the sum of the reward from another reward
    function and a penalty for each constraint violation (due dates and
    deadlines).

    Attributes:
        base_reward_observer:
            The base reward observer to use for calculating the reward.
        penalty_function:
            A function that takes a scheduled operation and the dispatcher as
            input and returns the penalty for that operation.

    Args:
        dispatcher:
            The dispatcher to observe.
        base_reward_observer:
            The base reward observer to use for calculating the reward. It
            must use the same dispatcher as this reward observer. If it is
            subscribed to the dispatcher, it will be unsubscribed.
        penalty_function:
            A function that takes a scheduled operation and the
            dispatcher as input and returns the penalty for that operation.
        subscribe:
            Whether to subscribe to the dispatcher upon initialization.

    Raises:
        ValidationError:
            If the base reward observer does not use the same dispatcher as
            this reward observer.

    .. versionadded:: 1.7.0

    .. seealso::
        The following functions (along with ``functools.partial``) can be
        used to create penalty functions:

        - :func:`~job_shop_lib.reinforcement_learning.get_deadline_violation_penalty`
        - :func:`~job_shop_lib.reinforcement_learning.get_due_date_violation_penalty`

    """  # noqa: E501

    def __init__(
        self,
        dispatcher: Dispatcher,
        *,
        base_reward_observer: RewardObserver,
        penalty_function: Callable[[ScheduledOperation, Dispatcher], float],
        subscribe: bool = True,
    ) -> None:
        super().__init__(dispatcher, subscribe=subscribe)
        self.base_reward_observer = base_reward_observer
        self.penalty_function = penalty_function
        if base_reward_observer.dispatcher is not dispatcher:
            raise ValidationError(
                "The base reward observer must use the same "
                "dispatcher as this reward observer."
            )
        if base_reward_observer in dispatcher.subscribers:
            dispatcher.unsubscribe(base_reward_observer)

    def reset(self) -> None:
        super().reset()
        self.base_reward_observer.reset()

    def update(self, scheduled_operation: ScheduledOperation):
        self.base_reward_observer.update(scheduled_operation)
        base_reward = self.base_reward_observer.last_reward
        penalty = self.penalty_function(scheduled_operation, self.dispatcher)
        self.rewards.append(base_reward - penalty)
