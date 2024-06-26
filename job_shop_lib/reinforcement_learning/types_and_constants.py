"""Contains types and enumerations used in the reinforcement learning
module."""

from enum import Enum
from typing import TypedDict, Required

import numpy as np

from job_shop_lib.dispatching.feature_observers import FeatureType


class GanttChartWrapperConfig(TypedDict, total=False):
    """Configuration for creating the plot function with the
    `plot_gantt_chart_wrapper` function."""

    title: str | None
    cmap: str
    show_available_operations: bool


class GifConfig(TypedDict, total=False):
    """Configuration for creating the GIF using the `create_gannt_chart_video`
    function."""

    gif_path: Required[str | None]
    fps: int
    remove_frames: bool
    frames_dir: str | None
    plot_current_time: bool


class VideoConfig(TypedDict, total=False):
    """Configuration for creating the video using the
    `create_gannt_chart_video` function."""

    video_path: str | None
    fps: int
    remove_frames: bool
    frames_dir: str | None
    plot_current_time: bool


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
