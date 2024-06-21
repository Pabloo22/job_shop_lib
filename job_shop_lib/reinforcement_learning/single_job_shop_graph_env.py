"""Home of the `SingleJobShopGraphEnv` class."""

from copy import deepcopy
from enum import Enum
from typing import Callable, Any
from matplotlib.figure import Figure

import gymnasium as gym
import numpy as np

from job_shop_lib import JobShopInstance, Operation, Schedule
from job_shop_lib.graphs import JobShopGraph
from job_shop_lib.dispatching import Dispatcher, prune_dominated_operations
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserverConfig,
    CompositeFeatureObserver,
    FeatureType,
)
from job_shop_lib.visualization import plot_gantt_chart_wrapper

from job_shop_lib.reinforcement_learning import RewardFunction


class ObservationSpaceKey(str, Enum):
    """Enumeration of the keys for the observation space dictionary."""

    REMOVED_NODES = "removed_nodes"
    EDGE_LIST = "edge_list"
    OPERATIONS = FeatureType.OPERATIONS.value
    JOBS = FeatureType.JOBS.value
    MACHINES = FeatureType.MACHINES.value


class SingleJobShopGraphEnv(gym.Env):
    """A Gymnasium environment for solving one particular instance of the
    Job Shop Scheduling Problem represented as a graph.

    The observation space is a dictionary with the following keys
        and values:
        - "removed_nodes": A binary vector indicating which nodes have been
            removed from the graph. It uses the MultiBinary space. The length
            of the vector is equal to the number of nodes in the graph.
            A value of 1 indicates that the node has been removed.
        - "edge_list": A matrix with the edges of the graph. It uses the
            MultiDiscrete space. The matrix has two rows and as many columns
            as edges in the graph. Each column contains the indices of the
            nodes connected by the edge.
        - The keys of the composite observer features and their corresponding
            matrices. The matrices are stored as Box spaces with shape equal to
            the shape of the matrix and unbounded values. It could be any of
            the following:
            - "operations"
            - "jobs"
            - "machines"

        Keys can be accessed using the `ObservationSpaceKey` enumeration."""

    def __init__(
        self,
        job_shop_graph: JobShopGraph,
        feature_observer_configs: list[FeatureObserverConfig],
        reward_function: type[RewardFunction],
        pruning_function: (
            Callable[[Dispatcher, list[Operation]], list[Operation]] | None
        ) = prune_dominated_operations,
    ) -> None:
        super().__init__()
        # Used for resetting the environment
        self.initial_job_shop_graph = deepcopy(job_shop_graph)

        self.job_shop_graph = job_shop_graph
        self.dispatcher = Dispatcher(
            self.instance, pruning_function=pruning_function
        )

        # Observers added to track the environment state
        self.composite_observer = (
            CompositeFeatureObserver.from_feature_observers_configs(
                self.dispatcher, feature_observer_configs
            )
        )
        self.reward_function = reward_function(self.dispatcher)

        self.action_space = gym.spaces.MultiDiscrete(
            [self.instance.num_jobs, self.instance.num_machines]
        )
        self.observation_space = self._get_observation_space()
        if render_function is None:
            render_function = plot_gantt_chart_wrapper()
        self.render_function = render_function

    @property
    def instance(self) -> JobShopInstance:
        """Returns the instance the environment is working on."""
        return self.job_shop_graph.instance

    def get_observation(self) -> dict[str, np.ndarray]:
        """Returns the current observation of the environment."""
        observation: dict[str, np.ndarray] = {
            ObservationSpaceKey.REMOVED_NODES.value: np.array(
                self.job_shop_graph.removed_nodes, dtype=int
            ),
            ObservationSpaceKey.EDGE_LIST.value: np.array(
                self.job_shop_graph.graph.edges(), dtype=int
            ).T,
        }
        for feature_type, matrix in self.composite_observer.features.items():
            observation[feature_type.value] = matrix
        return observation

    def _get_observation_space(self) -> gym.spaces.Dict:
        """Returns the observation space dictionary."""
        dict_space: dict[str, gym.Space] = {
            ObservationSpaceKey.REMOVED_NODES.value: gym.spaces.MultiBinary(
                len(self.job_shop_graph.nodes)
            ),
            ObservationSpaceKey.EDGE_LIST.value: gym.spaces.MultiDiscrete(
                np.full(
                    (2, self.job_shop_graph.num_edges),
                    fill_value=len(self.job_shop_graph.nodes),
                )
            ),
        }
        for feature_type, matrix in self.composite_observer.features.items():
            dict_space[feature_type.value] = gym.spaces.Box(
                low=-np.inf, high=np.inf, shape=matrix.shape
            )
        return gym.spaces.Dict(dict_space)

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[dict[str, np.ndarray], dict]:
        """Resets the environment."""
        super().reset(seed=seed, options=options)
        self.dispatcher.reset()
        self.job_shop_graph = deepcopy(self.initial_job_shop_graph)
        obs = self.get_observation()
        return obs, {}

    def render(self):
        """Renders the environment."""
        super().render()

    def step(
        self, action: tuple[int, int]
    ) -> tuple[dict[str, np.ndarray], float, bool, bool, dict[str, Any]]:
        """Takes a step in the environment.

        Args:
            action:
                The action to take. The action is a tuple of two integers
                (job_id, machine_id):
                the job ID and the machine ID in which to schedule the
                operation.

        Returns:
            A tuple containing the following elements:
            - The observation of the environment.
            - The reward obtained.
            - Whether the environment is done.
            - Whether the episode was truncated (always False).
            - Additional information (empty dictionary).
        """
        job_id, machine_id = action
        operation = self.dispatcher.next_operation(job_id)

        self.dispatcher.dispatch(operation, machine_id)
        self._remove_completed_nodes()

        reward = self.reward_function.last_reward
        done = self.dispatcher.schedule.is_complete()
        info: dict[str, Any] = {}
        truncated = False
        obs = self.get_observation()
        return obs, reward, done, truncated, info

    def _remove_completed_nodes(self):
        """Removes completed nodes from the graph."""
        for operation in self.dispatcher.completed_operations():
            node_id = operation.operation_id
            if self.job_shop_graph.removed_nodes[node_id]:
                continue
            self.job_shop_graph.remove_node(node_id)
