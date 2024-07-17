"""Contains grah updater functions to update """

from collections.abc import Iterable

from job_shop_lib import Operation
from job_shop_lib.graphs import JobShopGraph


def remove_completed_operations(
    job_shop_graph: JobShopGraph,
    completed_operations: Iterable[Operation],
) -> None:
    """Removes the operation node of the scheduled operation from the graph.

    Args:
        graph:
            The job shop graph to update.
        dispatcher:
            The dispatcher instance.
    """
    for operation in completed_operations:
        node_id = operation.operation_id
        if job_shop_graph.removed_nodes[node_id]:
            continue
        job_shop_graph.remove_node(node_id)
