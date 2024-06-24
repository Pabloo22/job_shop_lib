"""Contains types and enumerations used in the reinforcement learning 
module."""

from enum import Enum
from typing import TypedDict, Required

import numpy as np

from job_shop_lib.dispatching.feature_observers import FeatureType
from job_shop_lib.reinforcement_learning import (
    GanttChartWrapperConfig,
    VideoConfig,
    GifConfig,
)


class RenderConfig(TypedDict, total=False):
    """Configuration needed to initialize the `GanttChartCreator` class."""

    gantt_chart_wrapper_config: GanttChartWrapperConfig
    video_config: VideoConfig
    gif_config: GifConfig


class ObservationSpaceKey(str, Enum):
    """Enumeration of the keys for the observation space dictionary."""

    REMOVED_NODES = "removed_nodes"
    EDGE_INDEX = "edge_index"
    OPERATIONS = FeatureType.OPERATIONS.value
    JOBS = FeatureType.JOBS.value
    MACHINES = FeatureType.MACHINES.value


class ObservationDict(TypedDict, total=False):
    """A dictionary containing the observation of the environment."""

    removed_nodes: Required[np.ndarray]
    edge_index: Required[np.ndarray]
    operations: np.ndarray
    jobs: np.ndarray
    machines: np.ndarray
