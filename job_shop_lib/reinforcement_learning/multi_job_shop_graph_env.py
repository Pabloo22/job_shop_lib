"""Home of the `GraphEnvironment` class."""

from collections import defaultdict
from typing import Callable, Any
from copy import deepcopy

import gymnasium as gym
import numpy as np

from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.dispatching import (
    Dispatcher,
    prune_dominated_operations,
    DispatcherObserverConfig,
)
from job_shop_lib.dispatching.feature_observers import FeatureObserverConfig
from job_shop_lib.generation import InstanceGenerator
from job_shop_lib.graphs import JobShopGraph, build_agent_task_graph
from job_shop_lib.graphs.graph_updaters import (
    GraphUpdater,
    ResidualGraphUpdater,
)
from job_shop_lib.reinforcement_learning import (
    SingleJobShopGraphEnv,
    RewardFunction,
    RenderConfig,
    MakespanReward,
    ObservationDict,
    ObservationSpaceKey,
    add_padding,
)


class MultiJobShopGraphEnv(gym.Env):
    """Gymnasium environment for solving the Job Shop Scheduling Problem
    with reinforcement learning and Graph Neural Networks.

    Attributes:
        instance_generator:
            After each reset, the environment generates a new instance of the
            Job Shop Scheduling Problem using an `InstanceGenerator`, and
            creates a   graph representation of the instance using the
            `graph_builder` function.
        feature_observers:
            List of feature observer types to extract features from the
            `Dispatcher` instance. They are used to create a
            `CompositeFeatureObserver` that will be used to extract features
            from the `Dispatcher` instance.
        graph_builder:
            Function that creates a graph representation of the instance.
        pruning_function:
            The `pruning_function` is used to prune the list of operations
            that can be selected by the agent. By default, the
            `prune_dominated_operations` function is used.
        action_space:
            Discrete action space with the maximum number of jobs. The maximum
            number of jobs is determined by the `max_num_jobs` attribute of the
            `InstanceGenerator` instance.
        observation_space:
            Dictionary with the observation space keys and their corresponding
            gym spaces. The maximum number of nodes, edges and the shape of the
            feature vector are determined by generating an instance with the
            maximum number of jobs and machines, creating a graph, and
            initializing the `Dispatcher` class with the feature observers.
            Padding is used to ensure that each matrix has a fixed size.

            Keys are defined in the `ObservationSpaceKey` enum:
                - "removed_nodes": Binary vector indicating the removed nodes.
                    Shape: (max_num_nodes, 1).
                - "edge_index": Matrix with the edge list in COO format. Each
                    column represents an edge, and the first row contains the
                    source nodes, and the second row contains the target nodes.
                    Shape: (2, max_num_edges).
                - "operations": Matrix with the operations. Each row represents
                    an operation, and the columns represent the features
                    extracted by the feature observers. Shape:
                    (max_num_operations, num_features).
                - "jobs": Matrix with the jobs. Each row represents a job, and
                    the columns represent the features extracted by the feature
                    observers. Shape: (max_num_jobs, num_features). Only
                    available if feature observers that computes job features
                    are used.
                - "machines": Matrix with the machines. Each row represents a
                    machine, and the columns represent the features extracted
                    by the feature observers. Shape: (max_num_machines,
                    num_features). Only available if feature observers that
                    computes machine features are used.
        dispatcher:
            Current dispatcher instance that manages the scheduling of
            operations. It is `None` until the environment is reset for the
            first time.
        composite_observer:
            Current composite feature observer that aggregates features
            from other feature observers.
    """

    def __init__(
        self,
        instance_generator: InstanceGenerator,
        feature_observer_configs: list[FeatureObserverConfig],
        graph_initializer: Callable[
            [JobShopInstance], JobShopGraph
        ] = build_agent_task_graph,
        graph_updater_config: DispatcherObserverConfig[
            type[GraphUpdater]
        ] = DispatcherObserverConfig(class_type=ResidualGraphUpdater),
        pruning_function: Callable[
            [Dispatcher, list[Operation]], list[Operation]
        ] = prune_dominated_operations,
        reward_function_config: DispatcherObserverConfig[
            type[RewardFunction]
        ] = DispatcherObserverConfig(class_type=MakespanReward),
        render_mode: str | None = None,
        render_config: RenderConfig | None = None,
        use_padding: bool = True,
    ) -> None:
        super().__init__()

        # Create an instance with the maximum size
        instance_with_max_size = instance_generator.generate(
            num_jobs=instance_generator.max_num_jobs,
            num_machines=instance_generator.max_num_machines,
        )
        graph = graph_initializer(instance_with_max_size)

        self.single_job_shop_graph_env = SingleJobShopGraphEnv(
            job_shop_graph=graph,
            feature_observer_configs=feature_observer_configs,
            reward_function_config=reward_function_config,
            graph_updater_config=graph_updater_config,
            pruning_function=pruning_function,
            render_mode=render_mode,
            render_config=render_config,
            use_padding=use_padding,
        )
        self.instance_generator = instance_generator
        self.graph_initializer = graph_initializer
        self.render_mode = render_mode
        self.render_config = render_config
        self.feature_observer_configs = feature_observer_configs
        self.reward_function_config = reward_function_config
        self.graph_updater_config = graph_updater_config

        self.action_space = deepcopy(
            self.single_job_shop_graph_env.action_space
        )
        self.observation_space: gym.spaces.Dict = deepcopy(
            self.single_job_shop_graph_env.observation_space
        )

    @property
    def dispatcher(self) -> Dispatcher:
        """Returns the current dispatcher instance."""
        return self.single_job_shop_graph_env.dispatcher

    @property
    def reward_function(self) -> RewardFunction:
        """Returns the current reward function instance."""
        return self.single_job_shop_graph_env.reward_function

    @reward_function.setter
    def reward_function(self, reward_function: RewardFunction) -> None:
        """Sets the reward function instance."""
        self.single_job_shop_graph_env.reward_function = reward_function

    @property
    def pruning_function(
        self,
    ) -> Callable[[Dispatcher, list[Operation]], list[Operation]] | None:
        """Returns the current pruning function."""
        return self.single_job_shop_graph_env.dispatcher.pruning_function

    @pruning_function.setter
    def pruning_function(
        self,
        pruning_function: Callable[
            [Dispatcher, list[Operation]], list[Operation]
        ],
    ) -> None:
        """Sets the pruning function."""
        self.single_job_shop_graph_env.dispatcher.pruning_function = (
            pruning_function
        )

    @property
    def use_padding(self) -> bool:
        """Returns whether the padding is used."""
        return self.single_job_shop_graph_env.use_padding

    @use_padding.setter
    def use_padding(self, use_padding: bool) -> None:
        """Sets whether the padding is used."""
        self.single_job_shop_graph_env.use_padding = use_padding

    @property
    def job_shop_graph(self) -> JobShopGraph:
        """Returns the current job shop graph."""
        return self.single_job_shop_graph_env.job_shop_graph

    @property
    def instance(self) -> JobShopInstance:
        """Returns the current job shop instance."""
        return self.single_job_shop_graph_env.instance

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[ObservationDict, dict]:
        """Resets the environment and returns the initial observation.

        Returns:
            Tuple with the initial observation and the info dictionary.
        """
        instance = self.instance_generator.generate()
        graph = self.graph_initializer(instance)
        self.single_job_shop_graph_env = SingleJobShopGraphEnv(
            job_shop_graph=graph,
            feature_observer_configs=self.feature_observer_configs,
            reward_function_config=self.reward_function_config,
            pruning_function=self.pruning_function,
            render_mode=self.render_mode,
            render_config=self.render_config,
            use_padding=self.single_job_shop_graph_env.use_padding,
        )

        obs, info = self.single_job_shop_graph_env.reset(
            seed=seed, options=options
        )
        if self.use_padding:
            obs = self._add_padding_to_observation(obs)

        return obs, info

    def step(
        self, action: tuple[int, int]
    ) -> tuple[ObservationDict, float, bool, bool, dict]:
        """Executes the action and returns the next observation, reward,
        termination flag, and info dictionary.

        Args:
            action: Tuple with the selected job and machine.

        Returns:
            Tuple with the next observation, reward, termination flag, and
            info dictionary.
        """
        obs, reward, done, truncated, info = (
            self.single_job_shop_graph_env.step(action)
        )
        if self.use_padding:
            obs = self._add_padding_to_observation(obs)

        return obs, reward, done, truncated, info

    def _add_padding_to_observation(
        self, observation: ObservationDict
    ) -> ObservationDict:
        """Adds padding to the observation.

        "removed_nodes":
            input_shape: (num_nodes,)
            output_shape: (max_num_nodes,) (padded with True)
        "edge_index":
            input_shape: (2, num_edges)
            output_shape: (2, max_num_edges) (padded with -1)
        "operations":
            input_shape: (num_operations, num_features)
            output_shape: (max_num_operations, num_features) (padded with -1)
        "jobs":
            input_shape: (num_jobs, num_features)
            output_shape: (max_num_jobs, num_features) (padded with -1)
        "machines":
            input_shape: (num_machines, num_features)
            output_shape: (max_num_machines, num_features) (padded with -1)
        """
        padding_value: dict[str, float | bool] = defaultdict(lambda: -1)
        padding_value[ObservationSpaceKey.REMOVED_NODES.value] = True
        for key, value in observation.items():
            if not isinstance(value, np.ndarray):  # Make mypy happy
                continue
            expected_shape = self._get_output_shape(key)
            observation[key] = add_padding(  # type: ignore[literal-required]
                value,
                expected_shape,
                padding_value=padding_value[key],
            )
        return observation

    def _get_output_shape(self, key: str) -> tuple[int, ...]:
        """Returns the output shape of the observation space key."""
        output_shape = self.observation_space[key].shape
        assert output_shape is not None  # Make mypy happy
        return output_shape

    def render(self) -> None:
        self.single_job_shop_graph_env.render()
