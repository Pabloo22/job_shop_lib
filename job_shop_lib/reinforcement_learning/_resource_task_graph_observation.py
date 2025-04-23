"""Contains wrappers for the environments."""

from typing import TypeVar, TypedDict, Generic, Any
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

_NODE_TYPE_TO_FEATURE_TYPE = {
    NodeType.OPERATION: FeatureType.OPERATIONS,
    NodeType.MACHINE: FeatureType.MACHINES,
    NodeType.JOB: FeatureType.JOBS,
}
_FEATURE_TYPE_STR_TO_NODE_TYPE = {
    FeatureType.OPERATIONS.value: NodeType.OPERATION,
    FeatureType.MACHINES.value: NodeType.MACHINE,
    FeatureType.JOBS.value: NodeType.JOB,
}


class ResourceTaskGraphObservationDict(TypedDict):
    """Represents a dictionary for resource task graph observations."""

    edge_index_dict: dict[tuple[str, str, str], NDArray[np.int32]]
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

    Additionally, the node features are stored in a dictionary with keys
    corresponding to the node type names under the ``node_features_dict`` key.

    The node IDs are mapped to local IDs starting from 0. The
    ``original_ids_dict`` contains the original node IDs before removing nodes.

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
        self._start_from_zero_mapping: dict[str, dict[int, int]] = {}

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
        new_observation = self.observation(observation)
        new_info = self._info(info)
        return new_observation, reward, done, truncated, new_info

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
        new_observation = self.observation(observation)
        new_info = self._info(info)
        return new_observation, new_info

    def _info(self, info: dict[str, Any]) -> dict[str, Any]:
        """Updates the "available_operations_with_ids" key in the info
        dictionary so that they start from 0 using the
        `_start_from_zero_mapping` attribute.
        """
        new_available_operations_ids = []
        for operation_id, machine_id, job_id in info[
            "available_operations_with_ids"
        ]:
            if "operation" in self._start_from_zero_mapping:
                operation_id = self._start_from_zero_mapping["operation"][
                    operation_id
                ]
            if "machine" in self._start_from_zero_mapping:
                machine_id = self._start_from_zero_mapping["machine"][
                    machine_id
                ]
            if "job" in self._start_from_zero_mapping:
                job_id = self._start_from_zero_mapping["job"][job_id]
            new_available_operations_ids.append(
                (operation_id, machine_id, job_id)
            )
        info["available_operations_with_ids"] = new_available_operations_ids
        return info

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

    def observation(
        self, observation: ObservationDict
    ) -> ResourceTaskGraphObservationDict:
        """Processes the observation data into the resource task graph format.

        Args:
            observation: The observation dictionary. It must NOT have padding.

        Returns:
            A dictionary containing the following keys:

            - "edge_index_dict": A dictionary mapping edge types to edge index
              arrays.
            - "node_features_dict": A dictionary mapping node type names to
                node feature arrays.
            - "original_ids_dict": A dictionary mapping node type names to the
              original node IDs before removing nodes.
        """
        edge_index_dict = create_edge_type_dict(
            observation["edge_index"],
            type_ranges=self.type_ranges,
            relationship="to",
        )
        node_features_dict = self._create_node_features_dict(observation)
        node_features_dict, original_ids_dict = self._remove_nodes(
            node_features_dict, observation["removed_nodes"]
        )

        # mapping from global node ID to local node ID
        for key, edge_index in edge_index_dict.items():
            edge_index_dict[key] = map_values(
                edge_index, self.global_to_local_id
            )
        # mapping so that ids start from 0 in edge index
        self._start_from_zero_mapping = self._get_start_from_zero_mappings(
            original_ids_dict
        )
        for (type_1, to, type_2), edge_index in edge_index_dict.items():
            edge_index_dict[(type_1, to, type_2)][0] = map_values(
                edge_index[0], self._start_from_zero_mapping[type_1]
            )
            edge_index_dict[(type_1, to, type_2)][1] = map_values(
                edge_index[1], self._start_from_zero_mapping[type_2]
            )

        return {
            "edge_index_dict": edge_index_dict,
            "node_features_dict": node_features_dict,
            "original_ids_dict": original_ids_dict,
        }

    @staticmethod
    def _get_start_from_zero_mappings(
        original_indices_dict: dict[str, NDArray[np.int32]],
    ) -> dict[str, dict[int, int]]:
        mappings = {}
        for key, indices in original_indices_dict.items():
            mappings[key] = {idx: i for i, idx in enumerate(indices)}
        return mappings

    def _create_node_features_dict(
        self, observation: ObservationDict
    ) -> dict[str, NDArray]:
        """Creates a dictionary of node features for each node type.

        Args:
            observation: The observation dictionary.

        Returns:
            Dictionary mapping node type names to node features.
        """

        node_features_dict = {}
        for node_type, feature_type in _NODE_TYPE_TO_FEATURE_TYPE.items():
            if self.unwrapped.job_shop_graph.nodes_by_type[node_type]:
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
        node_features_dict: dict[str, NDArray[T]],
        removed_nodes: NDArray[np.bool_],
    ) -> tuple[dict[str, NDArray[T]], dict[str, NDArray[np.int32]]]:
        """Removes nodes from the node features dictionary.

        Args:
            node_features_dict: The node features dictionary.

        Returns:
            The node features dictionary with the nodes removed and a
            dictionary containing the original node ids.
        """
        removed_nodes_dict: dict[str, NDArray[T]] = {}
        original_ids_dict: dict[str, NDArray[np.int32]] = {}
        for feature_type, features in node_features_dict.items():
            node_type = _FEATURE_TYPE_STR_TO_NODE_TYPE[
                feature_type
            ].name.lower()
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
