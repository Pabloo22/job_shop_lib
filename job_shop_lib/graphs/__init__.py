"""Package for graph related classes and functions.

The main classes and functions available in this package are:

.. autosummary::
    JobShopGraph
    Node
    NodeType
    build_disjunctive_graph
    build_solved_disjunctive_graph
    build_resource_task_graph
    build_complete_resource_task_graph
    build_resource_task_graph_with_jobs

"""

from job_shop_lib.graphs._constants import EdgeType, NodeType
from job_shop_lib.graphs._node import Node
from job_shop_lib.graphs._job_shop_graph import JobShopGraph, NODE_ATTR
from job_shop_lib.graphs._build_disjunctive_graph import (
    build_disjunctive_graph,
    build_solved_disjunctive_graph,
    add_disjunctive_edges,
    add_conjunctive_edges,
    add_source_sink_nodes,
    add_source_sink_edges,
)
from job_shop_lib.graphs._build_resource_task_graphs import (
    build_resource_task_graph,
    build_complete_resource_task_graph,
    build_resource_task_graph_with_jobs,
    add_same_job_operations_edges,
    add_machine_nodes,
    add_operation_machine_edges,
    add_machine_machine_edges,
    add_job_nodes,
    add_operation_job_edges,
    add_global_node,
    add_machine_global_edges,
    add_job_global_edges,
)


__all__ = [
    "EdgeType",
    "NodeType",
    "Node",
    "JobShopGraph",
    "NODE_ATTR",
    "build_disjunctive_graph",
    "add_disjunctive_edges",
    "add_conjunctive_edges",
    "add_source_sink_nodes",
    "add_source_sink_edges",
    "build_resource_task_graph",
    "build_complete_resource_task_graph",
    "build_resource_task_graph_with_jobs",
    "add_same_job_operations_edges",
    "add_machine_nodes",
    "add_operation_machine_edges",
    "add_machine_machine_edges",
    "add_job_nodes",
    "add_operation_job_edges",
    "add_global_node",
    "add_machine_global_edges",
    "add_job_global_edges",
    "build_solved_disjunctive_graph",
]
