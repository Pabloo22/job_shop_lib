"""Home of the `SingleJobShopGraphEnv` class."""

from copy import deepcopy
from collections.abc import Callable, Sequence
from typing import Any, Dict, Tuple, List, Optional, Type

import matplotlib.pyplot as plt
import gymnasium as gym
import numpy as np
from numpy.typing import NDArray

from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.graphs import JobShopGraph
from job_shop_lib.graphs.graph_updaters import (
    GraphUpdater,
    ResidualGraphUpdater,
)
from job_shop_lib.exceptions import ValidationError
from job_shop_lib.dispatching import (
    Dispatcher,
    filter_dominated_operations,
    DispatcherObserverConfig,
)
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserverConfig,
    CompositeFeatureObserver,
)
from job_shop_lib.visualization.gantt import GanttChartCreator
from job_shop_lib.reinforcement_learning import (
    RewardObserver,
    MakespanReward,
    add_padding,
    RenderConfig,
    ObservationSpaceKey,
    ObservationDict,
)


class SingleJobShopGraphEnv(gym.Env):
    """A Gymnasium environment for solving a specific instance of the Job Shop
    Scheduling Problem represented as a graph.

    This environment manages the scheduling process for a single Job Shop
    instance, using a graph representation and various observers to track the
    state and compute rewards.

    Observation Space:
        A dictionary with the following keys:

        - "removed_nodes": Binary vector indicating removed graph nodes.
        - "edge_list": Matrix of graph edges in COO format.
        - Feature matrices: Keys corresponding to the composite observer
          features (e.g., "operations", "jobs", "machines").

    Action Space:
        MultiDiscrete space representing (job_id, machine_id) pairs.

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
            (job_id, machine_id). The machine_id can be -1 if the selected
            operation can only be scheduled in one machine.

        observation_space:
            Defines the observation space. The observation is a dictionary
            with the following keys:

            - "removed_nodes": Binary vector indicating removed graph nodes.
            - "edge_list": Matrix of graph edges in COO format.
            - Feature matrices: Keys corresponding to the composite observer
                features (e.g., "operations", "jobs", "machines").

        render_mode:
            The mode for rendering the environment ("human", "save_video",
            "save_gif").

        gantt_chart_creator:
            Creates Gantt chart visualizations. See
            :class:`~job_shop_lib.visualization.GanttChartCreator`.

        use_padding:
            Whether to use padding in observations. Padding maintains the
            observation space shape when the number of nodes changes.

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
        use_padding:
            Whether to use padding in observations. Padding maintains the
            observation space shape when the number of nodes changes.
    """

    metadata = {"render_modes": ["human", "save_video", "save_gif"]}

    # I think the class is easier to use this way. We could initiliaze the
    # class from Dispatcher or an already initialized RewardFunction. However,
    # it would be impossible to add good default values.
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        job_shop_graph: JobShopGraph,
        feature_observer_configs: Sequence[FeatureObserverConfig],
        reward_function_config: DispatcherObserverConfig[
            Type[RewardObserver]
        ] = DispatcherObserverConfig(class_type=MakespanReward),
        graph_updater_config: DispatcherObserverConfig[
            Type[GraphUpdater]
        ] = DispatcherObserverConfig(class_type=ResidualGraphUpdater),
        ready_operations_filter: Optional[
            Callable[[Dispatcher, List[Operation]], List[Operation]]
        ] = filter_dominated_operations,
        render_mode: Optional[str] = None,
        render_config: Optional[RenderConfig] = None,
        use_padding: bool = True,
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
        self.use_padding = use_padding

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

    def machine_utilization(self) -> NDArray[np.float32]:
        """Returns utilization percentage for each machine."""
        total_time = max(1, self.current_makespan())  # Avoid division by zero
        machine_busy_time = np.zeros(self.instance.num_machines)

        for m_id, m_schedule in enumerate(self.dispatcher.schedule.schedule):
            machine_busy_time[m_id] = sum(
                op.operation.duration for op in m_schedule
            )

        return machine_busy_time / total_time

    def _get_observation_space(self) -> gym.spaces.Dict:
        """Returns the observation space dictionary."""
        num_edges = self.job_shop_graph.num_edges
        dict_space: Dict[str, gym.Space] = {
            ObservationSpaceKey.REMOVED_NODES.value: gym.spaces.MultiBinary(
                len(self.job_shop_graph.nodes)
            ),
            ObservationSpaceKey.EDGE_INDEX.value: gym.spaces.MultiDiscrete(
                np.full(
                    (2, num_edges),
                    fill_value=len(self.job_shop_graph.nodes) + 1,
                    dtype=np.int32,
                ),
                start=np.full(
                    (2, num_edges),
                    fill_value=-1,  # -1 is used for padding
                    dtype=np.int32,
                ),
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
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[ObservationDict, dict]:
        """Resets the environment."""
        super().reset(seed=seed, options=options)
        self.dispatcher.reset()
        obs = self.get_observation()
        return obs, {
            "feature_names": self.composite_observer.column_names,
            "available_operations_with_ids": (
                self.get_available_actions_with_ids()
            ),
        }

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
        job_id, machine_id = action
        operation = self.dispatcher.next_operation(job_id)
        if machine_id == -1:
            machine_id = operation.machine_id

        self.dispatcher.dispatch(operation, machine_id)

        obs = self.get_observation()
        reward = self.reward_function.last_reward
        done = self.dispatcher.schedule.is_complete()
        truncated = False
        info: Dict[str, Any] = {
            "feature_names": self.composite_observer.column_names,
            "available_operations_with_ids": (
                self.get_available_actions_with_ids()
            ),
        }
        return obs, reward, done, truncated, info

    def get_observation(self) -> ObservationDict:
        """Returns the current observation of the environment."""
        observation: ObservationDict = {
            ObservationSpaceKey.REMOVED_NODES.value: np.array(
                self.job_shop_graph.removed_nodes, dtype=bool
            ),
            ObservationSpaceKey.EDGE_INDEX.value: self._get_edge_index(),
        }
        for feature_type, matrix in self.composite_observer.features.items():
            observation[feature_type.value] = matrix
        return observation

    def _get_edge_index(self) -> NDArray[np.int32]:
        """Returns the edge index matrix."""
        edge_index = np.array(
            self.job_shop_graph.graph.edges(), dtype=np.int32
        ).T

        if self.use_padding:
            output_shape = self.observation_space[
                ObservationSpaceKey.EDGE_INDEX.value
            ].shape
            assert output_shape is not None  # For the type checker
            edge_index = add_padding(
                edge_index, output_shape=output_shape, dtype=np.int32
            )
        return edge_index

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

    def get_available_actions_with_ids(self) -> List[Tuple[int, int, int]]:
        """Returns a list of available actions in the form of
        (operation_id, machine_id, job_id)."""
        available_operations = self.dispatcher.available_operations()
        available_operations_with_ids = []
        for operation in available_operations:
            job_id = operation.job_id
            operation_id = operation.operation_id
            for machine_id in operation.machines:
                available_operations_with_ids.append(
                    (operation_id, machine_id, job_id)
                )
        return available_operations_with_ids

    def validate_action(self, action: Tuple[int, int]) -> None:
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


if __name__ == "__main__":
    from job_shop_lib.dispatching.feature_observers import (
        FeatureObserverType,
        FeatureType,
    )
    from job_shop_lib.graphs import build_disjunctive_graph
    from job_shop_lib.benchmarking import load_benchmark_instance

    instance = load_benchmark_instance("ft06")
    job_shop_graph_ = build_disjunctive_graph(instance)
    feature_observer_configs_: List[DispatcherObserverConfig] = [
        DispatcherObserverConfig(
            FeatureObserverType.IS_READY,
            kwargs={"feature_types": [FeatureType.JOBS]},
        )
    ]

    env = SingleJobShopGraphEnv(
        job_shop_graph=job_shop_graph_,
        feature_observer_configs=feature_observer_configs_,
        render_mode="save_video",
        render_config={"video_config": {"fps": 4}},
    )
