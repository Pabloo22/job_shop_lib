"""Contains utility functions for updating the job shop graph."""

from collections.abc import Iterable

from job_shop_lib import Operation
from job_shop_lib.graphs import JobShopGraph, NodeType


def remove_completed_operations(
    job_shop_graph: JobShopGraph,
    completed_operations: Iterable[Operation],
) -> None:
    """Removes the operation node of the scheduled operation from the graph.

    Args:
        job_shop_graph:
            The job shop graph to update.
        dispatcher:
            The dispatcher instance.
    """
    for operation in completed_operations:
        if job_shop_graph.removed_nodes[NodeType.OPERATION.name.lower()][
            operation.operation_id
        ]:
            continue
        node_id = job_shop_graph.get_operation_node(
            operation.operation_id
        ).node_id
        job_shop_graph.remove_node(node_id)
