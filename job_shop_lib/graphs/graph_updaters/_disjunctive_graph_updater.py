"""Home of the `ResidualGraphUpdater` class."""

from job_shop_lib import ScheduledOperation
from job_shop_lib.graphs.graph_updaters import (
    ResidualGraphUpdater,
)
from job_shop_lib.exceptions import ValidationError


class DisjunctiveGraphUpdater(ResidualGraphUpdater):
    """Updates the graph based on the completed operations.

    This observer updates the graph by removing the completed
    operation, machine and job nodes from the graph. It subscribes to the
    :class:`~job_shop_lib.dispatching.feature_observers.IsCompletedObserver`
    to determine which operations, machines and jobs have been completed.

    After an operation is dispatched, one of two disjunctive arcs that
    connected it with the previous operation is dropped. Similarly, the
    disjunctive arcs associated with the previous scheduled operation are
    removed.

    Attributes:
        remove_completed_machine_nodes:
            If ``True``, removes completed machine nodes from the graph.
        remove_completed_job_nodes:
            If ``True``, removes completed job nodes from the graph.

    Args:
        dispatcher:
            The dispatcher instance to observe.
        job_shop_graph:
            The job shop graph to update.
        subscribe:
            If ``True``, automatically subscribes the observer to the
            dispatcher. Defaults to ``True``.
        remove_completed_machine_nodes:
            If ``True``, removes completed machine nodes from the graph.
            Defaults to ``True``.
        remove_completed_job_nodes:
            If ``True``, removes completed job nodes from the graph.
            Defaults to ``True``.
    """

    def update(self, scheduled_operation: ScheduledOperation) -> None:
        """Updates the disjunctive graph.

        After an operation is dispatched, one of two arcs that connected it
        with the previous operation is dropped. Similarly, the disjunctive
        arcs associated with the previous scheduled operation are removed.

        Args:
            scheduled_operation:
                The scheduled operation that was dispatched.
        """
        super().update(scheduled_operation)
        machine_schedule = self.dispatcher.schedule.schedule[
            scheduled_operation.machine_id
        ]
        if len(machine_schedule) <= 1:
            return

        previous_scheduled_operation = machine_schedule[-2]

        # Remove the disjunctive arcs between the scheduled operation and the
        # previous operation
        scheduled_operation_node = self.job_shop_graph.nodes[
            scheduled_operation.operation.operation_id
        ]
        if (
            scheduled_operation_node.operation
            is not scheduled_operation.operation
        ):
            raise ValidationError(
                "Scheduled operation node does not match scheduled operation."
                "Make sure that the operation nodes have been the first to be "
                "added to the graph. This method assumes that the operation id"
                " and node id are the same."
            )
        scheduled_id = scheduled_operation_node.node_id
        assert scheduled_id == scheduled_operation.operation.operation_id
        previous_id = previous_scheduled_operation.operation.operation_id
        if self.job_shop_graph.is_removed(
            previous_id
        ) or self.job_shop_graph.is_removed(scheduled_id):
            return
        self.job_shop_graph.graph.remove_edge(scheduled_id, previous_id)

        # Now, remove all the disjunctive edges between the previous scheduled
        # operation and the other operations in the machine schedule
        operations_with_same_machine = (
            self.dispatcher.instance.operations_by_machine[
                scheduled_operation.machine_id
            ]
        )
        already_scheduled_operations = {
            scheduled_op.operation.operation_id
            for scheduled_op in machine_schedule
        }
        for operation in operations_with_same_machine:
            if operation.operation_id in already_scheduled_operations:
                continue
            self.job_shop_graph.graph.remove_edge(
                previous_id, operation.operation_id
            )
            self.job_shop_graph.graph.remove_edge(
                operation.operation_id, previous_id
            )
