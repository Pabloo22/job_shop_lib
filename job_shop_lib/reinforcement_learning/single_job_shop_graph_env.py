"""Home of the `SingleJobShopGraphEnv` class."""

from copy import deepcopy
from collections.abc import Callable, Sequence
from typing import Any

import matplotlib.pyplot as plt
import gymnasium as gym
import numpy as np

from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.graphs import JobShopGraph
from job_shop_lib.graphs.graph_updaters import (
    GraphUpdater,
    ResidualGraphUpdater,
)
from job_shop_lib.dispatching import (
    Dispatcher,
    prune_dominated_operations,
    DispatcherObserverConfig,
)
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserverConfig,
    CompositeFeatureObserver,
)
from job_shop_lib.visualization import GanttChartCreator
from job_shop_lib.reinforcement_learning import (
    RewardFunction,
    MakespanReward,
    add_padding,
    RenderConfig,
    ObservationSpaceKey,
    ObservationDict,
)


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

    # I think the class is easier to use this way. We could initiliaze the
    # class from Dispatcher or an already initialized RewardFunction. However,
    # it would be impossible to add good default values.
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        job_shop_graph: JobShopGraph,
        feature_observer_configs: Sequence[FeatureObserverConfig],
        reward_function_config: DispatcherObserverConfig[
            type[RewardFunction]
        ] = DispatcherObserverConfig(class_type=MakespanReward),
        graph_updater_config: DispatcherObserverConfig[
            type[GraphUpdater]
        ] = DispatcherObserverConfig(class_type=ResidualGraphUpdater),
        pruning_function: (
            Callable[[Dispatcher, list[Operation]], list[Operation]] | None
        ) = prune_dominated_operations,
        render_mode: str | None = None,
        render_config: RenderConfig | None = None,
        use_padding: bool = True,
    ) -> None:
        """Initializes the SingleJobShopGraphEnv environment.

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
            pruning_function:
                The function to use for pruning dominated operations.
            render_mode:
                The mode for rendering the environment ("human", "save_video",
                "save_gif").
            render_config:
                Configuration for rendering (e.g., paths for saving videos
                or GIFs).
            use_padding:
                Whether to use padding for the edge index.
        """
        super().__init__()
        # Used for resetting the environment
        self.initial_job_shop_graph = deepcopy(job_shop_graph)

        self.dispatcher = Dispatcher(
            self.instance, pruning_function=pruning_function
        )

        # Observers added to track the environment state
        self.composite_observer = (
            CompositeFeatureObserver.from_feature_observer_configs(
                self.dispatcher, feature_observer_configs
            )
        )
        self.reward_function = reward_function_config.class_type(
            dispatcher=self.dispatcher, **reward_function_config.kwargs
        )
        self.graph_updater = graph_updater_config.class_type(
            dispatcher=self.dispatcher,
            job_shop_graph=job_shop_graph,
            **graph_updater_config.kwargs,
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

    def _get_observation_space(self) -> gym.spaces.Dict:
        """Returns the observation space dictionary."""
        num_edges = self.job_shop_graph.num_edges
        dict_space: dict[str, gym.Space] = {
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
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[ObservationDict, dict]:
        """Resets the environment."""
        super().reset(seed=seed, options=options)
        self.dispatcher.reset()
        obs = self.get_observation()
        return obs, {}

    def step(
        self, action: tuple[int, int]
    ) -> tuple[ObservationDict, float, bool, bool, dict[str, Any]]:
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

        obs = self.get_observation()
        reward = self.reward_function.last_reward
        done = self.dispatcher.schedule.is_complete()
        truncated = False
        info: dict[str, Any] = {
            "feature_names": self.composite_observer.column_names,
            "available_operations": self.dispatcher.available_operations(),
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

    def _get_edge_index(self) -> np.ndarray:
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
        """Renders the environment."""
        if self.render_mode == "human":
            self.gantt_chart_creator.plot_gantt_chart()
            plt.show(block=False)
        elif self.render_mode == "save_video":
            self.gantt_chart_creator.create_video()
        elif self.render_mode == "save_gif":
            self.gantt_chart_creator.create_gif()


if __name__ == "__main__":
    from job_shop_lib.dispatching.feature_observers import (
        FeatureObserverType,
        FeatureType,
    )
    from job_shop_lib.graphs import build_disjunctive_graph
    from job_shop_lib.benchmarking import load_benchmark_instance

    instance = load_benchmark_instance("ft06")
    job_shop_graph_ = build_disjunctive_graph(instance)
    feature_observer_configs_ = [
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
