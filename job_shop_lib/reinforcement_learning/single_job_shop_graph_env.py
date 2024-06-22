"""Home of the `SingleJobShopGraphEnv` class."""

from copy import deepcopy
from enum import Enum
from typing import Callable, Any, TypedDict

import matplotlib.pyplot as plt
import gymnasium as gym
import numpy as np

from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.graphs import JobShopGraph
from job_shop_lib.dispatching import Dispatcher, prune_dominated_operations
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserverConfig,
    CompositeFeatureObserver,
    FeatureType,
)

from job_shop_lib.reinforcement_learning import (
    RewardFunction,
    GanttChartCreator,
    GanttChartWrapperConfig,
    VideoConfig,
    GifConfig,
)


class ObservationSpaceKey(str, Enum):
    """Enumeration of the keys for the observation space dictionary."""

    REMOVED_NODES = "removed_nodes"
    EDGE_LIST = "edge_list"
    OPERATIONS = FeatureType.OPERATIONS.value
    JOBS = FeatureType.JOBS.value
    MACHINES = FeatureType.MACHINES.value


class RenderConfig(TypedDict, total=False):
    """Configuration needed to initialize the `GanttChartCreator` class."""

    gantt_chart_wrapper_config: GanttChartWrapperConfig
    video_config: VideoConfig
    gif_config: GifConfig


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

        Keys can be accessed using the `ObservationSpaceKey` enumeration.

    Render modes:
        - human: Renders the current Gannt chart.
        - save_video: Saves a video of the Gantt chart. Used only if the
            schedule is completed.
        - save_gif: Saves a GIF of the Gantt chart. Used only if the schedule
            is completed.
    """

    metadata = {"render_modes": ["human", "save_video", "save_gif"]}

    def __init__(
        self,
        job_shop_graph: JobShopGraph,
        feature_observer_configs: list[FeatureObserverConfig],
        reward_function: type[RewardFunction],
        pruning_function: (
            Callable[[Dispatcher, list[Operation]], list[Operation]] | None
        ) = prune_dominated_operations,
        render_mode: str | None = None,
        render_config: RenderConfig | None = None,
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
            [self.instance.num_jobs, self.instance.num_machines], start=[0, -1]
        )
        self.observation_space = self._get_observation_space()
        self.render_mode = render_mode
        if render_config is None:
            render_config = {}
        self.gantt_chart_creator = GanttChartCreator(
            dispatcher=self.dispatcher, **render_config
        )

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

    @property
    def instance(self) -> JobShopInstance:
        """Returns the instance the environment is working on."""
        return self.job_shop_graph.instance

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
        if machine_id == -1:
            machine_id = operation.machine_id
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
        if self.render_mode == "human":
            self.gantt_chart_creator.plot_gantt_chart()
            plt.show(block=False)
        elif self.render_mode == "save_video":
            self.gantt_chart_creator.create_video()
        elif self.render_mode == "save_gif":
            self.gantt_chart_creator.create_gif()
