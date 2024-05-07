"""Home of the `DurationObserver` class."""

import numpy as np

from job_shop_lib import ScheduledOperation
from job_shop_lib.graphs import NodeType
from job_shop_lib.dispatching.feature_extraction import FeatureObserver


class DurationObserver(FeatureObserver):
    """Observer that adds a feature indicating the duration of operations,
    and the cumulative duration of upcoming operations for job and machine
    nodes."""

    def initialize_features(self):
        """Initializes or resets the duration features for all nodes."""
        mapping = {
            NodeType.OPERATION: self._initialize_operation_durations,
            NodeType.MACHINE: self._initialize_machine_durations,
            NodeType.JOB: self._initialize_job_durations,
        }
        self.node_features = {}
        for node_type in NodeType:
            self.node_features[node_type] = np.zeros(
                (len(self.graph.nodes_by_type[node_type]), 1),
                dtype=np.float32,
            )
            if node_type in mapping:
                mapping[node_type]()

    def _initialize_operation_durations(self):
        """Sets the duration of each operation node."""
        duration_matrix = self.dispatcher.instance.durations_matrix
        operation_durations = np.array(duration_matrix).reshape(-1, 1)
        self.node_features[NodeType.OPERATION] = operation_durations

    def _initialize_machine_durations(self):
        """Sets the cumulative duration of upcoming operations for each
        machine node."""
        machine_durations = self.dispatcher.instance.machine_loads
        for machine_node in self.graph.nodes_by_type[NodeType.MACHINE]:
            machine_id = machine_node.machine_id
            self.node_features[NodeType.MACHINE][machine_id, 0] = (
                machine_durations[machine_id]
            )

    def _initialize_job_durations(self):
        """Sets the cumulative duration of upcoming operations for each job
        node."""
        job_durations = self.dispatcher.instance.job_durations
        for job_node in self.graph.nodes_by_type[NodeType.JOB]:
            job_id = job_node.job_id
            self.node_features[NodeType.JOB][job_id, 0] = job_durations[job_id]

    def update(self, scheduled_operation: ScheduledOperation):
        """Updates the duration features of the nodes in the graph."""
        self._update_operation_durations(scheduled_operation)
        if NodeType.MACHINE in self.graph.nodes_by_type:
            self._update_machine_durations(scheduled_operation)
        if NodeType.JOB in self.graph.nodes_by_type:
            self._update_job_durations(scheduled_operation)

    def _update_operation_durations(
        self, scheduled_operation: ScheduledOperation
    ):
        """Updates the duration of the scheduled operation."""
        virtual_start_time = max(
            scheduled_operation.start_time, self.dispatcher.current_time()
        )
        new_duration = scheduled_operation.end_time - virtual_start_time
        operation_id = scheduled_operation.operation.operation_id
        self.node_features[NodeType.OPERATION][operation_id, 0] = new_duration

    def _update_machine_durations(
        self, scheduled_operation: ScheduledOperation
    ):
        """Updates the cumulative duration of upcoming operations for the
        machine of the scheduled operation."""
        operation_id = scheduled_operation.operation.operation_id
        operation_duration = self.node_features[NodeType.OPERATION][
            operation_id, 0
        ]
        self.node_features[NodeType.MACHINE][
            scheduled_operation.machine_id, 0
        ] -= operation_duration

    def _update_job_durations(self, scheduled_operation: ScheduledOperation):
        """Updates the cumulative duration of upcoming operations for the job
        of the scheduled operation."""
        operation_id = scheduled_operation.operation.operation_id
        operation_duration = self.node_features[NodeType.OPERATION][
            operation_id, 0
        ]
        job_id = scheduled_operation.job_id
        self.node_features[NodeType.JOB][job_id, 0] -= operation_duration
