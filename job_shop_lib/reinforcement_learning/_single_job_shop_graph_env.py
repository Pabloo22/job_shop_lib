"""Home of the `SingleJobShopGraphEnv` class."""

from copy import deepcopy
from collections.abc import Callable, Sequence
from typing import Any
import warnings

import matplotlib.pyplot as plt
import gymnasium as gym
import numpy as np

from numpy.typing import NDArray

from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.graphs import JobShopGraph, NodeType
from job_shop_lib.graphs.graph_updaters import (
    GraphUpdater,
    ResidualGraphUpdater,
)
from job_shop_lib.dispatching import (
    Dispatcher,
    filter_dominated_operations,
    DispatcherObserverConfig,
)
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserverConfig,
    CompositeFeatureObserver,
    FeatureObserver,
    FeatureObserverType,
    FeatureType,
)
from job_shop_lib.visualization.gantt import GanttChartCreator
from job_shop_lib.reinforcement_learning import (
    RewardObserver,
    MakespanReward,
    RenderConfig,
    ObservationSpaceKey,
    ObservationDict,
)
from job_shop_lib.exceptions import ValidationError


_FEATURE_TYPE_STR_TO_NODE_TYPE = {
    FeatureType.OPERATIONS.value: NodeType.OPERATION,
    FeatureType.MACHINES.value: NodeType.MACHINE,
    FeatureType.JOBS.value: NodeType.JOB,
}


