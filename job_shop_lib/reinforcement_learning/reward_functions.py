"""Rewards functions are defined as `DispatcherObervers` and are used to
calculate the reward for a given state."""

from typing import SupportsFloat

from job_shop_lib.dispatching import DispatcherObserver
from job_shop_lib.dispatching.dispatcher import Dispatcher


class RewardFunction(DispatcherObserver):

    def __init__(self, dispatcher: Dispatcher) -> None:
        super().__init__(dispatcher)
        self.rewards: list[SupportsFloat] = []

    def reset(self) -> None:
        self.rewards = []

