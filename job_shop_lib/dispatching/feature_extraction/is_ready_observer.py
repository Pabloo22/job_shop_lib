"""Home of the `IsReadyObserver` class."""

import numpy as np

from job_shop_lib.graphs import NodeType
from job_shop_lib.dispatching.feature_extraction.feature_observer import (
    FeatureObserver,
)


class IsReadyObserver(FeatureObserver):
    """Feature creator that adds a binary feature indicating if the operation
    is ready to be dispatched."""

    def initialize_features(self):
        for node_type in self.graph.nodes_by_type:
            self._initialize_default_node_features(node_type)
            node_ids = self._get_ready_nodes(node_type)
            self.node_features[node_type][node_ids] = 1.0

    def _initialize_default_node_features(self, node_type: NodeType):
        self.node_features[node_type] = np.zeros(
            (len(self.graph.nodes_by_type[node_type]), 1),
            dtype=np.float32,
        )

    def _get_ready_nodes(self, node_type: NodeType) -> list[int]:
        mapping = {
            NodeType.OPERATION: self._get_ready_operation_nodes,
            NodeType.MACHINE: self.dispatcher.available_machines,
            NodeType.JOB: self.dispatcher.available_jobs,
        }
        if node_type not in mapping:
            return []
        return mapping[node_type]()

    def _get_ready_operation_nodes(self) -> list[int]:
        available_operations = self.dispatcher.available_operations()
        return [operation.operation_id for operation in available_operations]