class SingleJobShopGraphEnv(gym.Env):
    """A Gymnasium environment for solving a specific instance of the Job Shop
    Scheduling Problem represented as a graph.

    This environment manages the scheduling process for a single Job Shop
    instance, using a graph representation and various observers to track the
    state and compute rewards.

    Observation Space:
        A dictionary with the following keys:

        - "edge_index_dict": Dictionary mapping edge types to
          their COO format indices.
        - "available_operations_with_ids": List of available actions
          represented as (operation_id, machine_id, job_id) tuples.
        - "node_features_dict": (optional) Dictionary mapping node types to
          their feature matrices.

    Action Space:
        MultiDiscrete space representing (operation_id, machine_id) pairs.

    Render Modes:

    - "human": Displays the current Gantt chart.
    - "save_video": Saves a video of the complete Gantt chart.
    - "save_gif": Saves a GIF of the complete Gantt chart.

    Attributes:
        dispatcher:
            Manages the scheduling process. See
            :class:`~job_shop_lib.dispatching.Dispatcher`.

        composite_observer:
            A :class:`~job_shop_lib.dispatching.feature_observers.
            CompositeFeatureObserver` which aggregates features from multiple
            observers.

        graph_updater:
            Updates the graph representation after each action. See
            :class:`~job_shop_lib.graphs.GraphUpdater`.

        reward_function:
            Computes rewards for actions taken. See
            :class:`~job_shop_lib.reinforcement_learning.RewardObserver`.

        action_space:
            Defines the action space. The action is a tuple of two integers
            (operation_id, machine_id). The machine_id can be -1 if the
            selected operation can only be scheduled in one machine.

        observation_space:
            Defines the observation space. The observation is a dictionary
            with the following keys:

            - "edge_index_dict": Dictionary mapping edge types to
              their COO format indices.
            - "available_operations_with_ids": List of available
              actions represented as
              (operation_id, machine_id, job_id) tuples.
            - "node_features_dict": (optional) Dictionary mapping
              node types to their feature matrices.

        render_mode:
            The mode for rendering the environment ("human", "save_video",
            "save_gif").

        gantt_chart_creator:
            Creates Gantt chart visualizations. See
            :class:`~job_shop_lib.visualization.GanttChartCreator`.

    Args:
        job_shop_graph:
            The JobShopGraph instance representing the job shop problem.
        feature_observer_configs:
            A list of FeatureObserverConfig instances for the feature
            observers.
        reward_function_config:
            The configuration for the reward function.
        graph_updater_config:
            The configuration for the graph updater.
        ready_operations_filter:
            The function to use for pruning dominated operations.
        render_mode:
            The mode for rendering the environment ("human", "save_video",
            "save_gif").
        render_config:
            Configuration for rendering (e.g., paths for saving videos
            or GIFs). See :class:`~job_shop_lib.visualization.RenderConfig`.
    """

    metadata = {"render_modes": ["human", "save_video", "save_gif"]}

    # I think the class is easier to use this way. We could initiliaze the
    # class from Dispatcher or an already initialized RewardFunction. However,
    # it would be impossible to add good default values.
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        job_shop_graph: JobShopGraph,
        feature_observer_configs: Sequence[
            str
            | FeatureObserverType
            | type[FeatureObserver]
            | FeatureObserverConfig
        ],
        reward_function_config: DispatcherObserverConfig[
            type[RewardObserver]
        ] = DispatcherObserverConfig(class_type=MakespanReward),
        graph_updater_config: DispatcherObserverConfig[
            type[GraphUpdater]
        ] = DispatcherObserverConfig(class_type=ResidualGraphUpdater),
        ready_operations_filter: (
            Callable[[Dispatcher, list[Operation]], list[Operation]] | None
        ) = filter_dominated_operations,
        render_mode: str | None = None,
        render_config: RenderConfig | None = None,
    ) -> None:
        super().__init__()
        # Used for resetting the environment
        self.initial_job_shop_graph = deepcopy(job_shop_graph)

        self.dispatcher = Dispatcher(
            job_shop_graph.instance,
            ready_operations_filter=ready_operations_filter,
        )

        # Observers added to track the environment state
        self.composite_observer = (
            CompositeFeatureObserver.from_feature_observer_configs(
                self.dispatcher, feature_observer_configs
            )
        )
        self.graph_updater = graph_updater_config.class_type(
            dispatcher=self.dispatcher,
            job_shop_graph=job_shop_graph,
            **graph_updater_config.kwargs,
        )
        self.reward_function = reward_function_config.class_type(
            dispatcher=self.dispatcher, **reward_function_config.kwargs
        )
        self.action_space = gym.spaces.MultiDiscrete(
            [self.instance.num_jobs, self.instance.num_machines], start=[0, -1]
        )

        self.observation_space: gym.spaces.Dict = self._get_observation_space()
        self.render_mode = render_mode
        if render_config is None:
            render_config = {}
        self.gantt_chart_creator = GanttChartCreator(
            dispatcher=self.dispatcher, **render_config
        )

    @property
    def instance(self) -> JobShopInstance:
        """Returns the instance the environment is working on."""
        return self.job_shop_graph.instance

    @property
    def job_shop_graph(self) -> JobShopGraph:
        """Returns the job shop graph."""
        return self.graph_updater.job_shop_graph

    def current_makespan(self) -> int:
        """Returns current makespan of partial schedule."""
        return self.dispatcher.schedule.makespan()

    def machine_utilization(  # noqa: DOC201,DOC203
        self,
    ) -> NDArray[np.float32]:
        """Returns utilization percentage for each machine.

        Returns:
            Utilization percentage for each machine as a numpy array.

        .. deprecated:: 1.1.2
            This method is deprecated and will be removed in version 2.0.0.
        """
        warnings.warn(
            "machine_utilization is deprecated and will be removed in "
            "version 2.0.0",
            DeprecationWarning,
            stacklevel=2,
        )
        total_time = max(1, self.current_makespan())  # Avoid division by zero
        machine_busy_time = np.zeros(
            self.instance.num_machines, dtype=np.float32
        )

        for m_id, m_schedule in enumerate(self.dispatcher.schedule.schedule):
            machine_busy_time[m_id] = sum(
                op.operation.duration for op in m_schedule
            )

        return machine_busy_time / total_time  # type: ignore[return-value]

    def _get_observation_space(self) -> gym.spaces.Dict:
        """Returns the observation space dictionary."""

        obs_space = gym.spaces.Dict()
        initial_edge_index_dict = self.initial_job_shop_graph.edge_index_dict
        edge_index_space = gym.spaces.Dict(
            {
                key: gym.spaces.Box(  # type: ignore
                    low=0,
                    high=np.iinfo(np.int32).max,
                    shape=edges.shape,
                    dtype=np.int32,
                )
                for key, edges in initial_edge_index_dict.items()
            }
        )
        obs_space[ObservationSpaceKey.EDGE_INDEX] = edge_index_space

        num_available_actions = len(self.get_available_actions_with_ids())
        available_actions_with_ids_space = gym.spaces.Box(
            low=np.full((num_available_actions, 3), -1, dtype=np.int32),
            high=np.array(
                [
                    len(self.job_shop_graph.nodes_by_type[NodeType.OPERATION])
                    - 1,
                    len(self.job_shop_graph.nodes_by_type[NodeType.MACHINE])
                    - 1,
                    len(self.job_shop_graph.nodes_by_type[NodeType.JOB]) - 1,
                ],
                dtype=np.int32,
            )
            .reshape(1, 3)
            .repeat(num_available_actions, axis=0),
            shape=(num_available_actions, 3),
            dtype=np.int32,
        )
        obs_space[ObservationSpaceKey.ACTION_MASK] = (
            available_actions_with_ids_space
        )
        if not self.composite_observer.features:
            return obs_space
        node_features_space = gym.spaces.Dict(
            {
                feature_type.value: gym.spaces.Box(
                    low=-np.inf,
                    high=np.inf,
                    shape=matrix.shape,
                    dtype=np.float32,
                )
                for feature_type, matrix in
                self.composite_observer.features.items()
            }
        )
        obs_space[ObservationSpaceKey.NODE_FEATURES] = node_features_space

        return obs_space

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[ObservationDict, dict[str, Any]]:
        """Resets the environment.

        Args:
            seed:
                Added to match the signature of the parent class. It is not
                used in this method.
            options:
                Additional options to pass to the environment. Not used in
                this method.

        Returns:
            A tuple containing the following elements:

            - The observation of the environment.
            - A dictionary with additional information, keys
                include: "feature_names", the names of the features in the
                observation; and "available_operations_with_ids", a list of
                available a list of available actions in the form of
                (operation_id, machine_id, job_id).
        """
        super().reset(seed=seed, options=options)
        self.dispatcher.reset()
        obs = self.get_observation()
        return obs, {"feature_names": self.composite_observer.column_names}

    def step(
        self, action: tuple[int, int]
    ) -> tuple[ObservationDict, float, bool, bool, dict[str, Any]]:
        """Takes a step in the environment.

        Args:
            action:
                The action to take. The action is a tuple of two integers
                (operation_id, machine_id):
                the operation ID and the machine ID in which to schedule the
                operation.

        Returns:
            A tuple containing the following elements:

            - The observation of the environment.
            - The reward obtained.
            - Whether the environment is done.
            - Whether the episode was truncated (always False).
            - A dictionary with additional information. The dictionary
              contains the following keys: "feature_names", the names of the
              features in the observation.
        """
        node_operation_id, node_machine_id = action
        operation = self.job_shop_graph.nodes_map[
            ("operation", node_operation_id)
        ].operation
        if node_machine_id == -1:
            machine_id = operation.machine_id
        else:
            machine_id = self.job_shop_graph.nodes_map[
                ("machine", node_machine_id)
            ].machine_id

        self.dispatcher.dispatch(operation, machine_id)

        obs = self.get_observation()
        reward = self.reward_function.last_reward
        done = self.dispatcher.schedule.is_complete()
        truncated = False
        info: dict[str, Any] = {
            "feature_names": self.composite_observer.column_names
        }
        return obs, reward, done, truncated, info

    def get_observation(self) -> ObservationDict:
        """Returns the current observation of the environment."""
        node_features_dict: dict[str, NDArray[np.float32]] = {}
        removed_nodes = self.job_shop_graph.removed_nodes

        for feature_type, matrix in self.composite_observer.features.items():
            # Use the provided mapping for robust conversion
            node_type = _FEATURE_TYPE_STR_TO_NODE_TYPE[feature_type.value]
            removed_mask = removed_nodes.get(node_type.name.lower())

            current_matrix = matrix
            if removed_mask is not None:
                # The mask is True for removed nodes; invert to get active ones
                active_mask = ~np.array(removed_mask, dtype=bool)
                current_matrix = matrix[active_mask]

            node_features_dict[feature_type.value] = current_matrix

        # Construct the final observation dictionary with the nested structure
        observation: ObservationDict = {
            ObservationSpaceKey.EDGE_INDEX:  # type: ignore
            self.job_shop_graph.edge_index_dict,
            ObservationSpaceKey.ACTION_MASK:  # type: ignore
            self.get_available_actions_with_ids(),
            ObservationSpaceKey.NODE_FEATURES:  # type: ignore
            node_features_dict,
        }
        return observation

    def render(self):
        """Renders the environment.

        The rendering mode is set by the `render_mode` attribute:

        - human: Renders the current Gannt chart.
        - save_video: Saves a video of the Gantt chart. Used only if the
            schedule is completed.
        - save_gif: Saves a GIF of the Gantt chart. Used only if the schedule
            is completed.
        """
        if self.render_mode == "human":
            self.gantt_chart_creator.plot_gantt_chart()
            plt.show(block=False)
        elif self.render_mode == "save_video":
            self.gantt_chart_creator.create_video()
        elif self.render_mode == "save_gif":
            self.gantt_chart_creator.create_gif()

    def get_available_actions_with_ids(self) -> NDArray[np.int32]:
        """Returns a list of available actions in the form of
        (operation_id, machine_id, job_id)."""
        available_operations = self.dispatcher.available_operations()
        available_operations_with_ids = []
        for operation in available_operations:
            # For now only local operation ids are obtained
            # from the graph
            # jobs or machine ids will not be included
            # if not present in the graph
            operation_id = self.job_shop_graph.get_operation_node(
                operation.operation_id
            ).node_id[1]
            if len(self.job_shop_graph.nodes_by_type[NodeType.JOB]) > 0:
                job_id = self.job_shop_graph.get_job_node(
                    operation.job_id
                ).node_id[1]
            else:
                job_id = -1  # Use -1 to indicate job_id is not in the graph
            if len(self.job_shop_graph.nodes_by_type[NodeType.MACHINE]) > 0:
                for machine_id in operation.machines:
                    machine_id = self.job_shop_graph.get_machine_node(
                        machine_id
                    ).node_id[1]
                    available_operations_with_ids.append(
                        [operation_id, machine_id, job_id]
                    )
            else:
                available_operations_with_ids.append(
                    [operation_id, -1, job_id]
                )
        return np.array(available_operations_with_ids, dtype=np.int32)

    def validate_action(self, action: tuple[int, int]) -> None:
        """Validates that the action is legal in the current state.

        Args:
            action:
                The action to validate. The action is a tuple of two integers
                (job_id, machine_id).

        Raises:
            ValidationError: If the action is invalid.
        """
        job_id, machine_id = action
        if not 0 <= job_id < self.instance.num_jobs:
            raise ValidationError(f"Invalid job_id {job_id}")

        if not -1 <= machine_id < self.instance.num_machines:
            raise ValidationError(f"Invalid machine_id {machine_id}")

        # Check if job has operations left
        job = self.instance.jobs[job_id]
        if self.dispatcher.job_next_operation_index[job_id] >= len(job):
            raise ValidationError(f"Job {job_id} has no operations left")

        next_operation = self.dispatcher.next_operation(job_id)
        if machine_id == -1 and len(next_operation.machines) > 1:
            raise ValidationError(
                f"Operation {next_operation} requires a machine_id"
            )
