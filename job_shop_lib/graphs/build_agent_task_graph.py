"""Contains functions to build agent task graphs.

The agent-task graph was introduced by Junyoung Park et al. (2021).
In contrast to the disjunctive graph, instead of connecting operations that
share the same resources directly by disjunctive edges, operation nodes are
connected with machine ones. All machine nodes are connected between them, and
all operation nodes from the same job are connected by non-directed edges too.

We also support a generalization of this approach by the addition of job nodes
and a global node. Job nodes are connected to all operation nodes of the same
job, and the global node is connected to all machine and job nodes.

References:
- Junyoung Park, Sanjar Bakhtiyar, and Jinkyoo Park. Schedulenet: Learn to
solve multi-agent scheduling problems with reinforcement learning. ArXiv,
abs/2106.03051, 2021.
"""

import itertools

from job_shop_lib import JobShopInstance
from job_shop_lib.graphs import JobShopGraph, NodeType, Node


def build_agent_task_graph_complete(instance: JobShopInstance) -> JobShopGraph:
    graph = JobShopGraph(instance)

    add_machine_nodes(graph)
    add_operation_machine_edges(graph)

    add_job_nodes(graph)
    add_operation_job_edges(graph)

    add_global_node(graph)
    add_machine_global_edges(graph)
    add_job_global_edges(graph)

    return graph


def build_agent_task_graph_with_jobs(
    instance: JobShopInstance,
) -> JobShopGraph:
    graph = JobShopGraph(instance)

    add_machine_nodes(graph)
    add_operation_machine_edges(graph)
    add_machine_machine_edges(graph)

    add_job_nodes(graph)
    add_operation_job_edges(graph)
    add_job_job_edges(graph)

    return graph


def build_agent_task_graph(instance: JobShopInstance) -> JobShopGraph:
    graph = JobShopGraph(instance)

    add_machine_nodes(graph)
    add_operation_machine_edges(graph)
    add_machine_machine_edges(graph)

    add_same_job_operations_edges(graph)

    return graph


# BUILDING BLOCKS
# -----------------------------------------------------------------------------


def add_same_job_operations_edges(graph: JobShopGraph) -> None:
    for job in graph.nodes_by_job:
        for operation1, operation2 in itertools.combinations(job, 2):
            graph.add_edge(operation1, operation2)
            graph.add_edge(operation2, operation1)


# MACHINE NODES
# -------------
def add_machine_nodes(graph: JobShopGraph) -> None:
    for machine_id in range(graph.instance.num_machines):
        machine_node = Node(node_type=NodeType.MACHINE, machine_id=machine_id)
        graph.add_node(machine_node)


def add_operation_machine_edges(graph: JobShopGraph) -> None:
    for machine_node in graph.nodes_by_type[NodeType.MACHINE]:
        operation_nodes_in_machine = graph.nodes_by_machine[
            machine_node.machine_id
        ]
        for operation_node in operation_nodes_in_machine:
            graph.add_edge(machine_node, operation_node)
            graph.add_edge(operation_node, machine_node)


def add_machine_machine_edges(graph: JobShopGraph) -> None:
    for machine1, machine2 in itertools.combinations(
        graph.nodes_by_type[NodeType.MACHINE], 2
    ):
        graph.add_edge(machine1, machine2)
        graph.add_edge(machine2, machine1)


# JOB NODES
# ---------
def add_job_nodes(graph: JobShopGraph) -> None:
    for job_id in range(graph.instance.num_jobs):
        job_node = Node(node_type=NodeType.JOB, job_id=job_id)
        graph.add_node(job_node)


def add_operation_job_edges(graph: JobShopGraph) -> None:
    for job_node in graph.nodes_by_type[NodeType.JOB]:
        operation_nodes_in_job = graph.nodes_by_job[job_node.job_id]
        for operation_node in operation_nodes_in_job:
            graph.add_edge(job_node, operation_node)
            graph.add_edge(operation_node, job_node)


def add_job_job_edges(graph: JobShopGraph) -> None:
    for job1, job2 in itertools.combinations(
        graph.nodes_by_type[NodeType.JOB], 2
    ):
        graph.add_edge(job1, job2)
        graph.add_edge(job2, job1)


# GLOBAL NODE
# -----------
def add_global_node(graph: JobShopGraph) -> None:
    global_node = Node(node_type=NodeType.GLOBAL)
    graph.add_node(global_node)


def add_machine_global_edges(graph: JobShopGraph) -> None:
    global_node = graph.nodes_by_type[NodeType.GLOBAL][0]
    for machine_node in graph.nodes_by_type[NodeType.MACHINE]:
        graph.add_edge(global_node, machine_node)
        graph.add_edge(machine_node, global_node)


def add_job_global_edges(graph: JobShopGraph) -> None:
    global_node = graph.nodes_by_type[NodeType.GLOBAL][0]
    for job_node in graph.nodes_by_type[NodeType.JOB]:
        graph.add_edge(global_node, job_node)
        graph.add_edge(job_node, global_node)
