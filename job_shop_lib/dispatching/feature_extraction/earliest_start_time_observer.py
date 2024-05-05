"""Home of the `EarliestStartTimeObserver` class."""

import numpy as np

from job_shop_lib.graphs import NodeType
from job_shop_lib.dispatching.feature_extraction import (
    FeatureObserver,
)


class EarliestStartTimeObserver(FeatureObserver):
    """Observer that adds a feature indicating the earliest start time of
    each operation, machine, and job in the graph."""

    def initialize_features(self):
        """Initializes or resets the earliest start time features for all
        nodes."""
        self.node_features = {}
        for node_type in NodeType:
            self.node_features[node_type] = np.full(
                (len(self.graph.nodes_by_type[node_type]), 1),
                -1.0,
                dtype=np.float32,
            )
        self.update_features()

    def update_features(self):
        """Updates the features based on the current state of the
        dispatcher."""
        self._update_operation_nodes()
        self._update_machine_nodes()
        self._update_job_nodes()

    def _update_operation_nodes(self):
        """Updates the earliest start time for operation nodes."""
        for operation_node in self.graph.nodes_by_type[NodeType.OPERATION]:
            operation = operation_node.operation
            start_time = self.dispatcher.earliest_start_time(operation)
            # black formats is this way, see issue:
            # https://github.com/psf/black/issues/4349
            # pylint: disable=superfluous-parens
            self.node_features[NodeType.OPERATION][
                operation.operation_id, 0
            ] = (start_time - self.dispatcher.current_time())

    def _update_machine_nodes(self):
        """Updates the earliest start time for machine nodes."""
        for machine_id, start_time in enumerate(
            self.dispatcher.machine_next_available_time
        ):
            self.node_features[NodeType.MACHINE][machine_id, 0] = (
                start_time - self.dispatcher.current_time()
            )

    def _update_job_nodes(self):
        """Updates the earliest start time for job nodes."""
        for job_id, start_time in enumerate(
            self.dispatcher.job_next_available_time
        ):
            self.node_features[NodeType.JOB][job_id, 0] = (
                start_time - self.dispatcher.current_time()
            )
