"""Contains types and enumerations used in the reinforcement learning
module."""

from enum import Enum
from typing import TypedDict

import numpy as np
from numpy.typing import NDArray

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

    EDGE_INDEX = "edge_index_dict"
    NODE_FEATURES = "node_features_dict"

# NEW: TypedDict for the nested node features dictionary.
class NodeFeaturesDict(TypedDict, total=False):
    """A dictionary containing feature matrices for different node types.

    Keys correspond to FeatureType values (e.g., 'operations', 'jobs').
    Values are the corresponding feature matrices (num_nodes, num_features).
    """

    operations: NDArray[np.float32]
    jobs: NDArray[np.float32]
    machines: NDArray[np.float32]

class _ObservationDictRequired(TypedDict):
    """Required fields for the observation dictionary."""

    edge_index_dict: dict[tuple[str, str, str], NDArray[np.int32]]


# UPDATED: Now contains the nested dictionary for node features.
class _ObservationDictOptional(TypedDict, total=False):
    """Optional fields for the observation dictionary."""

    node_features_dict: NodeFeaturesDict


# UPDATED: Docstring now reflects the new nested structure.
class ObservationDict(_ObservationDictRequired, _ObservationDictOptional):
    """A dictionary containing the observation of the environment.

    This dictionary represents a heterogenous graph structure.

    Required fields:
        edge_index_dict: A dictionary mapping edge types
            (source_type, relation, destination_type) to their respective
            edge index tensors in COO format.

    Optional fields:
        node_features_dict: A dictionary mapping node type names (from
            FeatureType) to their corresponding feature matrices.
    """