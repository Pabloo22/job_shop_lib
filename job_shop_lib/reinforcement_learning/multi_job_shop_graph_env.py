"""Home of the `GraphEnvironment` class."""

from typing import Callable

import gymnasium as gym
import numpy as np

from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.dispatching import Dispatcher, prune_dominated_operations
from job_shop_lib.dispatching.feature_observers import (
    CompositeFeatureObserver,
    FeatureObserverConfig,
    feature_observer_factory,
)
from job_shop_lib.generation import InstanceGenerator
from job_shop_lib.graphs import JobShopGraph, build_agent_task_graph


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
                - "edge_list": Matrix with the edge list in COO format. Each
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
        graph_builder: Callable[
            [JobShopInstance], JobShopGraph
        ] = build_agent_task_graph,
        pruning_function: (
            Callable[[Dispatcher, list[Operation]], list[Operation]] | None
        ) = prune_dominated_operations,
    ) -> None:
        super().__init__()

        # Check no-composite feature observer
        self.instance_generator = instance_generator
        self.feature_observer_configs = feature_observer_configs
        self.graph_builder = graph_builder
        self.pruning_function = pruning_function

        self.action_space = gym.spaces.Discrete(
            instance_generator.max_num_jobs
        )
        self.observation_space = self._infer_observation_space()

        self.dispatcher = None
        self.composite_observer = None

    def _infer_observation_space(self):
        """Infer the observation space from the feature observers.

        The observation space can be inferred generating an instance with the
        maximum number of jobs and machines, creating a graph (number of nodes
        maximum, and edge types), and initializing the Dispatcher class with
        the feature observers (dimension of the feature vector).
        """
        instance_with_max_size = self.instance_generator.generate(
            num_jobs=self.instance_generator.max_num_jobs,
            num_machines=self.instance_generator.max_num_machines,
        )
        graph = self.graph_builder(instance_with_max_size)
        dispatcher = Dispatcher(instance_with_max_size)
        composite_observer = self._initialize_feature_observers(dispatcher)
        feature_dict = self._create_dict_space(graph, composite_observer)

        return gym.spaces.Dict(feature_dict)

    def _removed_nodes(self, graph: JobShopGraph) -> np.ndarray:
        """Return the removed nodes as a binary vector."""
        return np.array(graph.removed_nodes, dtype=np.int8).reshape(-1, 1)

    @staticmethod
    def _edge_list(graph: JobShopGraph) -> np.ndarray:
        """Return the edge list as a matrix."""
        return np.array(graph.graph.edges(), dtype=np.int32).T

    def _initialize_feature_observers(
        self, dispatcher: Dispatcher
    ) -> CompositeFeatureObserver:
        """Creates the composite feature observer."""
        observers = [
            feature_observer_factory(
                observer_config.feature_observer_type,
                dispatcher=dispatcher,
                **observer_config.kwargs
            )
            for observer_config in self.feature_observer_configs
        ]
        composite_observer = CompositeFeatureObserver(dispatcher, observers)
        return composite_observer

    @staticmethod
    def _create_dict_space(
        graph: JobShopGraph, composite_observer: CompositeFeatureObserver
    ) -> dict[str, gym.Space]:
        """Create the observation space as a dictionary."""
        dict_space: dict[str, gym.Space] = {
            "removed_nodes": gym.spaces.MultiBinary(len(graph.nodes)),
            "edge_list": gym.spaces.MultiDiscrete(
                np.full((2, graph.num_edges), fill_value=len(graph.nodes))
            ),
        }
        for feature_type, matrix in composite_observer.features.items():
            dict_space[feature_type.value] = gym.spaces.Box(
                low=-np.inf, high=np.inf, shape=matrix.shape
            )
        return dict_space


if __name__ == "__main__":
    import networkx as nx

    G = nx.Graph()  # or DiGraph, MultiGraph, MultiDiGraph, etc
    G.add_edge(0, 1)
    G.add_edge(1, 2)
    G.add_edge(2, 3, weight=5)
    print(np.array(G.edges()).T)
