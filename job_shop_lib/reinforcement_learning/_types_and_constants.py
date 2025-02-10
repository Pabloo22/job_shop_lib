"""Contains types and enumerations used in the reinforcement learning
module."""

from enum import Enum
from typing import TypedDict

import numpy as np

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

    removed_nodes: np.ndarray
    edge_index: np.ndarray


class _ObservationDictOptional(TypedDict, total=False):
    """Optional fields for the observation dictionary."""

    operations: np.ndarray
    jobs: np.ndarray
    machines: np.ndarray


class ObservationDict(_ObservationDictRequired, _ObservationDictOptional):
    """A dictionary containing the observation of the environment.

    Required fields:
        removed_nodes (np.ndarray): Binary vector indicating removed nodes.
        edge_index (np.ndarray): Edge list in COO format.

    Optional fields:
        operations (np.ndarray): Matrix of operation features.
        jobs (np.ndarray): Matrix of job features.
        machines (np.ndarray): Matrix of machine features.
    """
