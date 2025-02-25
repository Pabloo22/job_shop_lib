"""Contains types and enumerations used in the reinforcement learning
module."""

from enum import Enum
from typing import TypedDict

import numpy as np
from numpy.typing import NDArray

from job_shop_lib.dispatching.feature_observers import FeatureType
from job_shop_lib.visualization.gantt import (
    PartialGanttChartPlotterConfig,
    GifConfig,
    VideoConfig,
)


class RenderConfig(TypedDict, total=False):
    """Configuration needed to initialize the `GanttChartCreator` class."""

    partial_gantt_chart_plotter_config: PartialGanttChartPlotterConfig
    video_config: VideoConfig
    gif_config: GifConfig


class ObservationSpaceKey(str, Enum):
    """Enumeration of the keys for the observation space dictionary."""

    REMOVED_NODES = "removed_nodes"
    EDGE_INDEX = "edge_index"
    OPERATIONS = FeatureType.OPERATIONS.value
    JOBS = FeatureType.JOBS.value
    MACHINES = FeatureType.MACHINES.value


class _ObservationDictRequired(TypedDict):
    """Required fields for the observation dictionary."""

    removed_nodes: NDArray[np.bool_]
    edge_index: NDArray[np.int32]


class _ObservationDictOptional(TypedDict, total=False):
    """Optional fields for the observation dictionary."""

    operations: NDArray[np.float32]
    jobs: NDArray[np.float32]
    machines: NDArray[np.float32]


class ObservationDict(_ObservationDictRequired, _ObservationDictOptional):
    """A dictionary containing the observation of the environment.

    Required fields:
        removed_nodes: Binary vector indicating removed nodes.
        edge_index: Edge list in COO format.

    Optional fields:
        operations: Matrix of operation features.
        jobs: Matrix of job features.
        machines: Matrix of machine features.
    """
