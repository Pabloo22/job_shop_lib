"""Contains wrappers for the environments."""

from typing import TypeVar, TypedDict, Generic
from gymnasium import ObservationWrapper
import numpy as np
from numpy.typing import NDArray

from job_shop_lib.reinforcement_learning import (
    ObservationDict,
    SingleJobShopGraphEnv,
    MultiJobShopGraphEnv,
    create_edge_type_dict,
    map_values,
)
from job_shop_lib.graphs import NodeType
from job_shop_lib.dispatching.feature_observers import FeatureType

T = TypeVar("T", bound=np.number)
EnvType = TypeVar(  # pylint: disable=invalid-name
    "EnvType", bound=SingleJobShopGraphEnv | MultiJobShopGraphEnv
)


class ResourceTaskGraphObservationDict(TypedDict):
    """Represents a dictionary for resource task graph observations."""

    edge_index_dict: dict[str, NDArray[np.int64]]
    node_features_dict: dict[str, NDArray[np.float32]]
    original_ids_dict: dict[str, NDArray[np.int32]]


# pylint: disable=line-too-long
class ResourceTaskGraphObservation(ObservationWrapper, Generic[EnvType]):
    """Observation wrapper that converts an observation following the
    :class:`ObservationDict` format to a format suitable to PyG's
    [`HeteroData`](https://pytorch-geometric.readthedocs.io/en/latest/generated/torch_geometric.data.HeteroData.html).

    In particular, the ``edge_index`` is converted into a ``edge_index_dict``
    with keys ``(node_type_i, "to", node_type_j)``. The ``node_type_i`` and
    ``node_type_j`` are the node types of the source and target nodes,
    respectively.

    Attributes:
        global_to_local_id: A dictionary mapping global node IDs to local node
            IDs for each node type.
        type_ranges: A dictionary mapping node type names to (start, end) index
            ranges.

    Args:
        env: The environment to wrap.
    """

    def __init__(self, env: EnvType):
        super().__init__(env)
        self.env = env  # Unnecessary, but makes mypy happy
        self.global_to_local_id = self._compute_id_mappings()
        self.type_ranges = self._compute_node_type_ranges()

    def step(self, action: tuple[int, int]):
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
        observation, reward, done, truncated, info = self.env.step(action)
        return self.observation(observation), reward, done, truncated, info

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        """Resets the environment.

        Args:
            seed:
                Added to match the signature of the parent class. It is not
                used in this method.
            options:
                Additional options to pass to the environment. Not used in
                this method.

        Returns:
            A tuple containing the following elements:

            - The observation of the environment.
            - A dictionary with additional information, keys
                include: "feature_names", the names of the features in the
                observation; and "available_operations_with_ids", a list of
                available a list of available actions in the form of
                (operation_id, machine_id, job_id).
        """
        observation, info = self.env.reset()
        return self.observation(observation), info

    def _compute_id_mappings(self) -> dict[int, int]:
        """Computes mappings from global node IDs to type-local IDs.

        Returns:
            A dictionary mapping global node IDs to local node IDs for each
            node type.
        """
        mappings = {}
        for node_type in NodeType:
            type_nodes = self.unwrapped.job_shop_graph.nodes_by_type[node_type]
            if not type_nodes:
                continue
            # Create mapping from global ID to local ID
            # (0 to len(type_nodes)-1)
            type_mapping = {
                node.node_id: local_id
                for local_id, node in enumerate(type_nodes)
            }
            mappings.update(type_mapping)

        return mappings

    def _compute_node_type_ranges(self) -> dict[str, tuple[int, int]]:
        """Computes index ranges for each node type.

        Returns:
            Dictionary mapping node type names to (start, end) index ranges
        """
        type_ranges = {}
        for node_type in NodeType:
            type_nodes = self.unwrapped.job_shop_graph.nodes_by_type[node_type]
            if not type_nodes:
                continue
            start = min(node.node_id for node in type_nodes)
            end = max(node.node_id for node in type_nodes) + 1
            type_ranges[node_type.name.lower()] = (start, end)

        return type_ranges

    def observation(self, observation: ObservationDict):
        edge_index_dict = create_edge_type_dict(
            observation["edge_index"],
            type_ranges=self.type_ranges,
            relationship="to",
        )
        # mapping from global node ID to local node ID
        for key, edge_index in edge_index_dict.items():
            edge_index_dict[key] = map_values(
                edge_index, self.global_to_local_id
            )
        node_features_dict = self._create_node_features_dict(observation)
        node_features_dict, original_ids_dict = self._remove_nodes(
            node_features_dict, observation["removed_nodes"]
        )

        return {
            "edge_index_dict": edge_index_dict,
            "node_features_dict": node_features_dict,
            "original_ids_dict": original_ids_dict,
        }

    def _create_node_features_dict(
        self, observation: ObservationDict
    ) -> dict[str, NDArray]:
        """Creates a dictionary of node features for each node type.

        Args:
            observation: The observation dictionary.

        Returns:
            Dictionary mapping node type names to node features.
        """
        node_type_to_feature_type = {
            NodeType.OPERATION: FeatureType.OPERATIONS,
            NodeType.MACHINE: FeatureType.MACHINES,
            NodeType.JOB: FeatureType.JOBS,
        }
        node_features_dict = {}
        for node_type, feature_type in node_type_to_feature_type.items():
            if node_type in self.unwrapped.job_shop_graph.nodes_by_type:
                node_features_dict[feature_type.value] = observation[
                    feature_type.value
                ]
                continue
            if feature_type != FeatureType.JOBS:
                continue
            assert FeatureType.OPERATIONS.value in observation
            job_features = observation[
                feature_type.value  # type: ignore[literal-required]
            ]
            job_ids_of_ops = [
                node.operation.job_id
                for node in self.unwrapped.job_shop_graph.nodes_by_type[
                    NodeType.OPERATION
                ]
            ]
            job_features_expanded = job_features[job_ids_of_ops]
            operation_features = observation[FeatureType.OPERATIONS.value]
            node_features_dict[FeatureType.OPERATIONS.value] = np.concatenate(
                (operation_features, job_features_expanded), axis=1
            )
        return node_features_dict

    def _remove_nodes(
        self,
        node_features_dict: dict[str, NDArray[np.float32]],
        removed_nodes: NDArray[np.bool_],
    ) -> tuple[dict[str, NDArray[np.float32]], dict[str, NDArray[np.int32]]]:
        """Removes nodes from the node features dictionary.

        Args:
            node_features_dict: The node features dictionary.

        Returns:
            The node features dictionary with the nodes removed and a
            dictionary containing the original node ids.
        """
        removed_nodes_dict: dict[str, NDArray[np.float32]] = {}
        original_ids_dict: dict[str, NDArray[np.int32]] = {}
        feature_type_to_node_type = {
            FeatureType.OPERATIONS.value: NodeType.OPERATION,
            FeatureType.MACHINES.value: NodeType.MACHINE,
            FeatureType.JOBS.value: NodeType.JOB,
        }
        for feature_type, features in node_features_dict.items():
            node_type = feature_type_to_node_type[feature_type].name.lower()
            if node_type not in self.type_ranges:
                continue
            start, end = self.type_ranges[node_type]
            removed_nodes_of_this_type = removed_nodes[start:end]
            removed_nodes_dict[node_type] = features[
                ~removed_nodes_of_this_type
            ]
            original_ids_dict[node_type] = np.where(
                ~removed_nodes_of_this_type
            )[0]

        return removed_nodes_dict, original_ids_dict

    @property
    def unwrapped(self) -> EnvType:
        """Returns the unwrapped environment."""
        return self.env  # type: ignore[return-value]
