import itertools

from job_shop_lib import JobShopInstance
from job_shop_lib.graphs import JobShopGraph, NodeType, Node


def build_agent_task_graph_complete(instance: JobShopInstance) -> JobShopGraph:
    graph = build_agent_task_graph_with_jobs(instance)
    add_machine_nodes(graph)
    add_operation_machine_edges(graph)
    add_machine_machine_edges(graph)
    return graph


def build_agent_task_graph_with_jobs(
    instance: JobShopInstance,
) -> JobShopGraph:
    graph = build_agent_task_graph(instance)
    return graph


def build_agent_task_graph(instance: JobShopInstance) -> JobShopGraph:
    graph = JobShopGraph(instance)
    return graph


# BUILDING BLOCKS
# -----------------------------------------------------------------------------


# MACHINE NODES
# -------------
def add_machine_nodes(graph: JobShopGraph) -> None:
    for machine_id in range(graph.instance.num_machines):
        machine_node = Node.create_node_with_data(
            node_type=NodeType.MACHINE, data=machine_id
        )
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
        job_node = Node.create_node_with_data(
            node_type=NodeType.JOB, data=job_id
        )
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
