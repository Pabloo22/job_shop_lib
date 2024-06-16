"""Utility functions shared by the reinforcement learning components."""

import enum

import gymnasium as gym
import numpy as np

from job_shop_lib.graphs import JobShopGraph
from job_shop_lib.dispatching.feature_observers import (
    CompositeFeatureObserver,
    FeatureType,
)


class ObservationSpaceKey(str, enum.Enum):
    """Enumeration of the keys for the observation space dictionary."""

    REMOVED_NODES = "removed_nodes"
    EDGE_LIST = "edge_list"
    OPERATIONS = FeatureType.OPERATIONS.value
    JOBS = FeatureType.JOBS.value
    MACHINES = FeatureType.MACHINES.value


def create_dict_space(
    graph: JobShopGraph, composite_observer: CompositeFeatureObserver
) -> dict[str, gym.Space]:
    """Create the observation space as a dictionary."""
    dict_space: dict[str, gym.Space] = {
        ObservationSpaceKey.REMOVED_NODES.value: gym.spaces.MultiBinary(
            len(graph.nodes)
        ),
        ObservationSpaceKey.EDGE_LIST.value: gym.spaces.MultiDiscrete(
            np.full((2, graph.num_edges), fill_value=len(graph.nodes))
        ),
    }
    for feature_type, matrix in composite_observer.features.items():
        dict_space[feature_type.value] = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=matrix.shape
        )
    return dict_space


def create_observation(
    graph: JobShopGraph, composite_observer: CompositeFeatureObserver
) -> dict[str, np.ndarray]:
    """Create the observation dictionary."""
    observation: dict[str, np.ndarray] = {
        "removed_nodes": np.array(graph.removed_nodes, dtype=int),
        "edge_list": np.array(graph.graph.edges(), dtype=int).T,
    }
    for feature_type, matrix in composite_observer.features.items():
        observation[feature_type.value] = matrix
    return observation
