"""Home of the `GraphEnvironment` class."""

from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import Any, Tuple, Dict, List, Optional, Type
from copy import deepcopy

import gymnasium as gym
import numpy as np

from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.dispatching import (
    Dispatcher,
    filter_dominated_operations,
    DispatcherObserverConfig,
)
from job_shop_lib.dispatching.feature_observers import FeatureObserverConfig
from job_shop_lib.generation import InstanceGenerator
from job_shop_lib.graphs import JobShopGraph, build_resource_task_graph
from job_shop_lib.graphs.graph_updaters import (
    GraphUpdater,
    ResidualGraphUpdater,
)
from job_shop_lib.reinforcement_learning import (
    SingleJobShopGraphEnv,
    RewardObserver,
    RenderConfig,
    MakespanReward,
    ObservationDict,
    ObservationSpaceKey,
    add_padding,
)


class MultiJobShopGraphEnv(gym.Env):
    """Gymnasium environment for solving multiple Job Shop Scheduling Problems
    using reinforcement learning and Graph Neural Networks.

    This environment generates a new Job Shop Scheduling Problem instance
    for each reset, creates a graph representation, and manages the scheduling
    process using a :class:`~job_shop_lib.dispatching.Dispatcher`.

    The observation space includes:

    - removed_nodes: Binary vector indicating removed nodes.
    - edge_index: Edge list in COO format.
    - operations: Matrix of operation features.
    - jobs: Matrix of job features (if applicable).
    - machines: Matrix of machine features (if applicable).

    Internally, the class creates a
    :class:`~job_shop_lib.reinforcement_learning.SingleJobShopGraphEnv`
    environment to manage the scheduling process for each
    :class:`~job_shop_lib.JobShopInstance`.

    Attributes:
        instance_generator:
            A :class:`~job_shop_lib.generation.InstanceGenerator` that
            generates a new problem instance on each reset.

        action_space:
            :class:`gymnasium.spaces.Discrete`) action space with size equal to
            the maximum number of jobs.

        observation_space:
            Dictionary of observation spaces. Keys are defined in
            :class:`~job_shop_lib.reinforcement_learning.ObservationSpaceKey`.

        single_job_shop_graph_env:
            Environment for a specific Job Shop Scheduling Problem instance.
            See :class:`SingleJobShopGraphEnv`.

        graph_initializer:
            Function to create the initial graph representation. It should
            take a :class:`~job_shop_lib.JobShopInstance` as input and return
            a :class:`~job_shop_lib.graphs.JobShopGraph`.

        render_mode:
            Rendering mode for visualization. Supported modes are:

            - human: Renders the current Gannt chart.
            - save_video: Saves a video of the Gantt chart. Used only if the
              schedule is completed.
            - save_gif: Saves a GIF of the Gantt chart. Used only if the
              schedule is completed.

        render_config:
            Configuration for rendering. See
            :class:`~job_shop_lib.RenderConfig`.

        feature_observer_configs:
            List of :class:`~job_shop_lib.dispatching.DispatcherObserverConfig`
            for feature observers.
        reward_function_config:
            Configuration for the reward function. See
            :class:`~job_shop_lib.dispatching.DispatcherObserverConfig` and
            :class:`~job_shop_lib.dispatching.RewardObserver`.

        graph_updater_config:
            Configuration for the graph updater. The graph updater is used to
            update the graph representation after each action. See
            :class:`~job_shop_lib.dispatching.DispatcherObserverConfig` and
            :class:`~job_shop_lib.graphs.GraphUpdater`.
    Args:
        instance_generator:
            A :class:`~job_shop_lib.generation.InstanceGenerator` that
            generates a new problem instance on each reset.

        feature_observer_configs:
            Configurations for feature observers. Each configuration
            should be a
            :class:`~job_shop_lib.dispatching.DispatcherObserverConfig`
            with a class type that inherits from
            :class:`~job_shop_lib.dispatching.FeatureObserver` or a string
            or enum that represents a built-in feature observer.

        graph_initializer:
            Function to create the initial graph representation.
            If ``None``, the default graph initializer is used:
            :func:`~job_shop_lib.graphs.build_agent_task_graph`.
        graph_updater_config:
            Configuration for the graph updater. The graph updater is used
            to update the graph representation after each action. If
            ``None``, the default graph updater is used:
            :class:`~job_shop_lib.graphs.ResidualGraphUpdater`.

        ready_operations_filter:
            Function to filter ready operations. If ``None``, the default
            filter is used:
            :func:`~job_shop_lib.dispatching.filter_dominated_operations`.

        reward_function_config:
            Configuration for the reward function. If ``None``, the default
            reward function is used:
            :class:`~job_shop_lib.dispatching.MakespanReward`.

        render_mode:
            Rendering mode for visualization. Supported modes are:

            - human: Renders the current Gannt chart.
            - save_video: Saves a video of the Gantt chart. Used only if
                the schedule is completed.
            - save_gif: Saves a GIF of the Gantt chart. Used only if the
                schedule is completed.
        render_config:
            Configuration for rendering. See
            :class:`~job_shop_lib.RenderConfig`.

        use_padding:
            Whether to use padding in observations. If True, all matrices
            are padded to fixed sizes based on the maximum instance size.
            Values are padded with -1, except for the "removed_nodes" key,
            which is padded with ``True``, indicating that the node is
            removed.
    """

    def __init__(
        self,
        instance_generator: InstanceGenerator,
        feature_observer_configs: Sequence[FeatureObserverConfig],
        graph_initializer: Callable[
            [JobShopInstance], JobShopGraph
        ] = build_resource_task_graph,
        graph_updater_config: DispatcherObserverConfig[
            Type[GraphUpdater]
        ] = DispatcherObserverConfig(class_type=ResidualGraphUpdater),
        ready_operations_filter: Callable[
            [Dispatcher, List[Operation]], List[Operation]
        ] = filter_dominated_operations,
        reward_function_config: DispatcherObserverConfig[
            Type[RewardObserver]
        ] = DispatcherObserverConfig(class_type=MakespanReward),
        render_mode: Optional[str] = None,
        render_config: Optional[RenderConfig] = None,
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
            ready_operations_filter=ready_operations_filter,
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
    def reward_function(self) -> RewardObserver:
        """Returns the current reward function instance."""
        return self.single_job_shop_graph_env.reward_function

    @reward_function.setter
    def reward_function(self, reward_function: RewardObserver) -> None:
        """Sets the reward function instance."""
        self.single_job_shop_graph_env.reward_function = reward_function

    @property
    def ready_operations_filter(
        self,
    ) -> Optional[Callable[[Dispatcher, List[Operation]], List[Operation]]]:
        """Returns the current ready operations filter."""
        return (
            self.single_job_shop_graph_env.dispatcher.ready_operations_filter
        )

    @ready_operations_filter.setter
    def ready_operations_filter(
        self,
        pruning_function: Callable[
            [Dispatcher, List[Operation]], List[Operation]
        ],
    ) -> None:
        """Sets the ready operations filter."""
        self.single_job_shop_graph_env.dispatcher.ready_operations_filter = (
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
        seed: Optional[int] = None,
        options: Dict[str, Any] | None = None,
    ) -> Tuple[ObservationDict, Dict[str, Any]]:
        """Resets the environment and returns the initial observation.

        Args:
            seed: Random seed for reproducibility.
            options: Additional options for reset (currently unused).

        Returns:
            A tuple containing:
            - ObservationDict: The initial observation of the environment.
            - dict: An info dictionary containing additional information about
              the reset state. This may include details about the generated
              instance or initial graph structure.
        """
        instance = self.instance_generator.generate()
        graph = self.graph_initializer(instance)
        self.single_job_shop_graph_env = SingleJobShopGraphEnv(
            job_shop_graph=graph,
            feature_observer_configs=self.feature_observer_configs,
            reward_function_config=self.reward_function_config,
            ready_operations_filter=self.ready_operations_filter,
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
        self, action: Tuple[int, int]
    ) -> Tuple[ObservationDict, float, bool, bool, Dict[str, Any]]:
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
            - A dictionary with additional information. The dictionary
              contains the following keys: "feature_names", the names of the
              features in the observation; and "available_operations_with_ids",
              a list of available actions in the form of (operation_id,
              machine_id, job_id).
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
        padding_value: Dict[str, float | bool] = defaultdict(lambda: -1)
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

    def _get_output_shape(self, key: str) -> Tuple[int, ...]:
        """Returns the output shape of the observation space key."""
        output_shape = self.observation_space[key].shape
        assert output_shape is not None  # Make mypy happy
        return output_shape

    def render(self) -> None:
        self.single_job_shop_graph_env.render()

    def get_available_actions_with_ids(self) -> List[Tuple[int, int, int]]:
        """Returns a list of available actions in the form of
        (operation_id, machine_id, job_id)."""
        return self.single_job_shop_graph_env.get_available_actions_with_ids()

    def validate_action(self, action: Tuple[int, int]) -> None:
        """Validates the action.

        Args:
            action:
                The action to validate. The action is a tuple of two integers
                (job_id, machine_id): the job ID and the machine ID in which
                to schedule the operation.

        Raises:
            ValidationError: If the action is invalid.
        """
        self.single_job_shop_graph_env.validate_action(action)
