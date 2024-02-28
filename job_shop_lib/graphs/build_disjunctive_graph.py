import itertools

from job_shop_lib import JobShopInstance
from job_shop_lib.graphs import JobShopGraph, EdgeType, NodeType, Node


def build_disjunctive_graph(instance: JobShopInstance) -> JobShopGraph:
    graph = JobShopGraph(instance)
    add_disjunctive_edges(graph)
    add_conjunctive_edges(graph)
    add_source_sink_nodes(graph)
    add_source_sink_edges(graph)
    return graph


def add_disjunctive_edges(graph: JobShopGraph) -> None:
    """Adds disjunctive edges to the graph."""

    for machine in graph.nodes_by_machine:
        for node1, node2 in itertools.combinations(machine, 2):
            graph.add_edge(
                node1,
                node2,
                type=EdgeType.DISJUNCTIVE,
            )
            graph.add_edge(
                node2,
                node1,
                type=EdgeType.DISJUNCTIVE,
            )


def add_conjunctive_edges(graph: JobShopGraph) -> None:
    """Adds conjunctive edges to the graph."""

    for job_operations in graph.nodes_by_job:
        for i in range(1, len(job_operations)):
            graph.add_edge(
                job_operations[i - 1],
                job_operations[i],
                type=EdgeType.CONJUNCTIVE,
            )


def add_source_sink_nodes(graph: JobShopGraph) -> None:
    """Adds source and sink nodes to the graph."""
    source = Node(node_type=NodeType.SOURCE)
    sink = Node(node_type=NodeType.SINK)
    graph.add_node(source)
    graph.add_node(sink)


def add_source_sink_edges(graph: JobShopGraph) -> None:
    """Adds edges between source and sink nodes and operations."""
    source = graph.nodes_by_type[NodeType.SOURCE][0]
    sink = graph.nodes_by_type[NodeType.SINK][0]

    for job_operations in graph.nodes_by_job:
        graph.add_edge(source, job_operations[0], type=EdgeType.CONJUNCTIVE)
        graph.add_edge(job_operations[-1], sink, type=EdgeType.CONJUNCTIVE)
