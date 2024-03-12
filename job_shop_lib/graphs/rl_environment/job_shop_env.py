"""Job Shop Environment for Reinforcement Learning."""

from typing import Optional
from typing_extensions import override

import gymnasium as gym


class GraphJobShopEnv(gym.Env):
    """Job Shop Environment for Reinforcement Learning.

    Each observation is the edge list of the graph, and the feature matrix
    of the nodes. The action space is the set of all possible jobs.

    """

    metadata = {"render.modes": ["human"]}

    def __init__(self, num_machines: int, num_jobs: int, job_len: int):
        self.num_machines = num_machines
        self.num_jobs = num_jobs
        self.job_len = job_len

        self.action_space = gym.spaces.Discrete(num_jobs)
        # self.observation_space = ...

    @override
    def reset(self, *, seed=None, options: Optional[dict] = None):
        super().reset(seed=seed)

    @override
    def step(self, action):
        pass

    @override
    def render(self):
        pass

    @override
    def close(self):
        pass
