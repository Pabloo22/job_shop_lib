"""Graph-Based Environment for Job Shop Scheduling."""

from typing import Optional

import gymnasium as gym
from gymnasium import spaces

from job_shop_lib import InstanceGenerator


NUM_NODE_FEATURES = 10
NUM_EDGE_FEATURES = 4


class GraphJobShopEnv(gym.Env):
    """Job Shop Environment for Reinforcement Learning.

    Each observation is the edge list of the graph, and the feature matrix
    of the nodes. The action space is the set of all possible jobs.

    """

    metadata = {"render.modes": ["human"]}

    def __init__(self, instance_generator: InstanceGenerator):
        self.instance_generator = instance_generator
        self.observation_space = spaces.Graph(
            node_space=spaces.Box(low=0, high=1, shape=(NUM_NODE_FEATURES,)),
            edge_space=spaces.Box(low=0, high=1, shape=(NUM_EDGE_FEATURES,)),
        )
        _, max_number_of_jobs = instance_generator.num_jobs_range
        self.action_space = spaces.Discrete(max_number_of_jobs)
        self.current_instance = self.instance_generator.generate()

    def reset(self, *, seed=None, options: Optional[dict] = None):
        super().reset(seed=seed)
        self.current_instance = self.instance_generator.generate()

    def step(self, action: int):
        pass

    def render(self):
        pass

    def close(self):
        pass
