"""Home of the `GraphEnvironment` class."""

from typing import Callable
import copy

import gymnasium as gym

from job_shop_lib import JobShopInstance
from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    CompositeFeatureObserver,
)
from job_shop_lib.generation import InstanceGenerator
from job_shop_lib.graphs import JobShopGraph, build_agent_task_graph


class GraphEnvironment(gym.Env):
    """Gymnasium environment for solving the Job Shop Scheduling Problem
    with reinforcement learning and Graph Neural Networks.
    """

    def __init__(
        self,
        instance_generator: InstanceGenerator,
        feature_observers: list[FeatureObserver],
        graph_builder: Callable[
            [JobShopInstance], JobShopGraph
        ] = build_agent_task_graph,
    ) -> None:
        super().__init__()
        self.instance_generator = instance_generator
        self.feature_observers = feature_observers
        self.graph_builder = graph_builder

        self.action_space = gym.spaces.Discrete(
            instance_generator.max_num_jobs
        )

    def _infer_observation_space(self):
        """Infer the observation space from the feature observers.

        The observation space can be inferred generating an instance with the
        maximum number of jobs and machines, creating a graph (number of nodes
        maximum, and edge types), and initializing the Dispatcher class with
        the feature observers (dimension of the feature vector).
        """

        instance_with_max_size = self._generate_instance_with_max_size()

    def _generate_instance_with_max_size(self) -> JobShopInstance:
        copied_generator = copy.deepcopy(self.instance_generator)
        copied_generator.num_jobs_range = (
            copied_generator.max_num_jobs,
            copied_generator.max_num_jobs,
        )
        copied_generator.num_machines_range = (
            copied_generator.max_num_machines,
            copied_generator.max_num_machines,
        )
        return copied_generator.generate()
